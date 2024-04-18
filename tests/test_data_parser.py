import pytest

from utils import data_parser
import datetime
from bs4 import BeautifulSoup as bs
import sys

sys.path.append(".")

FILES = ["tests/ff7r.html", "tests/ff7r_fami.html"]


@pytest.fixture()
def soup(filename: str) -> bs:
    with open(filename, "r", encoding="utf-8", errors="ignore") as fp:
        return bs(fp, "html.parser")


@pytest.mark.parametrize("filename", [FILES[1]])
def test_parser_title(soup):
    assert data_parser.parse_title(soup) == (
        "Final Fantasy VII Remake",
        "PlayStation 4",
        "Square Enix",
    )


@pytest.mark.parametrize("filename, mode", [(FILES[1], "fami")])
def test_parser_date(soup, mode):
    assert data_parser.parse_date(soup, mode) == datetime.datetime(2020, 4, 10)


@pytest.mark.parametrize("filename", FILES)
def test_parser_price(soup):
    assert data_parser.parse_price(soup) == 8980.0


@pytest.mark.parametrize(
    "filename, mode, expected",
    [(FILES[0], "comg", [16, 470]), (FILES[1], "fami", [702853, 954342])],
)
def test_parser_sales(soup, mode, expected):
    s = data_parser.parse_sales(soup, mode)
    assert [s[0][1], s[-1][1]] == expected


@pytest.mark.parametrize("filename", [FILES[1]])
def test_parse_genre(soup):
    g = data_parser.parse_genre(soup)
    assert g == "RPG"
