import re


def get_teacher(teacher: str) -> str:
    return [*re.findall(r"(\(?\s*[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)?\s*\)?)", teacher), ""][0]
