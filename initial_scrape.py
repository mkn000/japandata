import concurrent.futures
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from utils import data_parser

games = []
url = "https://nichebarrier.com/weekly/2011-02-27"
latest = False

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    while not latest:
        resp = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

        content = resp.content

        soup = bs(content, "html.parser")

        next = soup.select("a.btn.btn-primary")[2]

        gametable = soup.select("td > a")
        links = [str(x.get("href")) for x in gametable]  # make picklable
        ids = [data_parser.parse_table_row(link) for link in links]
        new = [x for x in ids if not any(d["famitsu_id"] == x for d in games)]
        future_to_id = {
            executor.submit(data_parser.fetch_and_parse, id): id for id in new
        }
        for future in concurrent.futures.as_completed(future_to_id):
            g = future.result()
            games.append(g)

        url = next.get("href")

        latest = "disabled" in next.get_attribute_list("class")

df = pd.DataFrame(games)

# TODO: dataframe to database/file/whatever
