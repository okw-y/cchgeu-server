import json

from starlette.requests import Request

from v2.models import LastUpdateModel, FacultiesModel, TeachersModel, ScheduleModel, ClientSettingsModel
from v2.models.api import Schedule, Teacher

from fastapi import APIRouter, HTTPException
from peewee import DoesNotExist


v2router = APIRouter(prefix="/v2")


@v2router.get("/isActual", deprecated=True)
async def is_actual(group: str, date: str, time: str) -> bool:
    if group == "" or date == "" or time == "":
        raise HTTPException(
            status_code=400, detail="Fields is empty!"
        )

    try:
        row = LastUpdateModel.get(
            LastUpdateModel.name == group
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

    # try:
    #     last_update = LastUpdate.get(LastUpdate.name == group)
    # except DoesNotExist:
    #     raise HTTPException(
    #         status_code=400, detail="Group is not exists!"
    #     )

    lessons = ScheduleModel.select().where(
        (ScheduleModel.group == group) | (ScheduleModel.teacher == group)
    ).dicts()
    if len(lessons) == 0:
        raise HTTPException(
            status_code=400, detail="Group is not exists!"
        )

    return Schedule(
        date="last_update.date",
        time="last_update.time",
        schedule=list(lessons)
    )


@v2router.get("/getFaculties")
async def get_faculties() -> dict[str, list[str]]:
    return {
        faculty.name: json.loads(faculty.data) for faculty in FacultiesModel.select()
    }


@v2router.get("/getAllGroups")
async def get_faculties() -> list[str]:
    return list(
        set(obj.grop for obj in ScheduleModel.select(ScheduleModel.group))
    )


@v2router.get("/getAllTeachers")
async def get_all_teachers() -> dict[str, str]:
    teachers = list(
        set(teacher.teacher for teacher in ScheduleModel.select(ScheduleModel.group, ScheduleModel.teacher))
    )

    output = {}
    for teacher in teachers:
        try:
            output[teacher] = json.loads(
                TeachersModel.get(TeachersModel.name == teacher).data.replace("'", "\"")
            )["name"]
        except DoesNotExist:
            output[teacher] = teacher

    return output


@v2router.get("/getTeachers")
async def get_teachers(group: str = None, index: int = 0, limit: int = 20) -> dict[str, Teacher]:
    base = ScheduleModel.select(ScheduleModel.group, ScheduleModel.teacher)
    if group is not None:
        teachers = list(
            set(teacher.teacher for teacher in base.where(ScheduleModel.group == group))
        )
    else:
        teachers = list(
            set(teacher.teacher for teacher in base)
        )

    output = {}
    for teacher in teachers[index:limit - 1]:
        try:
            output[teacher] = Teacher(
                **json.loads(
                    TeachersModel.get(TeachersModel.name == teacher).data.replace("'", "\"")
                )
            )
        except DoesNotExist:
            output[teacher] = Teacher(name=teacher).model_dump()

    return output


@v2router.get("/adsEnabled")
async def ads_enabled(request: Request) -> bool:
    status = ClientSettingsModel.get_or_none(
        ClientSettingsModel.client_id == (request.headers.get("client-id") or "*")
    )
    if status:
        return status.ads_enabled

    return False


@v2router.post("/toggleAds")
async def toggle_ads(request: Request) -> dict:
    try:
        payload = await request.json()
        client_id = payload.get("client_id")
        enabled = payload.get("enabled", False)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required")

    if client_id == "*":
        query = ClientSettingsModel.update(
            {ClientSettingsModel.ads_enabled: enabled}
        )
        updated_rows = query.execute()

        return {
            "status": "success",
            "message": f"Ads for {updated_rows} clients set to {enabled}"
        }
    else:
        settings, created = ClientSettingsModel.get_or_create(client_id=client_id)
        settings.ads_enabled = enabled
        settings.save()

        return {
            "client_id": client_id,
            "ads_enabled": settings.ads_enabled,
            "status": "created" if created else "updated"
        }
