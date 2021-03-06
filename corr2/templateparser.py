import re
from lxml import etree
from copy import deepcopy


class WeightShortcut:
    def __init__(self, wstype, val=None, caption=None):
        self.type = wstype
        self.val = val
        self.realval = val
        self.caption = caption
        if (val == 0):
            self.type = 'min'


class Field:
    def get_type(self):
        return self.type


class GenField(Field):
    def __init__(self):
        self.type = 'gen'

    def __str__(self):
        return 'general field'


class GradeField(Field):
    def __init__(self):
        self.type = 'grade'

    def __str__(self):
        return 'grade field'


class Section:
    def __init__(self):
        self.mapped_fields = {}

    def map_field(self, field):
        fid = field.id
        if fid in self.mapped_fields:
            raise TemplateParserError('duplicate field ID "{}"'.format(fid))
        self.mapped_fields[fid] = field

    def get_field(self, fid):
        if fid not in self.mapped_fields:
            raise TemplateParserError('no such field with ID "{}"'.format(fid))
        return self.mapped_fields[fid]


class Template:
    def __init__(self):
        self.mapped_sections = {}

    def map_section(self, section):
        sid = section.id
        if sid in self.mapped_sections:
            raise TemplateParserError('duplicate section ID "{}"'.format(sid))
        self.mapped_sections[sid] = section

    def get_section(self, sid):
        if sid not in self.mapped_sections:
            raise TemplateParserError('no such section with ID "{}"'.format(sid))
        return self.mapped_sections[sid]

    def get_field(self, sid, fid):
        return self.get_section(sid).get_field(fid)


