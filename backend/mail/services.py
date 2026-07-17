"""Mail dispatch's public API.

Per ADR-0011, mail dispatch knows nothing about why a message is sent.
`send` takes a template name, a recipient, and rendering context, and queues
delivery off the request cycle. Callers (Authentication, Onboarding,
Notification, payroll communication) own the decision to call this; this
module owns getting the message there.
"""
from .tasks import send_mail_task


def send(*, template, recipient, context=None):
    send_mail_task.delay(template=template, recipient=recipient, context=context or {})
