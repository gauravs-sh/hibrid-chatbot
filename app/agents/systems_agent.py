from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import GameGenre, CharacterArchetype, SkillTree, StatSystem, InterviewQuestion
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class SystemsAgent:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        from dotenv import load_dotenv
        load_dotenv()
        import os
        LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        LLM_BASE_URL = os.getenv("LLM_BASE_URL")
        self.llm = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_BASE_URL else AsyncOpenAI(api_key=LLM_API_KEY)

    async def answer(self, query: str) -> str:
        # Simple logic: search for keywords and query relevant tables
        if "genre" in query.lower():
            result = await self.db_session.execute(select(GameGenre))
            genres = result.scalars().all()
            context = "\n".join([f"{g.name}: {g.description}" for g in genres])
        elif "archetype" in query.lower():
            result = await self.db_session.execute(select(CharacterArchetype))
            archetypes = result.scalars().all()
            context = "\n".join([f"{a.name}: {a.description}" for a in archetypes])
        elif "skill" in query.lower():
            result = await self.db_session.execute(select(SkillTree))
            skills = result.scalars().all()
            context = "\n".join([f"{s.name}: {s.description}" for s in skills])
        elif "stat" in query.lower():
            result = await self.db_session.execute(select(StatSystem))
            stats = result.scalars().all()
            context = "\n".join([f"{s.name}: {s.description}" for s in stats])
        elif "question" in query.lower():
            result = await self.db_session.execute(select(InterviewQuestion))
            questions = result.scalars().all()
            context = "\n".join([q.question for q in questions])
        else:
            context = "No relevant structured data found."
        # Prefer LLM if available, but fall back to deterministic response when quota/auth fails.
        prompt = (
            "You are a systems-focused game designer. Use the following structured data to answer the interview question "
            "as precisely as possible.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}"
        )
        try:
            response = await self.llm.chat.completions.create(
                model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a systems/constraints expert."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            # Deterministic fallback (no external LLM)
            lines = [
                "Systems / Constraints answer (LLM fallback):",
                "- Requirements: clear archetype role, progression pacing, and balance levers.",
                "- Use structured data below to justify choices.",
                "",
                "Structured context:",
                context,
                "",
                "Answer:",
                f"For '{query}', I would define the core role, then choose a stat system + skill tree with clear trade-offs. "
                "Balance by tuning resource costs, cooldowns, and scaling curves; validate against comparable archetypes in the DB.",
            ]
            return "\n".join(lines)
