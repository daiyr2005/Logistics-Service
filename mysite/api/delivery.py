from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import Delivery, Warehouse, Courier
from mysite.db.schema import Message, DeliveryCreate, DeliveryUpdate, DeliverySchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/delivery", tags=["delivery"])

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

@router.get("/", response_model=list[DeliverySchema])
def get_all(status: str | None = None, order_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Delivery)
    if status is not None:
        query = query.where(Delivery.status == status)
    if order_id is not None:
        query = query.where(Delivery.order_id == order_id)
    return db.scalars(query).all()

@router.get("/{delivery_id}", response_model=DeliverySchema)
def get_one(delivery_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Delivery, delivery_id)

@router.post("/", response_model=Message[DeliverySchema], status_code=201)
def create(data: DeliveryCreate, db: Session = Depends(get_db)):
    get_or_404(db, Warehouse, data.warehouse_id)
    if data.courier_id is not None:
        get_or_404(db, Courier, data.courier_id)
    obj = Delivery(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Доставка добавлена", "data": obj}

@router.put("/{delivery_id}", response_model=Message[DeliverySchema])
def update(delivery_id: int, data: DeliveryUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Delivery, delivery_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Доставка изменена", "data": obj}

@router.delete("/{delivery_id}", response_model=Message)
def delete(delivery_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Delivery, delivery_id))
    db.commit()
    return {"message": "Доставка удалена"}