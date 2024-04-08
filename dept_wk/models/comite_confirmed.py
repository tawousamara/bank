from odoo import models, fields, api, _


class ComiteConfirmed(models.Model):
    _name = 'wk.state.six'
    _description = "Données saisi par l'agence"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    date = fields.Date(string='Date')
    name = fields.Char(string='nom', default='لجنة التسهيلات')
    recommandation_fin_grp = fields.Text(string='Recommendation of the Finance Committee', related='workflow.recommandation_fin_grp')
