#!/bin/bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port $PORT