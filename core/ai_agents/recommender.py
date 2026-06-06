from core.ai_agents.vector_store import vector_store


def search_courses(query):
    from core.ai_agents.vector_store import vector_store

    return vector_store.similarity_search_with_score(
        query=query,
        k=2
    )