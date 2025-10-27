from .fields import IntegerListField

from peewee import SqliteDatabase, Model, IntegerField, CharField, TextField, BooleanField


db = SqliteDatabase("storage/ccgeu.db")


class BaseModel(Model):
    class Meta:
        database = db


class ScheduleModel(BaseModel):
    index = IntegerField()
    date = IntegerField()
    time = TextField()
    type = TextField()
    lesson = TextField()
    audience = TextField()
    teacher = TextField()
    group = TextField()
    subgroup = IntegerField()
    weeks = IntegerListField()
    wktp = IntegerField()


class Schedules(BaseModel):
    name = CharField()
    data = TextField()
    is_group = BooleanField()


class FacultiesModel(BaseModel):
    name = CharField()
    data = TextField()


class TeachersModel(BaseModel):
    name = CharField()
    data = TextField()


class LastUpdateModel(BaseModel):
    name = CharField()
    date = CharField()
    time = CharField()


class ClientSettingsModel(BaseModel):
    client_id = CharField(max_length=255, primary_key=True)
    ads_enabled = BooleanField(default=True)


db.connect()
db.create_tables(
    [Schedules, ScheduleModel, FacultiesModel, TeachersModel, LastUpdateModel, ClientSettingsModel]
)
