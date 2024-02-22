# -*- coding: utf-8 -*-
import base64
from io import BytesIO

import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt
from odoo import models, fields, api

TYPE_FORCAST = [
    ('1', "Chiffre d'affaire"),
    ('2', 'Achats consommés'),
    ('3', 'Autres charges fixes'),
    ('4', 'Salaires'),
    ('5', 'EBE'),
    ('6', 'EBE %')
]


class ManualRevenueForecast(models.Model):
    _name = 'manual.revenue.forecast'
    _description = "Prévisions de chiffre d`affaire manuelle"

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")
    chiffre_affaire = fields.Float("Chiffre d'affaire")
    line_ids = fields.One2many('manual.revenue.forecast.line', inverse_name='manual_forecast_id')
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)
    xls_file = fields.Binary(string='Fichier Excel')
    name_fichier = fields.Char(string='Nom du fichier', default='revenue_forecast_manuel.xlsx')
    graph = fields.Binary(string='Graphe')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('manual.revenue.forecast.seq')

        return super(ManualRevenueForecast, self).create(vals)

    def open_dossier_credit(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_demande_credit_form').id
            montage = self.env['montage.demande.credit'].search([('prevision_id', '=', rec.id)])
            if not montage:
                return {
                    'name': "Montage du dossier de crédit",
                    'res_model': 'montage.demande.credit',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'prevision_id': rec.id}
                }
            else:
                return {
                    'name': "Montage du dossier de crédit",
                    'res_model': 'montage.demande.credit',
                    'domain': [('prevision_id', '=', rec.id)],
                    'view_mode': 'tree,form',
                    'type': 'ir.actions.act_window',
                    'context': {'prevision_id': rec.id}
                }

    def action_count_ebe(self):
        self.ensure_one()
        lines = self.env['manual.revenue.forecast.line']
        for line in self.line_ids:
            line.amount_n1 = (line.amount_n * (
                        1 + (line.augment_hypothesis_n1 / 100))) if line.augment_hypothesis_n1 > 0 else 0
            line.amount_n2 = (line.amount_n1 * (
                        1 + (line.augment_hypothesis_n2 / 100))) if line.augment_hypothesis_n2 > 0 else 0
            line.amount_n3 = (line.amount_n2 * (
                        1 + (line.augment_hypothesis_n3 / 100))) if line.augment_hypothesis_n3 > 0 else 0
            line.amount_n4 = (line.amount_n3 * (
                        1 + (line.augment_hypothesis_n4 / 100))) if line.augment_hypothesis_n4 > 0 else 0
            line.amount_n5 = (line.amount_n4 * ( 1 + (line.augment_hypothesis_n5 / 100))) if line.augment_hypothesis_n5 > 0 else 0

        line_extra = self.line_ids.filtered(lambda r: r.type_forecast in ('2', '3', '4'))
        line_chifre_affaire = self.line_ids.filtered(lambda r: r.type_forecast == '1')

        ebe_amount_n = sum(line_extra.mapped('amount_n'))
        ebe_amount_n1 = sum(line_extra.mapped('amount_n1'))
        ebe_amount_n2 = sum(line_extra.mapped('amount_n2'))
        ebe_amount_n3 = sum(line_extra.mapped('amount_n3'))
        ebe_amount_n4 = sum(line_extra.mapped('amount_n4'))
        ebe_amount_n5 = sum(line_extra.mapped('amount_n5'))

        ebe_n = line_chifre_affaire.amount_n - ebe_amount_n
        ebe_n1 = line_chifre_affaire.amount_n1 - ebe_amount_n1
        ebe_n2 = line_chifre_affaire.amount_n2 - ebe_amount_n2
        ebe_n3 = line_chifre_affaire.amount_n3 - ebe_amount_n3
        ebe_n4 = line_chifre_affaire.amount_n4 - ebe_amount_n4
        ebe_n5 = line_chifre_affaire.amount_n5 - ebe_amount_n5

        ebe_porcent_n = (ebe_n / line_chifre_affaire.amount_n) * 100
        ebe_porcent_n1 = (ebe_n1 / line_chifre_affaire.amount_n1) * 100
        ebe_porcent_n2 = (ebe_n2 / line_chifre_affaire.amount_n2) * 100
        ebe_porcent_n3 = (ebe_n3 / line_chifre_affaire.amount_n3) * 100
        ebe_porcent_n4 = (ebe_n4 / line_chifre_affaire.amount_n4) * 100
        ebe_porcent_n5 = (ebe_n5 / line_chifre_affaire.amount_n5) * 100

        ebe_id = self.env['manual.revenue.forecast.line'].search([('type_forecast', '=', '5'),
                                                                  ('manual_forecast_id', '=', self.id)])
        ebe_porcent_id = self.env['manual.revenue.forecast.line'].search([('type_forecast', '=', '6'),
                                                                          ('manual_forecast_id', '=', self.id)])

        if not ebe_id:
            lines.create({
                'type_forecast': '5',
                'amount_n': ebe_n,
                'amount_n1': ebe_n1,
                'amount_n2': ebe_n2,
                'amount_n3': ebe_n3,
                'amount_n4': ebe_n4,
                'amount_n5': ebe_n5,
                'manual_forecast_id': self.id,
            })
        else:
            ebe_id.amount_n = ebe_n
            ebe_id.amount_n1 = ebe_n1
            ebe_id.amount_n2 = ebe_n2
            ebe_id.amount_n3 = ebe_n3
            ebe_id.amount_n4 = ebe_n4
            ebe_id.amount_n5 = ebe_n5

        if not ebe_id:
            lines.create({
                'type_forecast': '6',
                'amount_n': ebe_porcent_n,
                'amount_n1': ebe_porcent_n1,
                'amount_n2': ebe_porcent_n2,
                'amount_n3': ebe_porcent_n3,
                'amount_n4': ebe_porcent_n4,
                'amount_n5': ebe_porcent_n5,
                'manual_forecast_id': self.id,
            })
        else:
            ebe_porcent_id.amount_n = ebe_porcent_n
            ebe_porcent_id.amount_n1 = ebe_porcent_n1
            ebe_porcent_id.amount_n2 = ebe_porcent_n2
            ebe_porcent_id.amount_n3 = ebe_porcent_n3
            ebe_porcent_id.amount_n4 = ebe_porcent_n4
            ebe_porcent_id.amount_n5 = ebe_porcent_n5

        records = self.env['manual.revenue.forecast.line'].search([('manual_forecast_id', '=', self.id)])
        data = get_Data(records)
        create_xls(self, data)
        create_stacked_chart(self, data)

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.name + '] ' + str(rec.chiffre_affaire)
            result.append((rec.id, name))
        return result


