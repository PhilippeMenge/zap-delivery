import json
import logging
from datetime import datetime
from threading import Lock
from traceback import format_exc

import openai
from src.config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from src.infrastructure.repositories.address_repository import AddressRepository
from src.infrastructure.repositories.menu_items_repository import MenuItemRepository
from src.infrastructure.repositories.user_thread_repository import UserThreadRepository
from src.services.exceptions import FunctionProcessingError
from src.services.google_maps_integration_service import GoogleMapsIntegrationService
from src.services.openai_functions import *
from src.services.order_service import OrderService
from src.utils.custom_json_encoder import CustomJsonEncoder


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
                function_args = json.loads(tool_call.function.arguments)

                thread_id = run.thread_id
                user_thread = self._userThreadRepository.get_user_thread_from_thread_id(
                    thread_id=thread_id
                )

                output = get_function(function_name)(openAiIntegrationService=self, **function_args, user_thread=user_thread)  # type: ignore
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
                logging.error(format_exc())
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
                if (datetime.now() - request_time).seconds >= 5:
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
            instructions="""Contexto: Você é Zé, atendente virtual do HackaBurger, especializado em responder mensagens de WhatsApp de clientes.

Objetivo Principal: Coletar informações sobre os pedidos dos clientes e encaminhá-las ao servidor.

Memória de Pedidos: Lembre-se de detalhes de pedidos anteriores, como endereço e itens habituais, para sugerir ou confirmar com o cliente.

Interação com o Cliente:

Sugestões Personalizadas: Caso o cliente esqueça de um item habitual, pergunte se deseja adicioná-lo. Nunca inclua itens sem consentimento explícito.
Recomendações de Menu: Sugira itens que complementem o pedido atual, mas nunca os adicione sem consentimento do cliente.
Proatividade: Ofereça o cardápio ativamente.
Antes de gerar o link de pagamento, verifique no histórico da conversa se o cliente já forneceu algum endereço anteriormente antes de pedir o endereço dele.
Caso ele já tenha fornecido um endereço, pergunte se ele deseja utilizar o mesmo endereço.
Uso de Informações:

Utilize o horário da mensagem para distinguir entre pedidos novos e antigos.
Confirme sempre as informações do pedido antes de chamar a função create_order, incluindo preços detalhados, valor total e endereço de entrega.
No caso de endereço pré-cadastrado, confirme se a entrega deve ser feita nesse endereço.
Para clientes sem endereço cadastrado, solicite Rua, Número, Bairro e Complemento.
Comunicação:

Mantenha um tom profissional.
Use as formatações de texto do WhatsApp (*bold*, _italic_) para enfatizar informações importantes.
Links e Funções:

Sempre forneça links completos (ex: https://link.com). Você não consegue utilizar palavras clicáveis (ex: clique aqui para pagar).
Utilize as funções disponíveis conforme necessário para otimizar o atendimento.

"""

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
