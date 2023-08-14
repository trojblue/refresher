from refresher.base import *
import requests
import json

# Read the configuration from the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

# Extract Gradient and Lambda Labs settings
lambda_labs_config = config['lambda_labs']


def lambda_status():
    instance_str = lambda_labs_config['INSTANCE_TYPE']
    instances = get_instance_types()["data"]
    if instance_str in instances and instances[instance_str]["regions_with_capacity_available"]:
        return "Available"
    return "Unavailable"


def lambda_action():
    region_name = get_instance_types()["data"]["gpu_1x_h100_pcie"]["regions_with_capacity_available"][0]["name"]
    launch_instance(region_name, "gpu_1x_h100_pcie", lambda_labs_config['SSH_KEY_NAMES'], 1,
                    lambda_labs_config['NODE_NAME'])


def get_instance_types():
    headers = {"Authorization": f"Bearer {lambda_labs_config['KEY']}"}
    response = requests.get(f"{lambda_labs_config['API_BASE_URL']}/instance-types", headers=headers)
    return response.json()


def launch_instance(region_name, instance_type_name, ssh_key_names, quantity, name):
    headers = {"Authorization": f"Bearer {lambda_labs_config['KEY']}"}
    payload = {
        "region_name": region_name,
        "instance_type_name": instance_type_name,
        "ssh_key_names": ssh_key_names,
        "quantity": quantity,
        "name": name
    }
    response = requests.post(f"{lambda_labs_config['API_BASE_URL']}/instance-operations/launch", headers=headers,
                             json=payload)
    return response.json()


def monitor_lambda_status():
    while True:
        instances = get_instance_types()["data"]
        avai_ins = 0

        for instance, info in instances.items():
            if info["regions_with_capacity_available"]:
                print(instance, info["regions_with_capacity_available"])
                avai_ins += 1

        print(f"{get_curr_time(config['timezone'])} | {avai_ins} instances available")
        time.sleep(3)


if __name__ == '__main__':
    monitor_lambda_status()
    # monitor_services(service_status_func=lambda_status, service_action_func=lambda_action, timezone="UTC")
