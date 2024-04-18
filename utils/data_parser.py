from bs4 import BeautifulSoup as bs
import re
import json5 as json
import requests
import datetime


def fetch_and_parse(
    fami_id: int, mode: str = "fami"
) -> (
    dict[int, str, str, str, str, datetime.datetime, str, float, list[list[int, int]]]
    | int
):
    resp = requests.get(
        f"https://nichebarrier.com/game/{fami_id}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )

    content = resp.content

    soup = bs(content, "html.parser")
    try:
        (title, platform, publisher) = parse_title(soup)
        sales = parse_sales(soup, mode)
        price = parse_price(soup)
        date = parse_date(soup, mode)
        genre = parse_genre(soup)

        return {
            "famitsu_id": fami_id,
            "title": title,
            "platform": platform,
            "publisher": publisher,
            "genre": genre,
            "release_date": date,
            "price": price,
            "sales": sales,
        }
    except AttributeError:
        print(fami_id)
        print(soup)
        return 0


def parse_title(soup: bs) -> tuple[str, str, str]:
    game = soup.select_one("[itemprop=name]").text
    platform = soup.select_one("[itemprop=gamePlatform]").text
    publisher = soup.select_one("[itemprop=publisher]").text

    return (game, platform, publisher)


def parse_sales(soup: bs, mode: str) -> list[list[int, int]]:
    if mode == "comg":
        p_sales = re.compile(r"((var preorders = )(?P<sales>\[\n.*\]))")
        s = soup.find("script", string=p_sales)
        m2 = re.search(p_sales, s.string)
        return json.loads(m2.group("sales"))
    elif mode == "fami":
        p_sales = re.compile(r"((var sales = )(?P<sales>\[\n.*\]))")
        s = soup.find("script", string=p_sales)
        m2 = re.search(p_sales, s.string)
        return json.loads(m2.group("sales"))


def parse_price(soup: bs) -> float:
    p_price = re.compile(r"(Price: )\¥(?P<price>(\d{0,4}\,\d{3}))")
    find_price = soup.find("li", {"class": "list-group-item"}, string=p_price)
    rp: str = re.match(p_price, find_price.string).group("price")

    return float(rp.replace(",", ""))


def parse_date(soup: bs, mode) -> datetime:
    rd: str
    if mode == "comg":
        p_date = re.compile(r"(Release Date: )(?P<date>(\w+\s[0-9]{1,2},\s[0-9]{4}))")
        find_date = soup.find("li", {"class": "list-group-item"}, string=p_date)
        rd = re.match(p_date, find_date.string).group("date")
    elif mode == "fami":
        rd = soup.select_one("li.list-group-item > span").text

    return datetime.datetime.strptime(rd, "%B %d, %Y")


def parse_genre(soup: bs) -> str:
    return soup.select_one("div.badge.bg-secondary").text


def parse_table_row(row) -> int:
    p_famiurl = re.compile(
        r"https\:\/\/nichebarrier\.com\/game\/(?P<fami_id>[0-9]{1,9})-.*"
    )

    fami_id = re.match(p_famiurl, row).group("fami_id")
    return int(fami_id)
