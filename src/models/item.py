from dataclasses import dataclass


@dataclass
class Item:
    url: str
    name: str
    price: int
