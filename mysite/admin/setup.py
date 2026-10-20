from fastapi import FastAPI
from sqladmin import Admin
from mysite.db.db import engine
from .views import (
    WarehouseAdmin,
    InventoryAdmin,
    InventoryReservationAdmin,
    CourierAdmin,
    CourierLocationAdmin,
    DeliveryAdmin,
    RouteAdmin,
    RouteStopAdmin,
    TrackingEventAdmin,
)

def setup_admin(user_app: FastAPI):
    admin = Admin(user_app, engine)
    admin.add_view(WarehouseAdmin)
    admin.add_view(InventoryAdmin)
    admin.add_view(InventoryReservationAdmin)
    admin.add_view(CourierAdmin)
    admin.add_view(CourierLocationAdmin)
    admin.add_view(DeliveryAdmin)
    admin.add_view(RouteAdmin)
    admin.add_view(RouteStopAdmin)
    admin.add_view(TrackingEventAdmin)