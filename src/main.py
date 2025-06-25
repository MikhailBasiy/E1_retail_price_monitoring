from collections import defaultdict
from typing import DefaultDict, List

import pandas as pd
import tldextract
from datetime import date

from parsers.ozon_parser import OzonParser
from utils.logger import get_logger

logger = get_logger(__name__)


def collect_data(urls_by_domains: DefaultDict[str, List[str]]) -> pd.DataFrame:
    PARSERS = {
        "ozon.ru": OzonParser,
    }
    PARSED_ITEMS = pd.DataFrame(columns=["url", "name", "price"])
    for domain, urls in urls_by_domains.items():
        with PARSERS[domain]() as parser:
            for url in urls:
                parser.get_item_data(url)
            logger.info(f"Parsed items: {len(parser.parsed_data)}")
            PARSED_ITEMS = pd.concat(
                [PARSED_ITEMS, parser.export_to_df()], ignore_index=True
            )
    return PARSED_ITEMS


def get_urls_by_domains() -> DefaultDict[str, List[str]]:
    with open("data/urls.txt", "r") as file:
        all_urls = [line.strip() for line in file]
    urls_by_domains = defaultdict(list)
    for url in all_urls:
        domain = tldextract.extract(url).top_domain_under_public_suffix
        urls_by_domains[domain].append(url)
    return urls_by_domains


def main():
    urls_by_domains = get_urls_by_domains()
    data = collect_data(urls_by_domains)
    fdate = date.today().strftime("%b-%d-%Y")
    data.to_excel(f"data/{fdate}.xlsx", engine="xlsxwriter", index=False)


if __name__ == "__main__":
    main()
