from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# 🧪 Temporary: Return mock data for testing GPT plugin
def get_sheet_data():
    return [
        ["ID", "City", "Hospice", "Standing"],
        ["1", "Gambrills", "Yes", "In Good Standing"],
        ["2", "Baltimore", "No", "Probation"],
        ["3", "Annapolis", "Yes", "In Good Standing"]
    ]

@app.route('/openapi.yaml')
def serve_openapi_spec():
    with open("openapi.yaml", "r") as f:
        content = f.read()
    return content, 200, {'Content-Type': 'application/yaml'}

    headers = values[0]
    data_rows = values[1:]

    structured_data = []
    for row in data_rows:
        row_dict = {header: "" for header in headers}
        for i, value in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = value
        structured_data.append(row_dict)

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

# 🧠 Serve ai-plugin.json for GPT plugin
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory('.well-known', 'ai-plugin.json', mimetype='application/json')

# 📜 Serve openapi.yaml with absolute path fix for Render
@app.route('/openapi.yaml')
def serve_openapi_spec():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(base_dir, 'openapi.yaml', mimetype='application/yaml')

# 🌐 Run on the correct host/port for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
