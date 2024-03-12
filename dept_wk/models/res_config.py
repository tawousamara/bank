from odoo import models, fields, api, _


class ApiOcr(models.Model):
    _name = 'res.config.ocr'

    name = fields.Char(string='Nom')
    apikey = fields.Char(string='Api Key')


