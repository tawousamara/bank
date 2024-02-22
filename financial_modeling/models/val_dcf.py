# -*- coding: utf-8 -*-

from odoo import models, fields, api

import base64
from io import BytesIO

import numpy as np
import matplotlib.pyplot as plt

TYPE_YEAR = [
    ('1', 'EBE'),
    ('2', 'IBS'),
    ('3', 'Var. BFR'),
    ('4', 'Free Cash-Flow'),
    ('5', 'Discounted CF'),
]


class ValDCF(models.Model):
    _name = 'val.discouted.cash.flow'
    _description = "Valorisation d`entreprise par le Discouted Cash-Flow"

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")

    amount_ve = fields.Float(string="VE",  digits=(16, 3))
    tri = fields.Float(string="TRI", digits=(16, 3))

    line_ids = fields.One2many('val.discouted.cash.flow.line', 'val_id')

    ebe_id = fields.Many2one('manual.revenue.forecast', string="Prévisions de chiffre d`affaire - Manuelle")
    bfr_id = fields.Many2one('bfr.analysis', string="BFR Analysis")

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)
    graph = fields.Binary(string="Visualisation graphique")

    def action_import_ebe(self):
        self.ensure_one()
        lines_ebe = self.line_ids.filtered(lambda m: m.type == '1')
        if self.ebe_id:
            line_ebe = self.ebe_id.line_ids.filtered(lambda m: m.type_forecast == '5')
            if line_ebe and not lines_ebe:
                self.env['val.discouted.cash.flow.line'].create({
                    'type': '1',
                    'amount_n1': line_ebe.amount_n1,
                    'amount_n2': line_ebe.amount_n2,
                    'amount_n3': line_ebe.amount_n3,
                    'amount_n4': line_ebe.amount_n4,
                    'amount_n5': line_ebe.amount_n5,
                    'val_id': self.id,
                })
            elif line_ebe and lines_ebe:
                lines_ebe.update({
                    'amount_n1': line_ebe.amount_n1,
                    'amount_n2': line_ebe.amount_n2,
                    'amount_n3': line_ebe.amount_n3,
                    'amount_n4': line_ebe.amount_n4,
                    'amount_n5': line_ebe.amount_n5,
                })

    def action_import_bfr(self):
        self.ensure_one()
        lines_bfr = self.line_ids.filtered(lambda m: m.type == '3')
        if self.bfr_id:
            bfr_historical_id = self.bfr_id.bfr_historical_ids.filtered(lambda m: m.type_bfr == '5')
            bfr_amount_n = bfr_historical_id.amount_n if bfr_historical_id else 0

            bfr_forecast_id = self.bfr_id.bfr_forecast_ids.filtered(lambda m: m.type_bfr == '5')

            amount_n1 = bfr_forecast_id.amount_n1 if bfr_forecast_id else 0
            amount_n2 = bfr_forecast_id.amount_n2 if bfr_forecast_id else 0
            amount_n3 = bfr_forecast_id.amount_n3 if bfr_forecast_id else 0
            amount_n4 = bfr_forecast_id.amount_n4 if bfr_forecast_id else 0
            amount_n5 = bfr_forecast_id.amount_n5 if bfr_forecast_id else 0
            if not lines_bfr:
                self.env['val.discouted.cash.flow.line'].create({
                    'type': '3',
                    'amount_n1': bfr_amount_n-amount_n1,
                    'amount_n2': amount_n1-amount_n2,
                    'amount_n3': amount_n2-amount_n3,
                    'amount_n4': amount_n3-amount_n4,
                    'amount_n5': amount_n4-amount_n5,
                    'val_id': self.id,
                })
            else:
                lines_bfr.update({
                    'amount_n1': bfr_amount_n-amount_n1,
                    'amount_n2': amount_n1-amount_n2,
                    'amount_n3': amount_n2-amount_n3,
                    'amount_n4': amount_n3-amount_n4,
                    'amount_n5': amount_n4-amount_n5,
                })

    def actio_calcul(self):
        self.ensure_one()
        line_ids = self.line_ids.filtered(lambda m: m.type in ('1', '2', '3'))
        amount_n1 = sum(line_ids.mapped('amount_n1'))
        amount_n2 = sum(line_ids.mapped('amount_n2'))
        amount_n3 = sum(line_ids.mapped('amount_n3'))
        amount_n4 = sum(line_ids.mapped('amount_n4'))
        amount_n5 = sum(line_ids.mapped('amount_n5'))

        self.env['val.discouted.cash.flow.line'].create({
            'type': '4',
            'amount_n1': amount_n1,
            'amount_n2': amount_n2,
            'amount_n3': amount_n3,
            'amount_n4': amount_n4,
            'amount_n5': amount_n5,
            'val_id': self.id,
        })
        tri = self.tri
        discounted_cf = self.env['val.discouted.cash.flow.line'].create({
            'type': '5',
            'amount_n1': amount_n1/((1+tri)**1),
            'amount_n2': amount_n2/((1+tri)**2),
            'amount_n3': amount_n3/((1+tri)**3),
            'amount_n4': amount_n4/((1+tri)**4),
            'amount_n5': amount_n5/((1+tri)**5),
            'val_id': self.id,
        })
        self.amount_ve = discounted_cf.amount_n1 + discounted_cf.amount_n2 + discounted_cf.amount_n3 + discounted_cf.amount_n4 + discounted_cf.amount_n5
        self.graph = create_stacked_chart(get_Data(line_ids))

class ValDCFLine(models.Model):
    _name = 'val.discouted.cash.flow.line'
    _description = "Valorisation d`entreprise par le Discouted Cash-Flow - Line"

    type = fields.Selection(TYPE_YEAR)
    amount_n1 = fields.Float(string="N+1")
    amount_n2 = fields.Float(string="N+2")
    amount_n3 = fields.Float(string="N+3")
    amount_n4 = fields.Float(string="N+4")
    amount_n5 = fields.Float(string="N+5")

    val_id = fields.Many2one('val.discouted.cash.flow')

    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    active = fields.Boolean(string="Active", default=True)


def get_Data(data):
    recordset = []
    for i in data:
        element = {
            'type': TYPE_YEAR[int(i.type) - 1][1],
            'amount_n1': i.amount_n1,
            'amount_n2': i.amount_n2,
            'amount_n3': i.amount_n3,
            'amount_n4': i.amount_n4,
            'amount_n5': i.amount_n5
        }
        recordset.append(element)
    return recordset


def create_stacked_chart(data):
    print(data)
    data_tmp_1 = list(data[0].values())[1:]
    data_tmp_2 = list(data[2].values())[1:]
    data_tmp_3 = list(data[3].values())[1:]
    data1 = data_tmp_1
    data2 = data_tmp_2
    data3 = data_tmp_3
    year = ["N+1", "N+2", "N+3", "N+4", "N+5"]
    x = np.arange(len(year))  # the label locations
    width = 0.25  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, data1, width, color="blue", label="EBE")
    rects2 = ax.bar(x + width, data2, width, color="orange", label="Variation BFR")
    rects3 = ax.bar(x + width * 2, data3, width, color="grey", label="Free Cash-Flow")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Montant')
    ax.set_title('Montant par année')
    ax.set_xticks(x + width, year)
    ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects3, padding=3)

    fig.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    buf.close()
    return imageBase64