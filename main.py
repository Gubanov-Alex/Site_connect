from flask import Flask, request, jsonify
import waitress
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re
from email_validator import validate_email, EmailNotValidError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Getting the path to the JSON file from the environment variable
json_keyfile_path = os.getenv('GOOGLE_SHEETS_CREDS')
print(f"GOOGLE_SHEETS_CREDS path: {json_keyfile_path}")

if json_keyfile_path is None:
    raise RuntimeError("Environment variable 'GOOGLE_SHEETS_CREDS' is not set")

if not os.path.isfile(json_keyfile_path):
    raise FileNotFoundError(f"File'{json_keyfile_path}' not found")

if not json_keyfile_path:
    raise ValueError(
        "The path to the Google Sheets credentials JSON file must be set in the environment variable "
        "'GOOGLE_SHEETS_CREDS'"
    )

# Getting sheet name from environment variable
sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'test01')

app = Flask(__name__)

# Set up Google Sheets client scope and authorization
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']  # scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
client = gspread.authorize(credentials)
sheet = client.open("test01").sheet1


try:
    sheet = client.open(sheet_name).sheet1
except gspread.SpreadsheetNotFound:
    raise ValueError(f"The Google Sheet named '{sheet_name}' was not found.")

def validate_data(dat):
    """Function for checking data.
        Returns a list of errors,
        if any.
        """
    errors = []

    # Name Check
    if 'name' not in dat or dat['name'] == '':
        errors.append("error: Name requiring")
    elif not re.match(r"^[A-Za-zА-Яа-яЁё\s]+$", dat['name']):
        errors.append("error: Bad symbols")


    # Phone number check
    if 'phone_number' not in dat or dat['phone_number'] == '':
        errors.append("error: Phone number requiring")
    elif not re.match(r"\d{13}$", dat['phone_number']):
        errors.append("error: Invalid phone number format")


    # Mail check
    try:
        validate_email(dat['email'])
    except EmailNotValidError:
        errors.append("error: Email is not valid")

    return errors


@app.route('/submit', methods=['POST'])
def submit_form():
    """
    Route for receiving and processing form data.

    """
    data = request.json

    validate_errors = validate_data(data)

    if validate_errors:
        return jsonify({"errors": validate_errors}), 400

    # Add data to Google Sheets
    try:
        sheet.append_row([
            data['name'],
            data['email'],
            data['phone_number']
        ])
    except gspread.APIError as e:
        return jsonify({"error": "Failed to append row to Google Sheet", "details": str(e)}), 500

    return jsonify({"message": "Data was saved to Google Sheet"}), 201


if __name__ == '__main__':
    # app.run(debug=True)

    # Running an application using waitress
    waitress.serve(app, host='0.0.0.0', port=8080)