from flask import Flask, request, jsonify
import waitress
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re
from email_validator import validate_email, EmailNotValidError

app =Flask(__name__)

# scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('test01.json', scope)
client = gspread.authorize(credentials)
sheet = client.open("test01").sheet1

def validate_data(dat):
    errors = []

    if 'name' not in dat or dat['name'] == '':
        errors.append("error: Name requiring")
    elif not re.match(r"^[A-Za-zА-Яа-яЁё\\s]+$", dat['name']):
        errors.append("error: Bad symbols")

    if 'phone_number' not in dat or dat['phone_number'] == '':
        errors.append("error: Phone number requiring")
    elif not re.match(r"\d{13}$", dat['phone_number']):
        errors.append("error: Invalid phone number format")

    try:
        validate_email(dat['email'])
    except EmailNotValidError:
        errors.append("error: Email is not valid")

    return errors


@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json

    validate_errors = validate_data(data)

    if validate_errors:
        return jsonify({"errors": validate_errors}), 400

    sheet.append_row([
        data['name'],
        data['email'],
        data['phone_number']])

    return jsonify({"message": "Data was saved to Google Sheet"}), 201




if __name__ == '__main__':
      # app.run(debug=True)
      waitress.serve(app, host='0.0.0.0', port=8080)



