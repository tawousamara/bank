# -*- coding: utf-8 -*-
import base64
from io import BytesIO

import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt

from odoo import models, fields, api

TYPE_FORCAST = [
    ('1', 'Chiffre d`affaire'),
    ('2', 'Achats consommés'),
    ('3', 'Autres charges fixes'),
    ('4', 'Salaires'),
    ('5', 'EBE'),
    ('6', 'EBE %'),
    ('7', 'Stock'),
    ('8', 'Clients'),
    ('9', 'Fournisseurs'),
    ('10', 'BFR'),
    ('11', 'BFR en jours du CA'),
]


class StressTesting(models.Model):
    _name = 'stress.testing'
    _description = "Stress Testing"

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")

    line_ids = fields.One2many('stress.testing.line', inverse_name='stress_id')
    line_ids_temp = fields.One2many('stress.testing.line', inverse_name='stress_id')

    manual_forecast_id = fields.Many2one('manual.revenue.forecast', string="Prévisions de chiffre d'affaire manuelle")
    bfr_analysis_id = fields.Many2one('bfr.analysis', string="BFR")

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    xls_file = fields.Binary(string='Fichier Excel')
    name_fichier = fields.Char(string='Nom du fichier', default='stress_testing.xlsx')
    graph = fields.Binary(string='Graphe')

    def action_real_case(self):
        self.ensure_one()
        line_data = self.env['stress.testing.line']
        self.env['stress.testing.line'].search([('stress_id', '=', self.id)]).unlink()
        i = 0
        for rec in self.manual_forecast_id.line_ids:
            i += 1
            line_data.create({
                'type_forecast': rec.type_forecast,
                'amount_n1': rec.amount_n1,
                'amount_n2': rec.amount_n2,
                'amount_n3': rec.amount_n3,
                'amount_n4': rec.amount_n4,
                'amount_n5': rec.amount_n5,
                'stress_id': self.id,
                'sequence': i,
            })

        for rec in self.bfr_analysis_id.bfr_forecast_ids:
            i += 1
            if rec.type_bfr != '1':
                type_bfr = False
                if rec.type_bfr == '2':
                    type_bfr = '7'
                elif rec.type_bfr == '3':
                    type_bfr = '8'
                elif rec.type_bfr == '4':
                    type_bfr = '9'
                elif rec.type_bfr == '5':
                    type_bfr = '10'
                elif rec.type_bfr == '6':
                    type_bfr = '11'

                line_data.create({
                    'type_forecast': type_bfr,
                    'amount_n1': rec.amount_n1,
                    'amount_n2': rec.amount_n2,
                    'amount_n3': rec.amount_n3,
                    'amount_n4': rec.amount_n4,
                    'amount_n5': rec.amount_n5,
                    'stress_id': self.id,
                    'sequence': i,
                })
        records = self.env['stress.testing.line'].search([('stress_id', '=', self.id)])
        data = get_Data(records)
        create_xls(self, data)
        create_stacked_chart(self, data)

    def action_10_case(self):
        self.ensure_one()
        self.action_real_case()
        data1 = get_Data(self.line_ids)
        sum_ebe_n1 = amount_ca_n1 = 0
        sum_ebe_n2 = amount_ca_n2 = 0
        sum_ebe_n3 = amount_ca_n3 = 0
        sum_ebe_n4 = amount_ca_n4 = 0
        sum_ebe_n5 = amount_ca_n5 = 0
        for rec in self.line_ids:
            if rec.type_forecast == '2' or rec.type_forecast == '3' or rec.type_forecast == '4':
                sum_ebe_n1 += rec.amount_n1
                sum_ebe_n2 += rec.amount_n2
                sum_ebe_n3 += rec.amount_n3
                sum_ebe_n4 += rec.amount_n4
                sum_ebe_n5 += rec.amount_n5
            if rec.type_forecast == '1':
                amount_ca_n1 = rec.amount_n1 = (rec.amount_n1 * 90) / 100
                amount_ca_n2 = rec.amount_n2 = (rec.amount_n2 * 90) / 100
                amount_ca_n3 = rec.amount_n3 = (rec.amount_n3 * 90) / 100
                amount_ca_n4 = rec.amount_n4 = (rec.amount_n4 * 90) / 100
                amount_ca_n5 = rec.amount_n5 = (rec.amount_n5 * 90) / 100
            elif rec.type_forecast == '5':
                rec.amount_n1 = amount_ca_n1 - sum_ebe_n1
                rec.amount_n2 = amount_ca_n2 - sum_ebe_n2
                rec.amount_n3 = amount_ca_n3 - sum_ebe_n3
                rec.amount_n4 = amount_ca_n4 - sum_ebe_n4
                rec.amount_n5 = amount_ca_n5 - sum_ebe_n5
            elif rec.type_forecast == '6':
                rec.amount_n1 = ((amount_ca_n1 - sum_ebe_n1) / amount_ca_n1) * 100
                rec.amount_n2 = ((amount_ca_n2 - sum_ebe_n2) / amount_ca_n2) * 100
                rec.amount_n3 = ((amount_ca_n3 - sum_ebe_n3) / amount_ca_n3) * 100
                rec.amount_n4 = ((amount_ca_n4 - sum_ebe_n4) / amount_ca_n4) * 100
                rec.amount_n5 = ((amount_ca_n5 - sum_ebe_n5) / amount_ca_n5) * 100
            elif rec.type_forecast == '7':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca)
            elif rec.type_forecast == '9':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca, type=9)
            elif rec.type_forecast == '10':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca, type=10)
        self.line_ids_temp = self.line_ids
        data2 = get_Data(self.line_ids)
        create_xls(self, data1, data2)
        create_stacked_chart(self, data2)

    def action_20_case(self):
        self.ensure_one()
        self.action_real_case()
        data1 = get_Data(self.line_ids)
        if self.line_ids_temp:
            data2 = get_Data(self.line_ids_temp)
        sum_ebe_n1 = amount_ca_n1 = 0
        sum_ebe_n2 = amount_ca_n2 = 0
        sum_ebe_n3 = amount_ca_n3 = 0
        sum_ebe_n4 = amount_ca_n4 = 0
        sum_ebe_n5 = amount_ca_n5 = 0
        for rec in self.line_ids:
            if rec.type_forecast == '2' or rec.type_forecast == '3' or rec.type_forecast == '4':
                sum_ebe_n1 += rec.amount_n1
                sum_ebe_n2 += rec.amount_n2
                sum_ebe_n3 += rec.amount_n3
                sum_ebe_n4 += rec.amount_n4
                sum_ebe_n5 += rec.amount_n5
            if rec.type_forecast == '1':
                amount_ca_n1 = rec.amount_n1 = (rec.amount_n1 * 80) / 100
                amount_ca_n2 = rec.amount_n2 = (rec.amount_n2 * 80) / 100
                amount_ca_n3 = rec.amount_n3 = (rec.amount_n3 * 80) / 100
                amount_ca_n4 = rec.amount_n4 = (rec.amount_n4 * 80) / 100
                amount_ca_n5 = rec.amount_n5 = (rec.amount_n5 * 80) / 100
            elif rec.type_forecast == '5':
                rec.amount_n1 = amount_ca_n1 - sum_ebe_n1
                rec.amount_n2 = amount_ca_n2 - sum_ebe_n2
                rec.amount_n3 = amount_ca_n3 - sum_ebe_n3
                rec.amount_n4 = amount_ca_n4 - sum_ebe_n4
                rec.amount_n5 = amount_ca_n5 - sum_ebe_n5
            elif rec.type_forecast == '6':
                rec.amount_n1 = ((amount_ca_n1 - sum_ebe_n1) / amount_ca_n1) * 100
                rec.amount_n2 = ((amount_ca_n2 - sum_ebe_n2) / amount_ca_n2) * 100
                rec.amount_n3 = ((amount_ca_n3 - sum_ebe_n3) / amount_ca_n3) * 100
                rec.amount_n4 = ((amount_ca_n4 - sum_ebe_n4) / amount_ca_n4) * 100
                rec.amount_n5 = ((amount_ca_n5 - sum_ebe_n5) / amount_ca_n5) * 100
            elif rec.type_forecast == '7':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca)
            elif rec.type_forecast == '9':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca, type=9)
            elif rec.type_forecast == '10':
                bfr_ca = self.line_ids.filtered(lambda r: r.type_forecast == '1')
                recalcul_bfr(self, bfr_ca, type=10)
        data3 = get_Data(self.line_ids)
        create_xls(self, data1, data2, data3)
        create_stacked_chart(self, data3)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('stress.testing.seq')

        return super(StressTesting, self).create(vals)


