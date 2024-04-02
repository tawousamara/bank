from odoo import models, fields, api, _


class Confirmation(models.TransientModel):
    _name = 'import.ocr.wizard'
    _description = 'Confirmation of verification wizard'

    tcr_id = fields.Many2one('import.ocr.tcr', string="TCR")
    actif_id = fields.Many2one('import.ocr.actif', string="Actif")
    passif_id = fields.Many2one('import.ocr.passif', string="Passif")

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def confirm(self):
        print("send")
        print(self.env.context.get('active_ids')[0])
        print(self.env.context)
        if self.env.context.get('tcr_id'):
            model = 'import.ocr.tcr'
            id = self.env.context.get('tcr_id')
        elif self.env.context.get('actif_id'):
            model = 'import.ocr.actif'
            id = self.env.context.get('actif_id')
        elif self.env.context.get('passif_id'):
            model = 'import.ocr.passif'
            id = self.env.context.get('passif_id')
        state = self.env.context.get('state')
        print(state)
        rec = self.env[model].search([('id', 'in', [id])])
        if rec:
            if self.env.user.has_group('dept_wk.dept_wk_group_responsable_credit') and state == 'valide':
                rec.write({'state': 'modified'})
            elif self.env.user.has_group('dept_wk.dept_wk_group_responsable_credit') and state == 'validation':
                rec.write({'state': 'validation'})
            else:
                rec.write({'state': state})
            print('1')


class BilanExtracter(models.TransientModel):
    _name = 'extract.bilan.wizard'
    _description = 'Viewing Files wizard'

    pdf_1 = fields.Binary(string='PDF')
    pdf_2 = fields.Binary(string='PDF')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def confirm(self):
        if self.env.context.get('tcr_id'):
            tcr_id = self.env['import.ocr.tcr'].search([('id', '=', self.env.context.get('tcr_id'))])
            if tcr_id:
                tcr_id.extract_data()
        elif self.env.context.get('actif_id'):
            actif_id = self.env['import.ocr.actif'].search([('id', '=', self.env.context.get('actif_id'))])
            if actif_id:
                actif_id.extract_data()
        elif self.env.context.get('passif_id'):
            passif_id = self.env['import.ocr.passif'].search([('id', '=', self.env.context.get('passif_id'))])
            if passif_id:
                passif_id.extract_data()

