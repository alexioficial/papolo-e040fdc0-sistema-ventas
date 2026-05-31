from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None


async def get_db():
    """Obtiene la instancia de la base de datos."""
    if client is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return client[settings.database_name]


async def connect_db():
    """Conecta a MongoDB de forma asíncrona."""
    global client
    client = AsyncIOMotorClient(settings.mongodb_uri)
    # Verify connection
    try:
        await client.admin.command("ping")
        print(f"✅ Conectado a MongoDB: {settings.mongodb_uri}")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        raise


async def close_db():
    """Cierra la conexión a MongoDB."""
    global client
    if client:
        client.close()
        client = None
        print("🔌 Conexión a MongoDB cerrada")
