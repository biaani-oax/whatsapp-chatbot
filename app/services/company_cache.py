from app.database.connection import get_pool

COMPANY_CACHE = {}


async def load_company_cache():
    """Carga el conocimiento empresarial activo desde PostgreSQL."""

    global COMPANY_CACHE

    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT knowledge_key, category, content
            FROM company_knowledge
            WHERE is_active = TRUE
            ORDER BY category, knowledge_key;
        """)

    COMPANY_CACHE = {
        row["knowledge_key"]: {
            "category": row["category"],
            "content": row["content"]
        }
        for row in rows
    }

    print(
        f"Conocimiento de Biaani cargado en memoria: "
        f"{len(COMPANY_CACHE)} registros."
    )


def get_company_context():
    """Devuelve el conocimiento empresarial disponible."""

    return COMPANY_CACHE.copy()