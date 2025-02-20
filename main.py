import re
import socket
import smtplib
import dns.resolver
from email.utils import parseaddr
from urllib.parse import parse_qs
import json
from flask import Flask, request

app = Flask(__name__)

# Regular Expression for RFC 5322 Email Syntax Validation
EMAIL_REGEX = r"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)"

# Check if email is syntactically valid (RFC 5322 compliance)
def is_syntactic_valid(email):
    return re.match(EMAIL_REGEX, email) is not None

# Check domain validity (MX records)
def is_domain_valid(domain):
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

# Check SMTP deliverability
def check_smtp_deliverability(domain, email):
    try:
        # Get MX records for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        mailserver = str(mx_records[0].exchange)
        # Connect to the mail server
        with smtplib.SMTP(mailserver) as server:
            server.set_debuglevel(0)  # Disable debug output
            server.helo()
            server.mail('test@example.com')
            code, message = server.rcpt(email)
            return code == 250  # 250 means the recipient is valid
    except Exception as e:
        return False

# Placeholder for Authentication & Anti-Spam Measures
def check_authentication_anti_spam(email):
    # For simplicity, assume a basic anti-spam check (real checks would involve more complex mechanisms)
    domain = email.split('@')[1]
    return is_domain_valid(domain)

# Placeholder for User Engagement Check
def check_user_engagement(email):
    # For simplicity, we assume engagement check passes (would need additional marketing-related checks)
    return True

# Check mailbox availability by sending an SMTP request to the server
def check_mailbox_availability(email):
    domain = email.split('@')[1]
    return check_smtp_deliverability(domain, email)

# Validate email by running all tests
def validate_email(email):
    result = {}
    result['email'] = email
    # Syntactic Validity
    result['syntactic_valid'] = is_syntactic_valid(email)
    if not result['syntactic_valid']:
        return result

    # Domain Validity
    domain = email.split('@')[1]
    result['domain_valid'] = is_domain_valid(domain)
    if not result['domain_valid']:
        return result

    # SMTP Deliverability
    result['smtp_deliverable'] = check_smtp_deliverability(domain, email)
    if not result['smtp_deliverable']:
        return result

    # Authentication & Anti-Spam Measures
    result['authenticated'] = check_authentication_anti_spam(email)
    if not result['authenticated']:
        return result

    # User Engagement
    result['user_engaged'] = check_user_engagement(email)
    if not result['user_engaged']:
        return result

    # Mailbox Availability
    result['mailbox_available'] = check_mailbox_availability(email)
    if not result['mailbox_available']:
        return result

    result['valid'] = True  # If all checks pass
    return result

# Create the API endpoint using Flask
@app.route('/validate', methods=['GET'])
def validate():
    # Get emails from query parameters
    emails = request.args.get('email', '')
    
    if not emails:
        return json.dumps({'error': 'No email provided'}), 400

    emails = emails.split(',')
    results = [validate_email(email.strip()) for email in emails]
    return json.dumps(results), 200

# Main entry point for the application (Railway expects this)
if __name__ == '__main__':
    app.run(debug=True)
