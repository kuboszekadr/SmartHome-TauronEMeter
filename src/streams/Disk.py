import os
import json

from datetime import date


def stream_to_disk(data, root: str, data_date: date, type: str):
    file_name = data_date.strftime('%Y-%m-%d') + f"_{type}"
    folder_name = data_date.strftime('%Y-%m')

    folder_path = os.path.join(root, folder_name)
    file_path = os.path.join(folder_path, f'{file_name}.json')

    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f)
