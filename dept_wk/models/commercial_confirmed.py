from odoo import models, fields, api, _


class CommercialConfirmed(models.Model):
    _name = 'wk.state.three'
    _description = "Données saisi par le service commercial"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    date = fields.Date(string='Date')
    name = fields.Char(string='Name', default='مديرية الاعمال التجارية')

    visualisation = fields.Binary(string='visualisation', related='workflow.visualisation')

    analyse_secteur_act = fields.Text(string='Analysis of the client\'s business sector', related='workflow.analyse_secteur_act')
    analyse_concurrence = fields.Text(string='Competition analysis', related='workflow.analyse_concurrence')
    ampleur_benefice = fields.Float(string='Net Banking Income', related='workflow.ampleur_benefice')
    analyse_relation = fields.Text(string='Analyze the importance of the relationship in the medium term' , related='workflow.analyse_relation')

    weakness_ids = fields.One2many('wk.swot.weakness', related='workflow.weakness_ids')
    strength_ids = fields.One2many('wk.swot.strength', related='workflow.strength_ids')
    threat_ids = fields.One2many('wk.swot.threat', related='workflow.threat_ids')
    opportunitie_ids = fields.One2many('wk.swot.opportunitie', related='workflow.opportunitie_ids')
    documents = fields.One2many('wk.document.check', string='Verify the attached documents', related='workflow.documents')
