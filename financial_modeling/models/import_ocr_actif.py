
from odoo import models, fields, api, _

import json
from datetime import datetime
from odoo.exceptions import ValidationError
import re
import requests

class ImportActifOCR(models.Model):
    _name = "import.ocr.actif"
    _description = "Import Bilan Actif Data by OCR Functionality"

    name = fields.Char(string="Réf")
    date = fields.Date(string="Date d'importation", default=datetime.today())
    annee = fields.Char(string="Année de l'exercice")
    company = fields.Char(string="Désignation de l'entreprise")
    actif_lines = fields.One2many("import.ocr.actif.line", "actif_id", string="Lignes")
    file_import = fields.Binary(string="Import de fichier")
    file_import_name = fields.Char(string="Fichier")
    state = fields.Selection([("get_data", "Import données"),
                              ("validation", "Validation"),
                              ("valide", "Validé"),
                              ('modified', 'Modifié par le risque')], string="Etat", default="get_data")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.actif.seq')
        return super(ImportActifOCR, self).create(vals)

    def open_file(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.extract_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.file_import
            context['actif_id'] = rec.id
            wizard = self.env['extract.bilan.wizard'].create({'pdf_1': rec.file_import})
            return {
                'name': 'Actif',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'extract.bilan.wizard',
                'res_id': wizard.id,
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }

    def extract_data(self):
        for rec in self:
            pattern_alpha = r'^[a-zA-Z\séèàôâê\'-]+$'
            pattern_num = r'^[0-9\s]+$'
            if rec.actif_lines:
                rec.actif_lines.unlink()
            if rec.file_import:
                data = str(rec.file_import)
                data = data.replace("b'", '\n')
                data = data.replace("'", '')
                data = data.replace('\r\n', '\n')  # Replace Windows-style newline with Unix-style
                data = data.replace('\r', '\n')
                data = 'data:application/pdf;base64,' + data
                test_file = ocr_space_file(filename=data, api_key='K82274210888957', language='fre',
                                       isTable=True)
                json_dumps = test_file.content.decode()
                json_loads = json.loads(json_dumps)
                lines = json_loads['ParsedResults'][0]['TextOverlay']['Lines']
                same_line = []
                for line in lines:
                    if bool(re.match(pattern_alpha, line['LineText'])):
                        rubrique = self.env['import.ocr.config'].search([('name', '=', line['LineText'])])
                        if rubrique:
                            rec.env['import.ocr.actif.line'].create({'actif_id': rec.id,
                                                                 'name': line['LineText'],
                                                                 'rubrique': rubrique.id,
                                                                 'mintop': line['MinTop'],
                                                                 'height': line['MaxHeight'],
                                                                 'montant_1n': 0,
                                                                 'montant_2n': 0,
                                                                 'montant_n': 0,
                                                                 'montant_n1': 0})
                            dicty = {'min_top':line['MinTop'],
                                     'amounts': []}
                            same_line.append(dicty)
                    elif bool(re.match(pattern_num, line['LineText'])):
                        if line['MinTop'] == 389:
                            print(line['LineText'])
                        actif = rec.actif_lines.filtered(lambda l: l.mintop - l.height <= line['MinTop'] <= l.mintop + l.height)
                        if actif:
                            width = 0
                            for i in line['Words']:
                                width += i['Width']
                            for val in same_line:
                                if val['min_top'] == actif[0].mintop:
                                    val['amounts'].append({'amount': int(line['LineText'].replace(' ', '')),
                                                           'left': line['Words'][0]['Left'],
                                                           'width': width})
                count = 0
                first = []
                second = []
                third = []
                forth = []
                sum_height = 200
                for line in same_line:
                    print(line)
                    if len(line['amounts']) == 4:
                        count += 1
                        first.append(line['amounts'][0]['left'])
                        second.append(line['amounts'][1]['left'])
                        third.append(line['amounts'][2]['left'])
                        forth.append(line['amounts'][3]['left'])

                    for amount in line['amounts']:
                        if sum_height > amount['width']:
                            sum_height = amount['width']
                first.sort()
                second.sort()
                third.sort()
                forth.sort()
                first_moy = [first[0], first[-1] + sum_height]
                second_moy = [first[-1] + sum_height, second[-1]+sum_height]
                third_moy = [second[-1] + sum_height, third[-1]+sum_height]
                forth_moy = [third[-1] + sum_height, forth[-1]+sum_height]
                for line in same_line:
                    actif = rec.actif_lines.filtered(lambda l: l.mintop == line['min_top'])

                    if len(line['amounts']) == 4:
                        actif.montant_1n = line['amounts'][0]['amount']
                        actif.montant_2n = line['amounts'][1]['amount']
                        actif.montant_n = line['amounts'][2]['amount']
                        actif.montant_n1 = line['amounts'][3]['amount']

                    else:
                        assign_amounts(actif, line['amounts'], [first_moy, second_moy, third_moy, forth_moy])
                rec.state = "validation"
                for line in rec.actif_lines:
                    line.montant_n = line.montant_n / 1000
                    line.montant_n1 = line.montant_n1 / 1000
                    line.montant_1n = line.montant_1n / 1000
                    line.montant_2n = line.montant_2n / 1000

    def action_validation(self):
        for rec in self:
            list_validation = [4, 7, 16, 27, 18, 19, 24, 26, 20]
            actifs = rec.actif_lines.filtered(lambda r: r.rubrique.sequence in list_validation).mapped('rubrique.sequence')
            print(actifs)
            if not set(list_validation).issubset(set(actifs)):
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n"
                                      "- Trésorerie \n"
                                      "- Stock \n"
                                      "- Clients \n")
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['actif_id'] = rec.id
            context['state'] = 'valide'

            if not self._context.get('warning'):
                return {
                    'name': 'Validation',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.ocr.wizard',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': context,
                }

    def action_annulation(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['actif_id'] = rec.id
            context['state'] = 'validation'
            print(context)
            if not self._context.get('warning'):
                return {
                    'name': 'Annulation',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.ocr.wizard',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': context,
                }


class ImportActifOcrLine(models.Model):
    _name = "import.ocr.actif.line"
    _description = "Line de bilan actif importé"

    name = fields.Char(string="RUBRIQUES")
    mintop = fields.Integer(string='Rang')
    height = fields.Integer(string='Height')
    rubrique = fields.Many2one('import.ocr.config', string='Rubriques confirmés', domain="[('type','=','actif')]")
    montant_1n = fields.Float(string="Montants Bruts")
    montant_2n = fields.Float(string="Amortissements provisions et pertes de valeurs")
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    actif_id = fields.Many2one('import.ocr.actif', string="Actif ID")


def ocr_space_file(filename, overlay=False, api_key='helloworld', language='eng',isTable=False):
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'base64Image': filename,
               'isTable': isTable,
               'OCREngine': 2
               }
    print('called')
    r = requests.post('https://api.ocr.space/parse/image',
                          data=payload,
                          )
    return r


