import re

from .gaps import get_teacher

from v2.models import Lesson


def lesson_info(
        index: int,
        date: str,
        time: str,
        name: str | float,
        audience: str | float,
        group: str,
        subgroup: int,
        wktp: int
) -> Lesson | None:
    if not isinstance(name, str):
        return None
    if not isinstance(audience, str):
        audience = ""

    original_time = " - ".join(
        [chunk.zfill(5) for chunk in re.findall(r"(\d{1,2}:\d{2}):\d{2}", time)]
    )

    parts = [p.strip() for p in name.split("\n") if p.strip()]

    if not parts:
        return None

    if re.search(r'\d{1,2}:\d{2}', parts[0]):
        parsed_time = " - ".join(re.findall(r"(\d{1,2}:\d{2})", parts[0]))
        if parsed_time:
            original_time = parsed_time

        parts = parts[1:]

    if len(parts) < 2:
        if len(parts) == 1 and parts[0].lower() == "переезд":
            return None

        return None

    ltype = parts[0]
    lesson = parts[1]
    last_line = parts[-1]

    weeks = []
    teacher = ""

    teacher_match = re.search(r"\((.*)\)", last_line)
    if teacher_match:
        teacher = get_teacher(teacher_match.group(1).strip())
        last_line = last_line[:teacher_match.start()].strip()

    weeks_match = re.search(r"([\d, ]+) нед\.", last_line)
    if weeks_match:
        weeks = [
            int(w.strip()) for w in weeks_match.group(1).split(",") if w.strip()
        ]

    date = {
        "понедельник": 0,
        "вторник": 1,
        "среда": 2,
        "четверг": 3,
        "пятница": 4,
        "суббота": 5
    }[date.lower()]

    return Lesson(
        index=index,
        date=date,
        time=original_time,
        type=ltype,
        lesson=lesson,
        audience=audience,
        teacher=teacher,
        group=group,
        subgroup=subgroup,
        weeks=weeks,
        wktp=wktp
    )
