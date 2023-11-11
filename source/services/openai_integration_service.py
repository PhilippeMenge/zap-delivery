import json
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from threading import Lock

import openai
from config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from domain import Order, OrderStatus
from domain.OrderItem import OrderItem
from domain.UserThread import UserThread
from infrastructure.repositories import MenuItemRepository
from infrastructure.repositories.user_thread_repository import UserThreadRepository
from services.order_service import OrderService


class OpenAiIntegrationService:
    def __init__(
        self,
        menuItemsRepository: MenuItemRepository,
        userThreadRepository: UserThreadRepository,
        orderService: OrderService,
    ):
        self.client = openai.Client(api_key=OPENAI_API_KEY)
        self.assistant = self.client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

        self._menuItemsRepository = menuItemsRepository
        self._userThreadRepository = userThreadRepository
        self._orderService = orderService

        self.run_requests_lock = Lock()
        self.run_requests: dict[str, datetime] = {}

    def create_thread(self) -> str:
        """### Create a thread in OpenAI

        Returns:
            str: The ID of the thread.
        """
        thread = self.client.beta.threads.create()
        return thread.id

    def send_user_message(self, thread_id: str, message: str):
        """### Send a user message to OpenAI

        Args:
            thread_id (str): The ID of the thread.
            message (str): The message to send.
        """
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            content=message,
            role="user",
        )

    def _asdict_factory(self, data):
        """### Convert Enum to string when converting to dict

        Honestly this looks very very bad. I'm sorry.
        We should probably figure out a better way to do this.
        """

        def _convert(o):
            if isinstance(o, Enum):
                return o.value
            return o

        return dict((k, _convert(v)) for k, v in data)

    def _create_order(
        self, address: str, items: list[dict], user_thread: UserThread
    ) -> dict:
        """### Create an order

        Args:
            address (str): The address of the order.
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

            order_items.append(
                OrderItem(menu_item=menu_item, amount=amount, observation=observation)
            )

        order = Order(
            address=address,
            itens=order_items,
            status=OrderStatus.AWAITING_PAYMENT,
            user_thread=user_thread,
        )

        checkout_session_url = self._orderService.create_order(order)

        return {
            "payment_url": checkout_session_url,
            "order_info": asdict(order, dict_factory=self._asdict_factory),
        }

    def _get_all_menu_items(self, user_thread: UserThread):
        """### Get all menu items

        Args:
            user_thread (UserThread): The user thread.

        Returns:
            dict: The menu items.
        """
        menu_items = self._menuItemsRepository.get_all_menu_items()
        return {
            "menu_items": [
                asdict(menu_item, dict_factory=self._asdict_factory)
                for menu_item in menu_items
            ]
        }

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
            return {"error": "Pedido não encontrado."}
        return {"order_info": asdict(order, dict_factory=self._asdict_factory)}

    def _get_establishment_contact_info(self, user_thread: UserThread):
        """### Get establishment contact info

        Args:
            user_thread (UserThread): The user thread.

        Returns:
            dict: The establishment contact info.
        """
        return {
            "establishment_contact_info": {
                "phone_number": "+5511999999999",
            }
        }

    FUNCTIONS = {
        "get_all_menu_items": _get_all_menu_items,
        "create_order": _create_order,
        "get_order_details": _get_order_details,
        "get_establishment_contact_info": _get_establishment_contact_info,
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
                print(json.dumps(output))
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output),
                    }
                )

            except Exception as e:
                print(e)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": "Erro ao executar ação."}),
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

    def execute_due_requests(self) -> dict[str, str]:
        """### Executes all due run requests.

        Returns:
            dict[str, str]: A dictionary containing the thread_id as key and the response as value.
        """
        responses = {}
        with self.run_requests_lock:
            run_requests_copy = self.run_requests.copy()
            for thread_id, request_time in run_requests_copy.items():
                if (datetime.now() - request_time).seconds >= 10:
                    responses[thread_id] = self.run_assistant_on_thread(thread_id)
                    del self.run_requests[thread_id]
        return responses

    def run_assistant_on_thread(self, thread_id: str) -> str:
        """### Run the assistant on a thread.

        Args:
            thread_id (str): The ID of the thread.

        Returns:
            str: The assistant's response.
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

        return "\n".join(messages)
