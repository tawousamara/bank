from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import io
import pdfplumber
import ocrmypdf
import re
import json
import requests

class ImportPassifOCR(models.Model):
    _name = "import.ocr.passif"
    _description = "Import Bilan Passif Data by OCR Functionality"

    name = fields.Char(string="Réf")
    date = fields.Date(string="Date d'importation", default=datetime.today())
    annee = fields.Char(string="Année de l'exercice")
    company = fields.Char(string="Désignation de l'entreprise")
    passif_lines = fields.One2many("import.ocr.passif.line", "passif_id", string="Lignes")
    file_import = fields.Binary(string="Import de fichier")
    file_import_name = fields.Char(string="Fichier")
    state = fields.Selection([("get_data", "Import données"),
                              ("validation", "Validation"),
                              ("valide", "Validé")], string="Etat", default="get_data")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.passif.seq')
        return super(ImportPassifOCR, self).create(vals)

    def extract_data(self):
        for rec in self:
            if rec.file_import:
                pattern_alpha = r'^[a-zA-Z\séèàôâê\'();,*+-1]+$'
                pattern_num = r'^[0-9\s()\-]+$'
                if rec.passif_lines:
                    rec.passif_lines.unlink()
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
                    if line['LineText'] == 'TOTAL IIII':
                        line['LineText'] = 'TOTAL III'
                    if line['LineText'] == 'TOTAL GENERAL PASSIF (I+||+III)':
                        line['LineText'] = 'TOTAL GENERAL PASSIF (I+II+III)'
                    print(line['LineText'])
                    if bool(re.match(pattern_alpha, line['LineText'])):
                        rubrique = self.env['import.ocr.config'].search([('name', '=', line['LineText'])])
                        if rubrique:
                            rec.env['import.ocr.passif.line'].create({'passif_id': rec.id,
                                                                   'name': line['LineText'],
                                                                   'rubrique': rubrique.id,
                                                                   'mintop': line['MinTop'],
                                                                   'height': line['MaxHeight'],
                                                                   'montant_n': 0,
                                                                   'montant_n1': 0})
                            dicty = {'min_top': line['MinTop'],
                                     'type': rubrique.sequence,
                                     'amounts': []}
                            same_line.append(dicty)
                    elif bool(re.match(pattern_num, line['LineText'])):
                        line['LineText'] = line['LineText'].replace('(', '')
                        line['LineText'] = line['LineText'].replace(')', '')
                        passif = rec.passif_lines.filtered(
                            lambda l: l.mintop - l.height <= line['MinTop'] <= l.mintop + l.height)
                        if passif:
                            passif = passif[0]
                            width = 0
                            for i in line['Words']:
                                width += i['Width']
                            for val in same_line:
                                if val['min_top'] == passif.mintop:
                                    if '-' in line['LineText']:
                                        line['LineText'] = line['LineText'].replace('-', '')
                                        val['amounts'].append({'amount': - int(line['LineText'].replace(' ', '')),
                                                           'left': line['Words'][0]['Left'],
                                                           'width': width})
                                    else:
                                        val['amounts'].append({'amount': int(line['LineText'].replace(' ', '')),
                                                               'left': line['Words'][0]['Left'],
                                                               'width': width})
                count = 0
                first = []
                second = []
                sum_height = 200
                for line in same_line:
                    print(line)
                    if len(line['amounts']) == 2:
                        count += 1
                        first.append(line['amounts'][0]['left'])
                        second.append(line['amounts'][1]['left'])
                    elif len(line['amounts']) == 1:
                            second.append(line['amounts'][0]['left'])
                    for amount in line['amounts']:
                        if sum_height > amount['width']:
                            sum_height = amount['width']
                print(sum_height)
                first.sort()
                second.sort()

                first_moy = [first[0], first[-1] + sum_height]
                second_moy = [first[-1] + sum_height, second[-1] + sum_height]
                for line in same_line:
                    passif = rec.passif_lines.filtered(lambda l: l.mintop == line['min_top'])
                    if len(line['amounts']) == 2:
                        passif.montant_n = line['amounts'][0]['amount']
                        passif.montant_n1 = line['amounts'][1]['amount']
                    else:
                        assign_amounts(passif, line['amounts'], [first_moy, second_moy])

            rec.state = "validation"
            for line in rec.passif_lines:
                line.montant_n = line.montant_n / 1000
                line.montant_n1 = line.montant_n1 / 1000
                    
    def action_validation(self):
        for rec in self:
            list_validation = [12, 14, 20, 23, 24, 25]
            passifs = rec.passif_lines.filtered(lambda r: r.rubrique.sequence in list_validation)
            if len(passifs) != 6:
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n"
                                      "- Total I \n"
                                      "- Emprunts et dettes financières \n"
                                      "- Fournisseurs et comptes rattachés \n"
                                      "- Trésorerie passifs \n"
                                      "- Total III \n"
                                      "- Total General Passif (I+II+III)")
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['passif_id'] = rec.id
            context['state'] = 'valide'
            print(context)
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
            context['passif_id'] = rec.id
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
def ocr_space_file(filename, overlay=True, api_key='helloworld', language='eng',isTable=False):
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

class ImportPassifOcrLine(models.Model):
    _name = "import.ocr.passif.line"
    _description = "Line de bilan passif importé"

    name = fields.Char(string="RUBRIQUES")
    mintop = fields.Integer(string='Rang')
    height = fields.Integer(string='Height')
    rubrique = fields.Many2one('import.ocr.config', string='Rubriques confirmés', domain="[('type','=','passif')]")
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    passif_id = fields.Many2one('import.ocr.passif', string="Passif ID")

def assign_amounts(actif, amounts, intervals):
    for amount in amounts:
        if intervals[0][0] <= amount['left'] <= intervals[0][-1]:
            actif.montant_n = amount['amount']
        elif intervals[1][0] <= amount['left'] <= intervals[1][-1]:
            actif.montant_n1 = amount['amount']
        else:
            if intervals[0][0] <= amount['left'] - amount['left'] <= intervals[0][-1]:
                actif.montant_n = amount['amount']
            elif intervals[1][0] <= amount['left'] - amount['left'] <= intervals[1][-1]:
                actif.montant_n1 = amount['amount']
