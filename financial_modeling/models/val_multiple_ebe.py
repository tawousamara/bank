# -*- coding: utf-8 -*-

from odoo import models, fields, api

TYPE_YEAR = [
    ('n', 'Année N'),
    ('n1', 'Année N-1'),
    ('n3', 'Année N-2'),
]


class ValMultipleEBE(models.Model):
    _name = 'val.multiple.ebe'
    _description = "Valorisation d'entreprise par multiple d'EBE"

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")

    amount_average_ebe = fields.Float(string="Average EBE", compute='_compute_amount', digits=(16, 3))
    amount_ve = fields.Float(string="VE", compute='_compute_amount', digits=(16, 3))
    multiple = fields.Integer(string="Multiple")

    line_ids = fields.One2many('val.multiple.ebe.line', inverse_name='val_id')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    @api.depends('multiple', 'line_ids.amount')
    def _compute_amount(self):
        for rec in self:
            total_line = sum(rec.line_ids.mapped('amount'))
            amount_average_ebe = total_line/len(rec.line_ids) if rec.line_ids else 0
            rec.amount_ve = amount_average_ebe * rec.multiple
            rec.amount_average_ebe = amount_average_ebe

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('val.multiple.ebe.seq')

        return super(ValMultipleEBE, self).create(vals)


class ValMultipleEBELine(models.Model):
    _name = 'val.multiple.ebe.line'
    _description = "Valorisation d'entreprise par multiple d'EBE Line"

    year = fields.Selection(TYPE_YEAR)
    amount = fields.Float()

    val_id = fields.Many2one('val.multiple.ebe')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)



