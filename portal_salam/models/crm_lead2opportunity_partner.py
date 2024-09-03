from odoo import models, api

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.depends('lead_id')
    def _compute_action(self):
        for convert in self:
            convert.action = 'create'
