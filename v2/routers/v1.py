import json

from v2.models import Schedules, LastUpdate, Faculties, Teachers
from v2.models.api import Schedule, Teacher, Lesson

from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist


v1router = APIRouter(prefix="/v1")


@v1router.get("/isActual")
async def is_actual(group: str, date: str, time: str, aid: str | int = None) -> bool:
    if group == "" or date == "" or time == "":
        return True

    try:
        row = LastUpdate.get(
            LastUpdate.name == group
        )

        return row.date == date and row.time == time
    except DoesNotExist:
        return True


@v1router.get("/getActual")
async def is_actual(group: str, aid: str | int = None) -> list[str]:
    if group == "" :
        return ["", ""]

    try:
        row = LastUpdate.get(
            LastUpdate.name == group
        )

        return [row.date, row.time]
    except DoesNotExist:
        return ["", ""]


@v1router.get("/getSchedule")
async def get_schedule(group: str, aid: str | int = None) -> list[Lesson]:
    if group == "":
        return []

    try:
        schedule = Schedules.get(Schedules.name == group)
    except DoesNotExist:
        return []

    return json.loads(schedule.data.replace("'", "\""))


@v1router.get("/getFaculties")
async def get_faculties(aid: str | int = None) -> dict[str, list[str]]:
    return {
        faculty.name: json.loads(faculty.data) for faculty in Faculties.select()
    }
