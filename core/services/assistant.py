import os
import re
from django.conf import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Singletons (lazy-loaded on first use) ─────────────────────────────────

_embeddings = None
_llm = None


def _get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model="openai/text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
        )
    return _embeddings


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        # OpenRouter is OpenAI-API-compatible; only base_url differs
        _llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=512,
        )
    return _llm


# ── PDF text-cleaning helper ───────────────────────────────────────────────

def _clean_text(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return text
    single_alpha = sum(1 for t in tokens if len(t) == 1 and t.isalpha())
    if single_alpha / len(tokens) > 0.5:
        text = re.sub(r'(?<=[A-Za-z]) (?=[A-Za-z])', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── ChromaDB helpers ───────────────────────────────────────────────────────

def _get_vectorstore(course_id: int) -> Chroma:
    return Chroma(
        collection_name=f"course_{course_id}",
        embedding_function=_get_embeddings(),
        persist_directory=settings.CHROMA_PATH,
    )


# ── Document indexing (called by signals and `manage.py index_documents`) ──

def index_document(course_id: int, document_id: int, file_path: str, title: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only .pdf and .txt are allowed.")

    raw_docs = loader.load()

    for doc in raw_docs:
        doc.page_content = _clean_text(doc.page_content)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "course_id": course_id,
            "document_id": document_id,
            "document_title": title,
            "chunk_index": i,
        })

    vectorstore = _get_vectorstore(course_id)

    try:
        vectorstore._collection.delete(where={"document_id": document_id})
    except Exception:
        pass

    ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
    vectorstore.add_documents(chunks, ids=ids)


# ── Orchestrator ───────────────────────────────────────────────────────────

_ORCHESTRATOR_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a routing assistant for an e-learning platform. "
            "Course documents ARE uploaded and indexed — prefer searching them.\n\n"
            "Reply 'rag' when the question is about the course topic, concepts, or anything "
            "a student would normally ask their instructor about.\n"
            "Reply 'general' ONLY when the question is completely unrelated to the course "
            "(e.g. personal advice, off-topic subjects, greetings).\n\n"
            "When in doubt, choose 'rag'.\n\n"
            "Course: {course_title} | Category: {category} | Level: {level}\n"
            "Description: {course_description}\n\n"
            "Respond with exactly one word — 'rag' or 'general'."
        ),
    ),
    ("human", "{question}"),
])


def _orchestrate(question: str, course_context: dict) -> str:
    """Returns 'rag' or 'general'. Defaults to 'general' on ambiguous output."""
    chain = _ORCHESTRATOR_PROMPT | _get_llm() | StrOutputParser()
    result = chain.invoke({
        "course_title": course_context.get("title", ""),
        "category": course_context.get("category", ""),
        "level": course_context.get("level", ""),
        "course_description": course_context.get("description", ""),
        "question": question,
    })
    result_lower = result.strip().lower()
    if result_lower.startswith("rag") or '"rag"' in result_lower or "'rag'" in result_lower:
        return "rag"
    return "general"


# ── RAG Agent ──────────────────────────────────────────────────────────────

_RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a helpful course assistant. Answer the student's question using ONLY "
            "the course document excerpts provided below. "
            "If the excerpts do not contain enough information, say so and suggest they ask their teacher. "
            "Always mention which document(s) you used.\n\n"
            "--- Course document excerpts ---\n{context}\n--------------------------------\n\n"
            "Chat history:\n{chat_history}"
        ),
    ),
    ("human", "{question}"),
])


def _run_rag_agent(question: str, course_id: int, chat_history_text: str) -> dict:
    vectorstore = _get_vectorstore(course_id)

    if vectorstore._collection.count() == 0:
        return {
            "content": (
                "No course documents have been indexed yet. "
                "Please ask your teacher to upload and index course materials."
            ),
            "source": "rag_document",
            "references": [],
        }

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    references = list({doc.metadata.get("document_title", "Unknown") for doc in docs})
    context = "\n\n".join(
        f"[{doc.metadata.get('document_title', 'Document')}]\n{doc.page_content}"
        for doc in docs
    )

    chain = _RAG_PROMPT | _get_llm() | StrOutputParser()
    answer = chain.invoke({
        "context": context,
        "chat_history": chat_history_text,
        "question": question,
    })

    return {
        "content": answer.strip(),
        "source": "rag_document",
        "references": references,
    }


# ── General Agent ──────────────────────────────────────────────────────────

_GENERAL_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are a helpful course assistant for an e-learning platform. "
            "Answer the student's question using your general knowledge about the subject. "
            "Always note at the end that this answer is based on general knowledge, "
            "not specific course materials.\n\n"
            "Course: {course_title} | Category: {category} | Level: {level}\n\n"
            "Chat history:\n{chat_history}"
        ),
    ),
    ("human", "{question}"),
])


def _run_general_agent(question: str, course_context: dict, chat_history_text: str) -> dict:
    chain = _GENERAL_PROMPT | _get_llm() | StrOutputParser()
    answer = chain.invoke({
        "course_title": course_context.get("title", ""),
        "category": course_context.get("category", ""),
        "level": course_context.get("level", ""),
        "chat_history": chat_history_text,
        "question": question,
    })

    return {
        "content": answer.strip(),
        "source": "general_knowledge",
        "references": [],
    }


# ── Chat history formatter ─────────────────────────────────────────────────

def _format_history(messages) -> str:
    if not messages:
        return "No previous messages."
    lines = [
        f"{'Student' if m.role == 'user' else 'Assistant'}: {m.content}"
        for m in messages
    ]
    return "\n".join(lines)


# ── Public entry point (called by the API view and the MVT view) ───────────

def run_assistant(question: str, course, recent_messages) -> dict:
    course_context = {
        "title": course.title,
        "description": course.description,
        "category": course.category.name if course.category else "",
        "level": course.level,
    }
    chat_history_text = _format_history(recent_messages)

    has_docs = _get_vectorstore(course.id)._collection.count() > 0
    if not has_docs:
        return _run_general_agent(question, course_context, chat_history_text)

    route = _orchestrate(question, course_context)

    if route == "rag":
        return _run_rag_agent(question, course.id, chat_history_text)
    return _run_general_agent(question, course_context, chat_history_text)


def run_career_advisor(question: str, user) -> dict:
    """Lightweight wrapper to run the general assistant for the site-wide career advisor.

    This avoids routing/RAG logic which requires a course object and document index.
    """
    course_context = {
        "title": "Career Advisor",
        "description": "Platform-wide career and course guidance",
        "category": "",
        "level": "",
    }
    chat_history_text = "No previous messages."

    try:
        return _run_general_agent(question, course_context, chat_history_text)
    except Exception as e:
        print("Career advisor error:", e)
        return {"content": "The assistant is temporarily unavailable. Please try again.", "source": ""}
