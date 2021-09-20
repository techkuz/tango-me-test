import os
from random import randrange

from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=['POST'])
def generator():
    return {
        "reason": request.args.get("model_name"),
        "result": randrange(10)
    }


@app.route("/", methods=['GET'])
def ping():
    return {
        "pong"
    }


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
