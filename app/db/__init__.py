from .session import engine, get_db
from .models import Base

Base.metadata.create_all(bind=engine)
 