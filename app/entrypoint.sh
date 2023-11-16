#!/bin/bash

# start_server.sh
uvicorn src.app:api --host 0.0.0.0 --port 8000 --reload