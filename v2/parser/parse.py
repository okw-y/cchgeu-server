import logging

from .groups import get_groups
from .sheet import parse_sheet

from v2.models import Lesson

FACULTIES = [
        "https://cchgeu.ru/studentu/schedule/magistratura/",
        "https://cchgeu.ru/studentu/schedule/stf/",
        "https://cchgeu.ru/studentu/schedule/dtf/",
        "https://cchgeu.ru/studentu/schedule/spo/",
        "https://cchgeu.ru/studentu/schedule/sf/",
        "https://cchgeu.ru/studentu/schedule/fag/",
        "https://cchgeu.ru/studentu/schedule/fisis/",
        "https://cchgeu.ru/studentu/schedule/fitkb/",
        "https://cchgeu.ru/studentu/schedule/raspisanie-fakultet-mashinostroeniya-i-aerokosmicheskoy-tekhniki/",
        "https://cchgeu.ru/studentu/schedule/fre/",
        "https://cchgeu.ru/studentu/schedule/femit/",
        "https://cchgeu.ru/studentu/schedule/fesu/"
    ]


def get_all_schedules(
        old_last_update: dict[str, list[str]]
) -> tuple[dict[str, list[Lesson]], dict[str, list[str]], dict[str, list[str]]]:
    indexes, faculty_names, last_update = {}, {}, {}
    for faculty in FACULTIES:
        faculty_name, groups = get_groups(faculty)
        faculty_names[faculty_name] = []
        for data in groups:
            faculty_names[faculty_name].append(data["group"])
            if old_last_update.get(data["group"], []) == data["last_update"]:
                continue

            try:
                indexes[data["group"]] = parse_sheet(
                    data["file"], data["group"]
                )
                last_update[data["group"]] = data["last_update"]
            except Exception as error:
                logging.error(
                    f"{data['group']} ({faculty_name}) access to {data['file']} ended with error: {error}"
                )

    return indexes, faculty_names, last_update
