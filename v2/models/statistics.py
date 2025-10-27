import datetime

from peewee import (
    SqliteDatabase, Model, AutoField, DateTimeField,
    CharField, IntegerField, TextField
)


analytics_db = SqliteDatabase("storage/analytics.db")


class BaseModel(Model):
    class Meta:
        database = analytics_db


class RequestLog(BaseModel):
    id = AutoField()
    client_id = CharField(max_length=255, null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    method = CharField(max_length=10)

    path = CharField(max_length=255)
    params = TextField()

    status_code = IntegerField()
    latency_ms = IntegerField()
    client_host = CharField(max_length=50)
    headers = TextField()
    body = TextField(null=True)
    error_message = TextField(null=True)


analytics_db.connect()
analytics_db.create_tables([RequestLog])
