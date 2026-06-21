# Logistics & Supply Chain — Aerovora Industries

## Shipping & Receiving Operations

---

### Receiving Dock (Inbound)

**Location:** AeroFab-1, Dock A (4 receiving bays)

**Process Flow:**
```
[Carrier Arrival] → [RFID Gate Scan] → [Bay Assignment] → [Unload (robotic forklift)] → [QA Triage] → [Put-away (ASRS)]
```

| Step | Agent/System | Detail |
|------|-------------|--------|
| Arrival scan | Log-Arrival AI | Reads carrier barcode, cross-references PO, assigns bay |
| Unload | Robotic forklifts (2x) | Autonomous pallet movement, 30 pallets/hour each |
| QA triage | QA inspection robot | Visual scan, weight check, temp/humidity logger read |
| Put-away | ASRS (Automated Storage & Retrieval) | 15,000 bin locations, random-access retrieval under 90s |

**Supplier Network:**
| Component | Supplier | Lead Time | Min Stock |
|-----------|----------|-----------|-----------|
| Motors | T-Motor (CN) | 14 days | 500 units |
| Carbon fiber arms | DragonPlate (US) | 21 days | 200 sets |
| Jetson Orin | NVIDIA (direct) | 30 days | 100 units |
| Batteries | LiPoKing (KR) | 18 days | 400 units |
| Cameras | Sony Semi (JP) | 28 days | 300 units |
| Fasteners + hardware | McMaster-Carr (US) | 3 days | 10,000 units |

---

### Shipping Dock (Outbound)

**Location:** AeroFab-1, Dock B (6 shipping bays)

**Process Flow:**
```
[Order Received] → [Pick from Finished Goods] → [Pack & Label] → [Carrier Dispatch] → [Customer Notification]
```

| Step | Agent/System | Detail |
|------|-------------|--------|
| Order processing | Log-Order AI | Validates payment, checks stock, reserves unit, creates picklist |
| Pick | Robotic arm AV-1-07 | Retrieves from finished goods rack (2,000 unit capacity) |
| Pack | Pack robot | Custom foam insert, accessories kit, documentation, seal |
| Label | Print + apply | Shipping label, return label, regulatory stickers |
| Dispatch | Log-Dispatch AI | Carrier assignment (FedEx/UPS/DHL by destination/weight), pickup window scheduling |

**Shipping Options:**
| Service | Cost | Transit | Insurance |
|---------|------|---------|-----------|
| Standard (ground) | $75 | 3-5 days | $5,000 included |
| Express (air) | $185 | 1-2 days | $10,000 included |
| Premium (white glove) | $450 | 2-3 days | Full replacement, on-site setup |

---

### Inventory Management

| System | Detail |
|--------|--------|
| WMS | Automated via Log-Inventory AI |
| Reorder Point | Calculated per component (demand + lead time + safety stock) |
| Cycle Counting | Autonomous drone inventory scan nightly |
| Obsolescence | 180-day slow-move flag, auto-discount for clearance |
| Fulfillment target | 98.5% same-day ship, 99.8% within 24h |

---

### Warehouse Layout (AeroFab-1)

```
┌────────────────────────────────────────────────────────────────────┐
│  Receiving Dock A    │  ASRS (15K bins)  │  Shipping Dock B      │
│  [Bay1][Bay2]        │  ┌──────────────┐ │  [Bay1][Bay2][Bay3]   │
│  [Bay3][Bay4]        │  │ 30ft tall    │ │  [Bay4][Bay5][Bay6]   │
├──────────────────────┤  │ Auto-retrieve│ ├───────────────────────┤
│  QA Lab              │  └──────────────┘ │  Finished Goods (2K)  │
│  Component Testing   │                    │  Packing Station      │
├──────────────────────┴────────────────────┴───────────────────────┤
│  Production Floor (see production/pipeline.md)                    │
└───────────────────────────────────────────────────────────────────┘
```

---

### AI Logistics Agents

| Agent | Function |
|-------|----------|
| Log-Arrival | Inbound carrier management, dock scheduling, ASRS put-away orchestration |
| Log-Order | Order lifecycle management, picklist generation, customer comms |
| Log-Inventory | Stock level tracking, reorder calculation, cycle counting |
| Log-Dispatch | Carrier assignment, label generation, pickup scheduling |
| Log-Fleet | Service drone fleet logistics — battery swap scheduling, field service routing |