class StressTestingLine(models.Model):
    _name = 'stress.testing.line'
    _description = "Stress Testing - Line"
    _order = 'sequence asc'

    sequence = fields.Integer()

    stress_id = fields.Many2one('stress.testing')
    type_forecast = fields.Selection(TYPE_FORCAST)

    amount_n1 = fields.Float(string="N+1")
    amount_n2 = fields.Float(string="N+2")
    amount_n3 = fields.Float(string="N+3")
    amount_n4 = fields.Float(string="N+4")
    amount_n5 = fields.Float(string="N+5")

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


def get_Data(data):
    recordset = []
    for i in data:
        element = {
            'type_forecast': TYPE_FORCAST[int(i.type_forecast) - 1][1],
            'amount_n1': i.amount_n1,
            'amount_n2': i.amount_n2,
            'amount_n3': i.amount_n3,
            'amount_n4': i.amount_n4,
            'amount_n5': i.amount_n5
        }
        recordset.append(element)
    return recordset


def create_xls(self, data1, data2=1, data3=1):
    result = BytesIO()
    workbook = xlsxwriter.Workbook(result)
    worksheet = workbook.add_worksheet("Cas réel")
    worksheet.write(0, 0, 'type_forecast')
    worksheet.write(0, 2, 'N+1')
    worksheet.write(0, 3, 'N+2')
    worksheet.write(0, 4, 'N+3')
    worksheet.write(0, 5, 'N+4')
    worksheet.write(0, 6, 'N+5')
    for index, entry in enumerate(data1):
        worksheet.write(index + 1, 0, entry['type_forecast'])
        worksheet.write(index + 1, 2, entry['amount_n1'])
        worksheet.write(index + 1, 3, entry['amount_n2'])
        worksheet.write(index + 1, 4, entry['amount_n3'])
        worksheet.write(index + 1, 5, entry['amount_n4'])
        worksheet.write(index + 1, 6, entry['amount_n5'])
    if data2 != 1 and data2:
        print(type(data2))
        worksheet = workbook.add_worksheet("Cas -10% CA")
        worksheet.write(0, 0, 'type_forecast')
        worksheet.write(0, 2, 'N+1')
        worksheet.write(0, 3, 'N+2')
        worksheet.write(0, 4, 'N+3')
        worksheet.write(0, 5, 'N+4')
        worksheet.write(0, 6, 'N+5')
        for index, entry in enumerate(data2):
            worksheet.write(index + 1, 0, entry['type_forecast'])
            worksheet.write(index + 1, 2, entry['amount_n1'])
            worksheet.write(index + 1, 3, entry['amount_n2'])
            worksheet.write(index + 1, 4, entry['amount_n3'])
            worksheet.write(index + 1, 5, entry['amount_n4'])
            worksheet.write(index + 1, 6, entry['amount_n5'])
    if data3 != 1:
        worksheet = workbook.add_worksheet("Cas -20% CA")
        worksheet.write(0, 0, 'type_forecast')
        worksheet.write(0, 2, 'N+1')
        worksheet.write(0, 3, 'N+2')
        worksheet.write(0, 4, 'N+3')
        worksheet.write(0, 5, 'N+4')
        worksheet.write(0, 6, 'N+5')
        for index, entry in enumerate(data3):
            worksheet.write(index + 1, 0, entry['type_forecast'])
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
    data4 = list(data[4].values())[1:]
    data5 = list(data[0].values())[1:]

    year = ["N+1", "N+2", "N+3", "N+4", "N+5"]
    x = np.arange(len(year))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, data4, width, label='EBE')
    rects2 = ax.bar(x + width / 2, data5, width, label="Chiffre d'affaire")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Montant')
    ax.set_title('Montant par année')
    ax.set_xticks(x, year)
    ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    self.write({'graph': imageBase64})
    buf.close()

