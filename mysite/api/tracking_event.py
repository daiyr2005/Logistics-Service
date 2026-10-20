from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import TrackingEvent, Delivery
from mysite.db.schema import Message, TrackingEventCreate, TrackingEventSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/tracking-event", tags=["tracking-event"])

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

@router.get("/", response_model=list[TrackingEventSchema])
def get_all(delivery_id: int | None = None, db: Session = Depends(get_db)):
    query = select(TrackingEvent)
    if delivery_id is not None:
        query = query.where(TrackingEvent.delivery_id == delivery_id)
    return db.scalars(query).all()

@router.get("/{event_id}", response_model=TrackingEventSchema)
def get_one(event_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, TrackingEvent, event_id)

@router.post("/", response_model=Message[TrackingEventSchema], status_code=201)
def create(data: TrackingEventCreate, db: Session = Depends(get_db)):
    get_or_404(db, Delivery, data.delivery_id)
    obj = TrackingEvent(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Событие отслеживания добавлено", "data": obj}

@router.delete("/{event_id}", response_model=Message)
def delete(event_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, TrackingEvent, event_id))
    db.commit()
    return {"message": "Событие отслеживания удалено"}