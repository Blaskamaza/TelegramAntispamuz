from sqlmodel import SQLModel, create_engine, Session
from src.config import settings

# Handle 'postgres://' fix for SQLAlchemy if using Supabase connection string directly
db_url = settings.DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(db_url, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)