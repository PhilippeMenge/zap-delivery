import requests
import datetime

ENDPOINT = "https://713d-179-139-1-147.ngrok-free.app/whatsapp/execute_due_requests"

last_execution = datetime.datetime.now()
while True:
    if (datetime.datetime.now() - last_execution).seconds >= 1:
        last_execution = datetime.datetime.now()
        requests.get(ENDPOINT)

