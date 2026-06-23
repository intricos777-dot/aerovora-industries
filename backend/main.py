import os
import json
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from fastapi import FastAPI, Request, HTTPException, Depends, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
import stripe

from database import (
    init_db, get_db, SessionLocal, Order, ProductionUnit, InventoryItem,
    SupplierOrder, Shipment, OrderStatus, PaymentStatus
)

app = FastAPI(title="Aerovora Industries — Production & Fulfillment")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
BASE_URL = os.getenv("AEROVORA_BASE_URL", "http://0.0.0.0:8777")
SITE_URL = os.getenv("AEROVORA_SITE_URL", "https://intricos777-dot.github.io/aerovora-storefront")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

templates = Jinja2Templates(directory="/home/sin/Projects/aerovora-industries/backend/templates")


def next_order_number(db):
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    count = db.query(func.count(Order.id)).filter(
        Order.order_number.like(f"AV-{today}-%")
    ).scalar() or 0
    return f"AV-{today}-{count + 1:04d}"


def next_po_number(db):
    count = db.query(func.count(SupplierOrder.id)).scalar() or 0
    return f"PO-{count + 1:06d}"


def next_serial(sku):
    ts = datetime.now(timezone.utc).strftime("%y%m%d%H%M")
    return f"{sku}-{ts}"


STATIONS = [
    (0, "Queued", "Awaiting production start"),
    (1, "Parts Inbound & QA", "Component inspection station"),
    (2, "Sub-Assembly", "Motor, arm, flight controller assembly"),
    (3, "Final Assembly", "Full drone integration"),
    (4, "Calibration", "Sensor and payload calibration"),
    (5, "Flight Test", "32-point flight test sequence"),
    (6, "Pack & Label", "Foam packing, serialization, labeling"),
    (7, "Ready to Ship", "Finished goods — awaiting dispatch"),
]


@app.on_event("startup")
def startup():
    init_db()
    _seed_inventory()


def _seed_inventory():
    db = SessionLocal()
    try:
        if db.query(func.count(InventoryItem.id)).scalar() == 0:
            items = [
                InventoryItem(component="T-Motor MN4014", supplier="T-Motor", sku="MTR-4014", quantity=200, min_stock=50, unit_cost_cents=85000, lead_time_days=14),
                InventoryItem(component="Carbon Fiber Arm Set", supplier="DragonPlate", sku="CF-ARM-SET", quantity=80, min_stock=20, unit_cost_cents=420000, lead_time_days=21),
                InventoryItem(component="Jetson Orin NX 16GB", supplier="NVIDIA", sku="JETSON-ORNX-16", quantity=30, min_stock=10, unit_cost_cents=59900, lead_time_days=30),
                InventoryItem(component="6S 22,000mAh Battery", supplier="LiPoKing", sku="BAT-6S-22000", quantity=150, min_stock=40, unit_cost_cents=32000, lead_time_days=18),
                InventoryItem(component="Hyperspectral Camera Module", supplier="Sony Semi", sku="CAM-HYPER", quantity=25, min_stock=8, unit_cost_cents=180000, lead_time_days=28),
                InventoryItem(component="Pollination Wand Assembly", supplier="In-house", sku="PL-WAND", quantity=40, min_stock=15, unit_cost_cents=95000, lead_time_days=7),
                InventoryItem(component="Micro-Sprayer Module", supplier="In-house", sku="SPRAY-MICRO", quantity=35, min_stock=12, unit_cost_cents=72000, lead_time_days=7),
                InventoryItem(component="Fastener Kit (M3/M4/M5)", supplier="McMaster-Carr", sku="FST-KIT-234", quantity=500, min_stock=100, unit_cost_cents=2500, lead_time_days=3),
                InventoryItem(component="LiDAR Module", supplier="Sony Semi", sku="LIDAR-AV1", quantity=20, min_stock=5, unit_cost_cents=320000, lead_time_days=35),
                InventoryItem(component="Sample Collector", supplier="In-house", sku="SMPLR", quantity=30, min_stock=10, unit_cost_cents=45000, lead_time_days=7),
                InventoryItem(component="AV-1 Apis Scout (Finished)", supplier="Finished Goods", sku="FG-AV1-S", quantity=5, min_stock=2, unit_cost_cents=5800000, lead_time_days=0),
                InventoryItem(component="AV-1 Apis Pollinator (Finished)", supplier="Finished Goods", sku="FG-AV1-P", quantity=3, min_stock=1, unit_cost_cents=11000000, lead_time_days=0),
                InventoryItem(component="AV-1 Apis Complete (Finished)", supplier="Finished Goods", sku="FG-AV1-C", quantity=2, min_stock=1, unit_cost_cents=21000000, lead_time_days=0),
            ]
            db.add_all(items)
            db.commit()
    finally:
        db.close()


