import pytz
import time
import random
from tqdm.auto import tqdm
from threading import Lock
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def get_curr_time(timezone):
    configured_tz = pytz.timezone(timezone)
    return datetime.now(configured_tz).strftime("%Y-%m-%d %H:%M:%S")


def monitor_and_start_service(service_status_func, service_action_func, pbar, success_lock, success_flag, timezone):
    retries = 0
    start_retry_time = None

    while True:
        status = service_status_func()

        if status in ["Cancelled", "Preempted", "Failed"]:
            retries += 1
            pbar.update(1)
            if start_retry_time is None:
                start_retry_time = get_curr_time(timezone)
                print(f"Start retry time: {start_retry_time}")

            try:
                service_action_func()
            except Exception as e:
                pass
        else:
            if start_retry_time is not None:
                success_time = get_curr_time(timezone)
                print(f"First success time: {success_time}")
                start_retry_time = None

                with success_lock:
                    success_flag[0] = True

            with success_lock:
                if not success_flag[0]:
                    print(f"{get_curr_time(timezone)} sleeping 10min")
                    time.sleep(60 * 10 + 0.1)

        time.sleep(random.uniform(0.1, 0.3))


def monitor_services(service_status_func, service_action_func, timezone="UTC", num_workers=8):
    success_lock = Lock()
    success_flag = [False]

    with tqdm(total=None, desc="Number of retries", leave=True) as pbar:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(monitor_and_start_service, service_status_func, service_action_func, pbar,
                                success_lock, success_flag, timezone) for _ in range(num_workers)]
            for future in futures:
                future.result()
