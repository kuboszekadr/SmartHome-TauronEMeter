import yaml
import glob
import os
import json
import logging

from src.streams.InfluxDataCollector import InfluxDataCollector
from sys import stdout
from time import sleep
from os import environ

checkpoint_file = 'checkpoints/data_upload_ha.yaml'

def load_checkpoint():
    result = None
    try:
        with open(checkpoint_file, 'r') as f:
            data = yaml.load(f, yaml.FullLoader)
    except FileNotFoundError:
        data = {}
    result = data.get('latest_file', '2020-01-01.json')
    return result

def save_checkpoint(file_path: str):
    file_name = os.path.basename(file_path)

    with open(checkpoint_file, 'w') as f:
        data = {'latest_file': file_name}
        s = yaml.dump(data)
        f.write(s)

def get_files_to_read(root: str, latest_file: str) -> list:
    file_month = latest_file[:-8]
    start_file = os.path.join(root, file_month, latest_file)

    search_template = os.path.join('**', '*.json')
    root = os.path.join(root, search_template)

    files = glob.glob(
        root,
        recursive=True)
    files = filter(lambda x: x >= start_file, files)

    result = list(files)
    result = sorted(result)
    return result


logging.basicConfig(
    format="'%(asctime)s | %(name)s | %(message)s'",
    datefmt="%Y-%m-%d %H:%M:%S%z",
    level=logging.DEBUG
)
logging.getLogger().addHandler(logging.StreamHandler(stdout))

stream = InfluxDataCollector()

# Test connection before processing files
if not stream.test_connection():
    logging.error("Failed to connect to InfluxDB. Exiting.")
    exit(1)

last_file_read = load_checkpoint()
files_to_process = get_files_to_read('data/', last_file_read)

for file in files_to_process:
    logging.info(f"Processing file {file}...")
    with open(file, 'r') as f:
        data = json.load(f)

    logging.info(f"Sending to Home Assistant API...")

    try:
        stream.stream(data, file)
    except Exception as e:
        logging.exception(f"Unhandled error {e}: {repr(e)}")
        # Continue processing other files even if one fails
        continue
    else:
        save_checkpoint(file)
        logging.info(f"Successfully processed {file}")

    sleep(1)  # Rate limiting to avoid overwhelming InfluxDB