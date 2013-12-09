import sys
import os.path
import corr2.server
import corr2.templateparser
from optparse import OptionParser
import json


__version__ = 'cOrr 2.0.0'


def _cmdline_error(parser, err):
    sys.stderr.write('Error: ' + err + '\n')
    parser.print_help()
    sys.exit(1)


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


def start_server(host, port):
    server.run(host, port)


def run():
    # parse command line arguments
    opts, template_path = _parse_args()
    
    # parse template
    tparser = corr2.templateparser.TemplateParser.fromfile(template_path)
    template = tparser.parse()
    print(json.dumps(template.sections, indent=4, ensure_ascii=False))

    # start server
    #corr2.start_server(opts.host, opts.port)
