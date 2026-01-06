import asyncio
from app.db.models import Base, GameGenre, CharacterArchetype, SkillTree, StatSystem, DesignerProfile, InterviewQuestion
from app.db.session import engine, AsyncSessionLocal

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Seed Game Genres
        rpg = GameGenre(name="RPG", description="Role-Playing Game")
        fps = GameGenre(name="FPS", description="First Person Shooter")
        session.add_all([rpg, fps])
        await session.flush()

        # Seed Character Archetypes
        warrior = CharacterArchetype(name="Warrior", description="Strong melee fighter", genre=rpg)
        mage = CharacterArchetype(name="Mage", description="Master of magic", genre=rpg)
        sniper = CharacterArchetype(name="Sniper", description="Long-range shooter", genre=fps)
        session.add_all([warrior, mage, sniper])
        await session.flush()

        # Seed Skill Trees
        session.add_all([
            SkillTree(name="Sword Mastery", archetype=warrior, description="Skills for sword combat"),
            SkillTree(name="Elemental Magic", archetype=mage, description="Skills for elemental spells"),
            SkillTree(name="Sharpshooting", archetype=sniper, description="Skills for accuracy and range")
        ])
        await session.flush()

        # Seed Stat Systems
        session.add_all([
            StatSystem(name="Classic RPG Stats", description="STR, DEX, INT, etc.", archetype=warrior),
            StatSystem(name="Mana & Spell Power", description="Magic stats", archetype=mage),
            StatSystem(name="Accuracy & Stealth", description="Shooter stats", archetype=sniper)
        ])
        await session.flush()

        # Seed Designer Profiles
        designer = DesignerProfile(name="Alex Kim", experience_years=7, favorite_genre=rpg, bio="Loves deep character systems.")
        session.add(designer)
        await session.flush()

        # Seed Interview Questions
        session.add_all([
            InterviewQuestion(question="Describe your approach to designing a new character class.", category="General", difficulty="Medium"),
            InterviewQuestion(question="How do you balance skill trees for different archetypes?", category="Systems", difficulty="Hard", archetype=warrior),
            InterviewQuestion(question="What stats are most important for a mage?", category="Stats", difficulty="Easy", archetype=mage)
        ])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
