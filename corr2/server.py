import logging
import flask
import json
import datetime as DT
from corr2 import templateparser
from corr2 import __version__


_template_path = None
_template = None
_flask_app = flask.Flask(__name__)


@_flask_app.route('/', methods=['GET'])
def _ep_index():
    return flask.render_template('corr2.htm', template=_template)


@_flask_app.route('/save', methods=['POST'])
def _ep_save():
    # get results
    results = _get_results(flask.request.form, _template, _template_path)
    json_txt = json.dumps(results, indent=4, ensure_ascii=False)
    response = flask.Response(json_txt, content_type='application/json; charset=utf-8')
    return response


def _get_results(form_data, template, template_path):
    results = {
        'infos': {
            'title': template.title,
            'template_path': template_path,
            'date': DT.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': __version__,
            'max': template.max
        },
        'sections': {}
    }

    # get basic results out of form data
    basic_results = _get_basic_results(form_data)

    # add some infos about sections and fields to basic results
    res_sections = results['sections']
    total = 0
    for sid, fields in basic_results.items():
        t_section = template.get_section(sid)
        section = {
            'title': t_section.title,
            'fields': {}
        }
        res_sections[sid] = section
        for fid, result in fields.items():
            t_field = t_section.get_field(fid)
            field = {
                'title': t_field.title,
                'type': t_field.get_type()
            }
            if type(t_field) is templateparser.GradeField:
                field['max'] = t_field.max
                if not t_field.exclude_from_total:
                    result = float(result)
                    total += result
            field['result'] = result
            res_sections[sid]['fields'][fid] = field

    # set total
    if total > template.max and not template.options['allowTotalOverflow']:
        total = template.max
    elif total < 0 and not template.options['allowTotalUnderflow']:
        total = 0
    results['infos']['total'] = total

    return results


def _get_basic_results(form_data):
    results = {}
    for key, result in form_data.items():
        sid, fid = key.split('.')
        if sid not in results:
            results[sid] = {}
        results[sid][fid] = result

    return results


def run(host, port, template, template_path):
    global _template, _template_path
    _template = template
    _template_path = template_path
    _flask_app.run(host=host, port=port)
