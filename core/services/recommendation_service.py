from core.models import Enrollment
from core.ai_agents.recommender import search_courses
from core.ai_agents.explainer import explain_recommendation


SIMILARITY_THRESHOLD = 0.35  # Chroma Distance


def get_recommendations(user, query, use_ai_explainer=False):
    """
    Generate course recommendations using semantic search.
    Exclude enrolled courses and weak matches.
    """

    # ==========================================
    # 1. Get enrolled courses
    # ==========================================
    enrolled_courses = set(
        Enrollment.objects.filter(student=user)
        .values_list("course_id", flat=True)
    )

    # ==========================================
    # 2. Semantic Search
    # search_courses MUST return:
    # [(document, distance), ...]
    # ==========================================
    results = search_courses(query)

    unique = {}

    # ==========================================
    # 3. Filter Results
    # ==========================================
    for doc, distance in results:

        try:
            # Reject weak matches
            if distance > SIMILARITY_THRESHOLD:
                continue

            metadata = doc.metadata or {}

            course_id = metadata.get("course_id")

            if not course_id:
                continue

            course_id = int(course_id)

            # Skip enrolled
            if course_id in enrolled_courses:
                continue

            # Deduplicate
            if course_id in unique:
                continue

            title = metadata.get("title", "")
            category = metadata.get("category", "")
            level = metadata.get("level", "")

            reason = None

            if use_ai_explainer:
                reason = explain_recommendation(query, title)

            unique[course_id] = {
                "course_id": course_id,
                "title": title,
                "category": category,
                "level": level,
                "reason": reason,
                "score": round(distance, 3),
            }

        except Exception as e:
            print("Recommendation Error:", e)

    # ==========================================
    # 4. No relevant results
    # ==========================================
    if not unique:
        return []

    return list(unique.values())[:10]


# ==========================================
# Vector Indexing
# ==========================================
def index_course(course):
    from core.ai_agents.vector_store import vector_store

    text = f"""
    Title: {course.title}
    Category: {getattr(course.category, 'name', str(course.category))}
    Level: {course.level or ''}
    Description: {course.description or ''}
    """

    try:
        # Delete old version
        vector_store.delete(ids=[str(course.id)])
    except Exception:
        pass

    try:
        vector_store.add_texts(
            texts=[text],
            metadatas=[{
                "course_id": course.id,
                "title": course.title,
                "category": getattr(course.category, "name", str(course.category)),
                "level": course.level or "",
            }],
            ids=[str(course.id)]
        )

    except Exception as e:
        print("Indexing Error:", e)