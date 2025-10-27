import json
import logging
import time

from v2.models import Schedules, LastUpdateModel, FacultiesModel, FACULTIES, ScheduleModel
from v2.parser import parse_sheet
from v2.parser.groups import get_groups

from peewee import DoesNotExist


def update_groups(force_update: bool = False) -> None:
    start = time.time()
    for url in FACULTIES:
        try:
            faculty_name, groups = get_groups(url)
        except Exception as error:
            logging.error(
                f"Unable to obtain information about the faculty: {error}"
            )
            continue

        row, _ = FacultiesModel.get_or_create(name=faculty_name, defaults={"data": "[]"})
        row.data = json.dumps(
            [group["group"] for group in groups], ensure_ascii=False
        )

        for group in groups:
            try:
                row = LastUpdateModel.get(
                    LastUpdateModel.name == group["group"]
                )

                last_update = [row.date, row.time]
            except DoesNotExist:
                last_update = []

            if (group["last_update"] != last_update) or force_update:
                try:
                    #parsed = parse_sheet(group["file"], group["group"])
                    #
                    # row, _ = Schedules.get_or_create(name=group["group"], defaults={"data": "[]", "is_group": True})
                    # row.data = json.dumps(
                    #     [lesson.model_dump() for lesson in parsed], ensure_ascii=False
                    # )
                    # row.save()

                    ScheduleModel.delete().where(
                        ScheduleModel.group == group["group"]
                    ).execute()

                    for obj in parse_sheet(group["file"], group["group"]):
                        ScheduleModel.create(**obj.model_dump())

                    row, _ = LastUpdateModel.get_or_create(name=group["group"], defaults={"date": "", "time": ""})
                    row.date = group["last_update"][0]
                    row.time = group["last_update"][1]
                    row.save()

                    logging.info(f"Information about the group \"{group['group']}\" has been updated.")
                except Exception as error:
                    logging.error(
                        f"Unable to process group schedule \"{group['group']}\" due to an unexpected error: {error}"
                    )

    logging.info(
        f"Groups update completed in {time.time() - start}s."
    )

    # update_teachers()



def update_teachers() -> None:
    start = time.time()
    indexes = []
    for group in Schedules.select().where(Schedules.is_group == True):
        indexes.extend(
            json.loads(group.data.replace("'", "\""))
        )

    teachers = {}
    for lesson in indexes:
        if lesson["teacher"] not in teachers:
            teachers[lesson["teacher"]] = []

        teachers[lesson["teacher"]].append(lesson)

    for teacher, data in teachers.items():
        row, _ = Schedules.get_or_create(name=teacher, defaults={"data": "[]", "is_group": False})
        row.data = json.dumps(data, ensure_ascii=False)
        row.save()

    logging.info(
        f"Teachers update completed in {time.time() - start}s."
    )