# ─── Stripe Webhook ─────────────────────────────────────────────────


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        event = json.loads(payload)

    event_type = event.get("type") if isinstance(event, dict) else event.type
    data = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object

    db = SessionLocal()
    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(data, db)
        elif event_type == "payment_intent.succeeded":
            _handle_payment_succeeded(data, db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

    return {"status": "ok"}


def _handle_checkout_completed(data, db):
    session_id = data.get("id")
    existing = db.query(Order).filter(Order.stripe_session_id == session_id).first()
    if existing:
        return

    try:
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=["line_items.data.price.product_data", "customer_details"],
        )
    except stripe.error.StripeError:
        return

    line_items = getattr(session, "line_items", None)
    items_data = line_items.get("data", []) if line_items else []
    if not items_data:
        return

    item = items_data[0]
    price = item.get("price", {}) if isinstance(item, dict) else item.price
    price_id = price.get("id", "") if isinstance(price, dict) else getattr(price, "id", "")

    product_data = None
    if isinstance(price, dict):
        product_data = price.get("product_data", {})
    else:
        pd = getattr(price, "product_data", None)
        product_data = pd if pd else {}

    sku = _map_stripe_price_to_sku(price_id)

    customer_details = getattr(session, "customer_details", None) or data.get("customer_details", {})
    if isinstance(customer_details, dict):
        cd = customer_details
    else:
        cd = {"email": getattr(customer_details, "email", ""), "name": getattr(customer_details, "name", "")}

    session_dict = session if isinstance(session, dict) else session.__dict__

    order = Order(
        order_number=next_order_number(db),
        stripe_session_id=session_id,
        stripe_payment_intent=getattr(session, "payment_intent", None) or data.get("payment_intent"),
        customer_email=cd.get("email", "unknown@example.com"),
        customer_name=cd.get("name", "Unknown"),
        sku=sku,
        product_name=product_data.get("name", "AV-1 Apis Drone") if isinstance(product_data, dict) else "AV-1 Apis Drone",
        amount_cents=item.get("amount_total", 0) if isinstance(item, dict) else getattr(item, "amount_total", 0),
        status=OrderStatus.PAYMENT_CONFIRMED,
        payment_status=PaymentStatus.CONFIRMED,
        shipping_tier=_infer_shipping_tier(session_dict.get("shipping_options", [])),
    )
    db.add(order)
    db.flush()

    _create_production_unit(order, db)


def _map_stripe_price_to_sku(price_id: str) -> str:
    mapping = {
        "price_1TkwfeAF5qKRqiGoQ7kRzUvv": "AV1-S",
        "price_1TkwffAF5qKRqiGoYpFNyE4K": "AV1-P",
        "price_1TkwfgAF5qKRqiGoAdSGnImi": "AV1-C",
        "price_1TkwfiAF5qKRqiGorNmHWTOP": "DaaS-SCOUT",
        "price_1TkwfjAF5qKRqiGoLjcHdZsR": "DaaS-GROWER",
        "price_1TkwfkAF5qKRqiGo1YpXvITW": "DaaS-SWARM",
    }
    return mapping.get(price_id, "AV1-S")


def _infer_shipping_tier(shipping_options):
    if not shipping_options:
        return "standard"
    selected = [s for s in shipping_options if s.get("selected")]
    if selected:
        amt = selected[0].get("amount", 0)
        if amt >= 45000:
            return "premium"
        elif amt >= 18500:
            return "express"
    return "standard"


