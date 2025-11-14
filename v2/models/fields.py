from peewee import Field


class IntegerListField(Field):
    field_type = "integer_list"

    def db_value(self, value: list[int]) -> str:
        return ";".join([str(vl) for vl in value])

    def python_value(self, value: str) -> list[int]:
        return [int(vl) for vl in str(value).split(";") if vl]
