import json
import os
import secrets

from starlette.responses import HTMLResponse
from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from peewee import fn
from v2.models import RequestLog, FacultiesModel, ClientSettingsModel


security = HTTPBasic()
dashboard = APIRouter()


def safe_json_loads(json_string: str, default_value=None):
    if default_value is None:
        default_value = {}
    try:
        return json.loads(json_string.replace("'", "\""))
    except (json.JSONDecodeError, TypeError):
        return default_value if isinstance(default_value, dict) else json_string


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
def get_dashboard_data_v2(protected: bool = Depends(protect_dashboard)):  # noqa
    faculty_map = {}
    for faculty in FacultiesModel.select():
        try:
            groups = json.loads(faculty.data.replace("'", "\""))
            for group in groups:
                faculty_map[group] = faculty.name
        except:
            continue

    requests_data = []
    user_groups = {}

    all_logs = RequestLog.select().order_by(RequestLog.timestamp.desc())

    for log in all_logs.iterator():
        params = {}
        try:
            params = json.loads(log.params.replace("'", "\""))
        except:
            pass

        group = params.get("group", "")
        client_id = log.client_id

        requests_data.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "method": log.method,
            "path": log.path,
            "status": log.status_code,
            "responseTime": log.latency_ms,
            "ip": log.client_host,
            "faculty": faculty_map.get(group, "Unknown"),
            "group": group,
            "headers": log.headers,
            "body": log.body,
            "error": log.error_message if log.status_code >= 500 else None
        })

        if client_id and client_id not in user_groups:
            if group and "-" in group:
                user_groups[client_id] = {
                    "group": group,
                    "faculty": faculty_map.get(group, "Unknown")
                }

    ads_settings = ClientSettingsModel.select(
        ClientSettingsModel.client_id, ClientSettingsModel.ads_enabled
    )
    ads_map = {s.client_id: s.ads_enabled for s in ads_settings}

    first_requests = (
        RequestLog.select(
            RequestLog.client_id,
            fn.MIN(RequestLog.timestamp).alias('join_date')
        )
        .where(RequestLog.client_id.is_null(False))
        .group_by(RequestLog.client_id)
    )

    users_data = []
    for row in first_requests:
        cid = row.client_id
        grp_info = user_groups.get(cid, {})

        users_data.append({
            "client_id": cid,
            "username": f"user_{cid}",
            "ad_enabled": ads_map.get(cid, False),
            "join_date": row.join_date.isoformat(),
            "group": grp_info.get("group"),
            "faculty": grp_info.get("faculty")
        })

    return {
        "requests": requests_data,
        "users": users_data
    }


@dashboard.get("/dashboard", response_class=HTMLResponse)
def get_dashboard_page(protected: bool = Depends(protect_dashboard)) -> HTMLResponse:  # noqa
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
