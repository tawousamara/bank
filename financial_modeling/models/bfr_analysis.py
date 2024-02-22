# -*- coding: utf-8 -*-
import base64
from io import BytesIO

import xlsxwriter
import numpy as np
import matplotlib.pyplot as plt

from odoo import models, fields, api

TYPE_BFR = [
    ('1', 'Chiffre d`affaire'),
    ('2', 'Stock'),
    ('3', 'Clients'),
    ('4', 'Fournisseurs'),
    ('5', 'BFR'),
    ('6', 'BFR en jours du CA')
]


class BFRAnalysis(models.Model):
    _name = 'bfr.analysis'
    _description = "BFR Analysis"

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")

    bfr_historical_ids = fields.One2many('bfr.historical', inverse_name='bfr_id')
    bfr_forecast_ids = fields.One2many('bfr.forecast', inverse_name='bfr_id')
    bfr_forecast_table_ids = fields.One2many('bfr.forecast.recap.table', inverse_name='bfr_id')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)

    manual_forecast_id = fields.Many2one('manual.revenue.forecast', string="Prévisions de chiffre d'affaire manuelle")

    is_count_bfr_historical = fields.Boolean()
    is_count_bfr_forecast = fields.Boolean()
    is_importer_ch_aff = fields.Boolean()
    is_recalcul = fields.Boolean()

    xls_file = fields.Binary(string='Fichier Excel')
    name_fichier = fields.Char(string='Nom du fichier', default='bfr_analyse.xlsx')
    graph_recap = fields.Binary(string='Graphe', attachment=False)
    graph_historical = fields.Binary(string='Graphe' , attachment=False)
    pie_graph_prec = fields.Binary(string='Graphe', attachment=False)
    pie_graph_suiv = fields.Binary(string='Graphe', attachment=False)

    year_prec = fields.Selection([('3', 'N-3'), ('2', 'N-2'), ('1', 'N-1'), ('0', 'N')], string='Année')
    year_suiv = fields.Selection([('0', 'N+1'), ('1', 'N+2'), ('2', 'N+3'), ('3', 'N+4'), ('4', 'N+5')], string='Année')
    def action_recalcul(self):
        self.ensure_one()
        self.is_count_bfr_historical = False
        self.is_count_bfr_forecast = False
        self.is_importer_ch_aff = False
        self.is_recalcul = True

    def _forecast_recap_table(self):
        self.ensure_one()
        if self.bfr_forecast_table_ids:
            bfr_forecast_table_ids = self.env['bfr.forecast.recap.table'].search([('bfr_id', '=', self.id)]).unlink()

        for rec in self.bfr_forecast_ids:
            self.env['bfr.forecast.recap.table'].create({
                'type_bfr': rec.type_bfr,
                'amount_n1': rec.amount_n1,
                'amount_n2': rec.amount_n2,
                'amount_n3': rec.amount_n3,
                'amount_n4': rec.amount_n4,
                'amount_n5': rec.amount_n5,
                'bfr_id': self.id,
            })
        data = get_Data(self.bfr_forecast_table_ids)
        create_xls(self, data)
        img = create_stacked_chart(data)
        self.write({'graph_recap': img})
    def action_import_chiffre_affaire(self):
        self.ensure_one()
        bfr_forecast = self.env['bfr.forecast']
        bfr_forecast_chaffaire = self.bfr_forecast_ids.filtered(lambda r: r.type_bfr == '1')
        manual_revenue = self.env['manual.revenue.forecast.line'].search([
            ('manual_forecast_id', '=', self.manual_forecast_id.id),
            ('type_forecast', '=', '1')], limit=1)

        if not bfr_forecast_chaffaire:
            if manual_revenue:
                bfr_forecast.create({
                    'type_bfr': manual_revenue.type_forecast,
                    'bfr_id': self.id,
                    'amount_n1': manual_revenue.amount_n1,
                    'amount_n2': manual_revenue.amount_n2,
                    'amount_n3': manual_revenue.amount_n3,
                    'amount_n4': manual_revenue.amount_n4,
                    'amount_n5': manual_revenue.amount_n5,
                    'augment_hypothesis_n1': manual_revenue.augment_hypothesis_n1,
                    'augment_hypothesis_n2': manual_revenue.augment_hypothesis_n2,
                    'augment_hypothesis_n3': manual_revenue.augment_hypothesis_n3,
                    'augment_hypothesis_n4': manual_revenue.augment_hypothesis_n4,
                    'augment_hypothesis_n5': manual_revenue.augment_hypothesis_n5,
                    'active': True
                })
        else:
            bfr_forecast_chaffaire.amount_n1 = manual_revenue.amount_n1
            bfr_forecast_chaffaire.amount_n2 = manual_revenue.amount_n2
            bfr_forecast_chaffaire.amount_n3 = manual_revenue.amount_n3
            bfr_forecast_chaffaire.amount_n4 = manual_revenue.amount_n4
            bfr_forecast_chaffaire.amount_n5 = manual_revenue.amount_n5
            bfr_forecast_chaffaire.augment_hypothesis_n1 = manual_revenue.augment_hypothesis_n1
            bfr_forecast_chaffaire.augment_hypothesis_n2 = manual_revenue.augment_hypothesis_n2
            bfr_forecast_chaffaire.augment_hypothesis_n3 = manual_revenue.augment_hypothesis_n3
            bfr_forecast_chaffaire.augment_hypothesis_n4 = manual_revenue.augment_hypothesis_n4
            bfr_forecast_chaffaire.augment_hypothesis_n5 = manual_revenue.augment_hypothesis_n5
        self.is_importer_ch_aff = True
        return bfr_forecast_chaffaire

    def count_bfr_forecast(self):
        self.ensure_one()
        bfr_forecast = self.env['bfr.forecast']

        bfr_forecast_chaffaire = self.action_import_chiffre_affaire()

        for line in self.bfr_forecast_ids:
            if line.type_bfr != '1':
                line.amount_n1 = (line.augment_hypothesis_n1 * bfr_forecast_chaffaire.amount_n1) / 12
                line.amount_n2 = (line.augment_hypothesis_n2 * bfr_forecast_chaffaire.amount_n2) / 12
                line.amount_n3 = (line.augment_hypothesis_n3 * bfr_forecast_chaffaire.amount_n3) / 12
                line.amount_n4 = (line.augment_hypothesis_n4 * bfr_forecast_chaffaire.amount_n4) / 12
                line.amount_n5 = (line.augment_hypothesis_n5 * bfr_forecast_chaffaire.amount_n5) / 12

        # Fournisseurs
        chiffre_affaire44 = self.bfr_forecast_ids.filtered(lambda r: r.type_bfr in ('2', '3'))
        augment_hypothesis_n1 = sum(chiffre_affaire44.mapped('augment_hypothesis_n1'))
        augment_hypothesis_n2 = sum(chiffre_affaire44.mapped('augment_hypothesis_n2'))
        augment_hypothesis_n3 = sum(chiffre_affaire44.mapped('augment_hypothesis_n3'))
        augment_hypothesis_n4 = sum(chiffre_affaire44.mapped('augment_hypothesis_n4'))
        augment_hypothesis_n5 = sum(chiffre_affaire44.mapped('augment_hypothesis_n5'))

        fournisseurs_bfr = self.bfr_forecast_ids.filtered(lambda r: r.type_bfr == '4')
        if not fournisseurs_bfr:
            fournisseurs_bfr = bfr_forecast.create({
                'type_bfr': '4',
                'augment_hypothesis_n1': (augment_hypothesis_n1 * 70) / 100,
                'augment_hypothesis_n2': (augment_hypothesis_n2 * 70) / 100,
                'augment_hypothesis_n3': (augment_hypothesis_n3 * 70) / 100,
                'augment_hypothesis_n4': (augment_hypothesis_n4 * 70) / 100,
                'augment_hypothesis_n5': (augment_hypothesis_n5 * 70) / 100,
                'amount_n1': (((augment_hypothesis_n1 * 70) / 100) * bfr_forecast_chaffaire.amount_n1) / 12,
                'amount_n2': (((augment_hypothesis_n2 * 70) / 100) * bfr_forecast_chaffaire.amount_n2) / 12,
                'amount_n3': (((augment_hypothesis_n3 * 70) / 100) * bfr_forecast_chaffaire.amount_n3) / 12,
                'amount_n4': (((augment_hypothesis_n4 * 70) / 100) * bfr_forecast_chaffaire.amount_n4) / 12,
                'amount_n5': (((augment_hypothesis_n5 * 70) / 100) * bfr_forecast_chaffaire.amount_n5) / 12,
                'bfr_id': self.id,
            })
        else:
            fournisseurs_bfr.augment_hypothesis_n1 = (augment_hypothesis_n1 * 70) / 100
            fournisseurs_bfr.augment_hypothesis_n2 = (augment_hypothesis_n2 * 70) / 100
            fournisseurs_bfr.augment_hypothesis_n3 = (augment_hypothesis_n3 * 70) / 100
            fournisseurs_bfr.augment_hypothesis_n4 = (augment_hypothesis_n4 * 70) / 100
            fournisseurs_bfr.augment_hypothesis_n5 = (augment_hypothesis_n5 * 70) / 100
            fournisseurs_bfr.amount_n1 = (((augment_hypothesis_n1 * 70) / 100) * bfr_forecast_chaffaire.amount_n1) / 12
            fournisseurs_bfr.amount_n2 = (((augment_hypothesis_n2 * 70) / 100) * bfr_forecast_chaffaire.amount_n2) / 12
            fournisseurs_bfr.amount_n3 = (((augment_hypothesis_n3 * 70) / 100) * bfr_forecast_chaffaire.amount_n3) / 12
            fournisseurs_bfr.amount_n4 = (((augment_hypothesis_n4 * 70) / 100) * bfr_forecast_chaffaire.amount_n4) / 12
            fournisseurs_bfr.amount_n5 = (((augment_hypothesis_n5 * 70) / 100) * bfr_forecast_chaffaire.amount_n5) / 12

        # ----------------------------------------------------------------
        bfr_amount_n1 = sum(chiffre_affaire44.mapped('amount_n1'))
        bfr_amount_n2 = sum(chiffre_affaire44.mapped('amount_n2'))
        bfr_amount_n3 = sum(chiffre_affaire44.mapped('amount_n3'))
        bfr_amount_n4 = sum(chiffre_affaire44.mapped('amount_n4'))
        bfr_amount_n5 = sum(chiffre_affaire44.mapped('amount_n5'))

        bfr_n1 = bfr_amount_n1 - fournisseurs_bfr.amount_n1
        bfr_n2 = bfr_amount_n2 - fournisseurs_bfr.amount_n2
        bfr_n3 = bfr_amount_n3 - fournisseurs_bfr.amount_n3
        bfr_n4 = bfr_amount_n4 - fournisseurs_bfr.amount_n4
        bfr_n5 = bfr_amount_n5 - fournisseurs_bfr.amount_n5

        bfr_ca_n1 = round((
                                      bfr_n1 * 360) / bfr_forecast_chaffaire.amount_n1) if bfr_n1 > 0 and bfr_forecast_chaffaire.amount_n1 > 0 else 0
        bfr_ca_n2 = round((
                                      bfr_n2 * 360) / bfr_forecast_chaffaire.amount_n2) if bfr_n2 > 0 and bfr_forecast_chaffaire.amount_n2 > 0 else 0
        bfr_ca_n3 = round((
                                      bfr_n3 * 360) / bfr_forecast_chaffaire.amount_n3) if bfr_n3 > 0 and bfr_forecast_chaffaire.amount_n3 > 0 else 0
        bfr_ca_n4 = round((
                                      bfr_n4 * 360) / bfr_forecast_chaffaire.amount_n4) if bfr_n4 > 0 and bfr_forecast_chaffaire.amount_n4 > 0 else 0
        bfr_ca_n5 = round((
                                      bfr_n5 * 360) / bfr_forecast_chaffaire.amount_n5) if bfr_n5 > 0 and bfr_forecast_chaffaire.amount_n5 > 0 else 0

        bfr_id = self.env['bfr.forecast'].search([('type_bfr', '=', '5'), ('bfr_id', '=', self.id)])
        bfr_ca_id = self.env['bfr.forecast'].search([('type_bfr', '=', '6'), ('bfr_id', '=', self.id)])

        if not bfr_id:
            bfr_forecast.create({
                'type_bfr': '5',
                'amount_n1': bfr_n1,
                'amount_n2': bfr_n2,
                'amount_n3': bfr_n3,
                'amount_n4': bfr_n4,
                'amount_n5': bfr_n5,
                'bfr_id': self.id,
            })
        else:
            bfr_id.amount_n1 = bfr_n1
            bfr_id.amount_n2 = bfr_n2
            bfr_id.amount_n3 = bfr_n3
            bfr_id.amount_n4 = bfr_n4
            bfr_id.amount_n5 = bfr_n5

        if not bfr_ca_id:
            bfr_forecast.create({
                'type_bfr': '6',
                'amount_n1': bfr_ca_n1,
                'amount_n2': bfr_ca_n2,
                'amount_n3': bfr_ca_n3,
                'amount_n4': bfr_ca_n4,
                'amount_n5': bfr_ca_n5,
                'bfr_id': self.id,
            })
        else:
            bfr_ca_id.amount_n1 = bfr_ca_n1
            bfr_ca_id.amount_n2 = bfr_ca_n2
            bfr_ca_id.amount_n3 = bfr_ca_n3
            bfr_ca_id.amount_n4 = bfr_ca_n4
            bfr_ca_id.amount_n5 = bfr_ca_n5
        self._forecast_recap_table()
        self.is_count_bfr_forecast = True
        self.is_recalcul = False

    def count_bfr_historical(self):
        self.ensure_one()
        bfr_historical = self.env['bfr.historical']
        bfr_amount_n = self.bfr_historical_ids.mapped('amount_n')
        bfr_amount_n1 = self.bfr_historical_ids.mapped('amount_n1')
        bfr_amount_n2 = self.bfr_historical_ids.mapped('amount_n2')
        bfr_amount_n3 = self.bfr_historical_ids.mapped('amount_n3')

        bfr_n = bfr_amount_n[1] + bfr_amount_n[2] - bfr_amount_n[3]
        bfr_n1 = bfr_amount_n1[1] + bfr_amount_n1[2] - bfr_amount_n1[3]
        bfr_n2 = bfr_amount_n2[1] + bfr_amount_n2[2] - bfr_amount_n2[3]
        bfr_n3 = bfr_amount_n3[1] + bfr_amount_n3[2] - bfr_amount_n3[3]

        bfr_ca_n = round((bfr_n * 360) / bfr_amount_n[0])
        bfr_ca_n1 = round((bfr_n1 * 360) / bfr_amount_n1[0])
        bfr_ca_n2 = round((bfr_n2 * 360) / bfr_amount_n2[0])
        bfr_ca_n3 = round((bfr_n3 * 360) / bfr_amount_n3[0])

        bfr_id = self.env['bfr.historical'].search([('type_bfr', '=', '5'), ('bfr_id', '=', self.id)])
        bfr_ca_id = self.env['bfr.historical'].search([('type_bfr', '=', '6'), ('bfr_id', '=', self.id)])

        if not bfr_id:
            bfr_historical.create({
                'type_bfr': '5',
                'amount_n': bfr_n,
                'amount_n1': bfr_n1,
                'amount_n2': bfr_n2,
                'amount_n3': bfr_n3,
                'bfr_id': self.id,
            })
        else:
            bfr_id.amount_n = bfr_n
            bfr_id.amount_n1 = bfr_n1
            bfr_id.amount_n2 = bfr_n2
            bfr_id.amount_n3 = bfr_n3

        if not bfr_ca_id:
            bfr_historical.create({
                'type_bfr': '6',
                'amount_n': bfr_ca_n,
                'amount_n1': bfr_ca_n1,
                'amount_n2': bfr_ca_n2,
                'amount_n3': bfr_ca_n3,
                'bfr_id': self.id,
            })
        else:
            bfr_ca_id.amount_n = bfr_ca_n
            bfr_ca_id.amount_n1 = bfr_ca_n1
            bfr_ca_id.amount_n2 = bfr_ca_n2
            bfr_ca_id.amount_n3 = bfr_ca_n3

        self.is_count_bfr_historical = True
        img = create_stacked_chart(get_Data(self.bfr_historical_ids, type_class=2), type_class=2)
        self.write({'graph_historical': img})
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bfr.analysis.seq')

        return super(BFRAnalysis, self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.name + '] '
            result.append((rec.id, name))
        return result
    @api.onchange('year_prec')
    def compute_graph_prec(self):
        if self.year_prec and len(self.bfr_historical_ids) >= 6:
            records = self.bfr_historical_ids
            data = get_Data(records, type_class=2)
            sizes = []
            for i in data:
                row = list(i.values())
                if row[0] != "Chiffre d`affaire" and row[0] != "BFR" and row[0] != "BFR en jours du CA":
                    size = row[int(self.year_prec)+1]
                    sizes.append(size)
            img = create_pie(sizes)
            self.write({'pie_graph_prec': img})

    @api.onchange('year_suiv')
    def compute_graph_suiv(self):
        if self.year_suiv and len(self.bfr_forecast_table_ids) >= 6:
            records = self.bfr_forecast_table_ids
            data = get_Data(records)
            sizes = []
            for i in data:
                row = list(i.values())
                if row[0] != "Chiffre d`affaire" and row[0] != "BFR" and row[0] != "BFR en jours du CA":
                    size = row[int(self.year_suiv)+1]
                    sizes.append(size)
            print(sizes)
            img = create_pie(sizes)
            self.write({'pie_graph_suiv': img})

class BFRHistorical(models.Model):
    _name = 'bfr.historical'
    _description = "BFR Historical"

    type_bfr = fields.Selection(TYPE_BFR, string="Type BFR")
    bfr_id = fields.Many2one('bfr.analysis')

    amount_n = fields.Float(string="N")
    amount_n1 = fields.Float(string="N-1")
    amount_n2 = fields.Float(string="N-2")
    amount_n3 = fields.Float(string="N-3")

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


class BFRForecast(models.Model):
    _name = 'bfr.forecast'
    _description = "BFR Forecast"

    type_bfr = fields.Selection(TYPE_BFR, string="Type BFR")
    bfr_id = fields.Many2one('bfr.analysis')

    amount_n1 = fields.Float(string="N+1")
    amount_n2 = fields.Float(string="N+2")
    amount_n3 = fields.Float(string="N+3")
    amount_n4 = fields.Float(string="N+4")
    amount_n5 = fields.Float(string="N+5")

    augment_hypothesis_n1 = fields.Float(string="Hypothèse croissance N+1", digits=(16, 2))
    augment_hypothesis_n2 = fields.Float(string="Hypothèse croissance N+2", digits=(16, 2))
    augment_hypothesis_n3 = fields.Float(string="Hypothèse croissance N+3", digits=(16, 2))
    augment_hypothesis_n4 = fields.Float(string="Hypothèse croissance N+4", digits=(16, 2))
    augment_hypothesis_n5 = fields.Float(string="Hypothèse croissance N+5", digits=(16, 2))

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


class ForecastRecapTable(models.Model):
    _name = 'bfr.forecast.recap.table'
    _description = "BFR Forecast Recap Table"

    type_bfr = fields.Selection(TYPE_BFR, string="Type BFR")
    bfr_id = fields.Many2one('bfr.analysis')

    amount_n1 = fields.Float(string="N+1")
    amount_n2 = fields.Float(string="N+2")
    amount_n3 = fields.Float(string="N+3")
    amount_n4 = fields.Float(string="N+4")
    amount_n5 = fields.Float(string="N+5")

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True)


