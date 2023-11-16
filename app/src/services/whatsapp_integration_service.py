import logging

from heyoo import WhatsApp
from src.config import WHATSAPP_API_KEY, WHATSAPP_NUMBER_ID


class WhatsappIntegrationService:
    def __init__(self) -> None:
        self.messenger = WhatsApp(
            token=WHATSAPP_API_KEY, phone_number_id=WHATSAPP_NUMBER_ID
        )

    def get_message_text(self, data) -> tuple[str, str] | None:
        """### Get message text from webhook data

        Args:
            data (dict): webhook data

        Returns:
            tuple[str, str]: (message, mobile)
        """
        logging.info("Processing message...")
        changed_field = self.messenger.changed_field(data)
        if changed_field == "messages":
            new_message = self.messenger.is_message(data)
            if new_message:
                message_type = self.messenger.get_message_type(data)
                if message_type == "text":
                    message = self.messenger.get_message(data)
                    return message, self.messenger.get_mobile(data)
                else:
                    return None
            else:
                return None

        return None

    def send_message(self, message: str, mobile: str):
        """### Send a message to a phone number

        Args:
            message (str): The message to send
            mobile (str): The phone number to send the message to
        """
        self.messenger.send_message(message, mobile)
