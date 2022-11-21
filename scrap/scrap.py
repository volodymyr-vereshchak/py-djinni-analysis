import asyncio
import csv
import re
import httpx

from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

from httpx import AsyncClient
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime
from scrap.config import PRIMARY_KEYWORD, BASE_URL, HOME_URL


@dataclass
class Technologies:
    salary: int
    technologies: str
    experience: int
    views: int
    applications: int


def get_num_of_pages(soup: BeautifulSoup) -> int:
    return int(soup.select("li.page-item")[-2].text)


def get_all_detail_links(soup: BeautifulSoup) -> list[str]:
    return [tag.get("href") for tag in soup.select("a.profile")]


def get_detail(response: httpx.Response) -> list[Technologies]:
    soup = BeautifulSoup(response.content, "html.parser")
    salary_tag = soup.select_one(".public-salary-item")

    salary = int(re.findall(r"\d+", salary_tag.text)[0]) if salary_tag else None
    info_body = soup.select_one(".job-additional-info--body")
    info_text = info_body.select(".job-additional-info--item-text")
    stop = {
        "api",
        "python3",
        "development",
        "backend",
        "machine",
        "team",
        "framework",
        "data",
        "lead",
        "and",
        "shell",
        "support",
        "phyton",
        "marketing",
        "technical",
        "leadership",
    }
    technologies = (
        set(TextBlob(info_text[1].text.strip()).words.lower()) - stop
        if len(info_text) == 4
        else []
    )
    experience_text = info_text[-1].text.split()[0]
    experience = int(experience_text) if experience_text.isdigit() else 0
    views_tag = soup.select_one(
        ".profile-page-section.text-small .text-muted"
    ).text.split()
    views = int(views_tag[6])
    applications = int(views_tag[-2])
    return [
        Technologies(
            salary=salary,
            technologies=tech,
            experience=experience,
            views=views,
            applications=applications,
        )
        for tech in technologies
        if technologies is not None
    ]


async def get_detail_info_from_page(links: list[str]) -> list[Technologies]:
    vacancies = []
    async with AsyncClient() as client:
        responses = await asyncio.gather(
            *[client.get(urljoin(HOME_URL, link)) for link in links]
        )

    for response in responses:
        vacancies += get_detail(response)
    return vacancies


def write_csv_file(file_name: str, all_content: list[Technologies]) -> None:
    with open(file_name, "w", encoding="utf-8", newline="") as csvfile:
        object_writer = csv.writer(csvfile)
        object_writer.writerow([field.name for field in fields(Technologies)])
        object_writer.writerows([astuple(content) for content in all_content])


async def scrap() -> str:
    vacancies = []
    async with AsyncClient() as client:
        first_response = await client.get(
            BASE_URL, params={"primary_keyword": PRIMARY_KEYWORD}
        )
        first_soup = BeautifulSoup(first_response.content, "html.parser")
        pages = get_num_of_pages(first_soup)
        pages_links = get_all_detail_links(first_soup)
        vacancies += await get_detail_info_from_page(pages_links)
        responses = await asyncio.gather(
            *[
                client.get(
                    BASE_URL, params={"primary_keyword": PRIMARY_KEYWORD, "page": page}
                )
                for page in range(2, pages + 1)
            ]
        )

    for response in responses:
        pages_links = get_all_detail_links(
            BeautifulSoup(response.content, "html.parser")
        )
        vacancies += await get_detail_info_from_page(pages_links)

    file_name = f"scrap/csv/{datetime.now().strftime('%d-%m-%y--%H-%M-%S')}-djinni.csv"
    write_csv_file(file_name, vacancies)
    return file_name


if __name__ == "__main__":
    asyncio.run(scrap())
