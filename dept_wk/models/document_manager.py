from odoo import models, fields, api, _


class Documents(models.Model):
    _name = 'wk.documents'
    _description = 'gestion des images'

    name = fields.Char(string="Nom")
    picture = fields.Binary(string='الصور')
    etape_id = fields.Many2one('wk.etape')
    to_show = fields.Boolean(string='يظهر في التقرير النهائي؟')

    def open_image(self):
        for rec in self:
            view_id = self.env.ref('dept_wk.view_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.picture
            context['picture'] = True
            wizard = self.env['view.bilan.wizard'].create({'pdf_1': rec.picture})
            return {
                'name': 'الصورة',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'view.bilan.wizard',
                'res_id': wizard.id,
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }

    @api.model
    def create(self, vals):
        vals['name'] = 'image'
        return super(Documents, self).create(vals)

