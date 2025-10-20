import re


def split_lessons(data: str | float, audience: str | float, wktp: int) -> list[tuple[str, str, int]]:
    if not isinstance(data, str):
        return []

    pattern = r"(\([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.\)\s*)"

    teachers = re.findall(pattern, data)
    if not teachers or len(teachers) < 2:
        return [(data.strip(), audience, wktp)]

    lessons = [
        lesson for lesson in re.split(pattern, data) if lesson.strip()
    ]

    result = []
    current_lesson = ""

    for part in lessons:
        current_lesson += part
        if part in teachers:
            result.append(current_lesson.strip())
            current_lesson = ""

    if current_lesson.strip():
        result.append(current_lesson.strip())

    audience_list = ["" for _ in range(len(result))]
    if isinstance(audience, str):
        audience_list = [chunk.strip() for chunk in audience.split("\n")]

    return list(
        zip(result, audience_list, range(len(result)))
    )
