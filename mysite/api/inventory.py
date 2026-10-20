from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import Inventory, Warehouse
from mysite.db.schema import Message, InventoryCreate, InventoryUpdate, InventorySchema
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/inventory", tags=["inventory"])

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

@router.get("/", response_model=list[InventorySchema])
def get_all(warehouse_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Inventory)
    if warehouse_id is not None:
        query = query.where(Inventory.warehouse_id == warehouse_id)
    return db.scalars(query).all()

@router.get("/{inventory_id}", response_model=InventorySchema)
def get_one(inventory_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Inventory, inventory_id)

@router.post("/", response_model=Message[InventorySchema], status_code=201)
def create(data: InventoryCreate, db: Session = Depends(get_db)):
    get_or_404(db, Warehouse, data.warehouse_id)
    obj = Inventory(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"message": "Остаток добавлен", "data": obj}

@router.put("/{inventory_id}", response_model=Message[InventorySchema])
def update(inventory_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Inventory, inventory_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Остаток изменён", "data": obj}

@router.delete("/{inventory_id}", response_model=Message)
def delete(inventory_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Inventory, inventory_id))
    db.commit()
    return {"message": "Остаток удалён"}