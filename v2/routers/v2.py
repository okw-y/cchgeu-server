import json

from v2.models import Schedules, LastUpdate, Faculties, Teachers
from v2.models.api import Schedule, Teacher

from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist


v2router = APIRouter(prefix="/v2")


@v2router.get("/isActual")
async def is_actual(group: str, date: str, time: str) -> bool:
    if group == "" or date == "" or time == "":
        raise HTTPException(
            status_code=400, detail="Fields is empty!"
        )

    try:
        row = LastUpdate.get(
            LastUpdate.name == group
        )

        return row.date == date and row.time == time
    except DoesNotExist:
        raise HTTPException(
            status_code=400, detail="Group is not exists!"
        )


@v2router.get("/getSchedule")
async def get_schedule(group: str) -> Schedule:
    if group == "":
        raise HTTPException(
            status_code=400, detail="Group name is empty!"
        )

    try:
        last_update = LastUpdate.get(LastUpdate.name == group)
    except DoesNotExist:
        raise HTTPException(
            status_code=400, detail="Group is not exists!"
        )

    try:
        schedule = Schedules.get(Schedules.name == group)
    except DoesNotExist:
        raise HTTPException(
            status_code=400, detail="Group is not exists!"
        )

    return Schedule(
        date=last_update.date,
        time=last_update.time,
        schedule=json.loads(schedule.data.replace("'", "\""))
    )


@v2router.get("/getFaculties")
async def get_faculties() -> dict[str, list[str]]:
    return {
        faculty.name: json.loads(faculty.data) for faculty in Faculties.select()
    }


@v2router.get("/getAllGroups")
async def get_faculties() -> list[str]:
    return [
        group.name for group in Schedules.select().where(Schedules.is_group == True)
    ]


@v2router.get("/getTeachers")
async def get_teachers(group: str = None, index: int = 0, limit: int = 20) -> dict[str, Teacher]:
    base = Schedules.select().where(Schedules.is_group == False)
    if group is not None:
        teachers = [
            teacher.name for teacher in base.where(
                Schedules.data.contains(f"\"{group}\"") |
                Schedules.data.contains(f"'{group}'")
            )
        ]
    else:
        teachers = [teacher.name for teacher in base]

    output = {}
    for teacher in teachers[index:limit - 1]:
        try:
            output[teacher] = Teacher(
                **json.loads(
                    Teachers.get(Teachers.name == teacher).data.replace("'", "\"")
                )
            )
        except DoesNotExist:
            output[teacher] = Teacher(name=teacher)

    return output
