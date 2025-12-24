"""
Database session dependency provider for FastAPI endpoints.
This module provides an asynchronous session generator that yields
SQLAlchemy async sessions for dependency injection in API routes.
The actual database CRUD operations are implemented in backend.database.crud
by the database development team (dev3). This module focuses solely on
session management and lifecycle.
"""         

from backend.database.session import get_db 
                       
async def get_session():
    async for s in get_db():
        yield s
