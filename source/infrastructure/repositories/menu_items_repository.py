from sqlalchemy.orm import Session

from infrastructure.models.MenuItemModel import MenuItemModel
from domain.MenuItem import MenuItem

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

    def create_menu_item(self, menu_item: MenuItem):
        """### Create a menu item.

        """
        menu_item_model = MenuItemModel.from_entity(menu_item)
        self.session.merge(menu_item_model)
        self.session.commit()