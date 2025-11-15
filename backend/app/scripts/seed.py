"""
Seed database with sample data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models import User, Template


async def seed_database():
    """Seed the database with initial data"""
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Create sample user
        user = User(
            email="demo@alfacopilot.com",
            full_name="Demo User",
            is_active=True
        )
        session.add(user)
        
        # Create sample templates
        templates = [
            Template(
                name="Договор аренды",
                description="Стандартный договор аренды помещения",
                content="ДОГОВОР АРЕНДЫ №...\n\nМежду {{landlord_name}} и {{tenant_name}}...",
                category="legal"
            ),
            Template(
                name="Коммерческое предложение",
                description="Шаблон КП для клиентов",
                content="КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ\n\n{{company_name}} предлагает...",
                category="commercial"
            ),
            Template(
                name="Акт выполненных работ",
                description="Акт для закрытия сделки",
                content="АКТ ВЫПОЛНЕННЫХ РАБОТ №...\n\nЗаказчик: {{client_name}}...",
                category="financial"
            )
        ]
        
        for template in templates:
            session.add(template)
        
        await session.commit()
        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
