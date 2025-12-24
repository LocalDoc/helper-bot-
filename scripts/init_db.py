import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.session import engine
from backend.models.database import Base

if __name__ == "__main__":
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")