from odoo import models, fields, api, _


class Documents(models.Model):
    _name = 'wk.documents'
    _description = 'gestion des images'

    name = fields.Char(string="Nom")
    picture = fields.Binary(string='الصور')
    etape_id = fields.Many2one('wk.etape')

    @api.model
    def create(self, vals):
        vals['name'] = 'image'
        return super(Documents, self).create(vals)

