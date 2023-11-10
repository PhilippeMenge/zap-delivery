import json

import openai
from config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from domain.OrderItem import OrderItem
from infrastructure.repositories import MenuItemRepository
from domain import Order, OrderStatus

from infrastructure.repositories.order_repository import OrderRepository


class OpenAiIntegrationService:
    def __init__(
        self, menuItemsRepository: MenuItemRepository, orderRepository: OrderRepository
    ):
        self.client = openai.Client(api_key=OPENAI_API_KEY)
        self.assistant = self.client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
        self._menuItemsRepository = menuItemsRepository
        self._orderRepository = orderRepository

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

    def _create_order(self, address: str, items: list[dict]) -> Order:
        order_items = []
        for item in items:
            amount = item["amount"]
            observation = item.get("observation", "")
            menu_item = self._menuItemsRepository.get_menu_item_by_id(item["item_id"])

            order_items.append(
                OrderItem(menu_item=menu_item, amount=amount, observation=observation)
            )
        
        order = Order(address=address, itens=order_items, status=OrderStatus.CONFIRMED)
        self._orderRepository.add_order(order)
        print(order)
        return order
        
        

    def _get_all_menu_items(self):
        return self._menuItemsRepository.get_all_menu_items()

    FUNCTIONS = {
        "get_all_menu_items": _get_all_menu_items,
        "create_order": _create_order,
    }

    def _execute_actions(self, run) -> list[dict]:
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            if tool_call.type != "function":
                continue

            function_name = tool_call.function.name
            function_args = tool_call.function.arguments

            output = self.FUNCTIONS[function_name](self, **json.loads(function_args))
            tool_outputs.append(
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(output, default=lambda o: o.__dict__),
                }
            )

        return tool_outputs

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
                        tool_outputs=tool_outputs,
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

            message = (
                self.client.beta.threads.messages.retrieve(
                    thread_id=thread_id,
                    message_id=message_id,
                )
                .content[0]
                .text.value
            )

            messages.append(message)

        return "\n".join(messages)
