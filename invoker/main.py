import os
import random
import threading

import requests
import redis
from flask import Flask, request
from cachetools import cached, TTLCache

app = Flask(__name__)
TTL_cache = TTLCache(ttl=10, maxsize=100)
R = redis.Redis()


@app.route("/", methods=['GET'])
def recommend():
    viewer_id = request.args.get("viewer_id")

    data = get_from_local_cache()

    if not data:
        data = get_from_redis_cache(viewer_id=viewer_id)

    if not data:
        data = runcascade(viewer_id=viewer_id)
        write_to_cache(data, viewer_id=viewer_id)

    return {
        "viewer_id": viewer_id,
        "data": data
    }


@app.route("/", methods=['GET'])
def ping():
    return {
        "pong"
    }


def runcascade(viewer_id: int):
    threads = list()
    responses = list()

    def send_request(model_name):
        response = requests.post('127.0.0.1/', json={"model_name": model_name, "viewer_id": viewer_id}).json()
        responses.append(response)

    for index in range(5):
        thread = threading.Thread(target=send_request, args=(f"model_{index}",))
        threads.append(thread)
        thread.start()

    for index, thread in enumerate(threads):
        thread.join()

    return responses


def write_to_cache(data: list, viewer_id: int):
    val = random.randint(0, 1)
    if val == 0:
        dict_len = len(TTL_cache)
        if dict_len == 3:
            if not TTL_cache.get(viewer_id):
                TTL_cache.popitem()
            TTL_cache[viewer_id] = data

    if val == 1:
        R.mset({viewer_id: data})


@cached(TTL_cache)
def get_from_local_cache(viewer_id: int):
    return TTL_cache.get(viewer_id)


def get_from_redis_cache(viewer_id: int):
    return R.get(viewer_id)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
