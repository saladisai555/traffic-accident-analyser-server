from contextlib import asynccontextmanager
from app.database.mongo import connect_db, disconnect_db
from app.services.model_service import load_model


@asynccontextmanager
async def lifespan(app):
    print("Starting up...")
    try:
        await connect_db()
        load_model()
        print("All systems ready")
    except Exception as e:
        print(f"Startup failed: {e}")
        raise
    
    yield
    
    print("Shutting down...")
    try:
        await disconnect_db()
        print("Shutdown complete")
    except Exception as e:
        print(f"Shutdown error: {e}")
