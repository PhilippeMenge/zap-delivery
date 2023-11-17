from googlemaps import Client
from src.config import GOOGLE_MAPS_API_KEY
from src.domain.Address import Address


class GoogleMapsIntegrationService:
    def __init__(self):
        self.client = Client(key=GOOGLE_MAPS_API_KEY)

    def get_address_from_text(self, address_text: str) -> list[dict]:
        """### Gets details of a given address based on natural language text.

        Args:
            address_text (str): The natural language text of the address.

        Returns:
            list[dict]: A list of dictionaries containing the address details.
        """
        results = self.client.places(address_text)
        place_ids = [result["place_id"] for result in results["results"]]

        details = []
        for place_id in place_ids:
            detail_raw = self.client.place(place_id, fields=["address_component"])
            detail_processed = {}

            for address_component in detail_raw["result"]["address_components"]:
                detail_processed[address_component["types"][0]] = address_component[
                    "long_name"
                ]

            details.append(detail_processed)

        return details

    def get_time_between_addresses(
        self, origin: Address, destination: Address
    ) -> int | None:
        """### Gets the distance between two addresses.

        Args:
            origin (Address): The origin address.
            destination (Address): The destination address.

        Returns:
            int | None: The time in seconds between the two addresses. None if not found.
        """
        result = self.client.directions(str(origin), str(destination))

        if len(result) == 0:
            return None

        return result[0]["legs"][0]["duration"]["value"]