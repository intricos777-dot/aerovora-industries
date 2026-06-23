import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

DB_PATH = os.getenv("AEROVORA_DB", "/home/sin/Projects/aerovora-industries/data/aerovora.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    IN_PRODUCTION = "in_production"
    IN_QC = "in_qc"
    IN_CALIBRATION = "in_calibration"
    IN_FLIGHT_TEST = "in_flight_test"
    IN_PACKAGING = "in_packaging"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)
    stripe_session_id = Column(String(255), unique=True, nullable=True)
    stripe_payment_intent = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_address = Column(Text, nullable=True)
    sku = Column(String(20), nullable=False)
    product_name = Column(String(255), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(SAEnum(OrderStatus), default=OrderStatus.PENDING_PAYMENT)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    shipping_tier = Column(String(50), default="standard")
    tracking_number = Column(String(255), nullable=True)
    carrier = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ProductionUnit(Base):
    __tablename__ = "production_units"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=True)
    serial_number = Column(String(50), unique=True, nullable=True)
    sku = Column(String(20), nullable=False)
    current_station = Column(Integer, default=0)
    station_history = Column(JSON, default=list)
    qc_passed = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="queued")


class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    component = Column(String(100), nullable=False)
    supplier = Column(String(100), nullable=True)
    sku = Column(String(50), unique=True, nullable=False)
    quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    unit_cost_cents = Column(Integer, nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    last_restocked = Column(DateTime, nullable=True)


class SupplierOrder(Base):
    __tablename__ = "supplier_orders"

    id = Column(Integer, primary_key=True)
    po_number = Column(String(20), unique=True, nullable=False)
    supplier = Column(String(100), nullable=False)
    component = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    received = Column(Integer, default=0)
    status = Column(String(50), default="pending")
    ordered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    received_at = Column(DateTime, nullable=True)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    tracking_number = Column(String(255), nullable=True)
    carrier = Column(String(50), nullable=False)
    shipping_tier = Column(String(50), default="standard")
    cost_cents = Column(Integer, nullable=True)
    status = Column(String(50), default="label_created")
    shipped_at = Column(DateTime, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
