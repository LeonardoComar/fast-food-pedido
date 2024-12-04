from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://pedido_user:Mudar123!@db-servicos:3306/pedido"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)