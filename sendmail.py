import requests
import json
import base64

import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')


user = config.get('mailuser', 'user')


# Replace these with your app's credentials and tenant information
tenant_id =     config.get('emailconf', 'tenant_id')
client_id =     config.get('emailconf', 'client_id')
client_secret = config.get('emailconf', 'client_secret')

# OAuth 2.0 endpoint to obtain access token
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

#token_url = "https://login.microsoftonline.com/q3b8Q~NlgBj-TkewK3XP2Bv9BdRBSX34u11cPbnd/oauth2/v2.0/token"

# Data to be sent to obtain the token
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}

# Request the token
response = requests.post(token_url, data=token_data)
response.raise_for_status()  # Raise an exception for HTTP errors

# Extract the token from the response
access_token = response.json().get('access_token')
print(access_token)

# Define the email details
email_data = {
    "message": {
        "subject": "JMeter LoadTesting",
        "body": {
            "contentType": "Text",
            "content": "Summary Report Load testing."
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "address": "user"
                }
            }
        ],
        "attachments": [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "summaryreport.jtl",
                "contentType": "text/plain",
                "contentBytes": ""  # This will be replaced with base64 encoded file content
            }
        ]
    },
    "saveToSentItems": "true"
}

# Read the file and encode it in base64
file_path = '/summaryreport.jtl'
with open(file_path, 'rb') as file:
    file_content = file.read()
    encoded_file_content = base64.b64encode(file_content).decode('utf-8')

# Update the email_data with the base64 encoded file content
email_data["message"]["attachments"][0]["contentBytes"] = encoded_file_content
email_data["message"]["toRecipients"][0]["emailAddress"]["address"] = user
# Microsoft Graph API endpoint for sending email
#url = 'https://graph.microsoft.com/v1.0/comet-noreply@xl.co.id/sendMail'

#url = 'https://graph.microsoft.com/v1.0/me/sendMail'

url = config.get('emailconf', 'sendmail')

# Set up the headers with the access token
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Send the POST request to send the email
response = requests.post(url, headers=headers, data=json.dumps(email_data))

# Check the response
if response.status_code == 202:
    print('Email sent successfully')
else:
    print(f'Failed to send email. Status code: {response.status_code}')
    print(response.json())
