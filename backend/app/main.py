from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agent import router as agent_router
from backend.app.api.documents import router as documents_router
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    title="Enterprise AI Knowledge Assistant API",
    description="RAG + AI Agent for company knowledge base",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zhores-ai-agent.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}

app.include_router(documents_router)
app.include_router(agent_router)