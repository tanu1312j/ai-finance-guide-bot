from dotenv import load_dotenv
import os
import yaml
from typing import Dict, Any
from pydantic import BaseModel, Field

from langchain.tools import Tool, StructuredTool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock

from .prompts import SYSTEM_PROMPT
from .memory import ConversationBuffer
from .guardrails import validate_demographics, pii_minimize, DISCLAIMER
from .tools.savings_model import predict_savings_amount
from .tools.insurance_model import recommend_insurance
from .tools.profile_store import upsert_profile, get_profile
from .tools.market import market_snapshot
from .tools.market_data import get_stock_quote


env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------
CONFIG = {}
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        CONFIG = yaml.safe_load(f)
else:
    CONFIG = {
        "provider": "openai",
        "openai": {"model": "gpt-4o-mini", "temperature": 0.2},
        "memory": {"summary_window": 6},
    }
if "openai" not in CONFIG:
    CONFIG["openai"] = {}

CONFIG["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")

if not CONFIG["openai"]["api_key"]:
    raise EnvironmentError(
        "❌ OPENAI_API_KEY not found. Please set it in .env or as an environment variable."
    )
# ---------------------------------------------------------------------
# Memory buffer
# ---------------------------------------------------------------------
buffer = ConversationBuffer(window=int(CONFIG.get("memory", {}).get("summary_window", 6)))


# ---------------------------------------------------------------------
# Validation and persistence helpers
# ---------------------------------------------------------------------
def _ensure_profile(user_id: str, demographics: Dict[str, Any]) -> Dict[str, Any]:
    """Validate, scrub, and persist user demographics."""
    ok, msg = validate_demographics(demographics)
    if not ok:
        raise ValueError(msg)
    safe_demo = pii_minimize(demographics)
    return upsert_profile(user_id, safe_demo)


# ---------------------------------------------------------------------
# Tool logic (with graceful fallback)
# ---------------------------------------------------------------------
def _tool_savings(user_id: str, demographics: dict | None = None) -> Dict[str, Any]:
    """Estimate savings using ML model; fallback to stored profile if demographics missing."""
    if not demographics:
        stored = get_profile(user_id)
        if stored:
            demographics = stored
        else:
            return {
                "error": (
                    "Missing demographics. "
                    "Please provide age, marital_status, dependents, income, net_worth, and location."
                )
            }

    profile = _ensure_profile(user_id, demographics)
    res = predict_savings_amount(profile)
    res["profile"] = profile
    return res


def _tool_insurance(user_id: str, demographics: dict | None = None) -> Dict[str, Any]:
    """Recommend insurance using ML model; fallback to stored profile if demographics missing."""
    if not demographics:
        stored = get_profile(user_id)
        if stored:
            demographics = stored
        else:
            return {
                "error": (
                    "Missing demographics. "
                    "Please provide age, marital_status, dependents, income, net_worth, and location."
                )
            }

    profile = _ensure_profile(user_id, demographics)
    res = recommend_insurance(profile)
    res["profile"] = profile
    return res


def _tool_get_profile(user_id: str) -> Dict[str, Any]:
    """Return stored profile for a given user."""
    return get_profile(user_id)


def _tool_market() -> Dict[str, Any]:
    """Return mock market snapshot."""
    return market_snapshot()


# ---------------------------------------------------------------------
# Define structured tool schemas
# ---------------------------------------------------------------------
class SavingsInput(BaseModel):
    """Inputs for the savings model tool"""
    user_id: str = Field(..., description="User identifier")
    demographics: dict | None = Field(
        None,
        description="Demographic data of the user. "
                    "If missing, the tool will use stored profile or ask the user to provide it."
    )


class InsuranceInput(BaseModel):
    """Inputs for the insurance model tool"""
    user_id: str = Field(..., description="User identifier")
    demographics: dict | None = Field(
        None,
        description="Demographic data of the user. "
                    "If missing, the tool will use stored profile or ask the user to provide it."
    )


class GetProfileInput(BaseModel):
    """Inputs for retrieving stored profile"""
    user_id: str = Field(..., description="User identifier")


# ---------------------------------------------------------------------
# Define LangChain Tools (structured)
# ---------------------------------------------------------------------
tools = [
    StructuredTool.from_function(
        name="savings_model",
        description="Estimate savings amounts and rate for a user.",
        func=_tool_savings,
        args_schema=SavingsInput,
    ),
    StructuredTool.from_function(
        name="insurance_model",
        description="Recommend insurance coverages for a user.",
        func=_tool_insurance,
        args_schema=InsuranceInput,
    ),
    StructuredTool.from_function(
        name="get_profile",
        description="Load the user's stored profile by user_id.",
        func=lambda user_id: _tool_get_profile(user_id),
        args_schema=GetProfileInput,
    ),
    Tool(
        name="market_snapshot",
        description="Get a lightweight market snapshot.",
        func=lambda _: _tool_market(),
    ),
    Tool(
    name="stock_quote",
    description="Fetches real-time stock data from Alpha Vantage. Input should be a stock symbol like 'AAPL' or 'GOOGL'.",
    func=lambda symbol: get_stock_quote(symbol)
 ),
]


# ---------------------------------------------------------------------
# LLM provider factory
# ---------------------------------------------------------------------
def _make_llm():
    provider = CONFIG.get("provider", "openai")
    if provider == "bedrock":
        region = CONFIG.get("bedrock", {}).get("region", os.getenv("AWS_REGION", "us-east-1"))
        model_id = CONFIG.get("bedrock", {}).get(
            "model_id", "anthropic.claude-3-sonnet-20240229-v1:0"
        )
        temperature = CONFIG.get("bedrock", {}).get("temperature", 0.2)
        return ChatBedrock(model_id=model_id, region=region, temperature=temperature)
    else:
        model = CONFIG.get("openai", {}).get("model", "gpt-4o-mini")
        temperature = CONFIG.get("openai", {}).get("temperature", 0.2)
        return ChatOpenAI(model=model, temperature=temperature)


# ---------------------------------------------------------------------
# Build agent
# ---------------------------------------------------------------------
def build_agent():
    llm = _make_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),  # required for tool-calling
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor


# ---------------------------------------------------------------------
# Agent instance and chat interface
# ---------------------------------------------------------------------
AGENT = build_agent()


def chat(user_id: str, message: str) -> str:
    """Chat entrypoint for Streamlit/FastAPI."""
    buffer.add("human", message)
    try:
        res = AGENT.invoke({"input": message, "chat_history": buffer.get()})
        text = res.get("output", "").strip()
    except Exception as e:
        text = f"⚠️ Error: {e}"

    if DISCLAIMER not in text:
        text += f"\n\n{DISCLAIMER}"

    buffer.add("ai", text)
    return text
