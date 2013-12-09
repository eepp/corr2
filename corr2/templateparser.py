from lxml import etree


class Field:
    pass


class GenField(Field):
    def __str__(self):
        return 'general field'


class GradeField(Field):
    def __str__(self):
        return 'grade field'


class Section:
    pass


class Template:
    pass


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
            'allowTotalOverflow': self._parse_bool_option,
            'allowTotalUnderflow': self._parse_bool_option,
            'disableDefaultWeightShortcuts': self._parse_bool_option,
            'init': self._parse_str_option
        }
        self._fields_cb = {
            'gen': self._get_gen_field,
            'grade': self._get_grade_field
        }
        self._tree = tree

    def parse(self):
        # init template
        self._t = Template()

        # parse head
        self._parse_head(self._tree.xpath('/corr/head')[0])

        # parse body
        self._parse_body(self._tree.xpath('/corr/body')[0])

        # ensure no duplicate section/field IDs
        self._ensure_no_duplicates()

        # ensure unique ID points to existing field
        self._ensure_unique_id()

        return self._t

    def _bool_from_str(string):
        return string == 'true'

    def _parse_bool_option(self, option_el):
        val = TemplateParser._bool_from_str(option_el.get('value'))
        self._t.options[option_el.get('name')] = val

    def _parse_str_option(self, option_el):
        val = option_el.get('value')
        self._t.options[option_el.get('name')] = val

    def _get_dws(self, dws_el):
        shortcuts = []
        for shortcut_el in dws_el.findall('shortcut'):
            shortcut = {
                'type': shortcut_el.get('type'),
                'caption': None
            }
            val = shortcut_el.get('val')
            caption = shortcut_el.get('caption')
            if val is not None:
                shortcut['val'] = float(val)
            if caption is not None:
                shortcut['caption'] = caption
            shortcuts.append(shortcut)

        return shortcuts

    def _parse_settings(self, settings_el):
        # parse options
        self._t.options = {}
        for option_el in settings_el.findall('option'):
            self._options_cb[option_el.get('name')](option_el)

        # save default weight shortcuts
        dws_el = settings_el.find('default-weight-shortcuts')
        if dws_el is not None:
            self._dws = self._get_dws(dws_el)

        # save unique ID pointer
        uniqueid_el = settings_el.find('unique-id')
        self._usid = uniqueid_el.get('section-id')
        self._ufid = uniqueid_el.get('field-id')

    def _parse_head(self, head_el):
        # get title
        self._t.title = head_el.find('title').text

        # parse settings
        self._parse_settings(head_el.find('settings'))

    def _get_gen_field(self, field_el):
        field = GenField()

        # multiline
        field.multiline = False
        multiline = field_el.get('multiline')
        if multiline is not None:
            field.multiline = TemplateParser._bool_from_str(multiline)

        return field

    def _get_grade_field(self, field_el):
        field = GradeField()

        # max and exclude from total
        field.max = float(field_el.get('max'))
        field.exclude_from_total = False
        eft = field_el.get('exclude-from-total')
        if eft is not None:
            field.exclude_from_total = TemplateParser._bool_from_str(eft)

        return field

    def _get_field(self, field_el):
        # get specific field
        field = self._fields_cb[field_el.tag](field_el)

        # ID, title and default
        fid = field_el.get('id')
        title = field_el.get('title')
        default = field_el.get('default')
        field.id = fid
        field.title = fid
        field.info = None
        field.default = None
        if title is not None:
            field.title = title
        if default is not None:
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
        section.id = sid
        section.title = sid
        section.fields = {}
        if title is not None:
            section.title = title

        # parse all fields
        for field_el in section_el.findall('*'):
            field = self._get_field(field_el)
            section.fields[field.id] = field

        # add to template sections
        self._t.sections[section.id] = section

    def _parse_body(self, body_el):
        # parse all sections
        self._t.sections = {}
        for section_el in body_el.findall('section'):
            self._parse_section(section_el)

    def _ensure_no_duplicates(self):
        # build list of (section ID, field ID) pairs
        sections_fields = []
        for sid, section in self._t.sections.items():
            sections_fields.extend([(sid, fid) for fid in section.fields.keys()])

        # make sure there's no duplicate
        if len(set(sections_fields)) != len(sections_fields):
            raise TemplateParserError('duplicate section/field ID')

    def _ensure_unique_id(self):
        # try to find field pointed to by unique ID
        if self._usid in self._t.sections:
            if self._ufid in self._t.sections[self._usid].fields:
                return

        # not found
        raise TemplateParserError('cannot find unique ID (section "{}", field "{}")'.format(self._usid, self._ufid))
