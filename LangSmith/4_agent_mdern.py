import os
import requests

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()

os.environ['LANGSMITH_PROJECT']='Weather Chatbot'

WEATHER_API_KEY = os.getenv("WEATHER_KEY")

if not WEATHER_API_KEY:
    raise ValueError("WEATHER_KEY is not set in the .env file")


# ============================================================
# 2. Create tools
# ============================================================

search_tool = DuckDuckGoSearchRun()


@tool
def get_weather_data(city: str) -> str:
    """
    Get the current weather data for a given city.
    """

    url = "https://api.weatherstack.com/current"

    params = {
        "access_key": WEATHER_API_KEY,
        "query": city
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        return f"Weather API error: {data['error']}"

    current = data["current"]

    return (
        f"Weather in {city}:\n"
        f"Temperature: {current['temperature']}°C\n"
        f"Feels like: {current['feelslike']}°C\n"
        f"Weather: {current['weather_descriptions'][0]}\n"
        f"Humidity: {current['humidity']}%\n"
        f"Wind speed: {current['wind_speed']} km/h"
    )


# ============================================================
# 3. Create the LLM
# ============================================================

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

# ============================================================
# 4. Create the modern LangChain agent
# ============================================================

tools = [
    search_tool,
    get_weather_data
]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a helpful assistant. "
        "Use the weather tool whenever the user asks for weather information. "
        "Use the search tool when you need current information from the web. "
        "Do not guess information when a tool can provide it."
    )
)


# ============================================================
# 5. Invoke the agent
# ============================================================

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                # "content": "What is the current temperature of Kathmandu?",
                # "content": "What is the current temperature of Butwal?",
                # "content": "Identify the hottest city in Nepal. And give its current temperature.", # More complex prompt. No api data for nepalgunj 
                "content": "Identify the most polluted city in India. And give its current temperature.", # More complex prompt. 
            }
        ]
    }
)


# ============================================================
# 6. Get the final answer
# ============================================================

print(response["messages"][-1].content)