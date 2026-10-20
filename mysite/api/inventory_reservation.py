from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import InventoryReservation, Inventory
from mysite.db.schema import Message, InventoryReservationCreate, InventoryReservationUpdate, InventoryReservationSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/inventory-reservation", tags=["inventory-reservation"])

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

@router.get("/", response_model=list[InventoryReservationSchema])
def get_all(order_id: int | None = None, db: Session = Depends(get_db)):
    query = select(InventoryReservation)
    if order_id is not None:
        query = query.where(InventoryReservation.order_id == order_id)
    return db.scalars(query).all()

@router.get("/{reservation_id}", response_model=InventoryReservationSchema)
def get_one(reservation_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, InventoryReservation, reservation_id)

@router.post("/", response_model=Message[InventoryReservationSchema], status_code=201)
def create(data: InventoryReservationCreate, db: Session = Depends(get_db)):
    get_or_404(db, Inventory, data.inventory_id)
    obj = InventoryReservation(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Резервирование добавлено", "data": obj}

@router.put("/{reservation_id}", response_model=Message[InventoryReservationSchema])
def update(reservation_id: int, data: InventoryReservationUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, InventoryReservation, reservation_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Резервирование изменено", "data": obj}

@router.delete("/{reservation_id}", response_model=Message)
def delete(reservation_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, InventoryReservation, reservation_id))
    db.commit()
    return {"message": "Резервирование удалено"}