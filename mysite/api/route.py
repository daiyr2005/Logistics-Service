from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import Route, Courier
from mysite.db.schema import Message, RouteCreate, RouteUpdate, RouteSchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/route", tags=["route"])

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

@router.get("/", response_model=list[RouteSchema])
def get_all(courier_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Route)
    if courier_id is not None:
        query = query.where(Route.courier_id == courier_id)
    return db.scalars(query).all()

@router.get("/{route_id}", response_model=RouteSchema)
def get_one(route_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Route, route_id)

@router.post("/", response_model=Message[RouteSchema], status_code=201)
def create(data: RouteCreate, db: Session = Depends(get_db)):
    get_or_404(db, Courier, data.courier_id)
    obj = Route(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Маршрут добавлен", "data": obj}

@router.put("/{route_id}", response_model=Message[RouteSchema])
def update(route_id: int, data: RouteUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Route, route_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Маршрут изменён", "data": obj}

@router.delete("/{route_id}", response_model=Message)
def delete(route_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Route, route_id))
    db.commit()
    return {"message": "Маршрут удалён"}