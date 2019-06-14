from flask import Flask, request, jsonify
from flask_cors import CORS

from core import Core

app = Flask(__name__)
cors = CORS(supports_credentials=True)
cors.init_app(app)


@app.route('/auth', methods=['POST'])
def auth():
    try:
        r = Core.decrypt_auth(request.get_json()['code'])
        return jsonify({'res': r})
    except Exception:
        return jsonify({'res': 'code error'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5450)