class ManualRevenueForecastLine(models.Model):
    _name = 'manual.revenue.forecast.line'
    _description = "Prévisions de chiffre d`affaire manuelle - line"

    type_forecast = fields.Selection(TYPE_FORCAST)

    amount_n = fields.Float(string="N")
    amount_n1 = fields.Float(string="N+1")
    amount_n2 = fields.Float(string="N+2")
    amount_n3 = fields.Float(string="N+3")
    amount_n4 = fields.Float(string="N+4")
    amount_n5 = fields.Float(string="N+5")

    augment_hypothesis_n1 = fields.Float(string="Hypothèse croissance N+1", digits=(16, 1))
    augment_hypothesis_n2 = fields.Float(string="Hypothèse croissance N+2", digits=(16, 1))
    augment_hypothesis_n3 = fields.Float(string="Hypothèse croissance N+3", digits=(16, 1))
    augment_hypothesis_n4 = fields.Float(string="Hypothèse croissance N+4", digits=(16, 1))
    augment_hypothesis_n5 = fields.Float(string="Hypothèse croissance N+5", digits=(16, 1))

    manual_forecast_id = fields.Many2one('manual.revenue.forecast')
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


def get_Data(data):
    recordset = []
    for i in data:
        element = {
            'type_forecast': TYPE_FORCAST[int(i.type_forecast) - 1][1],
            'amount_n': i.amount_n,
            'amount_n1': i.amount_n1,
            'amount_n2': i.amount_n2,
            'amount_n3': i.amount_n3,
            'amount_n4': i.amount_n4,
            'amount_n5': i.amount_n5
        }
        recordset.append(element)
    return recordset


def create_xls(self, data):
    result = BytesIO()
    workbook = xlsxwriter.Workbook(result)
    worksheet = workbook.add_worksheet("first")
    worksheet.write(0, 0, 'type_forecast')
    worksheet.write(0, 1, 'N')
    worksheet.write(0, 2, 'N+1')
    worksheet.write(0, 3, 'N+2')
    worksheet.write(0, 4, 'N+3')
    worksheet.write(0, 5, 'N+4')
    worksheet.write(0, 6, 'N+5')
    for index, entry in enumerate(data):
        worksheet.write(index + 1, 0, entry['type_forecast'])
        worksheet.write(index + 1, 1, entry['amount_n'])
        worksheet.write(index + 1, 2, entry['amount_n1'])
        worksheet.write(index + 1, 3, entry['amount_n2'])
        worksheet.write(index + 1, 4, entry['amount_n3'])
        worksheet.write(index + 1, 5, entry['amount_n4'])
        worksheet.write(index + 1, 6, entry['amount_n5'])

    workbook.close()
    buf = base64.b64encode(result.getvalue())
    self.write({'xls_file': buf})
    result.close()


def create_stacked_chart(self, data):
    data1 = list(data[1].values())[1:]
    data2 = list(data[2].values())[1:]
    data3 = list(data[3].values())[1:]
    data4 = list(data[4].values())[1:]
    data5 = list(data[0].values())[1:]

    year = ["N", "N+1", "N+2", "N+3", "N+4", "N+5"]
    plt.figure(figsize=(9, 7))
    plt.bar(year, data4, color="green", label="EBE")
    plt.bar(year, data1, color="yellow", bottom=np.array(data4), label="Achats consommés")
    plt.bar(year, data5, color="blue", bottom=np.array(data4) + np.array(data1), label="Chiffre D'affaire")

    plt.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))
    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    self.write({'graph': imageBase64})
    buf.close()
