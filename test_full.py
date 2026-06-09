import sys, traceback
sys.path.insert(0, 'src')

print("Step 1: Loading config...")
from app.config import Settings
s = Settings.load()
print(f"  provider={s.provider} model={s.model}")

print("Step 2: Loading LLM...")
from provider import get_chat_model
llm = get_chat_model(s)
print("  LLM OK")

print("Step 3: Loading data store...")
from app.data_access import ShoppingDataStore, build_data_tools
ds = ShoppingDataStore(s.orders_path)
print(f"  DataStore OK: {len(ds._customer_by_id)} customers")

print("Step 4: Loading embeddings...")
from rag.embeddings import SentenceTransformerEmbeddings
emb = SentenceTransformerEmbeddings(s.embedding_model_name)
print("  Embeddings OK")

print("Step 5: Loading vector store...")
from rag.vector_store import ChromaPolicyStore
store = ChromaPolicyStore(s.chroma_dir, emb)
store.ensure_index(s.policy_path)
print(f"  VectorStore OK: {store._collection.count()} chunks")

print("Step 6: Building graph...")
import json
from langchain_core.tools import tool
data_tools = build_data_tools(ds)

@tool
def search_policy(query: str) -> str:
    """Tìm kiếm chính sách."""
    return json.dumps(store.search(query, top_k=s.top_k), ensure_ascii=False)

from app.graph import build_graph
graph = build_graph(llm=llm, policy_store=store, data_tools=data_tools, policy_tool=search_policy, top_k=s.top_k)
print("  Graph OK")

print("\nStep 7: Test single question...")
from app.state import ShoppingState
state = {"question": "Thời hạn hoàn trả hàng là bao lâu?", "route": {}, "policy_result": {}, "data_result": {}, "final_answer": "", "trace": []}
result = graph.invoke(state)
print("  Route:", result.get('route'))
print("  Answer:", result.get('final_answer', '')[:200])
