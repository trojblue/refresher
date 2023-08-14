from refresher.base import *
from gradient import NotebooksClient

API_KEY = "YOUR_API_KEY"
PRINT_TIMEZONE = "UTC"

def gradient_status():
    notebooks_client = NotebooksClient(API_KEY)
    response = notebooks_client.list(tags=[])
    return response[0].state

def gradient_action(notebook_id):
    notebooks_client = NotebooksClient(API_KEY)
    notebooks_client.start(id=notebook_id, machine_type='Free-A100-80G', shutdown_timeout=6)

notebooks_client = NotebooksClient(API_KEY)
response = notebooks_client.list(tags=[])
notebook_id = response[0].id

monitor_services(service_status_func=gradient_status,
                 service_action_func=lambda: gradient_action(notebook_id),
                 timezone=PRINT_TIMEZONE)