def get_Data(data, type_class=1):
    recordset = []
    if type_class != 1:
        for i in data:
            element = {
                'type_bfr': TYPE_BFR[int(i.type_bfr) - 1][1],
                'amount_n': i.amount_n,
                'amount_n1': i.amount_n1,
                'amount_n2': i.amount_n2,
                'amount_n3': i.amount_n3,
            }
            recordset.append(element)
    else:
        for i in data:
            element = {
                'type_bfr': TYPE_BFR[int(i.type_bfr) - 1][1],
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
    worksheet = workbook.add_worksheet("recap")
    worksheet.write(0, 0, 'type_bfr')
    worksheet.write(0, 1, 'N+1')
    worksheet.write(0, 2, 'N+2')
    worksheet.write(0, 3, 'N+3')
    worksheet.write(0, 4, 'N+4')
    worksheet.write(0, 5, 'N+5')
    for index, entry in enumerate(data):
        worksheet.write(index + 1, 0, entry['type_bfr'])
        worksheet.write(index + 1, 1, entry['amount_n1'])
        worksheet.write(index + 1, 2, entry['amount_n2'])
        worksheet.write(index + 1, 3, entry['amount_n3'])
        worksheet.write(index + 1, 4, entry['amount_n4'])
        worksheet.write(index + 1, 5, entry['amount_n5'])

    workbook.close()
    buf = base64.b64encode(result.getvalue())
    self.write({'xls_file': buf})
    result.close()


def create_stacked_chart(data, type_class=1):
    if type_class != 1:
        data1 = list(data[4].values())[1:]
        data2 = list(data[0].values())[1:]
        data4 = list(reversed(data1))
        data5 = list(reversed(data2))
        print(data4)
        print(data5)
        year = ["N-3", "N-2", "N-1", "N"]
    else:
        data4 = list(data[4].values())[1:]
        data5 = list(data[0].values())[1:]

        year = ["N+1", "N+2", "N+3", "N+4", "N+5"]
    x = np.arange(len(year))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, data4, width, label='BFR')
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
    buf.close()
    return imageBase64
def create_pie(data):
    labels = 'Stock', 'Clients', 'Fournisseurs'
    sizes = data

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes,  labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    buf.close()
    return imageBase64