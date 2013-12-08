from flask import Flask
app = Flask(__name__)


@app.route('/')
def _ep_index():
    return 'oh hi!'


def run(host, port):
    app.run(host=host, port=port, debug=True)
