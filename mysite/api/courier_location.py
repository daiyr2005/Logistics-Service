from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import CourierLocation, Courier
from mysite.db.schema import Message, CourierLocationCreate, CourierLocationSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/courier-location", tags=["courier-location"])

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

@router.get("/", response_model=list[CourierLocationSchema])
def get_all(courier_id: int | None = None, db: Session = Depends(get_db)):
    query = select(CourierLocation)
    if courier_id is not None:
        query = query.where(CourierLocation.courier_id == courier_id)
    return db.scalars(query).all()

@router.get("/{location_id}", response_model=CourierLocationSchema)
def get_one(location_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, CourierLocation, location_id)

@router.post("/", response_model=Message[CourierLocationSchema], status_code=201)
def create(data: CourierLocationCreate, db: Session = Depends(get_db)):
    get_or_404(db, Courier, data.courier_id)
    obj = CourierLocation(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Локация курьера добавлена", "data": obj}

@router.delete("/{location_id}", response_model=Message)
def delete(location_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, CourierLocation, location_id))
    db.commit()
    return {"message": "Локация удалена"}