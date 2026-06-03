from core.models import Enrollment
from core.ai_agents.recommender import search_courses
from core.ai_agents.explainer import explain_recommendation


def get_recommendations(user, query, use_ai_explainer=False):
    """
    Generate course recommendations based on semantic search
    and exclude already enrolled courses.
    """

    # ==========================================
    # 1. Get enrolled course IDs
    # ==========================================
    enrolled_courses = set(
        Enrollment.objects.filter(student=user)
        .values_list("course_id", flat=True)
    )

    # ==========================================
    # 2. Semantic search (Vector DB)
    # ==========================================
    results = search_courses(query)

    # ==========================================
    # 3. Deduplication + Filtering
    # ==========================================
    unique = {}

    for item in results:
        try:
            metadata = item.metadata or {}

            course_id = metadata.get("course_id")

            if course_id is None:
                continue

            course_id = int(course_id)

            # skip already enrolled courses
            if course_id in enrolled_courses:
                continue

            # keep only first occurrence
            if course_id not in unique:
                title = metadata.get("title", "")
                category = metadata.get("category", "")
                level = metadata.get("level", "")

                # optional AI explanation
                reason = None
                if use_ai_explainer:
                    reason = explain_recommendation(query, title)

                unique[course_id] = {
                    "course_id": course_id,
                    "title": title,
                    "category": category,
                    "level": level,
                    "reason": reason
                }

        except Exception as e:
            print("Recommendation error:", e)
            continue

    # ==========================================
    # 4. Final output
    # ==========================================
    return list(unique.values())[:10]


# ==========================================
# Index Course into Vector DB
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
        vector_store.delete(ids=[str(course.id)])
    except Exception:
        pass

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
    try:
        from core.ai_agents.vector_store import vector_store

        text = f"""
        Title: {course.title}
        Category: {getattr(course.category, 'name', str(course.category))}
        Level: {course.level or ''}
        Description: {course.description}
        """

        vector_store.add_texts(
            texts=[text],
            metadatas=[{
                "course_id": course.id,
                "title": course.title,
                "category": getattr(course.category, "name", str(course.category)),
                "level": course.level or ""
            }],
            ids=[str(course.id)]
        )

    except Exception as e:
        print("Indexing error:", e)