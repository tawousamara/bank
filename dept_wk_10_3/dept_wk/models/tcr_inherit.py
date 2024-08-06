from odoo import models, fields, api, _


class TCR(models.Model):
    _inherit = 'tcr.analysis.import'

    etape_id = fields.Many2one('wk.etape', string='Etape')
    taux_change = fields.Float(string='1$ = ?DA: سعر الصرف', related='etape_id.taux_change', store=True)

    @api.model
    def create(self, vals):
        res = super(TCR, self).create(vals)
        etape = self.env.context.get('etape_id')
        if etape:
            res.etape_id = etape
        print(etape)
        return res


class BilanGeneral(models.Model):
    _inherit = 'bilan.general'

    @api.model
    def create(self, vals):
        res = super(BilanGeneral, self).create(vals)
        return res
