from src.domain.Establishment import Establishment
from src.domain.MenuItem import MenuItem
from src.infrastructure.repositories.menu_items_repository import MenuItemRepository
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)


class MenuItemService:
    def __init__(
        self,
        menuItemRepository: MenuItemRepository,
    ):
        self._menuItemRepository = menuItemRepository

    def get_all_menu_items_by_establishment(
        self, establishment: Establishment
    ) -> list[MenuItem]:
        """### Get all menu items by establishment.

        Args:
            establishment (Establishment): The establishment instance.

        Returns:
            list[MenuItem]: The list of menu items.
        """
        logger.debug(f"Getting all menu items by establishment {establishment.id}")
        return self._menuItemRepository.get_all_menu_items_by_establishment(
            establishment
        )

    def get_menu_item_by_id(
        self, menu_item_id: str, establishment: Establishment
    ) -> MenuItem | None:
        """### Get menu item by id.

        Args:
            menu_item_id (str): The menu item id.

        Returns:
            MenuItem | None: The menu item instance or None.
        """
        logger.debug(f"Getting menu item by id {menu_item_id}")
        return self._menuItemRepository.get_menu_item_by_id(menu_item_id, establishment)

    def update_menu_item(self, menu_item: MenuItem):
        """### Update a menu item.

        Args:
            menu_item (MenuItem): The menu item to update.
        """
        logger.debug(f"Updating menu item {menu_item.id}")
        self._menuItemRepository.update_menu_item(menu_item)
