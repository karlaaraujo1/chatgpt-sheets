from flask import Flask, jsonify, request, send_from_directory
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

app = Flask(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheet_data():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet_id = '1fuBumZ6r4152F-xxEqmWyOADS4ZJKBVjM6JzGPHyy-Q'
    range_name = 'NEW_rawdata!A1:ZZ'

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()

    return result.get('values', [])

@app.route('/data', methods=['GET'])
def get_data():
    values = get_sheet_data()
    if not values or len(values) < 2:
        return jsonify([])

    headers = values[0]
    data_rows = values[1:]

    # Turn rows into dictionaries
    structured_data = []
    for row in data_rows:
        row_dict = {header: "" for header in headers}
        for i, value in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = value
        structured_data.append(row_dict)

    # Apply filters from query string
    filters = request.args.to_dict()
    if filters:
        filtered_data = []
        for row in structured_data:
            match = all(str(row.get(key, "")).strip().lower() == value.strip().lower()
                        for key, value in filters.items())
            if match:
                filtered_data.append(row)
        return jsonify(filtered_data)

    return jsonify(structured_data)

# 🧠 Serve plugin files for GPT
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory('.well-known', 'ai-plugin.json', mimetype='application/json')

@app.route('/openapi.yaml')
def serve_openapi_spec():
    return send_from_directory('.', 'openapi.yaml', mimetype='application/yaml')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
