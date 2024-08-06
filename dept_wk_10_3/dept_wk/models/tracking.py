from odoo import models, fields, api, _


class Tracking(models.Model):
    _name = 'wk.tracking'
    _description = "Tracking"

    workflow_id = fields.Many2one('wk.workflow.dashboard', string='Demande')
    etape_id = fields.Many2one('wk.etape', string='Demande')
    date_debut = fields.Date(string='تاريخ البدء')
    date_fin = fields.Date(string='تاريخ الانتهاء')
    date_difference = fields.Char(string='الوقت المستغرق', compute='_compute_date')
    state1 = fields.Char(string='حالة الملف')
    state = fields.Selection([('branch_1', 'الفرع'),
                              ('branch_2', 'مدير الفرع'),
                              ('branch_3', ' الفرع'),
                              ('branch_4', 'مدير الفرع'),
                              ('finance_1', 'مدير التمويلات'),
                              ('finance_2', 'المحلل المالي'),
                              ('finance_3', 'مدير التمويلات'),
                              ('commercial_1', 'مدير الاعمال التجارية'),
                              ('commercial_2', 'مديرية الاعمال التجارية'),
                              ('commercial_3', 'مدير الاعمال التجارية'),
                              ('risque_1', 'ادارة المخاطر')], string='حالة الملف')
    comment = fields.Text(string='التعليق')
    raison_a_revoir = fields.Text(string='التعليق')
    is_revision = fields.Boolean()
    time = fields.Integer(string='الاجال', related='time_id.time')
    difference = fields.Integer(string='الاجال', )
    time_id = fields.Many2one('wk.time', string='الاجال', compute='compute_time')
    depasse = fields.Boolean(string='depasse')
    def _compute_date(self):
        for rec in self:
            if rec.date_fin:
                rec.difference = (rec.date_fin - rec.date_debut).days
                rec.date_difference = str(rec.difference) + 'يوم'
                if rec.difference > rec.time:
                    rec.depasse = True
                else:
                    rec.depasse = False
            else:
                rec.date_difference = 'طور الانجاز'

    def compute_time(self):
        for rec in self:
            time_id = self.env['wk.time'].search([('state', '=', rec.state)])
            if time_id:
                rec.time_id = time_id.id
            else:
                rec.time_id = False
