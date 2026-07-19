import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import DefaultDict, Optional

import pandas as pd
import tldextract

from parsers.bestmebelshop import BestmebelshopParser
from parsers.config import VALID_LOCATIONS
from parsers.hoff_parser import HoffParser
from parsers.lemanapro import LemanaproParser
from parsers.mnogomebeli import MnogomebeliParser
from parsers.nonton import NontonParser
from parsers.ozon import OzonParser
from parsers.pm import PmParser
from parsers.pushe import PusheParser
from parsers.wildberries import WildberriesParser
from settings import data_dir as DEFAULT_DIRECTORY
from settings import max_workers as DEFAULT_MAX_WORKERS
from utils.logger import get_logger

logger = get_logger(__name__)


def dump_to_excel(data: pd.DataFrame) -> None:
    output_dir = Path(DEFAULT_DIRECTORY)
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


def _process_single_location(
    domain: str, urls: list[str], location: str
) -> pd.DataFrame:
    parser_class = PARSERS.get(domain)

    if parser_class is None:
        logger.warning(f"No parser found for {domain}")
        return pd.DataFrame(columns=["url", "name", "price"])

    try:
        logger.info(f"Start parsing {domain} in {location}")

        with parser_class(location) as parser:
            parser.set_location()
            parser.collect_data(urls)
            result = parser.export_to_df()

        logger.info(
            f"Finished parsing {domain} in {location}. " f"Parsed {len(result)} items"
        )
        return result

    except Exception:
        logger.exception(f"Failed while processing {domain} in {location}")
        return pd.DataFrame(columns=["url", "name", "price"])


def process_domain(domain: str, urls: list[str], locations: list[str]) -> pd.DataFrame:
    results = []
    for location in locations:
        df = _process_single_location(domain, urls, location)
        if not df.empty:
            results.append(df)

    if not results:
        return pd.DataFrame(columns=["url", "name", "price", "city"])

    return pd.concat(results, ignore_index=True)


def collect_data(
    urls_by_domains: DefaultDict[str, list[str]],
    locations: list[str],
) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []

    workers = min(DEFAULT_MAX_WORKERS or 4, len(urls_by_domains))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_domain, domain, urls, locations): domain
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
        domain = tldextract.extract(url).top_domain_under_public_suffix
        if domain:
            urls_by_domains[domain].append(url)

    return urls_by_domains


def _build_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(description="Web parser for furniture shops.")

    arg_to_domain = {domain.split(".")[0]: domain for domain in PARSERS}

    for arg_name, domain in arg_to_domain.items():
        arg_parser.add_argument(
            f"--{arg_name}",
            action="store_true",
            help=f"Run parser for {domain}",
        )

    arg_parser.add_argument(
        "--location",
        nargs="+",
        default=None,
        choices=VALID_LOCATIONS,
        help=(
            "Список городов для парсинга. "
            "Пример: --location Москва Новосибирск. "
            "По умолчанию — все города из geo_settings."
        ),
    )

    return arg_parser, arg_to_domain


def main():
    arg_parser, arg_to_domain = _build_arg_parser()
    args = arg_parser.parse_args()

    locations = args.location or VALID_LOCATIONS
    logger.info(f"Locations: {', '.join(locations)}")

    selected_domains = [
        domain for arg, domain in arg_to_domain.items() if getattr(args, arg, False)
    ]

    domain_urls = get_domain_urls()

    if selected_domains:
        domain_urls = {
            d: urls for d, urls in domain_urls.items() if d in selected_domains
        }
        logger.info(f"Filtering runs for: {', '.join(selected_domains)}")

    if not domain_urls:
        logger.warning("No URLs found for the selected domains or urls.txt is empty.")
        return

    collected_data = collect_data(domain_urls, locations)

    if not collected_data.empty:
        location_suffix = "_".join(locations) if len(locations) <= 2 else "multi"
        dump_to_excel(collected_data)
    else:
        logger.warning("No data was collected, skipping export.")


if __name__ == "__main__":
    main()
