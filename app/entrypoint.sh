#!/bin/bash

# Check if RELOAD environment variable is set and its value is "true"
if [ "$RELOAD" = "true" ]; then
    # If RELOAD is set to "true", include the --reload flag
    uvicorn src.app:api --host 0.0.0.0 --port 8000 --reload --log-level warning
else
    # If RELOAD is not set to "true", omit the --reload flag
    uvicorn src.app:api --host 0.0.0.0 --port 8000 --log-level warning
fi