from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import Courier, Warehouse
from mysite.db.schema import Message, CourierCreate, CourierUpdate, CourierSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/courier", tags=["courier"])

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

@router.get("/", response_model=list[CourierSchema])
def get_all(status: str | None = None, db: Session = Depends(get_db)):
    query = select(Courier)
    if status is not None:
        query = query.where(Courier.status == status)
    return db.scalars(query).all()

@router.get("/{courier_id}", response_model=CourierSchema)
def get_one(courier_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Courier, courier_id)

@router.post("/", response_model=Message[CourierSchema], status_code=201)
def create(data: CourierCreate, db: Session = Depends(get_db)):
    get_or_404(db, Warehouse, data.warehouse_id)
    obj = Courier(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Курьер добавлен", "data": obj}

@router.put("/{courier_id}", response_model=Message[CourierSchema])
def update(courier_id: int, data: CourierUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Courier, courier_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Курьер изменён", "data": obj}

@router.delete("/{courier_id}", response_model=Message)
def delete(courier_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Courier, courier_id))
    db.commit()
    return {"message": "Курьер удалён"}