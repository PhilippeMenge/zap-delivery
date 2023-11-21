import datetime
from time import sleep

import requests

ENDPOINT = "http://app:8000/whatsapp/execute_due_requests"

sleep(5)

last_execution = datetime.datetime.now()
while True:
    if (datetime.datetime.now() - last_execution).seconds >= 1:
        last_execution = datetime.datetime.now()
        requests.get(ENDPOINT)
