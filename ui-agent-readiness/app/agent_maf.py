"""Day 4 optional: REAL Microsoft Agent Framework tool-calling agent.
Run: python -m app.agent_maf
Requires: pip install -r requirements-optional.txt and Azure OpenAI chat deployment.
Microsoft Agent Framework changes rapidly: verify latest official samples if imports move.
"""
import asyncio
import os
from dotenv import load_dotenv
from app.logic import calculate_emi
from app.retrieval import retrieve

load_dotenv()


def find_bank_policy(query: str) -> str:
    """Look up a bank policy by keywords and return grounded source excerpts."""
    matches = retrieve(query)
    return "\n".join(f"{m['id']}: {m['content']}" for m in matches) or "No policy found"


def estimate_loan_emi(principal: float, annual_rate: float, years: int) -> str:
    """Estimate a monthly EMI in INR from amount, annual percent and duration."""
    return f"Estimated monthly EMI: INR {calculate_emi(principal, annual_rate, years)}"


async def main():
    # Import here so the ordinary Day-1 API does not require the Agent Framework SDK.
    from agent_framework import Agent, tool
    from agent_framework.openai import OpenAIChatCompletionClient

    @tool
    def policy_tool(query: str) -> str:
        """Search demonstration banking policy documents and return relevant excerpts."""
        return find_bank_policy(query)

    @tool
    def emi_tool(principal: float, annual_rate: float, years: int) -> str:
        """Calculate a monthly loan EMI given principal, annual interest rate and years."""
        return estimate_loan_emi(principal, annual_rate, years)

    agent = Agent(
        client=OpenAIChatCompletionClient(
            model=os.environ["AZURE_OPENAI_CHAT_MODEL"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        ),
        name="BankingPolicyAgent",
        instructions=(
            "You are a learning-demo bank assistant, not a financial adviser. "
            "Use policy_tool for policy questions. Use emi_tool for EMI maths. "
            "Cite policy IDs; do not invent facts or execute transactions."
        ),
        tools=[policy_tool, emi_tool],
    )
    result = await agent.run("Which documents are needed for a home loan? Also estimate EMI for INR 500000 at 8% for 5 years.")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
