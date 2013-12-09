from lxml import etree


class Template: pass


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
        self._unique_id = {
            'section_id': uniqueid_el.get('section-id'),
            'field_id': uniqueid_el.get('field-id')
        }
    
    def _parse_head(self, head_el):
        # get title
        self._t.title = head_el.find('title').text
        
        # parse settings
        self._parse_settings(head_el.find('settings'))
    
    def _get_gen_field(self, field_el):
        return {'lol': 'gen'}
    
    def _get_grade_field(self, field_el):
        return {'lol': 'grade'}
    
    def _get_field(self, field_el):
        # ID and title
        fid = field_el.get('id')
        title = field_el.get('title')
        field = {
            'id': fid,
            'title': fid,
            'info': None
        }
        if title is not None:
            field['title'] = title
        
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
            field['info'] = info
        
        # update field with specific field's values
        field.update(self._fields_cb[field_el.tag](field_el))
        
        return field
    
    def _parse_section(self, section_el):
        # ID and title
        sid = section_el.get('id')
        title = section_el.get('title')
        section = {
            'id': sid,
            'title': sid,
            'fields': []
        }
        if title is not None:
            section['title'] = title
        
        # parse all fields
        for field_el in section_el.findall('*'):
            section['fields'].append(self._get_field(field_el))
        
        # add to template sections
        self._t.sections.append(section)
    
    def _parse_body(self, body_el):
        # parse all sections
        self._t.sections = []
        for section_el in body_el.findall('section'):
            self._parse_section(section_el)

