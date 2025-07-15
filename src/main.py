from collections import defaultdict
from datetime import date
from typing import DefaultDict, List

import pandas as pd
import tldextract

from parsers.bestmebelshop_parser import BestmebelshopParser
from parsers.divanru_parser import DivanParser
from parsers.fabrikastilru_parser import FabrikaStilParser
from parsers.hoffru_parser import HoffParser
from parsers.legkomarketru import LegkomarketParser
from parsers.mebelionru_parser import MebelionParser
from parsers.mnogomebeli_parser import MnogomebeliParser
from parsers.ozonru_parser import OzonParser
from parsers.parkmebelicom_parser import ParkmebeliParser
from parsers.pm_parser import PmParser
from parsers.stolplit_parser import StolplitParser
from utils.logger import get_logger

logger = get_logger(__name__)


def dump_to_excel(data: pd.DataFrame) -> None:
    fdate = date.today().strftime("%b-%d-%Y")
    data.to_excel(f"data/{fdate}.xlsx", engine="xlsxwriter", index=False)


def collect_data(urls_by_domains: DefaultDict[str, List[str]]) -> pd.DataFrame:
    """
    Try...except не используется осознанно. Требуется собирать все данные, падение скрипта нужна исправлять, но не перехватывать для продолжения.
    """
    PARSERS = {
        "ozon.ru": OzonParser,
        "divan.ru": DivanParser,
        "hoff.ru": HoffParser,
        "stolplit.ru": StolplitParser,
        "mebelion.ru": MebelionParser,
        "mnogomebeli.com": MnogomebeliParser,
        "bestmebelshop.ru": BestmebelshopParser,
        "pm.ru": PmParser,
        "fabrika-stil.ru": FabrikaStilParser,
        "legkomarket.ru": LegkomarketParser,
        "parkmebeli.com": ParkmebeliParser,
    }
    PARSED_ITEMS = pd.DataFrame(columns=["url", "name", "price"])
    for domain, urls in urls_by_domains.items():
        # try:
        with PARSERS[domain]() as parser:
            parser.set_location("Москва")
            parser.collect_data(urls)
            PARSED_ITEMS = pd.concat(
                [PARSED_ITEMS, parser.export_to_df()], ignore_index=True
            )
        # except KeyError:
        #     logger.info(f"No parser found for {domain}")
    return PARSED_ITEMS


def get_domain_urls() -> DefaultDict[str, List[str]]:
    with open("data/urls.txt", "r") as file:
        all_urls = [line.strip() for line in file]
    urls_by_domains = defaultdict(list)
    for url in all_urls:
        domain = tldextract.extract(url).top_domain_under_public_suffix
        urls_by_domains[domain].append(url)
    return urls_by_domains


def main():
    domain_urls = get_domain_urls()
    collected_data = collect_data(domain_urls)
    dump_to_excel(collected_data)


if __name__ == "__main__":
    main()