def recalcul_bfr(self,bfr_ca,type=7):
    bfr_forecast = self.env['bfr.forecast']
    print('recalcul executed')
    line_data = self.env['stress.testing.line']
    bfr_forecast_chaffaire = bfr_ca
    i = len(self.line_ids)
    if type == 7:
        for line in self.bfr_analysis_id.bfr_forecast_ids:
            if line.type_bfr != '1':
                type_bfr = False
                if line.type_bfr == '2':
                    type_bfr = '7'
                elif line.type_bfr == '3':
                    type_bfr = '8'
                elif line.type_bfr == '4':
                    type_bfr = '9'
                elif line.type_bfr == '5':
                    type_bfr = '10'
                elif line.type_bfr == '6':
                    type_bfr = '11'
                amount_n1 = (line.augment_hypothesis_n1 * bfr_forecast_chaffaire.amount_n1) / 12
                amount_n2 = (line.augment_hypothesis_n2 * bfr_forecast_chaffaire.amount_n2) / 12
                amount_n3 = (line.augment_hypothesis_n3 * bfr_forecast_chaffaire.amount_n3) / 12
                amount_n4 = (line.augment_hypothesis_n4 * bfr_forecast_chaffaire.amount_n4) / 12
                amount_n5 = (line.augment_hypothesis_n5 * bfr_forecast_chaffaire.amount_n5) / 12
                line_data.search([('type_forecast', '=', type_bfr)]).write({
                                    'amount_n1': amount_n1,
                                    'amount_n2': amount_n2,
                                    'amount_n3': amount_n3,
                                    'amount_n4': amount_n4,
                                    'amount_n5': amount_n5,
                                    'stress_id': self.id,
                                })

    # Fournisseurs
    chiffre_affaire44 = self.bfr_analysis_id.bfr_forecast_ids.filtered(lambda r: r.type_bfr in ('2', '3'))

    augment_hypothesis_n1 = sum(chiffre_affaire44.mapped('augment_hypothesis_n1'))
    augment_hypothesis_n2 = sum(chiffre_affaire44.mapped('augment_hypothesis_n2'))
    augment_hypothesis_n3 = sum(chiffre_affaire44.mapped('augment_hypothesis_n3'))
    augment_hypothesis_n4 = sum(chiffre_affaire44.mapped('augment_hypothesis_n4'))
    augment_hypothesis_n5 = sum(chiffre_affaire44.mapped('augment_hypothesis_n5'))

    fournisseurs_bfr_amount_n1 = (((augment_hypothesis_n1 * 70) / 100) * bfr_forecast_chaffaire.amount_n1) / 12
    fournisseurs_bfr_amount_n2 = (((augment_hypothesis_n2 * 70) / 100) * bfr_forecast_chaffaire.amount_n2) / 12
    fournisseurs_bfr_amount_n3 = (((augment_hypothesis_n3 * 70) / 100) * bfr_forecast_chaffaire.amount_n3) / 12
    fournisseurs_bfr_amount_n4 = (((augment_hypothesis_n4 * 70) / 100) * bfr_forecast_chaffaire.amount_n4) / 12
    fournisseurs_bfr_amount_n5 = (((augment_hypothesis_n5 * 70) / 100) * bfr_forecast_chaffaire.amount_n5) / 12
    if type == 9:
        line_data.search([('type_forecast', '=', "9")]).write({
            'amount_n1': fournisseurs_bfr_amount_n1,
            'amount_n2': fournisseurs_bfr_amount_n2,
            'amount_n3': fournisseurs_bfr_amount_n3,
            'amount_n4': fournisseurs_bfr_amount_n4,
            'amount_n5': fournisseurs_bfr_amount_n5,
            'stress_id': self.id,
        })
        i += 1
    # ----------------------------------------------------------------

    bfr_amount_n1 = sum(chiffre_affaire44.mapped('amount_n1'))
    bfr_amount_n2 = sum(chiffre_affaire44.mapped('amount_n2'))
    bfr_amount_n3 = sum(chiffre_affaire44.mapped('amount_n3'))
    bfr_amount_n4 = sum(chiffre_affaire44.mapped('amount_n4'))
    bfr_amount_n5 = sum(chiffre_affaire44.mapped('amount_n5'))

    bfr_n1 = bfr_amount_n1 - fournisseurs_bfr_amount_n1
    bfr_n2 = bfr_amount_n2 - fournisseurs_bfr_amount_n2
    bfr_n3 = bfr_amount_n3 - fournisseurs_bfr_amount_n3
    bfr_n4 = bfr_amount_n4 - fournisseurs_bfr_amount_n4
    bfr_n5 = bfr_amount_n5 - fournisseurs_bfr_amount_n5

    bfr_ca_n1 = round(
        (bfr_n1 * 360) / bfr_forecast_chaffaire.amount_n1) if bfr_n1 > 0 and bfr_forecast_chaffaire.amount_n1 > 0 else 0
    bfr_ca_n2 = round(
        (bfr_n2 * 360) / bfr_forecast_chaffaire.amount_n2) if bfr_n2 > 0 and bfr_forecast_chaffaire.amount_n2 > 0 else 0
    bfr_ca_n3 = round(
        (bfr_n3 * 360) / bfr_forecast_chaffaire.amount_n3) if bfr_n3 > 0 and bfr_forecast_chaffaire.amount_n3 > 0 else 0
    bfr_ca_n4 = round(
        (bfr_n4 * 360) / bfr_forecast_chaffaire.amount_n4) if bfr_n4 > 0 and bfr_forecast_chaffaire.amount_n4 > 0 else 0
    bfr_ca_n5 = round(
        (bfr_n5 * 360) / bfr_forecast_chaffaire.amount_n5) if bfr_n5 > 0 and bfr_forecast_chaffaire.amount_n5 > 0 else 0
    if type==10:

        bfr_id = line_data.search([('type_forecast', '=', '10'), ('stress_id', '=', self.id)])\
            .write({
                'amount_n1': bfr_n1,
                'amount_n2': bfr_n2,
                'amount_n3': bfr_n3,
                'amount_n4': bfr_n4,
                'amount_n5': bfr_n5,
                'stress_id': self.id,
            })
        i += 1
        bfr_ca_id = line_data.search([('type_forecast', '=', '11'), ('stress_id', '=', self.id)])\
            .write({'amount_n1': bfr_ca_n1,
                'amount_n2': bfr_ca_n2,
                'amount_n3': bfr_ca_n3,
                'amount_n4': bfr_ca_n4,
                'amount_n5': bfr_ca_n5,
                'stress_id': self.id,
            })