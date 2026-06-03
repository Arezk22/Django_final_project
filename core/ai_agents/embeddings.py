from langchain_core.documents import Document


def course_to_document(course):

    category = getattr(course.category, "name", None) or str(course.category or "")
    level = course.level or ""

    content = f"""
Course Title: {course.title}

Description:
{course.description or ""}

Category:
{category}

Level:
{level}
"""

    return Document(
        page_content=content.strip(),
        metadata={
            "course_id": course.id,
            "title": course.title,
            "category": category,
            "level": level,
        }
    )