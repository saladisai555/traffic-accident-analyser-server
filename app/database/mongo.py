from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def connect_db():
    global client, db
    if not settings.mongo_url:
        print("MongoDB URL not configured, skipping connection")
        return
    
    try:
        client = AsyncIOMotorClient(
            settings.mongo_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=1,
        )
        db = client[settings.mongo_db]
        await client.admin.command('ping')
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Troubleshooting tips:")
        print("1. Ensure your IP is whitelisted in MongoDB Atlas")
        print("2. Check network/firewall allows outbound connections to MongoDB")
        print("3. Verify MongoDB credentials are correct")
        print("4. Try using a local MongoDB instance for development")


async def disconnect_db():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_db():
    if db is None:
        raise RuntimeError("Database not connected")
    return db