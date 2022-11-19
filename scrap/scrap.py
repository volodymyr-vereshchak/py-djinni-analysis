import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient
from bs4 import BeautifulSoup
from textblob import TextBlob
from config import PRIMARY_KEYWORD, BASE_URL, HOME_URL


@dataclass
class Technologies:
    salary: int
    technologies: set[str]
    experience: int
    views: int
    applications: int


def get_num_of_pages(soup: BeautifulSoup) -> int:
    return int(soup.select("li.page-item")[-2].text)


def get_all_detail_links(soup: BeautifulSoup) -> list[str]:
    return [tag.get("href") for tag in soup.select("a.profile")]


def get_detail(response: httpx.Response) -> Technologies:
    soup = BeautifulSoup(response.content, "html.parser")
    salary_tag = soup.get(".public-salary-item")
    salary = salary_tag.text if salary_tag else None
    t_body = soup.select_one(".job-additional-info--body")
    t = t_body.select(".job-additional-info--item-text")
    technologies = set(TextBlob(t[1].text.strip()).words) if len(t) == 4 else None
    experience_text = t[-1].text.split()[0]
    experience = int(experience_text) if experience_text.isdigit() else 0
    views_tag = soup.select_one(".profile-page-section.text-small .text-muted").text.split()
    views = int(views_tag[6])
    applications = int(views_tag[-2])
    return Technologies(
        salary=salary,
        technologies=technologies,
        experience=experience,
        views=views,
        applications=applications
    )


async def get_detail_info_from_page(links: list[str]) -> list[Technologies]:
    vacancies = []
    async with AsyncClient() as client:
        responses = await asyncio.gather(*[client.get(urljoin(HOME_URL, link)) for link in links])

    for response in responses:
        vacancies.append(get_detail(response))
    return vacancies


async def main():
    vacancies = []
    async with AsyncClient() as client:
        first_response = await client.get(BASE_URL, params={"primary_keyword": PRIMARY_KEYWORD})
        first_soup = BeautifulSoup(first_response.content, "html.parser")
        pages = get_num_of_pages(first_soup)
        pages_links = get_all_detail_links(first_soup)
        vacancies += await get_detail_info_from_page(pages_links)
        responses = await asyncio.gather(*[
            client.get(
                BASE_URL, params={"primary_keyword": PRIMARY_KEYWORD, "page": i}
            ) for i in range(2, pages + 1)
        ])

    for response in responses:
        pages_links = get_all_detail_links(BeautifulSoup(response.content, "html.parser"))
        vacancies += await get_detail_info_from_page(pages_links)
    pass


if __name__ == '__main__':
    asyncio.run(main())
