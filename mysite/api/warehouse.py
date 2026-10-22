from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from mysite.db.model import Warehouse
from mysite.db.schema import Message, WarehouseCreate, WarehouseUpdate, WarehouseSchema, DeleteMessage
from mysite.db.db import SessionLocal

router = APIRouter(prefix="/warehouse", tags=["warehouse"])

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

@router.get("/", response_model=list[WarehouseSchema])
def get_all(db: Session = Depends(get_db)):
    return db.scalars(select(Warehouse)).all()

@router.get("/{warehouse_id}", response_model=WarehouseSchema)
def get_one(warehouse_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Warehouse, warehouse_id)

@router.post("/", response_model=Message[WarehouseSchema], status_code=201)
def create(data: WarehouseCreate, db: Session = Depends(get_db)):
    obj = Warehouse(**data.model_dump())

    db.add(obj)
    db.commit()
    db.refresh(obj)

    return {
        "message": "Склад добавлен",
        "data": obj
    }

@router.put("/{warehouse_id}", response_model=Message[WarehouseSchema])
def update(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Warehouse, warehouse_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return {"message": "Склад изменён", "data": obj}



from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Импортируй DeleteMessage из своего файла схем
# Например:
# from mysite.schemas.warehouse import DeleteMessage


@router.delete("/{warehouse_id}", response_model=DeleteMessage)
def delete(
    warehouse_id: int,
    db: Session = Depends(get_db)
):
    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.id == warehouse_id)
        .first()
    )

    if warehouse is None:
        raise HTTPException(
            status_code=404,
            detail="Склад не найден"
        )

    db.delete(warehouse)
    db.commit()

    return {
        "message": "Склад успешно удалён"
    }
