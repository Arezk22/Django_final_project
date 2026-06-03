from core.ai_agents.vector_store import vector_store


def search_courses(query, k=4):
    from core.ai_agents.vector_store import vector_store

    try:
        results = vector_store.similarity_search(query, k=k)
        return results
    except Exception as e:
        print("Search error:", e)
        return []