class TemplateParserError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class TemplateParser:
    def fromstring(string):
        tree = etree.fromstring(string)
        return TemplateParser(tree)

    def fromfile(filename):
        with open(filename) as xmlf:
            tree = etree.parse(xmlf)
        return TemplateParser(tree)

    def __init__(self, tree):
        self._options_cb = {
            'allowTotalOverflow': self._get_bool_option,
            'allowTotalUnderflow': self._get_bool_option,
            'init': self._get_str_option
        }
        self._fields_cb = {
            'gen': self._get_gen_field,
            'grade': self._get_grade_field
        }
        self._dws = [
            WeightShortcut(wstype='max', val=None, caption=None),
            WeightShortcut(wstype='mul', val=0.75, caption='¾'),
            WeightShortcut(wstype='mul', val=0.5, caption='½'),
            WeightShortcut(wstype='mul', val=0.25, caption='¼'),
            WeightShortcut(wstype='mul', val=0, caption='0')
        ]
        self._def_options = {
            'allowTotalOverflow': True,
            'allowTotalUnderflow': True,
            'init': 'default'
        }
        self._tree = tree

    def parse(self):
        # init template
        self._t = Template()

        # parse head
        self._parse_head(self._tree.xpath('/corr/head')[0])

        # parse body
        self._parse_body(self._tree.xpath('/corr/body')[0])

        # ensure unique ID points to existing field
        self._ensure_unique_id()

        # compute max
        self._compute_max()

        return self._t

    def _bool_from_str(string):
        return string == 'true'

    def _is_valid_id(tid):
        return re.match('^[a-zA-Z][a-zA-Z0-9_-]*$', tid)

    def _get_bool_option(self, option_el):
        return TemplateParser._bool_from_str(option_el.get('value'))

    def _get_str_option(self, option_el):
        return option_el.get('value')

    def _get_ws(self, ws_el):
        shortcuts = []
        for shortcut_el in ws_el.findall('shortcut'):
            wstype = shortcut_el.get('type')
            val = shortcut_el.get('val')
            caption = shortcut_el.get('caption')
            if val is not None:
                val = float(val)
            if caption is not None:
                caption = caption
            ws = WeightShortcut(wstype=wstype, val=val, caption=caption)
            shortcuts.append(ws)

        return shortcuts

    def _parse_settings(self, settings_el):
        # parse options
        self._t.options = deepcopy(self._def_options)
        for option_el in settings_el.findall('option'):
            option_val = self._options_cb[option_el.get('name')](option_el)
            self._t.options[option_el.get('name')] = option_val

        # save default weight shortcuts
        dws_el = settings_el.find('default-weight-shortcuts')
        if dws_el is not None:
            self._dws = self._get_ws(dws_el)

        # save unique ID pointer
        uniqueid_el = settings_el.find('unique-id')
        self._t.usid = uniqueid_el.get('section-id')
        self._t.ufid = uniqueid_el.get('field-id')

    def _parse_head(self, head_el):
        # get title
        self._t.title = head_el.find('title').text

        # parse settings
        self._parse_settings(head_el.find('settings'))

    def _get_gen_field(self, field_el):
        field = GenField()

        # multiline, mandatory
        field.multiline = False
        field.mandatory = False
        multiline = field_el.get('multiline')
        mandatory = field_el.get('mandatory')
        if multiline is not None:
            field.multiline = TemplateParser._bool_from_str(multiline)
        if mandatory is not None:
            field.mandatory = TemplateParser._bool_from_str(mandatory)

        return field

    def _resolve_field_ws(self, field):
        for ws in field.ws:
            if ws.type == 'mul':
                ws.realval = round(ws.val * field.max, 10)
            elif ws.type == 'max':
                ws.realval = field.max
            if int(ws.realval) == ws.realval:
                ws.realval = int(ws.realval)
            if ws.caption is None:
                c = round(ws.realval, 2)
                if int(c) == c:
                    c = int(c)
                ws.caption = str(c)

    def _get_grade_field(self, field_el):
        field = GradeField()

        # max and exclude from total
        field.max = float(field_el.get('max'))
        field.exclude_from_total = False
        eft = field_el.get('exclude-from-total')
        if eft is not None:
            field.exclude_from_total = TemplateParser._bool_from_str(eft)

        # custom weight shortcuts
        cws_el = field_el.find('custom-weight-shortcuts')
        if cws_el is not None:
            field.ws = self._get_ws(cws_el)
        else:
            field.ws = deepcopy(self._dws)
        self._resolve_field_ws(field)

        return field

    def _get_field(self, field_el):
        # get specific field
        field = self._fields_cb[field_el.tag](field_el)

        # ID, title and default
        fid = field_el.get('id')
        title = field_el.get('title')
        default = field_el.get('default')
        if not TemplateParser._is_valid_id(fid):
            raise TemplateParserError('invalid ID format: "{}"'.format(fid))
        field.id = fid
        field.title = fid
        field.info = None
        field.default = None
        if title is not None:
            field.title = title
        if default is not None:
            if type(field) is GradeField and default == 'max':
                default = str(field.max)
            field.default = default

        # info
        info_el = field_el.find('info')
        if info_el is not None:
            info = {
                'text': info_el.text,
                'escape': False
            }
            escape = info_el.get('escape')
            if escape is not None:
                info['escape'] = TemplateParser._bool_from_str(escape)
            field.info = info

        return field

    def _parse_section(self, section_el):
        # ID and title
        sid = section_el.get('id')
        title = section_el.get('title')
        section = Section()
        if not TemplateParser._is_valid_id(sid):
            raise TemplateParserError('invalid ID format: "{}"'.format(sid))
        section.id = sid
        section.title = sid
        section.fields = []
        if title is not None:
            section.title = title
        self._t.map_section(section)

        # parse all fields
        for field_el in section_el.findall('*'):
            field = self._get_field(field_el)
            section.fields.append(field)
            section.map_field(field)

        # add to template sections
        self._t.sections.append(section)

    def _parse_body(self, body_el):
        # parse all sections
        self._t.sections = []
        for section_el in body_el.findall('section'):
            self._parse_section(section_el)

    def _ensure_unique_id(self):
        # try to find field pointed to by unique ID
        try:
            field = self._t.get_field(self._t.usid, self._t.ufid)
            field.mandatory = True
        except TemplateParserError:
            raise TemplateParserError('cannot find unique ID field (section "{}", field "{}")'.format(self._t.usid, self._t.ufid))

    def _compute_max(self):
        self._t.max = 0
        for section in self._t.sections:
            for field in section.fields:
                if type(field) is GradeField and not field.exclude_from_total:
                    if field.max >= 0:
                        self._t.max += field.max
