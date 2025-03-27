uv init --package chainlit_chatbot
cd chainlit_chatbot
uv add chainlit
uv add openai-agents
uv run chainlit run chatbot.py -w