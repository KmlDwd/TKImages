import json
import os

def check_format(paths, format_types):
    filtered_paths = []
    for path in paths:
        _, ext = os.path.splitext(path)
        if ext in format_types:
            filtered_paths.append(path)
    return filtered_paths


def process_request(body):
    body = json.loads(body)
    params = body["params"]

    result = check_format(paths=body["paths"],format_types=params["format"])
    return result
