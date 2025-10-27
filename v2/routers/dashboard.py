import datetime
import json
import os
import secrets
from collections import defaultdict

from starlette.responses import JSONResponse, HTMLResponse

from v2.models import RequestLog, FacultiesModel

from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from peewee import fn, SQL

security = HTTPBasic()
dashboard = APIRouter()


def protect_dashboard(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    user = os.getenv("DASHBOARD_USERNAME", "admin")
    password = os.getenv("DASHBOARD_PASSWORD", "password")

    correct_user = secrets.compare_digest(credentials.username, user)
    correct_pwd = secrets.compare_digest(credentials.password, password)

    if not (correct_user and correct_pwd):
        raise HTTPException(
            status_code=401, detail="Auth failed", headers={"WWW-Authenticate": "Basic"}
        )

    return True


@dashboard.get("/dashboard-data")
def get_dashboard_data(period: str = "day", protected: bool = Depends(protect_dashboard)):  # noqa
    # period
    now = datetime.datetime.now()
    if period == "week":
        start_date = now - datetime.timedelta(days=7)
    elif period == "month":
        start_date = now - datetime.timedelta(days=30)
    elif period == "all":
        start_date = RequestLog.select(
            fn.MIN(RequestLog.timestamp)
        ).scalar() or now
    else:
        start_date = now - datetime.timedelta(days=1)

    base_query = RequestLog.select().where(
        RequestLog.timestamp >= start_date
    )

    # KPIs
    total = base_query.count()
    errors = base_query.where(RequestLog.status_code >= 400).count()
    avg_latency = RequestLog.select(fn.AVG(RequestLog.latency_ms)).where(
        RequestLog.timestamp >= start_date
    ).scalar() or 0

    # timeline
    timeline_labels = []
    timeline_data = []

    if period == "day":
        time_group_format = "%Y-%m-%d %H:00"
    elif period == "all" and (now - start_date).days > 60:
        time_group_format = "%Y-%m"
    else:
        time_group_format = "%Y-%m-%d"

    strftime_func = fn.strftime(time_group_format, RequestLog.timestamp)
    timeline_query = (
        RequestLog.select(
            strftime_func.alias("time_group"),
            fn.COUNT(RequestLog.id).alias('count')
        )
        .where(RequestLog.timestamp >= start_date)
        .group_by(SQL("time_group"))
        .order_by(SQL("time_group"))
        .dicts()
    )

    for row in timeline_query:
        timeline_labels.append(row["time_group"])
        timeline_data.append(row["count"])

    # status codes
    status_dist = {
        "2xx (success)": base_query.where(RequestLog.status_code.between(200, 299)).count(),
        "4xx (client error)": base_query.where(RequestLog.status_code.between(400, 499)).count(),
        "5xx (server error)": base_query.where(RequestLog.status_code.between(500, 599)).count()
    }

    # faculties & groups
    group_counts = defaultdict(int)
    faculty_counts = defaultdict(int)

    faculty_map = {}
    for faculty in FacultiesModel.select().execute():
        for group in json.loads(faculty.data.replace("'", "\"")):
            faculty_map[group] = faculty.name

    # subquery = (
    #     RequestLog.select(RequestLog.client_id, fn.MAX(RequestLog.id).alias('max_id'))
    #     .where(
    #         (RequestLog.timestamp >= start_date) &
    #         (RequestLog.client_id.is_null(False)) &
    #         (RequestLog.path.in_(["/v2/getSchedule", "/v2/getTeachers"]))
    #     )
    #     .group_by(RequestLog.client_id).alias("t2")
    # )

    # query = (
    #     RequestLog.select(RequestLog.params)
    #     .alias("t1")
    #     .join(subquery, on=(SQL("t1.id") == subquery.c.max_id))
    # )

    query = base_query.where(
        RequestLog.client_id.is_null(False)
    )
    for log in query.execute():
        try:
            params = json.loads(log.params)
            group = params.get("group")
            if group:
                group_counts[group] += 1
                if group in faculty_map:
                    faculty_counts[faculty_map[group]] += 1
        except (json.JSONDecodeError, AttributeError):
            continue

    # live log
    logs = []
    for log in RequestLog.select().order_by(RequestLog.id.desc()).limit(100):
        logs.append({
            "id": log.id,
            "time": log.timestamp.strftime('%H:%M:%S'),
            "method": log.method,
            "path": log.path,
            "status": log.status_code,
            "latency": log.latency_ms,
            "details": {
                "headers": json.loads(log.headers),
                "body": json.loads(log.body) if log.body and log.body.startswith('{') else log.body,
                "error": log.error_message
            }
        })

    return JSONResponse({
        "summary": {
            "total": total,
            "avg_latency": round(avg_latency),
            "error_rate": round(errors / total * 100, 2) if total else 0
        },
        "timeline": {
            "labels": timeline_labels,
            "data": timeline_data
        },
        "status_dist": status_dist,
        "faculties": dict(faculty_counts),
        "groups": dict(group_counts),
        "logs": logs
    })


@dashboard.get("/dashboard", response_class=HTMLResponse)
def get_dashboard_page(protected: bool = Depends(protect_dashboard)) -> HTMLResponse:  # noqa
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
