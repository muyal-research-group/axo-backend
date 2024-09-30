#!/bin/bash
uvicorn axobackend.server:app --host ${AXO_BACKEND_API_HOST-localhost} --port ${AXO_BACKEND_API_PORT-17000} --reload --log-level debug
