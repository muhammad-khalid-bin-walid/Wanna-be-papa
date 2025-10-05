from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Server running"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "up"})

@app.route('/data', methods=['POST'])
def data():
    try:
        return jsonify(request.get_json()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
