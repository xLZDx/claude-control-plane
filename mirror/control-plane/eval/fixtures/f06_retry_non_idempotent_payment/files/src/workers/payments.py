import time


def pay(client, payload):
    for attempt in range(3):
        try:
            return client.post("/payouts", json=payload)
        except TimeoutError:
            time.sleep(1)
    raise RuntimeError("payout failed")
