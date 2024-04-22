import base64
import json
import random
from pdx_auth.exceptions import HostNameNotFound
from django.template.loader import get_template
from urllib.parse import parse_qs, urlparse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def get_organization_data(request):
    host_name = request.META.get("HTTP_HOST_NAME")
    if not host_name:
        raise HostNameNotFound()
    return host_name


def generate_OTP():
    return random.randint(11111, 99999)


def send_otp(user_obj, org_name):
    subject = "OTP verification"
    html_content = get_template("emails/send_otp.html").render(
        {"otp": user_obj.otp, "organization_data": org_name}
    )

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=[user_obj.email],
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response
    except Exception as e:
        return e


def extract_org(state: str):
    if state:
        extra_data = decode_state(state)
        if "org_name" in extra_data:
            return extra_data["org_name"]
    return None


def extract_state(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("state", [""])[0]


def decode_state(state: str):
    if state:
        decoded_state = base64.b64decode(state).decode("utf-8")
        return json.loads(decoded_state)
    return None


def send_password_reset_link(user_obj, reset_url):
    subject = "Password Reset"
    html_content = get_template("registration/password_reset_email.html").render(
        {
            "reset_url": reset_url,
            "user": user_obj,
            "site_name": "PDX Auth server",
        }
    )

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=[user_obj.email],
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response
    except Exception as e:
        return e
