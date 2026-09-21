#!/usr/bin/env bash
pip install -r requirements.txt
cd src/ui/frontend && npm install --include=dev && npm run build
