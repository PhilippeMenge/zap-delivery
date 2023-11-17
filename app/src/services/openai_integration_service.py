import json
import logging
from datetime import datetime
from threading import Lock

import openai
from src.config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from src.domain.Address import Address
from src.domain.Order import Order, OrderStatus
from src.domain.OrderItem import OrderItem
from src.domain.UserThread import UserThread
from src.infrastructure.repositories.address_repository import AddressRepository
from src.infrastructure.repositories.menu_items_repository import MenuItemRepository
from src.infrastructure.repositories.user_thread_repository import UserThreadRepository
from src.services.google_maps_integration_service import GoogleMapsIntegrationService
from src.services.order_service import OrderService
from src.utils.custom_json_encoder import CustomJsonEncoder


class FunctionProcessingError(Exception):
    """### Exception raised when an error occurs while processing a function.

    Note that the message will be sent to OpenAI, so it should be in portuguese.
    """

    def __init__(self, message: str):
        self.message = message


class OpenAiIntegrationService:
    def __init__(
        self,
        menuItemsRepository: MenuItemRepository,
        userThreadRepository: UserThreadRepository,
        orderService: OrderService,
        googleMapsIntegrationService: GoogleMapsIntegrationService,
        addressRepository: AddressRepository,
    ):
        self.client = openai.Client(api_key=OPENAI_API_KEY)

        if OPENAI_ASSISTANT_ID is None:
            raise Exception("OPENAI_ASSISTANT_ID is not defined.")

        self.assistant = self.client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

        self._menuItemsRepository = menuItemsRepository
        self._userThreadRepository = userThreadRepository
        self._orderService = orderService
        self._googleMapsIntegrationService = googleMapsIntegrationService
        self._addressRepository = addressRepository

        self.run_requests_lock = Lock()
        self.run_requests: dict[str, datetime] = {}

    def create_thread(self) -> str:
        """### Create a thread in OpenAI

        Returns:
            str: The ID of the thread.
        """
        thread = self.client.beta.threads.create()
        logging.info(f"Created thread {thread.id}")
        return thread.id

    def send_user_message(self, thread_id: str, message: str):
        """### Send a user message to OpenAI

        Args:
            thread_id (str): The ID of the thread.
            message (str): The message to send.
        """
        message = f"{datetime.now().strftime('%d/%m/%Y, %H:%M')} - {message}"
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            content=message,
            role="user",
        )
        logging.info(f"Added message to thread {thread_id}: {message}")

    def _get_eta(self, user_address_id: str, user_thread: UserThread) -> dict:
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
        user_address = self._addressRepository.get_address(user_address_id)

        if user_address is None:
            raise FunctionProcessingError(
                "Endereço não encontrado do usuário não encontrado."
            )

        seconds_between_addresses = (
            self._googleMapsIntegrationService.get_time_between_addresses(
                origin=establishment_address, destination=user_address
            )
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

    def _create_order(
        self, address_id: str, items: list[dict], user_thread: UserThread
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
            menu_item = self._menuItemsRepository.get_menu_item_by_id(item["item_id"])

            if menu_item is None:
                raise FunctionProcessingError(f"Item {item['item_id']} não encontrado.")

            order_items.append(
                OrderItem(menu_item=menu_item, amount=amount, observation=observation)
            )

        address = self._addressRepository.get_address(address_id)

        if address is None:
            raise FunctionProcessingError("Endereço não encontrado.")

        order = Order(
            address=address,
            itens=order_items,
            status=OrderStatus.AWAITING_PAYMENT,
            user_thread=user_thread,
        )

        checkout_session_url = self._orderService.create_order(order)

        logging.info(
            f"Created order {order.id} for user {user_thread.phone_number}, checkout session URL: {checkout_session_url}"
        )

        return {
            "payment_url": checkout_session_url,
            "order_info": order,
        }

    def _get_address_data_from_text(self, text: str, user_thread: UserThread):
        """### Get address data from text

        Uses Google Maps API to get the address data from a text.

        Args:
            text (str): The text.
            user_thread (UserThread): The user thread.

        Returns:
            dict: The address data.
        """
        address_data = self._googleMapsIntegrationService.get_address_from_text(text)

        if len(address_data) == 0:
            raise FunctionProcessingError("Não foi possível encontrar o endereço.")

        logging.info(
            f"Address data for user {user_thread.phone_number}: {address_data}"
        )
        return address_data

    def _get_all_menu_items(self, user_thread: UserThread):
        """### Get all menu items

        Args:
            user_thread (UserThread): The user thread.

        Returns:
            dict: The menu items.
        """
        menu_items = self._menuItemsRepository.get_all_menu_items()
        logging.info(f"Menu items for user {user_thread.phone_number}: {menu_items}")
        return {"menu_items": menu_items}

    def _get_order_details(self, order_id: str, user_thread: UserThread):
        """### Get order details

        Args:
            order_id (str): The ID of the order.
            user_thread (UserThread): The user thread.

        Returns:
            dict: The order details.
        """
        order = self._orderService.get_order(order_id)

        if order is None:
            raise FunctionProcessingError("Pedido não encontrado.")

        logging.info(f"Order details for user {user_thread.phone_number}: {order}")
        return {"order_info": order}

    def _get_establishment_contact_info(self, user_thread: UserThread):
        """### Get establishment contact info

        Args:
            user_thread (UserThread): The user thread.

        Returns:
            dict: The establishment contact info.
        """
        establishment_phone_number = "+5511999999999"

        logging.info(
            f"Establishment contact info for user {user_thread.phone_number}: {establishment_phone_number}"
        )
        return {
            "establishment_contact_info": {
                "phone_number": establishment_phone_number,
            }
        }

    def _create_address(
        self,
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

        self._addressRepository.add_address(address)

        logging.info(f"Created address for user {user_thread.phone_number}: {address}")
        return {"address_info": address}

    FUNCTIONS = {
        "get_all_menu_items": _get_all_menu_items,
        "create_order": _create_order,
        "get_order_details": _get_order_details,
        "get_establishment_contact_info": _get_establishment_contact_info,
        "get_address_data_from_text": _get_address_data_from_text,
        "create_address": _create_address,
        "get_eta": _get_eta,
    }

    def _execute_actions(self, run) -> list[dict]:
        """### Execute all actions in a run.

        Args:
            run (Run): The OpenAI run.

        Returns:
            list[dict]: The outputs of the actions.
        """
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            try:
                if tool_call.type != "function":
                    continue

                function_name = tool_call.function.name
                function_args = tool_call.function.arguments

                thread_id = run.thread_id
                user_thread = self._userThreadRepository.get_user_thread_from_thread_id(
                    thread_id=thread_id
                )

                output = self.FUNCTIONS[function_name](self, **json.loads(function_args), user_thread=user_thread)  # type: ignore
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": CustomJsonEncoder().encode(output),
                    }
                )

            except FunctionProcessingError as e:
                logging.error(e)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": e.message}),
                    }
                )

            except Exception as e:
                logging.error(e)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(
                            {"error": "Erro inexperado ao executar ação."}
                        ),
                    }
                )

        return tool_outputs

    def request_run_assistant_on_thread(self, thread_id: str):
        """### Request a run on a thread.

        Adds the thread to the run requests list. The run will be executed in the next 10 seconds, unless another request is made.
        This is done to allow users to send multiple messages before the assistant runs.

        Args:
            thread_id (str): The ID of the thread.
        """
        with self.run_requests_lock:
            self.run_requests[thread_id] = datetime.now()

    def execute_due_requests(self) -> dict[str, list[str]]:
        """### Executes all due run requests.

        Returns:
            dict[str, list[str]]: A dict with the thread IDs as keys and the messages sent by the assistant as values.
        """
        responses = {}
        with self.run_requests_lock:
            run_requests_copy = self.run_requests.copy()
            for thread_id, request_time in run_requests_copy.items():
                if (datetime.now() - request_time).seconds >= 10:
                    responses[thread_id] = self.run_assistant_on_thread(thread_id)
                    del self.run_requests[thread_id]
        return responses

    def run_assistant_on_thread(self, thread_id: str) -> list[str]:
        """### Run the assistant on a thread.

        Args:
            thread_id (str): The ID of the thread.

        Returns:
            list[str]: The messages sent by the assistant.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
        )

        run_completed = False
        while not run_completed:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )

            match run.status:
                case "completed":
                    run_completed = True
                case "requires_action":
                    tool_outputs = self._execute_actions(run)

                    self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs,  # type: ignore
                    )

                    continue

                case _:
                    continue

        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=thread_id,
            run_id=run.id,
        )

        messages = []

        for run_step in run_steps:
            if run_step.step_details.type != "message_creation":
                continue

            message_id = run_step.step_details.message_creation.message_id

            contents = self.client.beta.threads.messages.retrieve(
                thread_id=thread_id,
                message_id=message_id,
            ).content

            for content in contents:
                if content.type != "text":
                    continue

                messages.append(content.text.value)

        messages.reverse()  # For some baffling reason, the messages are returned in reverse order by OpenAI.
        return messages
