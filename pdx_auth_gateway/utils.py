import re


def extract_name_from_email(email):
    # Define the pattern for extracting the name
    pattern = r"([^@]+)"

    # Search for the pattern in the email
    match = re.search(pattern, email)

    if match:
        name = match.group(1)
        return name
    else:
        return None


def get_username(email, org_name):
    return "%s@%s" % (extract_name_from_email(email), org_name)
