
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


# =========================
# ENUMS
# =========================

class WarehouseStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class CourierTransportType(str, Enum):
    walking = "walking"
    bicycle = "bicycle"
    motorcycle = "motorcycle"
    car = "car"


class CourierStatus(str, Enum):
    offline = "offline"
    available = "available"
    busy = "busy"
    suspended = "suspended"


class ReservationStatus(str, Enum):
    active = "active"
    committed = "committed"
    released = "released"
    expired = "expired"


class DeliveryStatus(str, Enum):
    pending = "pending"
    assigned = "assigned"
    picked_up = "picked_up"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"
    failed = "failed"


class RouteStatus(str, Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class StopType(str, Enum):
    pickup = "pickup"
    dropoff = "dropoff"


class RouteStopStatus(str, Enum):
    pending = "pending"
    arrived = "arrived"
    completed = "completed"
    skipped = "skipped"


# =========================
# BASE
# =========================

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class Message(BaseModel, Generic[T]):
    message: str
    data: T


class DeleteMessage(BaseModel):
    message: str


# =========================
# WAREHOUSE
# =========================

class WarehouseBase(BaseModel):
    city_id: int
    code: str
    name: str
    street: str
    latitude: Decimal
    longitude: Decimal
    capacity: int = 0
    status: WarehouseStatus = WarehouseStatus.active


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    city_id: int | None = None
    code: str | None = None
    name: str | None = None
    street: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    capacity: int | None = None
    status: WarehouseStatus | None = None


class WarehouseSchema(WarehouseBase, ORMBase):
    id: int
    created_at: datetime


# =========================
# INVENTORY
# =========================

class InventoryBase(BaseModel):
    warehouse_id: int
    product_id: int
    quantity: int = 0
    reserved_quantity: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int | None = None
    reserved_quantity: int | None = None


class InventorySchema(InventoryBase, ORMBase):
    id: int
    updated_at: datetime


# =========================
# INVENTORY RESERVATION
# =========================

class InventoryReservationBase(BaseModel):
    order_id: int
    inventory_id: int
    quantity: int
    expires_at: datetime
    status: ReservationStatus = ReservationStatus.active


class InventoryReservationCreate(InventoryReservationBase):
    pass


class InventoryReservationUpdate(BaseModel):
    quantity: int | None = None
    status: ReservationStatus | None = None
    expires_at: datetime | None = None


class InventoryReservationSchema(InventoryReservationBase, ORMBase):
    id: int
    created_at: datetime


# =========================
# COURIER
# =========================

# user_id не принимается от клиента при создании.
# Он должен определяться по Access Token в API.
class CourierBase(BaseModel):
    warehouse_id: int
    transport_type: CourierTransportType
    status: CourierStatus = CourierStatus.offline
    max_active_orders: int = 3


class CourierCreate(CourierBase):
    pass


class CourierUpdate(BaseModel):
    warehouse_id: int | None = None
    transport_type: CourierTransportType | None = None
    status: CourierStatus | None = None
    max_active_orders: int | None = None


# user_id возвращается клиенту в ответе API.
class CourierSchema(CourierBase, ORMBase):
    id: int
    user_id: int
    created_at: datetime


# =========================
# COURIER LOCATION
# =========================

class CourierLocationBase(BaseModel):
    courier_id: int
    latitude: Decimal
    longitude: Decimal


class CourierLocationCreate(CourierLocationBase):
    pass


class CourierLocationSchema(CourierLocationBase, ORMBase):
    id: int
    recorded_at: datetime


# =========================
# DELIVERY
# =========================

class DeliveryBase(BaseModel):
    order_id: int
    warehouse_id: int
    courier_id: int | None = None
    tracking_code: str
    status: DeliveryStatus = DeliveryStatus.pending
    destination_address: str
    destination_latitude: Decimal
    destination_longitude: Decimal
    estimated_delivery_at: datetime | None = None
    delivered_at: datetime | None = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    courier_id: int | None = None
    status: DeliveryStatus | None = None
    destination_address: str | None = None
    destination_latitude: Decimal | None = None
    destination_longitude: Decimal | None = None
    estimated_delivery_at: datetime | None = None
    delivered_at: datetime | None = None


class DeliverySchema(DeliveryBase, ORMBase):
    id: int
    created_at: datetime


# =========================
# ROUTE
# =========================

class RouteBase(BaseModel):
    courier_id: int
    status: RouteStatus = RouteStatus.planned
    total_distance_km: Decimal = Decimal("0.00")
    estimated_duration_min: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    status: RouteStatus | None = None
    total_distance_km: Decimal | None = None
    estimated_duration_min: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RouteSchema(RouteBase, ORMBase):
    id: int
    created_at: datetime


# =========================
# ROUTE STOP
# =========================

class RouteStopBase(BaseModel):
    route_id: int
    delivery_id: int
    stop_type: StopType
    sequence: int
    latitude: Decimal
    longitude: Decimal
    status: RouteStopStatus = RouteStopStatus.pending
    arrived_at: datetime | None = None


class RouteStopCreate(RouteStopBase):
    pass


class RouteStopUpdate(BaseModel):
    status: RouteStopStatus | None = None
    sequence: int | None = None
    arrived_at: datetime | None = None


class RouteStopSchema(RouteStopBase, ORMBase):
    id: int


# =========================
# TRACKING EVENT
# =========================

class TrackingEventBase(BaseModel):
    delivery_id: int
    status: DeliveryStatus
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    description: str | None = None


class TrackingEventCreate(TrackingEventBase):
    pass


class TrackingEventSchema(TrackingEventBase, ORMBase):
    id: int
    created_at: datetime
