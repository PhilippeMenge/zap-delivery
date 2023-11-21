from heyoo import WhatsApp
from src.config import WHATSAPP_API_KEY, WHATSAPP_NUMBER_ID
from src.domain.Establishment import Establishment
from src.utils.logging import get_configured_logger

logger = get_configured_logger(__name__)


class WhatsappIntegrationService:
    def get_messenger_for_establishment(self, establishment: Establishment) -> WhatsApp:
        """### Get a WhatsApp messenger for a given establishment

        Args:
            establishment (Establishment): The establishment to get the messenger for

        Returns:
            WhatsApp: The WhatsApp messenger
        """
        return WhatsApp(
            token=establishment.whatsapp_api_key,
            phone_number_id=establishment.whatsapp_number_id,
        )

    def get_message_text(
        self, data, establishment: Establishment
    ) -> tuple[str, str] | None:
        """### Get message text from webhook data

        Args:
            data (dict): webhook data
            establishment (Establishment): The establishment to get the messenger for

        Returns:
            tuple[str, str]: (message, mobile)
        """
        messenger = self.get_messenger_for_establishment(establishment)

        changed_field = messenger.changed_field(data)
        if changed_field == "messages":
            new_message = messenger.is_message(data)
            if new_message:
                message_type = messenger.get_message_type(data)
                if message_type == "text":
                    message = messenger.get_message(data)
                    return message, messenger.get_mobile(data)
                else:
                    return None
            else:
                return None

        return None

    def send_message(self, message: str, mobile: str, establishment: Establishment):
        """### Send a message to a phone number

        Args:
            message (str): The message to send
            mobile (str): The phone number to send the message to
            establishment (Establishment): The establishment to get the messenger for
        """

        messenger = self.get_messenger_for_establishment(establishment)
        messenger.send_message(message, mobile)
        logger.debug(f"Sent message {message} to {mobile}.")
