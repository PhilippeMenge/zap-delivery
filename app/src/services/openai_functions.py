from __future__ import annotations

import logging
from typing import Callable

from src.domain.Address import Address
from src.domain.Order import Order, OrderStatus
from src.domain.OrderItem import OrderItem
from src.domain.UserThread import UserThread
from src.services import openai_integration_service
from src.services.exceptions import FunctionProcessingError

FUNCTIONS: dict[str, Callable] = {}


def register_function(name: str):
    """### A decorator to register a function in the FUNCTIONS dict.

    Args:
        name (str): The name of the function.
    """

    def decorator(func: Callable):
        FUNCTIONS[name] = func
        return func

    return decorator


def get_function(name: str) -> Callable:
    """### Get a function by name.

    Internally, this function uses the FUNCTIONS dict to get the function.

    Args:
        name (str): The name of the function.

    Returns:
        Callable: The function.
    """
    return FUNCTIONS[name]


@register_function("get_eta")
def get_eta(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    user_address_id: str,
    user_thread: UserThread,
) -> dict:
    """### Calculates the ETA for a given address.

    For now, values for the prep time and restaurant location are hardcoded.
    In the future, the restaurant data will be retrieved from the UserThread.

    Args:
        user_address_id (str): The ID of the user's address.
        user_thread (UserThread): The user thread.

    Returns:
        dict: The ETA.
    """
    establishment_address = Address(
        street="Av Boa Viagem",
        number="2080",
        complement="Sala 1001",
        neighborhood="Boa Viagem",
        city="Recife",
        state="PE",
        country="Brasil",
        zipcode="51111-000",
    )

    establhisment_production_time_minutes = 30
    establishment_error_margin_minutes = 10

    user_address = openAiIntegrationService._addressRepository.get_address(
        user_address_id
    )

    if user_address is None:
        raise FunctionProcessingError(
            "Endereço não encontrado do usuário não encontrado."
        )

    seconds_between_addresses = openAiIntegrationService._googleMapsIntegrationService.get_time_between_addresses(
        origin=establishment_address, destination=user_address
    )

    if seconds_between_addresses is None:
        raise FunctionProcessingError(
            "Não foi possível calcular o tempo entre os endereços. A rota pode não existir."
        )

    seconds_between_addresses += establhisment_production_time_minutes * 60
    seconds_between_addresses += establishment_error_margin_minutes * 60
    minutes_between_addresses = seconds_between_addresses // 60

    logging.info(
        f"ETA for user {user_thread.phone_number} is {minutes_between_addresses} minutes."
    )
    return {
        "eta_seconds": seconds_between_addresses,
        "eta_minutes": minutes_between_addresses,
    }


@register_function("create_order")
def create_order(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    address_id: str,
    items: list[dict],
    user_thread: UserThread,
) -> dict:
    """### Create an order

    Args:
        address_id (str): The ID of the address.
        items (list[dict]): The items of the order.
        user_thread (UserThread): The user thread.

    Returns:
        dict: The order info and the payment URL.
    """
    order_items = []
    for item in items:
        amount = item["amount"]
        observation = item.get("observation", "")
        menu_item = openAiIntegrationService._menuItemsRepository.get_menu_item_by_id(
            item["item_id"]
        )

        if menu_item is None:
            raise FunctionProcessingError(f"Item {item['item_id']} não encontrado.")

        order_items.append(
            OrderItem(menu_item=menu_item, amount=amount, observation=observation)
        )

    address = openAiIntegrationService._addressRepository.get_address(address_id)

    if address is None:
        raise FunctionProcessingError("Endereço não encontrado.")

    order = Order(
        address=address,
        itens=order_items,
        status=OrderStatus.AWAITING_PAYMENT,
        user_thread=user_thread,
    )

    checkout_session_url = openAiIntegrationService._orderService.create_order(order)
    logging.info(
        f"Created order {order.id} for user {user_thread.phone_number}, checkout session URL: {checkout_session_url}"
    )

    return {
        "payment_url": checkout_session_url,
        "order_info": order,
    }


@register_function("get_address_data_from_text")
def get_address_data_from_text(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    text: str,
    user_thread: UserThread,
):
    """### Get address data from text

    Uses Google Maps API to get the address data from a text.

    Args:
        text (str): The text.
        user_thread (UserThread): The user thread.

    Returns:
        dict: The address data.
    """
    address_data = (
        openAiIntegrationService._googleMapsIntegrationService.get_address_from_text(
            text
        )
    )

    if len(address_data) == 0:
        raise FunctionProcessingError("Não foi possível encontrar o endereço.")

    logging.info(f"Address data for user {user_thread.phone_number}: {address_data}")
    return address_data


@register_function("get_all_menu_items")
def get_all_menu_items(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    user_thread: UserThread,
):
    """### Get all menu items

    Args:
        user_thread (UserThread): The user thread.

    Returns:
        dict: The menu items.
    """
    menu_items = openAiIntegrationService._menuItemsRepository.get_all_menu_items()

    logging.info(f"Menu items for user {user_thread.phone_number}: {menu_items}")
    return {"menu_items": menu_items}


@register_function("get_order_details")
def get_order_details(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    order_id: str,
    user_thread: UserThread,
):
    """### Get order details

    Args:
        order_id (str): The ID of the order.
        user_thread (UserThread): The user thread.

    Returns:
        dict: The order details.
    """
    order = openAiIntegrationService._orderService.get_order(order_id)

    if order is None:
        raise FunctionProcessingError("Pedido não encontrado.")

    logging.info(f"Order details for user {user_thread.phone_number}: {order}")
    return {"order_info": order}


@register_function("get_establishment_contact_info")
def get_establishment_contact_info(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    user_thread: UserThread,
):
    """### Get establishment contact info

    Args:
        user_thread (UserThread): The user thread.

    Returns:
        dict: The establishment contact info.
    """
    establishment_phone_number = "+5511999999999"

    logging.info(
        f"Establishment contact info for user {user_thread.phone_number}:{establishment_phone_number}"
    )
    return {
        "establishment_contact_info": {
            "phone_number": establishment_phone_number,
        }
    }


@register_function("create_address")
def create_address(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    street: str,
    number: str,
    neighborhood: str,
    city: str,
    state: str,
    country: str,
    zipcode: str,
    user_thread: UserThread,
    complement: str | None = None,
) -> dict:
    """### Create an address

    Args:
        street (str): The street.
        number (str): The number.
        complement (str): The complement.
        neighborhood (str): The neighborhood.
        city (str): The city.
        state (str): The state.
        country (str): The country.
        zipcode (str): The zipcode.
        user_thread (UserThread): The user thread.

    Returns:
        dict: The address data.
    """
    address = Address(
        street=street,
        number=number,
        complement=complement,
        neighborhood=neighborhood,
        city=city,
        state=state,
        country=country,
        zipcode=zipcode,
    )

    openAiIntegrationService._addressRepository.add_address(address)
    logging.info(f"Created address for user {user_thread.phone_number}: {address}")
    return {"address_info": address}
