from src.domain.MenuItem import MenuItem
from src.infrastructure.models.MenuItemModel import MenuItemModel
from sqlalchemy.orm import Session


class MenuItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_menu_items(self) -> list[MenuItem]:
        """### Get all menu items.

        Returns:
            list[MenuItem]: The list of menu items.
        """
        menu_item_models = self.session.query(MenuItemModel).all()
        return [menu_item_model.to_entity() for menu_item_model in menu_item_models]

    def get_menu_item_by_id(self, menu_item_id: str) -> MenuItem | None:
        """### Get a menu item from its id.

        Args:
            menu_item_id (str): The id of the menu item.

        Returns:
            MenuItem: The menu item instance. None if not found.
        """
        menu_item_model = self.session.query(MenuItemModel).get(menu_item_id)
        if menu_item_model is None:
            return None
        return menu_item_model.to_entity()

    def create_menu_item(self, menu_item: MenuItem):
        """### Create a menu item."""
        menu_item_model = MenuItemModel.from_entity(menu_item)
        self.session.merge(menu_item_model)
        self.session.commit()
