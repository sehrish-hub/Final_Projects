import chainlit as cl 
import requests # for fetching the weather and news data
import os # for loading the environment variables
from dotenv import load_dotenv, find_dotenv # for loading the environment variables
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner # for the agent
from openai.types.responses import ResponseTextDeltaEvent # for the response
from agents.tool import function_tool # for the tool
import pytz # for the timezone
from datetime import datetime # for the datetime
from timezonefinder import TimezoneFinder # for the timezone
from geopy.geocoders import Nominatim # for the geolocator
import logging # for the logging
logging.basicConfig(level=logging.ERROR) #
import httpx
logging.getLogger("httpx").setLevel(logging.WARNING)#  

# Initialize objects
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="geoapi")

# Load API Keys from .env
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

# Set up Gemini provider
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Configure model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider,
)

# Define run configuration
run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

# Weather Fetching Function
@function_tool("get_weather")
def get_weather(location: str, unit: str = "C") -> str:
    """
    Fetch real-time weather data for a given location.
    """
    if not weather_api_key:
        return "Weather API key is missing. Please check your .env file."

    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={location}&aqi=no"

    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return f"Could not fetch weather for {location}. Try another city."

        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]

        if unit.upper() == "F":
            return f"The weather in {location} is {temp_f}°F with {condition}."
        else:
            return f"The weather in {location} is {temp_c}°C with {condition}."

    except Exception as e:
        return f"Error fetching weather data: {str(e)}"
# News Fetching Function
@function_tool("get_news")
def get_news(city: str = "karachi") -> str:
    """Fetch the latest news for a given city."""
    if not news_api_key:
        return "News API key is missing. Please check your .env file."

    try:
        url = f"https://newsapi.org/v2/everything?q={city}&language=en&apiKey={news_api_key}"
        response = requests.get(url).json()

        if response["status"] != "ok":
            return "Failed to fetch news."

        articles = response.get("articles", [])[:5]  # Fetch top 5 news articles
        news_list = "\n".join([f"📰 {a['title']} - {a['source']['name']}" for a in articles])
        return news_list if news_list else f"No news found for {city}."

    except:
        return "News fetch failed. Try again."

@function_tool("get_time")
def get_time(city: str) -> str:
    """
    Fetch the current time for any given city dynamically.
    """
    try:
        location = geolocator.geocode(city)
        if not location:
            return f"Could not find location for {city}. Try another city."

        # Find the timezone dynamically
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not timezone_str:
            return f"Could not determine the timezone for {city}."

        # Get the current time in the found timezone
        timezone = pytz.timezone(timezone_str)
        current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        return f"The current time in {city.title()} is {current_time}."
    
    except Exception as e:
        return f"Error fetching time for {city}: {str(e)}"


# AI Agent with Weather Tool
agent1 = Agent(
    instructions="You are a helpful assistant. Use the get_weather tool to fetch weather information for any location.",
    name="WeatherBot",
    tools=[get_weather, get_news, get_time]
)

# Chat Start Handler
@cl.on_chat_start
async def handle_chat_start():
    """Initialize chat history when conversation starts."""
    cl.user_session.set("history", [])  # Clear session history
    await cl.Message(content="Hello! I am the panaversity support agent. How can I help you today?").send()

# Message Handler
@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages and generate AI responses."""
    history = cl.user_session.get("history", [])  # Retrieve or initialize history
    msg = cl.Message(content="")  # Create empty message object
    await msg.send()

    history.append({"role": "user", "content": message.content})  # Store user message

    # Run AI agent
    result = Runner.run_streamed(
        input=history,
        run_config=run_config,
        starting_agent=agent1  # Agent should be passed first
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)    

    history.append({"role": "assistant", "content": result.final_output})  # Store AI response
    cl.user_session.set("history", history)  # Save history for future interactions