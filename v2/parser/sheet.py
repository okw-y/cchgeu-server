import io
import pandas
import requests

from .lesson import lesson_info
from .gaps import split_lessons

from v2.models import Lesson


def consolidate_subgroups(pairs: list[Lesson]) -> list[Lesson]:
    output, previous = [pairs[0]], pairs[0]
    for pair in pairs[1:]:
        if not pair.equals(previous):
            output.append(pair)
            previous = pair
        else:
            output[-1].subgroup = -1

    return output[:]


def parse_sheet(path: str, group: str) -> list[Lesson]:
    sheet = pandas.read_excel(
        io.BytesIO(
            requests.get(
                path, verify=False, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
                }
            ).content
        ), index_col=None
    )

    schedule, last_day, last_time, last_pair = [], "", "", 0
    for index, array in enumerate(sheet.values[4:]):
        row = list(array)

        if isinstance(row[0], str):
            last_day = row[0]
            last_pair = -1

        if isinstance(row[1], str):
            last_time = row[1]

        if index % 2 == 0:
            last_pair += 1

        week = index % 2
        if isinstance(row[-1], str):
            results = []
            for split_name, split_audience, split_wktp in split_lessons(row[3], row[-1], week):
                results.append(
                    lesson_info(
                        index=last_pair,
                        date=last_day,
                        time=last_time,
                        name=split_name,
                        audience=split_audience,
                        group=group,
                        subgroup=-1,
                        wktp=split_wktp
                    )
                )

            results = [result for result in results if result]
            if results is not None:
                schedule.extend(
                    sorted(results, key=lambda value: value.wktp)
                )
        else:
            subrow = row[3:]
            for number, subgroup in enumerate(range(0, len(row) - 4, 2)):
                results = []
                for split_name, split_audience, split_wktp in split_lessons(
                        subrow[subgroup], subrow[subgroup + 1], week
                ):
                    results.append(
                        lesson_info(
                            index=last_pair,
                            date=last_day,
                            time=last_time,
                            name=split_name,
                            audience=split_audience,
                            group=group,
                            subgroup=number + 1,
                            wktp=split_wktp
                        )
                    )

                results = [result for result in results if result]
                if results is not None:
                    schedule.extend(
                        sorted(results, key=lambda value: value.wktp)
                    )

    return consolidate_subgroups(schedule)
