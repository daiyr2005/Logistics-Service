from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import RouteStop, Route, Delivery
from mysite.db.schema import Message, RouteStopCreate, RouteStopUpdate, RouteStopSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/route-stop", tags=["route-stop"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_404(db, model, obj_id):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Не найдено")
    return obj

@router.get("/", response_model=list[RouteStopSchema])
def get_all(route_id: int | None = None, db: Session = Depends(get_db)):
    query = select(RouteStop)
    if route_id is not None:
        query = query.where(RouteStop.route_id == route_id)
    return db.scalars(query).all()

@router.get("/{stop_id}", response_model=RouteStopSchema)
def get_one(stop_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, RouteStop, stop_id)

@router.post("/", response_model=Message[RouteStopSchema], status_code=201)
def create(data: RouteStopCreate, db: Session = Depends(get_db)):
    get_or_404(db, Route, data.route_id)
    get_or_404(db, Delivery, data.delivery_id)
    obj = RouteStop(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Остановка маршрута добавлена", "data": obj}

@router.put("/{stop_id}", response_model=Message[RouteStopSchema])
def update(stop_id: int, data: RouteStopUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, RouteStop, stop_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Остановка маршрута изменена", "data": obj}

@router.delete("/{stop_id}", response_model=Message)
def delete(stop_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, RouteStop, stop_id))
    db.commit()
    return {"message": "Остановка маршрута удалена"}