
"""
datanase functions should be provided by dev 3 in backend.database.crud
dev2 to add a proper description later 
"""           

from backend.database.session import get_db 
                       
async def get_session():
    async for s in get_db():
        yield s
