import enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from mysite.db.db import Base

def utc_now():
    return datetime.now(timezone.utc)

class WarehouseStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"

class CourierTransportType(str, enum.Enum):
    walking = "walking"
    bicycle = "bicycle"
    motorcycle = "motorcycle"
    car = "car"

class CourierStatus(str, enum.Enum):
    offline = "offline"
    available = "available"
    busy = "busy"
    suspended = "suspended"

class ReservationStatus(str, enum.Enum):
    active = "active"
    committed = "committed"
    released = "released"
    expired = "expired"

class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    picked_up = "picked_up"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"
    failed = "failed"

class RouteStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class StopType(str, enum.Enum):
    pickup = "pickup"
    dropoff = "dropoff"

class RouteStopStatus(str, enum.Enum):
    pending = "pending"
    arrived = "arrived"
    completed = "completed"
    skipped = "skipped"

class Warehouse(Base):
    __tablename__ = "warehouses"
    __table_args__ = (CheckConstraint("capacity >= 0", name="ck_warehouse_capacity"),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city_id: Mapped[int] = mapped_column(Integer, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    street: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[WarehouseStatus] = mapped_column(Enum(WarehouseStatus), default=WarehouseStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    inventory: Mapped[list["Inventory"]] = relationship(back_populates="warehouse", cascade="all, delete-orphan")
    couriers: Mapped[list["Courier"]] = relationship(back_populates="warehouse")
    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="warehouse")

class Inventory(Base):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_inventory_warehouse_product"),
        CheckConstraint("quantity >= 0", name="ck_inventory_quantity"),
        CheckConstraint("reserved_quantity >= 0", name="ck_inventory_reserved_quantity"),
        CheckConstraint("reserved_quantity <= quantity", name="ck_inventory_reserved_lte_quantity"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    warehouse: Mapped["Warehouse"] = relationship(back_populates="inventory")
    reservations: Mapped[list["InventoryReservation"]] = relationship(back_populates="inventory")

class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_reservation_quantity"),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, index=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventories.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), default=ReservationStatus.active, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    inventory: Mapped["Inventory"] = relationship(back_populates="reservations")

class Courier(Base):
    __tablename__ = "couriers"
    __table_args__ = (CheckConstraint("max_active_orders >= 1", name="ck_courier_max_active_orders"),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True)
    transport_type: Mapped[CourierTransportType] = mapped_column(Enum(CourierTransportType))
    status: Mapped[CourierStatus] = mapped_column(Enum(CourierStatus), default=CourierStatus.offline, index=True)
    max_active_orders: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    warehouse: Mapped["Warehouse"] = relationship(back_populates="couriers")
    locations: Mapped[list["CourierLocation"]] = relationship(back_populates="courier", cascade="all, delete-orphan")
    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="courier")
    routes: Mapped[list["Route"]] = relationship(back_populates="courier")

class CourierLocation(Base):
    __tablename__ = "courier_locations"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("couriers.id", ondelete="CASCADE"), index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    courier: Mapped["Courier"] = relationship(back_populates="locations")

class Delivery(Base):
    __tablename__ = "deliveries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True)
    courier_id: Mapped[int | None] = mapped_column(ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True, index=True)
    tracking_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.pending, index=True)
    destination_address: Mapped[str] = mapped_column(Text)
    destination_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    destination_longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    estimated_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    warehouse: Mapped["Warehouse"] = relationship(back_populates="deliveries")
    courier: Mapped["Courier | None"] = relationship(back_populates="deliveries")
    route_stops: Mapped[list["RouteStop"]] = relationship(back_populates="delivery")
    tracking_events: Mapped[list["TrackingEvent"]] = relationship(back_populates="delivery", cascade="all, delete-orphan")

class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (
        CheckConstraint("total_distance_km >= 0", name="ck_route_total_distance"),
        CheckConstraint("estimated_duration_min >= 0", name="ck_route_estimated_duration"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    courier_id: Mapped[int] = mapped_column(ForeignKey("couriers.id", ondelete="RESTRICT"), index=True)
    status: Mapped[RouteStatus] = mapped_column(Enum(RouteStatus), default=RouteStatus.planned, index=True)
    total_distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    estimated_duration_min: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    courier: Mapped["Courier"] = relationship(back_populates="routes")
    stops: Mapped[list["RouteStop"]] = relationship(back_populates="route", cascade="all, delete-orphan", order_by="RouteStop.sequence")

class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "sequence", name="uq_route_stop_sequence"),
        CheckConstraint("sequence >= 1", name="ck_route_stop_sequence"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), index=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id", ondelete="RESTRICT"), index=True)
    stop_type: Mapped[StopType] = mapped_column(Enum(StopType))
    sequence: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7))
    status: Mapped[RouteStopStatus] = mapped_column(Enum(RouteStopStatus), default=RouteStopStatus.pending)
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    route: Mapped["Route"] = relationship(back_populates="stops")
    delivery: Mapped["Delivery"] = relationship(back_populates="route_stops")

class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id", ondelete="CASCADE"), index=True)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), index=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    delivery: Mapped["Delivery"] = relationship(back_populates="tracking_events")