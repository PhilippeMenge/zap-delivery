from fastapi.security import OAuth2PasswordBearer
from src.config import WHATSAPP_API_KEY, WHATSAPP_NUMBER_ID
from src.domain.Address import Address
from src.domain.Establishment import Establishment
from src.domain.MenuItem import MenuItem
from src.infrastructure.init_db import get_db
from src.infrastructure.repositories.address_repository import AddressRepository
from src.infrastructure.repositories.establishment_repository import (
    EstablishmentRepository,
)
from src.infrastructure.repositories.menu_items_repository import MenuItemRepository
from src.infrastructure.repositories.operator_repository import OperatorRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.infrastructure.repositories.user_repository import UserRepository
from src.services.google_maps_integration_service import GoogleMapsIntegrationService
from src.services.menu_items_service import MenuItemService
from src.services.openai_integration_service import OpenAiIntegrationService
from src.services.operator_service import OperatorService
from src.services.order_service import OrderService
from src.services.stripe_integration_service import StripeIntegrationService
from src.services.whatsapp_integration_service import WhatsappIntegrationService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

MENU_ITEMS_REPOSITORY = MenuItemRepository(session=get_db())
ORDER_REPOSITORY = OrderRepository(session=get_db())
USER_REPOSITORY = UserRepository(session=get_db())
ADDRESS_REPOSITORY = AddressRepository(session=get_db())
ESTABLISHMENT_REPOSITORY = EstablishmentRepository(session=get_db())
OPERATOR_REPOSITORY = OperatorRepository(session=get_db())

WHATSAPP_INTEGRATION_SERVICE = WhatsappIntegrationService()
STRIPE_INTEGRATION_SERVICE = StripeIntegrationService()
MENU_ITEMS_SERVICE = MenuItemService(menuItemRepository=MENU_ITEMS_REPOSITORY)
GOOGLE_MAPS_INTEGRATION_SERVICE = GoogleMapsIntegrationService()
ORDER_SERVICE = OrderService(
    orderRepository=ORDER_REPOSITORY,
    stripeIntegrationService=STRIPE_INTEGRATION_SERVICE,
    whatsappIntegrationService=WHATSAPP_INTEGRATION_SERVICE,
)
OPENAI_INTEGRATION_SERVICE = OpenAiIntegrationService(
    menuItemsRepository=MENU_ITEMS_REPOSITORY,
    userRepository=USER_REPOSITORY,
    orderService=ORDER_SERVICE,
    googleMapsIntegrationService=GOOGLE_MAPS_INTEGRATION_SERVICE,
    addressRepository=ADDRESS_REPOSITORY,
)
OPERATOR_SERVICE = OperatorService(
    operatorRepository=OPERATOR_REPOSITORY,
    establishmentRepository=ESTABLISHMENT_REPOSITORY,
)


def populate_db(
    menuItemRepository: MenuItemRepository,
    orderRepository: OrderRepository,
    establishmentRepository: EstablishmentRepository,
):
    PROMPT = """Contexto: Você é Zé, atendente virtual do HackaBurger, especializado em responder mensagens de WhatsApp de clientes.

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

Sempre forneça links completos (ex: https://link.com).
Utilize as funções disponíveis conforme necessário para otimizar o atendimento.

"""

    menuItemRepository.remove_all_menu_items()
    establishments = [
        Establishment(
            id="1",
            name="Burguer King",
            address=Address(
                street="Av boa viagem",
                number="2080",
                complement="Ap 601",
                neighborhood="Boa Viagem",
                city="Recife",
                state="PE",
                country="Brasil",
                zipcode="51111-000",
            ),
            contact_number="81999999999",
            estimated_production_minutes=30,
            custom_prompt_section=PROMPT,
            whatsapp_api_key=WHATSAPP_API_KEY,
            whatsapp_number_id=WHATSAPP_NUMBER_ID,
        ),
    ]

    for establishment in establishments:
        establishmentRepository.create_establishment(establishment)

    menu_items = [
        MenuItem(
            id="1",
            name="Henrique Burguer",
            price="25.00",
            description="Um delicioso e suculento hambúrguer com carne de 160g, queijo mussarela massaricado, bacon e molho especial da casa.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="2",
            name="MengeBurger",
            price="28.00",
            description="Um delicioso e suculento hambúrguer com carne de 160g, queijo mussarela massaricado, bacon, alface, tomate, picles e molho especial da casa.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="3",
            name="Biburguer",
            price="30.00",
            description="Uma combinaçǎo de queijos mussarela, cheddar e catupiry, com carne de 160g, bacon e molho especial da casa.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="30",
            name="Fritas",
            price="12.00",
            description="Porção de fritas.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="31",
            name="Onion Rings",
            price="11.50",
            description="Porção de Onion Rings.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="32",
            name="Batata Rústica",
            price="15.00",
            description="Porção de Batata Rústica.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="33",
            name="Fritas com cheddar e bacon",
            price="18.50",
            description="Porção de Batata Frita com cheddar e bacon.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="100",
            name="Milkshake de Ovomaltine",
            price="12.00",
            description="Milkshake de chocolate com toda a crocância do Ovomaltine.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="101",
            name="Milkshake de Chocolate",
            price="10.00",
            description="Milkshake de chocolate.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="102",
            name="Milkshake de Morango",
            price="10.00",
            description="Milkshake de morango.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="103",
            name="Milkshake de Baunilha",
            price="10.00",
            description="Milkshake de baunilha.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="104",
            name="Milkshake de Oreo",
            price="12.00",
            description="Milkshake de chocolate com Oreo.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="105",
            name="Milkshake de Leite Ninho",
            price="12.00",
            description="Milkshake de chocolate com Leite Ninho.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="106",
            name="Casquinha de Chocolate",
            price="4.00",
            description="Casquinha de chocolate.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="107",
            name="Casquinha de Baunilha",
            price="4.00",
            description="Casquinha de baunilha.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="108",
            name="Sundae de Chocolate",
            price="8.00",
            description="Sundae de chocolate.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="109",
            name="Sundae de Morango",
            price="8.00",
            description="Sundae de morango.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="110",
            name="Sundae de Caramelo",
            price="8.00",
            description="Sundae de caramelo.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="111",
            name="Sundae de Leite Ninho",
            price="8.00",
            description="Sundae de Leite Ninho.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="112",
            name="Sundae de Ovomaltine",
            price="10.00",
            description="Sundae de Ovomaltine.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="113",
            name="Sundae de Oreo",
            price="10.00",
            description="Sundae de Oreo.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="114",
            name="Sundae de Kit Kat",
            price="10.00",
            description="Sundae de Kit Kat.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="50",
            name="Soda",
            price="3",
            description="Lata de Soda.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="51",
            name="Guaraná",
            price="3",
            description="Lata de Guaraná Antártica.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="52",
            name="Coca-Cola",
            price="3",
            description="Lata de Coca-Cola.",
            is_active=True,
            establishment=establishments[0],
        ),
        MenuItem(
            id="53",
            name="Fanta Laranja",
            price="3",
            description="Lata de Fanta Laranja.",
            is_active=True,
            establishment=establishments[0],
        ),
    ]

    for menu_item in menu_items:
        menuItemRepository.create_menu_item(menu_item)


populate_db(MENU_ITEMS_REPOSITORY, ORDER_REPOSITORY, ESTABLISHMENT_REPOSITORY)
