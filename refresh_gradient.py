from refresher.base import *
from gradient import NotebooksClient

import json

# Read the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

# Extract Gradient and Lambda Labs settings
gradient_config = config['gradient']
lambda_labs_config = config['lambda_labs']


def gradient_status():
    notebooks_client = NotebooksClient(gradient_config['API_KEY'])
    response = notebooks_client.list(tags=[])
    return response[0].state


def gradient_action(notebook_id):
    notebooks_client = NotebooksClient(gradient_config['API_KEY'])
    notebooks_client.start(id=notebook_id, machine_type='Free-A100-80G', shutdown_timeout=6)


if __name__ == '__main__':
    notebooks_client = NotebooksClient(gradient_config['API_KEY'])
    response = notebooks_client.list(tags=[])
    notebook_id = response[0].id

    monitor_services(service_status_func=gradient_status,
                     service_action_func=lambda: gradient_action(notebook_id),
                     timezone=gradient_config['TIMEZONE'])
