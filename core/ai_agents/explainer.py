import os
from openai import OpenAI

client = None

if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()


def explain_recommendation(query, course_title):

    if client is None:
        return f"This course is recommended because it matches your interests related to '{query}'."

    prompt = f"""
    Student Query:
    {query}

    Course:
    {course_title}

    Explain briefly why this course matches.
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text