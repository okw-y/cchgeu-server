import asyncio
import urllib3

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from apitally.fastapi import ApitallyMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from v2.middlewares import StatisticsMiddleware
from v2.routers import update_groups, v1router, v2router, dashboard


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    # await asyncio.to_thread(update_groups, True)

    scheduler.add_job(
        update_groups, IntervalTrigger(hours=6), id="update"
    )
    scheduler.start()

    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)
app.add_middleware(
    ApitallyMiddleware,

    client_id="9c2b0bc7-2780-493e-a7b3-490882fe734c",
    env="prod",

    enable_request_logging=True,
    log_request_headers=True,
    log_request_body=True,
    log_response_body=True,
    capture_logs=True
)
app.add_middleware(StatisticsMiddleware)

app.include_router(v1router)
app.include_router(v2router)
app.include_router(dashboard)
