#!/bin/bash
poetry install
poetry run python texasgpt/app/server.py --reload

