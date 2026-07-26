"""SMS dispatch's public API.

Mirrors `mail.services` (ADR-0011): this module knows nothing about why a
message is sent. `send` takes a destination number and a body, and queues
delivery off the request cycle. Callers own the decision to call this; this
module owns getting the message there.
"""
from .tasks import send_sms_task


def send(*, to, body):
    send_sms_task.delay(to=to, body=body)
