from dataclasses import dataclass

from domain import MenuItem


@dataclass
class OrderItem:
    menu_item: MenuItem
    amount: int
    observation: str
