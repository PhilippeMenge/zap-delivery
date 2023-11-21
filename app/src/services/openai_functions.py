from __future__ import annotations

from typing import Callable

from src.domain.Address import Address
from src.domain.Order import Order, OrderStatus
from src.domain.OrderItem import OrderItem
from src.domain.User import User
from src.services import openai_integration_service
from src.services.exceptions import FunctionProcessingError
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)

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
    user: User,
) -> dict:
    """### Calculates the ETA for a given address.

    For now, values for the prep time and restaurant location are hardcoded.
    In the future, the restaurant data will be retrieved from the User.

    Args:
        user_address_id (str): The ID of the user's address.
        user (User): The user.

    Returns:
        dict: The ETA.
    """
    logger.info(
        f"Calculating ETA for user {user.phone_number} on address {user_address_id}."
    )
    establishment_address = user.establishment.address
    establhisment_production_time_minutes = (
        user.establishment.estimated_production_minutes
    )

    establishment_error_margin_minutes = 10

    user_address = openAiIntegrationService._addressRepository.get_address(
        user_address_id
    )

    if user_address is None:
        logger.error(f"User address {user_address_id} not found.")

        raise FunctionProcessingError("Endereço do usuário não encontrado.")

    seconds_between_addresses = openAiIntegrationService._googleMapsIntegrationService.get_time_between_addresses(
        origin=establishment_address, destination=user_address
    )

    if seconds_between_addresses is None:
        logger.error(
            f"Could not calculate time between addresses for user {user.phone_number}"
        )

        raise FunctionProcessingError(
            "Não foi possível calcular o tempo entre os endereços. A rota pode não existir."
        )

    seconds_between_addresses += establhisment_production_time_minutes * 60
    seconds_between_addresses += establishment_error_margin_minutes * 60
    minutes_between_addresses = seconds_between_addresses // 60

    logger.info(
        f"ETA for user {user.phone_number}: {minutes_between_addresses} minutes"
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
    user: User,
) -> dict:
    """### Create an order

    Args:
        address_id (str): The ID of the address.
        items (list[dict]): The items of the order.
        user (User): The user.

    Returns:
        dict: The order info and the payment URL.
    """
    logger.info(f"Creating order for user {user.phone_number}")

    order_items = []
    for item in items:
        amount = item["amount"]
        observation = item.get("observation", "")
        menu_item = openAiIntegrationService._menuItemsRepository.get_menu_item_by_id(
            item["item_id"], user.establishment
        )

        if menu_item is None:
            logger.error(f"Item {item['item_id']} not found.")

            raise FunctionProcessingError(f"Item {item['item_id']} não encontrado.")

        order_items.append(
            OrderItem(menu_item=menu_item, amount=amount, observation=observation)
        )

    address = openAiIntegrationService._addressRepository.get_address(address_id)

    if address is None:
        logger.error(f"Address {address_id} not found.")

        raise FunctionProcessingError("Endereço não encontrado.")

    order = Order(
        address=address,
        itens=order_items,
        status=OrderStatus.AWAITING_PAYMENT,
        user=user,
    )

    checkout_session_url = openAiIntegrationService._orderService.create_order(order)
    logger.info(
        f"Created order {order.id} for user {user.phone_number}, checkout session URL: {checkout_session_url}"
    )

    return {
        "payment_url": checkout_session_url,
        "order_info": order,
    }


@register_function("get_address_data_from_text")
def get_address_data_from_text(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    text: str,
    user: User,
):
    """### Get address data from text

    Uses Google Maps API to get the address data from a text.

    Args:
        text (str): The text.
        user (User): The user.

    Returns:
        dict: The address data.
    """
    logger.info(f"Getting address data from text: {text}")
    address_data = (
        openAiIntegrationService._googleMapsIntegrationService.get_address_from_text(
            text
        )
    )

    if len(address_data) == 0:
        logger.error(f"Could not get address data from text: {text}")

        raise FunctionProcessingError("Não foi possível encontrar o endereço.")

    logger.info(f"Succesfully got address data from text: {address_data}")
    return address_data


@register_function("get_all_menu_items")
def get_all_menu_items(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    user: User,
):
    """### Get all menu items

    Args:
        user (User): The user.

    Returns:
        dict: The menu items.
    """
    menu_items = openAiIntegrationService._menuItemsRepository.get_all_menu_items_by_establishment(
        user.establishment
    )

    logger.info(f"Sucessfully got menu items for user {user.phone_number}")
    logger.debug(f"Menu items: {menu_items}")
    return {"menu_items": menu_items}


@register_function("get_order_details")
def get_order_details(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    order_id: str,
    user: User,
):
    """### Get order details

    Args:
        order_id (str): The ID of the order.
        user (User): The user.

    Returns:
        dict: The order details.
    """
    logger.info(f"Getting order details for order {order_id}")
    order = openAiIntegrationService._orderService.get_order(order_id)

    if order is None:
        logger.error(f"Order {order_id} not found.")

        raise FunctionProcessingError("Pedido não encontrado.")

    logger.info(f"Sucessfully got order details for order {order_id}")
    logger.debug(f"Order details: {order}")
    return {"order_info": order}


@register_function("get_establishment_contact_info")
def get_establishment_contact_info(
    openAiIntegrationService: openai_integration_service.OpenAiIntegrationService,
    user: User,
):
    """### Get establishment contact info

    Args:
        user (User): The user.

    Returns:
        dict: The establishment contact info.
    """
    establishment_phone_number = user.establishment.contact_number

    logger.info(
        f"Sucessfully got establishment contact info for user {user.phone_number}"
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
    user: User,
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
        user (User): The user.

    Returns:
        dict: The address data.
    """
    logger.info(f"Creating address for user {user.phone_number}")
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

    logger.info(
        f"Sucessfully created address for user {user.phone_number}: {address.id}"
    )
    return {"address_info": address}
