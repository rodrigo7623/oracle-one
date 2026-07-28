"""Cadena RAG: recupera fragmentos relevantes del PDF y le pide a Claude
que responda basándose únicamente en ellos.
"""
from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    EMBEDDING_MODEL_NAME,
    INDEX_DIR,
    RETRIEVER_K,
)

SYSTEM_PROMPT = (
    "Eres el asistente virtual de soporte de NovaShop, una tienda online. "
    "Respondé la pregunta del cliente ÚNICAMENTE con la información provista "
    "en el CONTEXTO. Si el contexto no contiene la respuesta, decí "
    "claramente que no tenés esa información y sugerí contactar a "
    "soporte@novashop.com. No inventes datos, plazos ni políticas. "
    "Respondé en español, de forma breve y clara."
)


class NovaShopAgent:
    def __init__(self) -> None:
        if not INDEX_DIR.exists():
            raise FileNotFoundError(
                f"No se encontró el índice en {INDEX_DIR}. "
                "Ejecutá primero: python -m app.ingest"
            )
        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "Falta ANTHROPIC_API_KEY. Definila en tu archivo .env "
                "(ver .env.example)."
            )

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.vectorstore = FAISS.load_local(
            str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
        self.llm = ChatAnthropic(model=CLAUDE_MODEL, temperature=0, api_key=ANTHROPIC_API_KEY)

    def _format_context(self, docs: list[Document]) -> str:
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    def ask(self, question: str) -> dict:
        docs = self.retriever.invoke(question)
        context = self._format_context(docs)

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", f"CONTEXTO:\n{context}\n\nPREGUNTA: {question}"),
        ]
        response = self.llm.invoke(messages)

        return {
            "pregunta": question,
            "respuesta": response.content,
            "fuentes": [
                {
                    "pagina": doc.metadata.get("page", "?"),
                    "fragmento": doc.page_content[:200],
                }
                for doc in docs
            ],
        }


@lru_cache(maxsize=1)
def get_agent() -> NovaShopAgent:
    return NovaShopAgent()
