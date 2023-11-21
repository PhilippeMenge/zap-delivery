from googlemaps import Client
from src.config import GOOGLE_MAPS_API_KEY
from src.domain.Address import Address
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)


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
        logger.info(f"Getting address from text: {address_text}")

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

        logger.info(f"Succesfully got address from text {address_text}")
        logger.debug(f"Address details: {details}")
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
        logger.info(f"Getting time between addresses: {origin} and {destination}")

        result = self.client.directions(str(origin), str(destination))

        if len(result) == 0:
            return None

        seconds_between_addresses = result[0]["legs"][0]["duration"]["value"]

        logger.info(
            f"Succesfully got time between addresses {origin} and {destination}: {seconds_between_addresses} seconds"
        )
        return seconds_between_addresses
