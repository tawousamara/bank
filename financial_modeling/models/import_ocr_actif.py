import base64
import io
import pandas as pd
from odoo import models, fields, api, _

import json
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
import re
import requests

class ImportActifOCR(models.Model):
    _name = "import.ocr.actif"
    _description = "Import Bilan Actif Data by OCR Functionality"

    name = fields.Char(string="Réf")
    date = fields.Date(string="Date d'importation", default=datetime.today())
    annee = fields.Char(string="Année de l'exercice")
    company = fields.Char(string="Désignation de l'entreprise")
    actif_lines = fields.One2many("import.ocr.actif.line", "actif_id", string="Lignes", domain=lambda self: self._get_domain())
    file_import = fields.Binary(string="Import de fichier")
    file_import_name = fields.Char(string="Fichier")
    hide_others = fields.Boolean(string="Filter que les lignes concernées")
    state = fields.Selection([("get_data", "Import données"),
                              ("validation", "Validation"),
                              ("valide", "Validé"),
                              ('modified', 'Modifié par le risque')], string="Etat", default="get_data")

    def _get_domain(self):
        if self.hide_others:
            return [('sequence', 'in', [4, 7, 16, 27, 18, 19, 20, 24, 26])]
        else:
            []

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.actif.seq')
        return super(ImportActifOCR, self).create(vals)

    def process_import_actif_file(self, col):
        actif_lines = []
        print("Processing import TCR OCR")
        try:
            # Decode the file and read the Excel data
            file_content = base64.b64decode(self.file_import)
            excel_file = io.BytesIO(file_content)
            df = pd.read_excel(excel_file, header=0)
            df.columns = df.columns.str.strip()
            print("DataFrame head:")
            print(df.head())
            print("DataFrame info:")
            print(df.info())
            column_idx = ord(col.upper()) - ord('A')
            if column_idx >= len(df.columns):
                raise UserError(f"Column {col} is out of range in the file.")
            montant_n_col = df.iloc[:, column_idx]
            montant_n1_col = None
            if col.upper() != 'E':
                montant_n1_col = df.iloc[:, column_idx + 1]
            sequences = [4, 7, 16, 18, 20, 19, 24, 26, 27]
            for position, (row, sequence) in enumerate(zip(df.iloc[11:20].iterrows(), sequences)):
                name = row[1].iloc[0]
                montant_n = montant_n_col.iloc[position + 11]
                montant_n1 = None
                if montant_n1_col is not None:
                    montant_n1 = montant_n1_col.iloc[position + 11]
                print(f"Row: {row[1].to_dict()}, Montant (N): {montant_n}")
                if montant_n1 is not None:
                    print(f"Montant (N-1): {montant_n1}")
                if pd.isna(montant_n):
                    montant_n = 0
                    print("Montant (N) was NaN, set to 0.")
                if montant_n1 is not None and pd.isna(montant_n1):
                    montant_n1 = 0
                    print("Montant (N-1) was NaN, set to 0.")
                if isinstance(montant_n, float):
                    montant_n = int(montant_n)
                    print(f"Converted montant_n to integer: {montant_n}")
                if montant_n1 is not None and isinstance(montant_n1, float):
                    montant_n1 = int(montant_n1)
                    print(f"Converted montant_n1 to integer: {montant_n1}")
                rubrique_vals = {
                    'name': name,
                    'type': 'actif',
                    'sequence': sequence
                }
                rubrique = self.env['import.ocr.config'].create(rubrique_vals)
                actif_line_vals = {
                    'name': name,
                    'montant_n': montant_n,
                    'actif_id': self.id,
                    'rubrique': rubrique.id
                }
                if montant_n1 is not None:
                    actif_line_vals['montant_n1'] = montant_n1
                new_line = self.env['import.ocr.actif.line'].create(actif_line_vals)
                actif_lines.append(new_line)
            self.actif_lines = [(6, 0, [line.id for line in actif_lines])]
        except Exception as e:
            print(f"Error processing file: {e}")


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
                if test_file.status_code == 200:
                    json_loads = json.loads(json_dumps)
                    if not json_loads['IsErroredOnProcessing']:
                        lines = json_loads['ParsedResults'][0]['TextOverlay']['Lines']
                        lines = group_words_by_line(lines)
                        list_tcr = self.env['import.ocr.config'].search([('type', '=', 'actif')])
                        for line in lines:
                            print(line)
                            rubrique = self.env['import.ocr.config'].search(
                                [('name', '=', line['Words'][0]['WordText'])])
                            value_text = line['Words'][0]['WordText']
                            if not rubrique:
                                value_text = value_text.replace(';', '')
                                value_text = value_text.replace(',', '')
                                value_text = value_text.replace('-', '')
                                for i in list_tcr:
                                    val = i.name
                                    val = val.replace(';', '')
                                    val = val.replace(',', '')
                                    val = val.replace('-', '')
                                    if value_text == val:
                                        print(value_text == val)
                            if rubrique:
                                value = rec.env['import.ocr.actif.line'].create({'actif_id': rec.id,
                                                                                  'name': line['Words'][0]['WordText'],
                                                                                  'rubrique': rubrique.id,
                                                                                  })
                                if len(line['Words']) == 5:
                                    try:
                                        value.write(
                                            {'montant_n': int(re.sub(r'[^0-9]', '', line['Words'][4]['WordText']))})
                                    except:
                                        value.write({'montant_n': 0})
                                    try:
                                        value.write(
                                            {'montant_n1': int(re.sub(r'[^0-9]', '', line['Words'][3]['WordText']))})
                                    except:
                                        value.write({'montant_n1': 0})
                                    try:
                                        value.write(
                                            {'montant_2n': int(re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))})
                                    except:
                                        value.write({'montant_2n': 0})
                                    try:
                                        value.write(
                                            {'montant_1n': int(re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                    except:
                                        value.write({'montant_1n': 0})
                                elif len(line['Words']) == 4:
                                    montant_1 = int(re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))
                                    montant_2 = int(re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))
                                    montant1_1 = int(re.sub(r'[^0-9]', '', line['Words'][1]['WordText'])) / 1000
                                    montant1_2 = int(re.sub(r'[^0-9]', '', line['Words'][2]['WordText'])) / 1000
                                    print('montant_1', montant_1)
                                    print('montant_2', montant_2)
                                    print('montant1_2', montant1_2)
                                    print('montant1_1', montant1_1)
                                    if (montant_1 == montant_2) or (int(montant1_1) == int(montant1_2)):
                                        try:
                                            value.write(
                                                {'montant_n1': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][3]['WordText']))})
                                        except:
                                            value.write({'montant_n1': 0})
                                        try:
                                            value.write(
                                                {'montant_n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))})
                                        except:
                                            value.write({'montant_n': 0})
                                        try:
                                            value.write(
                                                {'montant_1n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                        except:
                                            value.write({'montant_1n': 0})
                                    else:
                                        try:
                                            value.write(
                                                {'montant_n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][3]['WordText']))})
                                        except:
                                            value.write({'montant_n': 0})
                                        try:
                                            value.write(
                                                {'montant_2n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))})
                                        except:
                                            value.write({'montant_2n': 0})
                                        try:
                                            value.write(
                                                {'montant_1n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                        except:
                                            value.write({'montant_1n': 0})

                                elif len(line['Words']) == 3:
                                    separator = line['Words'][2]['Left'] - line['Words'][0]['Left']
                                    if separator > 700:
                                        try:
                                            value.write(
                                                {'montant_n1': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))})
                                        except:
                                            value.write({'montant_n1': 0})
                                        try:
                                            value.write(
                                                {'montant_n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                        except:
                                            value.write({'montant_n': 0})
                                    else:
                                        try:
                                            value.write(
                                                {'montant_n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][2]['WordText']))})
                                        except:
                                            value.write({'montant_n': 0})
                                        try:
                                            value.write(
                                                {'montant_1n': int(
                                                    re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                        except:
                                            value.write({'montant_1n': 0})
                                else:
                                    try:
                                        value.write(
                                            {'montant_n': int(re.sub(r'[^0-9]', '', line['Words'][1]['WordText']))})
                                    except:
                                        value.write({'montant_n': 0})
                        rec.state = "validation"
                        for line in rec.actif_lines:
                            line.montant_n = line.montant_n / 1000
                            line.montant_n1 = line.montant_n1 / 1000
                            line.montant_2n = line.montant_2n / 1000
                            line.montant_1n = line.montant_1n / 1000
                    else:
                        raise UserError(
                            'Vous devriez verifier la qualité, le nombre et la taille du fichier \n Le fichier ne doit pas dépasser 1024KB. \n Le fichier doit contenir une seule page.')
                else:
                    raise UserError('Un probleme est survenu, vous devriez réessayer ulterieurement.')

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
    sequence = fields.Integer(related='rubrique.sequence')
    montant_1n = fields.Float(string="Montants Bruts")
    montant_2n = fields.Float(string="Amortissements provisions et pertes de valeurs")
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    actif_id = fields.Many2one('import.ocr.actif', string="Actif ID")
    hide_others = fields.Boolean(string="Filter que les lignes concernées", compute='compute_hide', store=True)

    @api.depends('actif_id')
    def compute_hide(self):
        for rec in self:
            if rec.actif_id.hide_others and rec.rubrique.sequence not in [4, 7, 16, 27, 18, 19, 20, 24, 26]:
                rec.hide_others = True
            else:
                rec.hide_others = False


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

def group_words_by_line(json_data):
    # Trier les mots par leur position verticale (Top)
    sorted_words = sorted(json_data, key=lambda x: x['MinTop'])

    lines = []
    current_line = {'LineText': '', 'Words': []}
    previous_top = None
    previous_max_height = None

    for item in sorted_words:
        top = item['MinTop']
        max_height = item['MaxHeight']
        word_text = item['LineText']
        left = item['Words'][0]['Left']  # Get the Left position of the first word in this line

        if previous_top is None:
            current_line['LineText'] = word_text
            current_line['Words'].append({'WordText': word_text, 'Left': left})
            previous_top = top
            previous_max_height = max_height
        elif top >= previous_top and top <= (previous_top + previous_max_height):
            # Vérifier si le mot contient des caractères alphabétiques
            if any(c.isalpha() for c in word_text):
                # Vérifier si d'autres mots alphabétiques sont déjà présents dans la ligne
                if any(any(c.isalpha() for c in word['WordText']) for word in current_line['Words']):
                    lines.append(current_line)
                    current_line = {'LineText': word_text, 'Words': [{'WordText': word_text, 'Left': left}]}
                    previous_top = top
                    previous_max_height = max_height
                else:
                    current_line['LineText'] += " " + word_text
                    current_line['Words'].append({'WordText': word_text, 'Left': left})
                    previous_max_height = max(previous_max_height, max_height)
            else:
                current_line['LineText'] += " " + word_text
                current_line['Words'].append({'WordText': word_text, 'Left': left})
                previous_max_height = max(previous_max_height, max_height)
        else:
            # Trier les mots de la ligne par leur position horizontale (Left)
            current_line['Words'] = sorted(current_line['Words'], key=lambda x: x['Left'])
            lines.append(current_line)
            current_line = {'LineText': word_text, 'Words': [{'WordText': word_text, 'Left': left}]}
            previous_top = top
            previous_max_height = max_height

    current_line['Words'] = sorted(current_line['Words'], key=lambda x: x['Left'])
    lines.append(current_line)  # Ajouter la dernière ligne
    for line in lines:
        line['Words'] = sorted(line['Words'], key=lambda x: x['Left'])

    return lines




