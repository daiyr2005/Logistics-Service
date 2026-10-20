import uvicorn
from fastapi import FastAPI
from mysite.admin.setup import setup_admin
from mysite.api import (
    warehouse, inventory, inventory_reservation, courier,
    courier_location, delivery, route, route_stop, tracking_event
)

app = FastAPI(title="GoodsLogistics")

app.include_router(warehouse.router)
app.include_router(inventory.router)
app.include_router(inventory_reservation.router)
app.include_router(courier.router)
app.include_router(courier_location.router)
app.include_router(delivery.router)
app.include_router(route.router)
app.include_router(route_stop.router)
app.include_router(tracking_event.router)

setup_admin(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)