def assign_amounts(actif, amounts, intervals):
    for amount in amounts:
        if intervals[0][0] <= amount['left'] <= intervals[0][-1]:
            actif.montant_1n = amount['amount']
        elif intervals[1][0] <= amount['left'] <= intervals[1][-1]:
            actif.montant_2n = amount['amount']
        elif intervals[2][0] <= amount['left'] <= intervals[2][-1]:
            actif.montant_n = amount['amount']
        elif intervals[3][0] <= amount['left'] <= intervals[3][-1]:
            actif.montant_n1 = amount['amount']
        else:
            if intervals[0][0] <= amount['left'] + amount['width'] <= intervals[0][-1]:
                actif.montant_1n = amount['amount']
            elif intervals[1][0] <= amount['left']+amount['width'] <= intervals[1][-1]:
                actif.montant_2n = amount['amount']
            elif intervals[2][0] <= amount['left']+amount['width'] <= intervals[2][-1]:
                actif.montant_n = amount['amount']
            elif intervals[3][0] <= amount['left']+amount['width'] <= intervals[3][-1]:
                actif.montant_n1 = amount['amount']
            else:
                if intervals[0][0] <= amount['left'] - amount['width'] <= intervals[0][-1]:
                    actif.montant_1n = amount['amount']
                elif intervals[1][0] <= amount['left'] - amount['width'] <= intervals[1][-1]:
                    actif.montant_2n = amount['amount']
                elif intervals[2][0] <= amount['left'] - amount['width'] <= intervals[2][-1]:
                    actif.montant_n = amount['amount']
                elif intervals[3][0] <= amount['left'] - amount['width'] <= intervals[3][-1]:
                    actif.montant_n1 = amount['amount']





