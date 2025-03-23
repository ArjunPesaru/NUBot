#!/bin/bash
echo "starting script execution"

pip install -r requirements.txt
python src/dataflow/scraper.py
python src/dataflow/chunk_data.py
echo "script executed successfully"
python main.py
