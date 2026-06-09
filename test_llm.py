import sys
sys.path.insert(0, 'src')
from app.config import Settings
from provider import get_chat_model
from langchain_core.messages import HumanMessage

s = Settings.load()
print("Provider:", s.provider, "| Model:", s.model)
llm = get_chat_model(s)
r = llm.invoke([HumanMessage(content="Xin chào, trả lời 1 câu ngắn.")])
print("OK:", r.content)
