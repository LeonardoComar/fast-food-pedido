from fastapi import APIRouter, HTTPException
from app.models.database import SessionLocal
from app.models.tables import cliente
from app.models.schemas import Cliente

router = APIRouter()

@router.post("/cliente")
async def criar_cliente(cliente_data: Cliente):
    session = SessionLocal()
    try:
        insert_query = cliente.insert().values(**cliente_data.model_dump(exclude={"id"}))
        result = session.execute(insert_query)
        session.commit()
        return {"message": "Cliente criado com sucesso", "id": result.lastrowid}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()
