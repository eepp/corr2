import logging
from flask import Flask


flask_app = Flask(__name__)


@flask_app.route('/')
def _ep_index():
    return 'oh hi!'


def run(host, port, template):
    flask_app.run(host=host, port=port)
