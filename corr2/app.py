import sys
import os.path
import logging
from optparse import OptionParser
from corr2 import server
from corr2 import templateparser


__version__ = 'cOrr 2.0.0'


def _cmdline_error(parser, err_msg):
    sys.stderr.write('Command-line error: ' + err_msg + '\n')
    parser.print_help()
    sys.exit(1)


def _template_error(err):
    sys.stderr.write('Template error: ' + str(err) + '\n')
    sys.exit(2)


def _unknown_error(err):
    sys.stderr.write('Unknown error: ' + str(err) + '\n')
    raise err


def _parse_args():
    # use optparse to parse options
    parser = OptionParser(version=__version__,
                          usage='%prog [options] TEMPLATE',
                          description='Start a cOrr2 server with grading template TEMPLATE.')
    parser.add_option('-H', '--host', dest='host', metavar='ADDR',
                      default='127.0.0.1', help='listen on host ADDR')
    parser.add_option('-p', '--port', dest='port', metavar='PORT', type='int',
                      default=8080, help='listen on port PORT')
    opts, args = parser.parse_args()

    # validate options
    if opts.port < 1 or opts.port > 65535:
        _cmdline_error(parser, 'invalid port: {}.'.format(opts.port))

    # check positional arguments
    if len(args) < 1:
        _cmdline_error(parser, 'no template path provided.')
    elif not os.path.isfile(args[0]):
        _cmdline_error(parser, '"{}" does not exist or is not a file.'.format(args[0]))

    return opts, args[0]


def _log_template(template):
    logging.info('    Title: {}'.format(template.title))
    logging.info('    Sections:')
    for section in template.sections:
        logging.info('        {}:'.format(section.title))
        for field in section.fields:
            logging.info('            {}  [{}]'.format(field.title, str(field)))


def start(host, port, template_path):
    # parse template
    logging.info('Parsing template "{}"'.format(template_path))
    try:
        tparser = templateparser.TemplateParser.fromfile(template_path)
        template = tparser.parse()
        #print(json.dumps(template.sections, indent=4, ensure_ascii=False))
    except templateparser.TemplateParserError as err:
        _template_error(err)
    except Exception as err:
        _unknown_error(err)
    logging.info('Parsed template:')
    _log_template(template)

    # start server
    logging.info('Starting cOrr2 server')
    server.run(host, port, template)


def run():
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # parse command line arguments
    opts, template_path = _parse_args()

    # start app
    logging.info('Starting cOrr2')
    start(opts.host, opts.port, template_path)
    logging.info('Stopping cOrr2')