def _handle_payment_succeeded(data, db):
    payment_intent = data.get("id")
    order = db.query(Order).filter(Order.stripe_payment_intent == payment_intent).first()
    if order:
        order.payment_status = PaymentStatus.CONFIRMED
        if order.status == OrderStatus.PENDING_PAYMENT:
            order.status = OrderStatus.PAYMENT_CONFIRMED
            _create_production_unit(order, db)


def _create_production_unit(order, db):
    daas_skus = ("DaaS-SCOUT", "DaaS-GROWER", "DaaS-SWARM")

    if order.sku in daas_skus:
        order.status = OrderStatus.PAYMENT_CONFIRMED
        return

    unit = ProductionUnit(
        order_id=order.id,
        sku=order.sku,
        serial_number=next_serial(order.sku),
        current_station=0,
        station_history=[],
        status="queued",
    )
    db.add(unit)

    if order.sku in ("FG-AV1-S", "FG-AV1-P", "FG-AV1-C") or order.sku.startswith("FG-"):
        unit.status = "ready_to_ship"
        unit.current_station = 7
        order.status = OrderStatus.IN_PACKAGING
    else:
        order.status = OrderStatus.IN_PRODUCTION


class OrderCreate(BaseModel):
    customer_email: str
    customer_name: str
    sku: str = "AV1-S"
    product_name: str = ""
    amount_cents: int
    currency: str = "usd"
    shipping_tier: str = "standard"


@app.post("/api/test-order")
def create_test_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    product_map = {"AV1-S": "AV-1 Apis Scout", "AV1-P": "AV-1 Apis Pollinator", "AV1-C": "AV-1 Apis Complete"}
    product = order_data.product_name or product_map.get(order_data.sku, "AV-1 Apis Drone")
    order = Order(
        order_number=next_order_number(db),
        customer_email=order_data.customer_email,
        customer_name=order_data.customer_name,
        sku=order_data.sku,
        product_name=product,
        amount_cents=order_data.amount_cents,
        currency=order_data.currency,
        status=OrderStatus.PAYMENT_CONFIRMED,
        payment_status=PaymentStatus.CONFIRMED,
        shipping_tier=order_data.shipping_tier,
    )
    db.add(order)
    db.flush()
    _create_production_unit(order, db)
    db.commit()
    return {"status": "ok", "order_number": order.order_number, "order_id": order.id}


@app.post("/api/orders/{order_id}/notes")
def update_order_notes(order_id: int, notes: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.notes = notes
    db.commit()
    return {"status": "ok"}


# ─── API Routes ──────────────────────────────────────────────────────


@app.get("/api/orders")
def list_orders(status: str = None, db: Session = Depends(get_db)):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.created_at.desc()).limit(100).all()
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer": o.customer_name,
            "email": o.customer_email,
            "product": o.product_name,
            "sku": o.sku,
            "amount": f"${o.amount_cents / 100:.2f}",
            "status": o.status.value,
            "payment": o.payment_status.value,
            "tracking": o.tracking_number,
            "created": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


