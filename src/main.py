import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import DefaultDict, List

import pandas as pd
import tldextract

from parsers.bestmebelshop_parser import BestmebelshopParser
from parsers.config import max_workers as DEFAULT_MAX_WORKERS
from parsers.hoff_parser import HoffParser
from parsers.lemanapro import LemanaproParser
from parsers.mnogomebeli_parser import MnogomebeliParser
from parsers.nonton_parser import NontonParser
from parsers.ozon_parser import OzonParser
from parsers.pm import PmParser
from parsers.pushe import PusheParser
from parsers.wildberries_parser import WildberriesParser
from utils.logger import get_logger

logger = get_logger(__name__)


def dump_to_excel(data: pd.DataFrame) -> None:
    output_dir = Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)
    fdate = date.today().strftime("%Y-%m-%d")
    file_path = output_dir / f"{fdate}.xlsx"
    data.to_excel(file_path, engine="xlsxwriter", index=False)
    logger.info(f"Data dumped to {file_path}")


PARSERS = {
    "bestmebelshop.ru": BestmebelshopParser,
    "hoff.ru": HoffParser,
    "lemanapro.ru": LemanaproParser,
    "mnogomebeli.com": MnogomebeliParser,
    "nonton.ru": NontonParser,
    "ozon.ru": OzonParser,
    "pm.ru": PmParser,
    "pushe.ru": PusheParser,
    "wildberries.ru": WildberriesParser,
}


def process_domain(domain: str, urls: list[str]) -> pd.DataFrame:
    parser_class = PARSERS.get(domain)

    if parser_class is None:
        logger.warning(f"No parser found for {domain}")
        return pd.DataFrame(columns=["url", "name", "price"])

    try:
        logger.info(f"Start parsing {domain}")

        with parser_class() as parser:
            parser.set_location("Москва")
            parser.collect_data(urls)
            result = parser.export_to_df()

        logger.info(f"Finished parsing {domain}. Parsed {len(result)} items")
        return result

    except Exception:
        logger.exception(f"Failed while processing domain {domain}")
        return pd.DataFrame(columns=["url", "name", "price"])


def collect_data(urls_by_domains: DefaultDict[str, list[str]]) -> pd.DataFrame:
    dfs = []

    # Используем импортированный max_workers, если он задан
    workers = min(DEFAULT_MAX_WORKERS or 4, len(urls_by_domains))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_domain, domain, urls): domain
            for domain, urls in urls_by_domains.items()
        }

        for future in as_completed(futures):
            domain = futures[future]

            try:
                dfs.append(future.result())

            except Exception:
                logger.exception(
                    f"Unexpected error while collecting result for {domain}"
                )

    if not dfs:
        return pd.DataFrame(columns=["url", "name", "price"])

    return pd.concat(dfs, ignore_index=True)


def get_domain_urls() -> DefaultDict[str, list[str]]:
    file_path = Path("data/urls.txt")
    if not file_path.exists():
        logger.error(f"Source file {file_path} not found")
        return defaultdict(list)

    with open(file_path, "r", encoding="utf-8") as file:
        all_urls = [line.strip() for line in file if line.strip()]

    urls_by_domains = defaultdict(list)
    for url in all_urls:
        domain = tldextract.extract(url).registered_domain
        if domain:
            urls_by_domains[domain].append(url)

    return urls_by_domains


def main():
    parser = argparse.ArgumentParser(description="Web parser for furniture shops.")

    # Создаем маппинг "имя аргумента -> домен" на основе ключей PARSERS
    # Например: 'wildberries' -> 'wildberries.ru'
    arg_to_domain = {domain.split(".")[0]: domain for domain in PARSERS}

    for arg_name in arg_to_domain:
        parser.add_argument(
            f"--{arg_name}",
            action="store_true",
            help=f"Run parser for {arg_to_domain[arg_name]}",
        )

    args = parser.parse_args()

    # Проверяем, были ли переданы какие-либо флаги для фильтрации
    selected_domains = [
        domain for arg, domain in arg_to_domain.items() if getattr(args, arg)
    ]

    domain_urls = get_domain_urls()

    # Если указаны конкретные парсеры, фильтруем список задач
    if selected_domains:
        domain_urls = {
            d: urls for d, urls in domain_urls.items() if d in selected_domains
        }
        logger.info(f"Filtering runs for: {', '.join(selected_domains)}")

    if not domain_urls:
        logger.warning("No URLs found for the selected domains or urls.txt is empty.")
        return

    collected_data = collect_data(domain_urls)

    if not collected_data.empty:
        dump_to_excel(collected_data)
    else:
        logger.warning("No data was collected, skipping export.")


if __name__ == "__main__":
    main()
