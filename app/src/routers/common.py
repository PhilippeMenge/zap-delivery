from src.domain.MenuItem import MenuItem
from src.infrastructure.init_db import get_db
from src.infrastructure.repositories.address_repository import AddressRepository
from src.infrastructure.repositories.menu_items_repository import MenuItemRepository
from src.infrastructure.repositories.order_repository import OrderRepository
from src.infrastructure.repositories.user_thread_repository import UserThreadRepository
from src.services.google_maps_integration_service import GoogleMapsIntegrationService
from src.services.openai_integration_service import OpenAiIntegrationService
from src.services.order_service import OrderService
from src.services.stripe_integration_service import StripeIntegrationService
from src.services.whatsapp_integration_service import WhatsappIntegrationService

MENU_ITEMS_REPOSITORY = MenuItemRepository(session=get_db())
ORDER_REPOSITORY = OrderRepository(session=get_db())
USER_THREAD_REPOSITORY = UserThreadRepository(session=get_db())
ADDRESS_REPOSITORY = AddressRepository(session=get_db())

WHATSAPP_INTEGRATION_SERVICE = WhatsappIntegrationService()
STRIPE_INTEGRATION_SERVICE = StripeIntegrationService()
GOOGLE_MAPS_INTEGRATION_SERVICE = GoogleMapsIntegrationService()
ORDER_SERVICE = OrderService(
    orderRepository=ORDER_REPOSITORY,
    stripeIntegrationService=STRIPE_INTEGRATION_SERVICE,
    whatsappIntegrationService=WHATSAPP_INTEGRATION_SERVICE,
)
OPENAI_INTEGRATION_SERVICE = OpenAiIntegrationService(
    menuItemsRepository=MENU_ITEMS_REPOSITORY,
    userThreadRepository=USER_THREAD_REPOSITORY,
    orderService=ORDER_SERVICE,
    googleMapsIntegrationService=GOOGLE_MAPS_INTEGRATION_SERVICE,
    addressRepository=ADDRESS_REPOSITORY,
)


def populate_db(
    menuItemRepository: MenuItemRepository, orderRepository: OrderRepository
):
    menu_items = [
        MenuItem(
            id="1",
            name="Henrique Melo Burguer",
            price="25.00",
            description="Um delicioso e suculento hambúrguer com carne de 160g, queijo mussarela massaricado, bacon e molho especial da casa.",
            is_active=True,
        ),
        MenuItem(
            id="2",
            name="MengeBurger",
            price="28.00",
            description="Um delicioso e suculento hambúrguer com carne de 160g, queijo mussarela massaricado, bacon, alface, tomate, picles e molho especial da casa.",
            is_active=True,
        ),
        MenuItem(
            id="3",
            name="Biburguer",
            price="30.00",
            description="Uma combinaçǎo de queijos mussarela, cheddar e catupiry, com carne de 160g, bacon e molho especial da casa.",
            is_active=True,
        ),
        MenuItem(
            id="30",
            name="Fritas",
            price="12.00",
            description="Porção de fritas.",
            is_active=True,
        ),
        MenuItem(
            id="31",
            name="Onion Rings",
            price="11.50",
            description="Porção de Onion Rings.",
            is_active=True,
        ),
        MenuItem(
            id="32",
            name="Batata Rústica",
            price="15.00",
            description="Porção de Batata Rústica.",
            is_active=True,
        ),
        MenuItem(
            id="33",
            name="Fritas com cheddar e bacon",
            price="18.50",
            description="Porção de Batata Frita com cheddar e bacon.",
            is_active=True,
        ),
        MenuItem(
            id="100",
            name="Milkshake de Ovomaltine",
            price="12.00",
            description="Milkshake de chocolate com toda a crocância do Ovomaltine.",
            is_active=True,
        ),
        MenuItem(
            id="101",
            name="Milkshake de Chocolate",
            price="10.00",
            description="Milkshake de chocolate.",
            is_active=True,
        ),
        MenuItem(
            id="102",
            name="Milkshake de Morango",
            price="10.00",
            description="Milkshake de morango.",
            is_active=True,
        ),
        MenuItem(
            id="103",
            name="Milkshake de Baunilha",
            price="10.00",
            description="Milkshake de baunilha.",
            is_active=True,
        ),
        MenuItem(
            id="104",
            name="Milkshake de Oreo",
            price="12.00",
            description="Milkshake de chocolate com Oreo.",
            is_active=True,
        ),
        MenuItem(
            id="105",
            name="Milkshake de Leite Ninho",
            price="12.00",
            description="Milkshake de chocolate com Leite Ninho.",
            is_active=True,
        ),
        MenuItem(
            id="106",
            name="Casquinha de Chocolate",
            price="4.00",
            description="Casquinha de chocolate.",
            is_active=True,
        ),
        MenuItem(
            id="107",
            name="Casquinha de Baunilha",
            price="4.00",
            description="Casquinha de baunilha.",
            is_active=True,
        ),
        MenuItem(
            id="108",
            name="Sundae de Chocolate",
            price="8.00",
            description="Sundae de chocolate.",
            is_active=True,
        ),
        MenuItem(
            id="109",
            name="Sundae de Morango",
            price="8.00",
            description="Sundae de morango.",
            is_active=True,
        ),
        MenuItem(
            id="110",
            name="Sundae de Caramelo",
            price="8.00",
            description="Sundae de caramelo.",
            is_active=True,
        ),
        MenuItem(
            id="111",
            name="Sundae de Leite Ninho",
            price="8.00",
            description="Sundae de Leite Ninho.",
            is_active=True,
        ),
        MenuItem(
            id="112",
            name="Sundae de Ovomaltine",
            price="10.00",
            description="Sundae de Ovomaltine.",
            is_active=True,
        ),
        MenuItem(
            id="113",
            name="Sundae de Oreo",
            price="10.00",
            description="Sundae de Oreo.",
            is_active=True,
        ),
        MenuItem(
            id="114",
            name="Sundae de Kit Kat",
            price="10.00",
            description="Sundae de Kit Kat.",
            is_active=True,
        ),
        MenuItem(
            id="50",
            name="Soda",
            price="3",
            description="Lata de Soda.",
            is_active=True,
        ),
        MenuItem(
            id="51",
            name="Guaraná",
            price="3",
            description="Lata de Guaraná Antártica.",
            is_active=True,
        ),
        MenuItem(
            id="52",
            name="Coca-Cola",
            price="3",
            description="Lata de Coca-Cola.",
            is_active=True,
        ),
        MenuItem(
            id="53",
            name="Fanta Laranja",
            price="3",
            description="Lata de Fanta Laranja.",
            is_active=True,
        ),
    ]

    for menu_item in menu_items:
        menuItemRepository.create_menu_item(menu_item)


populate_db(MENU_ITEMS_REPOSITORY, ORDER_REPOSITORY)
