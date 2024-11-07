#!/bin/bash
uvicorn axobackend.main:app --host ${AXO_BACKEND_API_HOST-localhost} --port ${AXO_BACKEND_API_PORT-17000} --reload --log-level debug
