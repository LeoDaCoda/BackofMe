from flask import Flask, jsonify, request
from backup import serialize_local_fs

import os


app = Flask(__name__)


data = serialize_local_fs("dir")


@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data) # jsonify or raw data?


if __name__ == '__main__':
    app.run()
