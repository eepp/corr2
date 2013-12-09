import logging
import flask


_template = None
_flask_app = flask.Flask(__name__)


@_flask_app.route('/')
def _ep_index():
    return flask.render_template('corr2.htm', template=_template)


def run(host, port, template):
    global _template
    _template = template
    _flask_app.run(host=host, port=port)
