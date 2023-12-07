from sqlalchemy.orm import Session
from src.domain.Establishment import Establishment
from src.domain.MenuItem import MenuItem
from src.infrastructure.models.MenuItemModel import MenuItemModel


class MenuItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_menu_items_by_establishment(
        self, establishment: Establishment
    ) -> list[MenuItem]:
        """### Get all menu items by establishment.

        Args:
            establishment (Establishment): The establishment instance.

        Returns:
            list[MenuItem]: The list of menu items.
        """
        menu_item_models = (
            self.session.query(MenuItemModel)
            .filter_by(establishment_id=establishment.id)
            .all()
        )
        return [menu_item_model.to_entity() for menu_item_model in menu_item_models]

    def get_menu_item_by_id(
        self, menu_item_id: str, establishment: Establishment
    ) -> MenuItem | None:
        """### Get a menu item from its id.

        Args:
            menu_item_id (str): The id of the menu item.
            establishment (Establishment): The establishment instance.

        Returns:
            MenuItem: The menu item instance. None if not found.
        """
        menu_item_model = (
            self.session.query(MenuItemModel)
            .filter_by(id=menu_item_id, establishment_id=establishment.id)
            .first()
        )
        if menu_item_model is None:
            return None
        return menu_item_model.to_entity()

    def create_menu_item(self, menu_item: MenuItem):
        """### Create a menu item.

        Args:
            menu_item (MenuItem): The menu item to create.
        """
        menu_item_model = MenuItemModel.from_entity(menu_item)
        self.session.merge(menu_item_model)
        self.session.commit()

    def remove_all_menu_items(self):
        """### Remove all menu items.

        This should NEVER be used in production. PLEASE DON'T DO IT.
        """
        self.session.query(MenuItemModel).delete()
        self.session.commit()

    def update_menu_item(self, menu_item: MenuItem):
        """### Update a menu item.

        Args:
            menu_item (MenuItem): The menu item to update.
        """
        self.session.query(MenuItemModel).filter_by(
            id=menu_item.id, establishment_id=menu_item.establishment.id
        ).update(
            {
                MenuItemModel.name: menu_item.name,
                MenuItemModel.price: menu_item.price,
                MenuItemModel.description: menu_item.description,
                MenuItemModel.is_active: menu_item.is_active,
            }
        )
        self.session.commit()
