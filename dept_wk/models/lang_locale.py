import locale

from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class Lang(models.Model):
    _inherit = 'res.lang'

    def _create_lang(self, lang, lang_name=None):
        print('executed language')
        """ Create the given language and make it active. """
        # create the language with locale information
        fail = True
        iso_lang = tools.get_iso_codes(lang)
        for ln in tools.get_locales(lang):
            try:
                locale.setlocale(locale.LC_ALL, 'fr')
                fail = False
                break
            except locale.Error:
                continue
        if fail:
            lc = locale.getlocale()[0]
            msg = 'Unable to get information for locale %s. Information from the default locale (%s) have been used.'
            _logger.warning(msg, lang, lc)

        if not lang_name:
            lang_name = lang

        def fix_xa0(s):
            """Fix badly-encoded non-breaking space Unicode character from locale.localeconv(),
               coercing to utf-8, as some platform seem to output localeconv() in their system
               encoding, e.g. Windows-1252"""
            if s == '\xa0':
                return '\xc2\xa0'
            return s

        def fix_datetime_format(format):
            """Python's strftime supports only the format directives
               that are available on the platform's libc, so in order to
               be 100% cross-platform we map to the directives required by
               the C standard (1989 version), always available on platforms
               with a C standard implementation."""
            # For some locales, nl_langinfo returns a D_FMT/T_FMT that contains
            # unsupported '%-' patterns, e.g. for cs_CZ
            format = format.replace('%-', '%')
            for pattern, replacement in tools.DATETIME_FORMATS_MAP.items():
                format = format.replace(pattern, replacement)
            return str(format)

        conv = locale.localeconv()
        lang_info = {
            'code': lang,
            'iso_code': iso_lang,
            'name': lang_name,
            'active': True,
            'date_format' : fix_datetime_format(locale.nl_langinfo(locale.D_FMT)),
            'time_format' : fix_datetime_format(locale.nl_langinfo(locale.T_FMT)),
            'decimal_point' : fix_xa0(str(conv['decimal_point'])),
            'thousands_sep' : fix_xa0(str(conv['thousands_sep'])),
            'grouping' : str(conv.get('grouping', [])),
        }
        try:
            return self.create(lang_info)
        finally:
            tools.resetlocale()

    def _activate_lang(self, code):
        print('language activated')
        """ Activate languages
        :param code: code of the language to activate
        :return: the language matching 'code' activated
        """
        lang = self.with_context(active_test=False).search([('code', '=', code)])
        loc = locale.setlocale(locale.LC_ALL, 'fr')
        if lang and not lang.active:
            lang.active = True
        print(loc)
        return lang