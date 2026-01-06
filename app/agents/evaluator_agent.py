import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class EvaluatorAgent:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        import os
        LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        LLM_BASE_URL = os.getenv("LLM_BASE_URL")
        self.llm = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_BASE_URL else AsyncOpenAI(api_key=LLM_API_KEY)

    async def evaluate(self, query: str, creative_answer: str, systems_answer: str) -> str:
        prompt = f"You are an expert interviewer. Given the following interview question and two candidate answers, select the best one or merge them for the most complete response.\n\nQuestion: {query}\n\nCreative Agent Answer:\n{creative_answer}\n\nSystems Agent Answer:\n{systems_answer}\n\nRespond with the best or a merged answer."
        try:
            response = await self.llm.chat.completions.create(
                model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are an expert interviewer and answer evaluator."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            # Deterministic merge fallback
            parts = [
                f"Interview response for: {query}",
                "",
                "(Creative)\n" + (creative_answer or ""),
                "",
                "(Systems)\n" + (systems_answer or ""),
                "",
                "Merged takeaway:",
                "I’d combine a strong character fantasy and readable combat loop (creative) with explicit balance levers and progression constraints (systems).",
            ]
            return "\n".join(parts)

    async def score(self, query: str, answer: str) -> float:
        prompt = f"Score the following answer to the interview question on a scale of 0 to 1.\n\nQuestion: {query}\nAnswer: {answer}\nScore:"
        response = await self.llm.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "system", "content": "You are a strict answer grader. Only return a number between 0 and 1."},
                      {"role": "user", "content": prompt}]
        )
        try:
            score = float(response.choices[0].message.content.strip())
        except Exception:
            score = 0.0
        return score
