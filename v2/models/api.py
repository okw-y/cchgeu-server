from pydantic import BaseModel


class Lesson(BaseModel):
    index: int
    date: int
    time: str
    type: str
    lesson: str
    audience: str
    teacher: str
    group: str
    subgroup: int = -1
    weeks: list[int] = []
    wktp: int = 0

    def equals(self, other: "Lesson") -> bool:
        return all((
            self.index == other.index,
            self.date == other.date,
            self.time == other.time,
            self.type == other.type,
            self.lesson == other.lesson,
            self.audience == other.audience,
            self.teacher == other.teacher,
            self.group == other.group,
            self.weeks == other.weeks,
            self.wktp == other.wktp
        ))


class Schedule(BaseModel):
    date: str
    time: str
    schedule: list[Lesson]


class Teacher(BaseModel):
    name: str
    photo: str = ""
    graduation: str = ""
    university: str = ""
    url: str = ""
    emails: list[str] = []
