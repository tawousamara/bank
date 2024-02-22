# -*- coding: utf-8 -*-

from odoo import models, fields, api
from itertools import groupby
from datetime import datetime
MONTH_SELECTION = [
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]


class AutomaticRevenueForecast(models.Model):
    _name = 'automatic.revenue.forecast'
    _description = "Prévisions de chiffre d`affaire automatique"

    type_data = fields.Selection([
        ('facture', 'Facture'),
        ('crm', 'CRM')])
    name = fields.Char("reference")
    year = fields.Char()
    line_ids = fields.One2many('automatic.revenue.forecast.line', inverse_name='auto_revenue_id')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    def action_get_revenue_forecast(self):
        self.ensure_one()
        if self.type_data == 'facture':
            accounts = self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('state', '=', 'posted')])

            for month, grouped_lines in groupby(accounts, lambda m: m.invoice_date.month):
                grouped_lines = list(grouped_lines)
                amount = sum(l.amount_untaxed for l in grouped_lines)
                year = datetime.now().year
                revenue_forecast = self.env['automatic.revenue.forecast.line'].search([
                    ('year', '=', year), ('month', '=', str(month)), ('type_data', '=', self.type_data),
                    ('auto_revenue_id', '=', self.id)])
                if not revenue_forecast:
                    self.env['automatic.revenue.forecast.line'].create({
                        'month': str(month),
                        'year': year,
                        'ca_ht': amount,
                        'type_data': self.type_data,
                        'auto_revenue_id': self.id,
                    })
                else:
                    revenue_forecast.ca_ht = amount

        if self.type_data == 'crm':
            leads = self.env['crm.lead'].search([])

            for month, grouped_lines in groupby(leads, lambda m: m.create_date.month):
                grouped_lines = list(grouped_lines)
                amount = sum(l.expected_revenue for l in grouped_lines)
                year = datetime.now().year
                revenue_forecast = self.env['automatic.revenue.forecast.line'].search(
                    [('year', '=', year), ('month', '=', str(month)), ('type_data', '=', self.type_data),
                     ('auto_revenue_id', '=', self.id)])
                if not revenue_forecast:
                    self.env['automatic.revenue.forecast.line'].create({
                        'month': str(month),
                        'year': year,
                        'ca_ht': amount,
                        'type_data': self.type_data,
                        'auto_revenue_id': self.id,
                    })
                else:
                    revenue_forecast.ca_ht = amount

    @api.model
    def create(self, vals):
        if vals['type_data'] == 'facture':
            vals['name'] = self.env['ir.sequence'].next_by_code('automatic.revenue.forecast.facture')
        elif vals['type_data'] == 'crm':
            vals['name'] = self.env['ir.sequence'].next_by_code('automatic.revenue.forecast.crm')

        return super(AutomaticRevenueForecast, self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.name + ']' + rec.year
            result.append((rec.id, name))
        return result


class AutomaticRevenueForecastLine(models.Model):
    _name = 'automatic.revenue.forecast.line'
    _description = "Prévisions de chiffre d`affaire automatique - line"

    type_data = fields.Selection([
        ('facture', 'Facture'),
        ('crm', 'CRM')])

    month = fields.Selection(MONTH_SELECTION)
    ca_ht = fields.Float(string="CA H.T")
    year = fields.Char()
    auto_revenue_id = fields.Many2one('automatic.revenue.forecast')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


