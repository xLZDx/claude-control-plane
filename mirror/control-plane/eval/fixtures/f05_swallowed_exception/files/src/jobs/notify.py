import logging

log = logging.getLogger(__name__)


def send_all(client, messages):
    sent = 0
    for m in messages:
        try:
            client.send(m)
            sent += 1
        except Exception:
            pass
    return {"status": "ok", "sent": sent}