@app.get("/api/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    unit = db.query(ProductionUnit).filter(ProductionUnit.order_id == o.id).first()
    shipment = db.query(Shipment).filter(Shipment.order_id == o.id).first()
    return {
        "order": {
            "id": o.id,
            "order_number": o.order_number,
            "customer_email": o.customer_email,
            "customer_name": o.customer_name,
            "sku": o.sku,
            "product_name": o.product_name,
            "amount_cents": o.amount_cents,
            "status": o.status.value if o.status else None,
            "payment_status": o.payment_status.value if o.payment_status else None,
            "tracking_number": o.tracking_number,
            "carrier": o.carrier,
            "shipping_tier": o.shipping_tier,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        },
        "production": {
            "serial_number": unit.serial_number if unit else None,
            "current_station": unit.current_station if unit else None,
            "station_name": STATIONS[unit.current_station][1] if unit and unit.current_station < len(STATIONS) else "N/A",
            "status": unit.status if unit else None,
        } if unit else None,
        "shipment": {
            "carrier": shipment.carrier if shipment else None,
            "tracking": shipment.tracking_number if shipment else None,
            "tier": shipment.shipping_tier if shipment else None,
            "status": shipment.status if shipment else None,
        } if shipment else None,
    }


@app.post("/api/orders/{order_id}/advance")
def advance_production(order_id: int, station: int = Query(..., description="Station number (0-7)"), db: Session = Depends(get_db)):
    unit = db.query(ProductionUnit).filter(ProductionUnit.order_id == order_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="No production unit for this order")

    if station < 0 or station > 7:
        raise HTTPException(status_code=400, detail="Station must be 0-7")
    if station < unit.current_station:
        raise HTTPException(status_code=400, detail="Cannot move backward")

    history = unit.station_history or []
    history.append({
        "station": station,
        "station_name": STATIONS[station][1],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    unit.station_history = history
    unit.current_station = station

    order = db.query(Order).filter(Order.id == order_id).first()
    station_map = {
        1: OrderStatus.IN_PRODUCTION,
        2: OrderStatus.IN_PRODUCTION,
        3: OrderStatus.IN_PRODUCTION,
        4: OrderStatus.IN_CALIBRATION,
        5: OrderStatus.IN_FLIGHT_TEST,
        6: OrderStatus.IN_PACKAGING,
        7: OrderStatus.IN_PACKAGING,
    }
    if station in station_map:
        order.status = station_map[station]

    if station == 7:
        unit.status = "ready_to_ship"

    db.commit()
    return {"status": "ok", "current_station": station, "station_name": STATIONS[station][1]}


@app.get("/api/production")
def production_status(db: Session = Depends(get_db)):
    units = db.query(ProductionUnit).order_by(ProductionUnit.id.desc()).limit(50).all()
    return [
        {
            "id": u.id,
            "serial": u.serial_number,
            "sku": u.sku,
            "station": u.current_station,
            "station_name": STATIONS[u.current_station][1] if u.current_station < len(STATIONS) else "Done",
            "status": u.status,
            "started": u.started_at.isoformat() if u.started_at else None,
        }
        for u in units
    ]


@app.get("/api/inventory")
def list_inventory(low_stock: bool = False, db: Session = Depends(get_db)):
    q = db.query(InventoryItem)
    if low_stock:
        q = q.filter(InventoryItem.quantity <= InventoryItem.min_stock)
    items = q.order_by(InventoryItem.component).all()
    return [
        {
            "id": i.id,
            "component": i.component,
            "supplier": i.supplier,
            "sku": i.sku,
            "quantity": i.quantity,
            "min_stock": i.min_stock,
            "unit_cost": f"${i.unit_cost_cents / 100:.2f}" if i.unit_cost_cents else "N/A",
            "lead_time_days": i.lead_time_days,
            "low_stock": i.quantity <= i.min_stock,
        }
        for i in items
    ]


@app.post("/api/inventory/receive")
def receive_stock(
    sku: str = Form(...),
    quantity: int = Form(..., ge=1),
    db: Session = Depends(get_db),
):
    item = db.query(InventoryItem).filter(InventoryItem.sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity += quantity
    item.last_restocked = datetime.now(timezone.utc)

    po = db.query(SupplierOrder).filter(
        SupplierOrder.component == item.component,
        SupplierOrder.status == "pending",
    ).first()
    if po:
        po.received += quantity
        if po.received >= po.quantity:
            po.status = "received"
            po.received_at = datetime.now(timezone.utc)

    db.commit()
    return {"status": "ok", "component": item.component, "new_quantity": item.quantity}


@app.get("/api/suppliers")
def list_supplier_orders(status: str = None, db: Session = Depends(get_db)):
    q = db.query(SupplierOrder)
    if status:
        q = q.filter(SupplierOrder.status == status)
    orders = q.order_by(SupplierOrder.ordered_at.desc()).all()
    return [
        {
            "id": o.id,
            "po": o.po_number,
            "supplier": o.supplier,
            "component": o.component,
            "quantity": o.quantity,
            "received": o.received,
            "status": o.status,
            "ordered": o.ordered_at.isoformat() if o.ordered_at else None,
        }
        for o in orders
    ]


@app.post("/api/suppliers/order")
def create_supplier_order(
    supplier: str = Form(...),
    component: str = Form(...),
    quantity: int = Form(..., ge=1),
    db: Session = Depends(get_db),
):
    po = SupplierOrder(
        po_number=next_po_number(db),
        supplier=supplier,
        component=component,
        quantity=quantity,
    )
    db.add(po)
    db.commit()
    return {"status": "ok", "po_number": po.po_number}


@app.post("/api/ship/{order_id}")
def create_shipment(
    order_id: int,
    carrier: str = Form("FedEx"),
    tracking: str = Form(""),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    unit = db.query(ProductionUnit).filter(ProductionUnit.order_id == order_id).first()
    if unit:
        unit.status = "shipped"

    order.status = OrderStatus.SHIPPED
    order.tracking_number = tracking
    order.carrier = carrier

    shipment = Shipment(
        order_id=order_id,
        tracking_number=tracking,
        carrier=carrier,
        shipping_tier=order.shipping_tier,
        status="shipped",
        shipped_at=datetime.now(timezone.utc),
        estimated_delivery=datetime.now(timezone.utc) + timedelta(days=5 if order.shipping_tier == "standard" else 2),
    )
    db.add(shipment)
    db.commit()
    return {"status": "ok", "order": order.order_number, "carrier": carrier, "tracking": tracking}


@app.get("/api/status")
def system_status(db: Session = Depends(get_db)):
    order_count = db.query(func.count(Order.id)).scalar()
    pending_orders = db.query(func.count(Order.id)).filter(Order.status.in_([
        OrderStatus.PAYMENT_CONFIRMED, OrderStatus.IN_PRODUCTION
    ])).scalar()
    in_production = db.query(func.count(ProductionUnit.id)).filter(
        ProductionUnit.status.notin_(["shipped", "ready_to_ship"])
    ).scalar()
    ready_to_ship = db.query(func.count(ProductionUnit.id)).filter(
        ProductionUnit.status == "ready_to_ship"
    ).scalar()
    low_stock = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity <= InventoryItem.min_stock
    ).scalar()
    revenue = db.query(func.sum(Order.amount_cents)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0

    return {
        "total_orders": order_count,
        "pending_fulfillment": pending_orders,
        "in_production": in_production,
        "ready_to_ship": ready_to_ship,
        "low_stock_items": low_stock,
        "revenue_cents": revenue,
        "revenue": f"${revenue / 100:.2f}",
    }


# ─── Dashboard Pages ────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    status = _dashboard_data(db)
    return templates.TemplateResponse(request, "dashboard.html", {"request": request, **status})


@app.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse(request, "orders.html", {"request": request, "orders": orders, "stations": STATIONS})


@app.get("/production", response_class=HTMLResponse)
def production_page(request: Request, db: Session = Depends(get_db)):
    units = db.query(ProductionUnit).order_by(ProductionUnit.id.desc()).all()
    return templates.TemplateResponse(request, "production.html", {"request": request, "units": units, "stations": STATIONS})


@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(InventoryItem).order_by(InventoryItem.component).all()
    return templates.TemplateResponse(request, "inventory.html", {"request": request, "items": items})


def _dashboard_data(db):
    total = db.query(func.count(Order.id)).scalar() or 0
    pending = db.query(func.count(Order.id)).filter(Order.status.in_([
        OrderStatus.PAYMENT_CONFIRMED, OrderStatus.IN_PRODUCTION
    ])).scalar() or 0
    shipped = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.SHIPPED).scalar() or 0
    in_prod = db.query(func.count(ProductionUnit.id)).filter(
        ProductionUnit.status.notin_(["shipped", "ready_to_ship"])
    ).scalar() or 0
    rts = db.query(func.count(ProductionUnit.id)).filter(
        ProductionUnit.status == "ready_to_ship"
    ).scalar() or 0
    low = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity <= InventoryItem.min_stock
    ).scalar() or 0
    rev = db.query(func.sum(Order.amount_cents)).filter(
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0
    recent = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    return {
        "total_orders": total,
        "pending": pending,
        "shipped": shipped,
        "in_production": in_prod,
        "ready_to_ship": rts,
        "low_stock": low,
        "revenue": rev,
        "revenue_display": f"${rev / 100:,.2f}",
        "recent_orders": recent,
        "stations": STATIONS,
    }
