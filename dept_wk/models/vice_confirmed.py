from odoo import models, fields, api, _


class ViceConfirmed(models.Model):
    _name = 'wk.state.five'
    _description = "Données saisi par l'agence"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    date = fields.Date(string='Date')
    name = fields.Char(string='Name', default='Deputy General Manager')
    recommandation_vice_dir_fin = fields.Text(string='Deputy General Manager recommendation', related='workflow.recommandation_vice_dir_fin')
