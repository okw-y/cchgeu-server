import bs4
import requests
import re


def get_groups(url: str) -> tuple[str, list[dict]]:
    parser = bs4.BeautifulSoup(
        requests.get(
            url, verify=False, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
            }
        ).text, "html.parser"
    )

    faculty = parser.find("h1").text.replace("Расписание ", "")
    schedule = parser.find("div", attrs={"class": "docs pane"})

    files = []
    for file in schedule.find_all("a"):
        files.append(
            {
                "group": file.text.replace(".xlsx", "").replace(".xls", ""),
                "file": f"https://cchgeu.ru{file.get('href')}",
            }
        )

    for index, update in enumerate(schedule.find_all("small")):
        files[index]["last_update"] = list(
            re.findall(r"(\d{2}\.\d{2}\.\d{4})\s(\d{2}:\d{2})", update.text)[0]
        )

    return faculty, files