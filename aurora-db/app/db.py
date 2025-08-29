from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# HOST:gateway01.us-east-1.prod.aws.tidbcloud.com

# PORT:4000

# USERNAME: 3Eo7CXZzQYFQ3i5.root

# PASSWORD:sgCKlsXv6OhBfMta

# DATABASE:aurora

#Feo eso quemado 😤
USER = "3Eo7CXZzQYFQ3i5.root"
PASSWORD = "sgCKlsXv6OhBfMta"
HOST = "gateway01.us-east-1.prod.aws.tidbcloud.com"
PORT = 4000
DB = "aurora"

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

# Crear conexión
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency de DB (para inyectar en rutas)
def get_aurora_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()