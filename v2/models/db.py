from peewee import SqliteDatabase, Model, CharField, TextField, BooleanField


db = SqliteDatabase("storage/ccgeu.db")


class BaseModel(Model):
    class Meta:
        database = db


class Schedules(BaseModel):
    name = CharField()
    data = TextField()
    is_group = BooleanField()


class Faculties(BaseModel):
    name = CharField()
    data = TextField()


class Teachers(BaseModel):
    name = CharField()
    data = TextField()


class LastUpdate(BaseModel):
    name = CharField()
    date = CharField()
    time = CharField()


db.connect()
db.create_tables(
    [Schedules, Faculties, Teachers, LastUpdate]
)
