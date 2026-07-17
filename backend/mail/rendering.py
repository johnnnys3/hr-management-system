"""Renders a mail dispatch template.

Each template is a directory under `mail/templates/mail/<name>/` containing
`subject.txt` and `body.txt`, with an optional `body.html` for a rich variant.
"""
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


def render(template, context):
    subject = render_to_string(f'mail/{template}/subject.txt', context).strip()
    text_body = render_to_string(f'mail/{template}/body.txt', context)
    try:
        html_body = render_to_string(f'mail/{template}/body.html', context)
    except TemplateDoesNotExist:
        html_body = None
    return subject, text_body, html_body
