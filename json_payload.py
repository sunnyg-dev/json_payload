from flask import Flask, request, jsonify
from functools import wraps
import datetime

app = Flask(__name__)

# Authentication decorator
def authenticate(username, password):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = request.authorization
            if not auth or auth.username != username or auth.password != password:
                return jsonify({"error": "Unauthorized"}), 401
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Date validation decorator
def validate_dates(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            datetime.datetime.strptime(start_date, "%d-%m-%Y")
            datetime.datetime.strptime(end_date, "%d-%m-%Y")
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid date format. Expected DD-MM-YYYY."}), 422
        return func(*args, **kwargs)
    return wrapper

# JSON payload validation decorator
def validate_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = request.json
        if not payload or not isinstance(payload, dict):
            return jsonify({"error": "Invalid JSON payload"}), 422
        if 'date' not in payload or 'amount' not in payload:
            return jsonify({"error": "Missing required fields in JSON payload"}), 422
        try:
            datetime.datetime.strptime(payload['date'], "%d-%m-%Y")
            if not isinstance(payload['amount'], (int, float)):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid payload data types"}), 422
        return func(*args, **kwargs)
    return wrapper

# Endpoint
@app.route('/endpoint/<client_id>', methods=['GET', 'POST'])
@authenticate(username="user", password="password")
@validate_dates
@validate_json
def endpoint(client_id):
    payload = request.json if request.method == 'POST' else {}
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return jsonify({
        "message": "Request processed successfully",
        "client_id": client_id,
        "start_date": start_date,
        "end_date": end_date,
        "payload": payload
    })

if __name__ == "__main__":
    app.run(debug=True)
