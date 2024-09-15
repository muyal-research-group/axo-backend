#!/bin/bash
uvicorn mictlanxapi.server:app --host ${MICTLANX_API_HOST-localhost} --port ${MICTLANX_API_PORT-16666} --reload --log-level debug
