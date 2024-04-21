
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import re
import json
import requests
import io
import PyPDF2
import base64
from PIL import Image

class ImportTcrOCR(models.Model):
    _name = 'import.ocr.tcr'
    _description = "Import Tcr Data by OCR Functionality"

    name = fields.Char(string="Réf")
    date = fields.Date(string="Date d'importation", default=datetime.today())
    annee = fields.Char(string="Année de l'exercice")
    company = fields.Char(string="Désignation de l'entreprise")
    tcr_lines = fields.One2many("import.ocr.tcr.line", "tcr_id", string="Lignes")
    file_import = fields.Binary(string="Import de fichier")
    file_import2 = fields.Binary(string="Import de fichier")
    file_import_name = fields.Char(string="Fichier")
    state = fields.Selection([("get_data", "Import données"),
                              ("validation", "Validation"),
                              ("valide", "Validé"),
                              ('modified', 'Modifié par le risque')], string="Etat", default="get_data")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.tcr.seq')
        return super(ImportTcrOCR, self).create(vals)

    def open_file(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.extract_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.file_import
            context['pdf_2'] = rec.file_import2
            context['tcr_id'] = rec.id
            wizard = self.env['extract.bilan.wizard'].create({'pdf_1': rec.file_import,
                                                              'pdf_2': rec.file_import2,})
            return {
                'name': 'TCR',
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
            if rec.file_import:
                pattern_alpha = r'^[a-zA-Z\séèàôâê\'-();,*+]+$'
                pattern_num = r'^[0-9\s]+$'
                credit = [1,2,3,4,5,6,7,8,9,10,11,30,33,34,40,41,44,45,49,50]
                debit = [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,31,32,35,36,37,38,39,42,43,46,47,48]
                if rec.tcr_lines:
                    rec.tcr_lines.unlink()
                first_credit = []
                second_credit = []
                first_debit = []
                second_debit = []
                first_moy_credit = []
                second_moy_credit = []
                first_moy_debit = []
                second_moy_debit = []
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
                        if bool(re.match(pattern_alpha, line['LineText'])) or line['LineText'] == 'IX-RESULTAT NET DE L\'EXERCICE' or  line['LineText'] =='IV-Excédent brut d\'exploitation':
                            rubrique = self.env['import.ocr.config'].search([('name', '=', line['LineText'])])
                            if rubrique:
                                rec.env['import.ocr.tcr.line'].create({'tcr_id': rec.id,
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
                            tcr = rec.tcr_lines.filtered(
                                lambda l: l.mintop - l.height <= line['MinTop'] <= l.mintop + l.height)
                            if tcr:
                                if len(tcr) > 1:
                                    tcr = rec.tcr_lines.filtered(
                                        lambda l: (l.mintop - (l.height-5)) <= line['MinTop'] <= (l.mintop + (l.height-5)) )
                                width = 0
                                for i in line['Words']:
                                    width += i['Width']
                                for val in same_line:
                                    if val['min_top'] == tcr.mintop:
                                        val['amounts'].append({'amount': int(line['LineText'].replace(' ', '')),
                                                               'left': line['Words'][0]['Left'],
                                                               'width': width})
                    count = 0
                    one_value_c = 0
                    one_value_d = 0
                    sum_height = 200
                    for line in same_line:
                        print(line)
                        if len(line['amounts']) == 2:
                            count += 1
                            if line['type'] in credit:
                                first_credit.append(line['amounts'][0]['left'])
                                second_credit.append(line['amounts'][1]['left'])
                            elif line['type'] in debit:
                                first_debit.append(line['amounts'][0]['left'])
                                second_debit.append(line['amounts'][1]['left'])
                        elif len(line['amounts']) == 1:
                            if line['type'] in credit:
                                one_value_c += 1
                                second_credit.append(line['amounts'][0]['left'])
                            elif line['type'] in debit:
                                one_value_d += 1
                                second_debit.append(line['amounts'][0]['left'])
                        for amount in line['amounts']:
                            if sum_height > amount['width']:
                                sum_height = amount['width']
                    first_credit.sort()
                    first_debit.sort()
                    second_credit.sort()
                    second_debit.sort()
                    try:
                        first_moy_credit = [first_credit[0], first_credit[-1] + sum_height] if one_value_c != 0 and len(first_credit) > 1 else []
                    except:
                        first_moy_credit = []
                    try:
                        second_moy_credit = [first_credit[-1] + sum_height, second_credit[-1] + sum_height] if one_value_c != 0 and len(second_debit) > 1 else []
                    except:
                        second_moy_credit = []
                    try:
                        first_moy_debit = [first_debit[0], first_debit[-1] + sum_height] if one_value_d != 0 and len(first_debit) > 1 else []
                    except:
                        first_moy_debit = []
                    try:
                        second_moy_debit = [first_debit[-1] + sum_height, second_debit[-1] + sum_height] if one_value_d and len(second_debit) > 1 else []
                    except:
                        second_moy_debit = []
                    for line in same_line:
                        tcr = rec.tcr_lines.filtered(lambda l: l.mintop == line['min_top'])
                        if len(line['amounts']) == 2:
                            tcr.montant_n = line['amounts'][0]['amount']
                            tcr.montant_n1 = line['amounts'][1]['amount']
                        else:
                            if line['type'] in credit:
                                assign_amounts(tcr, line['amounts'], [first_moy_credit, second_moy_credit])
                            elif line['type'] in debit:
                                assign_amounts(tcr, line['amounts'], [first_moy_debit, second_moy_debit])

                if rec.file_import2:
                    data = str(rec.file_import2)
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
                        print(line['LineText'])
                        if bool(re.match(pattern_alpha, line['LineText'])) or line['LineText'] == 'IX-RESULTAT NET DE L\'EXERCICE' or  line['LineText'] =='IV-Excédent brut d\'exploitation':

                            rubrique = self.env['import.ocr.config'].search([('name', '=', line['LineText'])])
                            if rubrique:
                                rec.env['import.ocr.tcr.line'].create({'tcr_id': rec.id,
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
                            tcr = rec.tcr_lines.filtered(
                                lambda l: l.mintop - l.height <= line['MinTop'] <= l.mintop + l.height)
                            if tcr:
                                tcr = tcr[0]
                                width = 0
                                for i in line['Words']:
                                    width += i['Width']
                                for val in same_line:
                                    if val['min_top'] == tcr.mintop:
                                        val['amounts'].append({'amount': int(line['LineText'].replace(' ', '')),
                                                               'left': line['Words'][0]['Left'],
                                                               'width': width})
                    count = 0
                    one_value_c = 0
                    one_value_d = 0
                    sum_height = 200
                    for line in same_line:
                        print(line)
                        if len(line['amounts']) == 2:
                            count += 1
                            if line['type'] in credit:
                                first_credit.append(line['amounts'][0]['left'])
                                second_credit.append(line['amounts'][1]['left'])
                            elif line['type'] in debit:
                                first_debit.append(line['amounts'][0]['left'])
                                second_debit.append(line['amounts'][1]['left'])
                        elif len(line['amounts']) == 1:
                            if line['type'] in credit:
                                one_value_c += 1
                                second_credit.append(line['amounts'][0]['left'])
                            elif line['type'] in debit:
                                one_value_d += 1
                                second_debit.append(line['amounts'][0]['left'])
                        for amount in line['amounts']:
                            if sum_height > amount['width']:
                                sum_height = amount['width']
                    print(sum_height)
                    first_credit.sort()
                    first_debit.sort()
                    second_credit.sort()
                    second_debit.sort()
                    print(first_debit)
                    print(second_debit)
                    print(first_credit)
                    print(second_credit)
                    print(one_value_c != 0 and len(first_credit) > 1)
                    try:
                        first_moy_credit = [first_credit[0], first_credit[-1] + sum_height] if one_value_c != 0 and len(first_credit) > 1 else []
                    except:
                        first_moy_credit = [first_credit[0], first_credit[0] + sum_height]
                    try:
                        second_moy_credit = [first_credit[-1] + sum_height, second_credit[-1] + sum_height] if one_value_c != 0 and len(second_debit) > 1 else []
                    except:
                        second_moy_credit = [first_credit[0] + sum_height, second_credit[0] + sum_height]
                    try:
                        first_moy_debit = [first_debit[0], first_debit[-1] + sum_height] if one_value_d != 0 and len(first_debit) > 1 else []
                    except:
                        first_moy_debit = [first_debit[0], first_debit[0] + sum_height]
                    try:
                        second_moy_debit = [first_debit[-1] + sum_height, second_debit[-1] + sum_height] if one_value_d and len(second_debit) > 1 else []
                    except:
                        second_moy_debit = [first_debit[0] + sum_height, second_debit[0] + sum_height]
                    for line in same_line:
                        tcr = rec.tcr_lines.filtered(lambda l: l.mintop == line['min_top'])
                        if len(line['amounts']) == 2:
                            tcr.montant_n = line['amounts'][0]['amount']
                            tcr.montant_n1 = line['amounts'][1]['amount']
                        else:
                            if line['type'] in credit:
                                assign_amounts(tcr, line['amounts'], [first_moy_credit, second_moy_credit])
                            elif line['type'] in debit:
                                assign_amounts(tcr, line['amounts'], [first_moy_debit, second_moy_debit])

                rec.state = "validation"
                for line in rec.tcr_lines:
                    line.montant_n = line.montant_n / 1000
                    line.montant_n1 = line.montant_n1 / 1000

    def action_validation(self):
        for rec in self:
            list_validation = [7, 12, 13, 14, 33, 50, 42]
            tcr = rec.tcr_lines.filtered(lambda r: r.rubrique.sequence in list_validation)
            if len(tcr) != 7:
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n "
                                      "- Chiffre d'affaires net des rabais, Remises, Ristournes \n"
                                      "- Achats de marchandises vendues \n"
                                      "- Matières premieres \n"
                                      "- Autres approvisionnements \n"
                                      "- Excédent brut de l'exploitation \n"
                                      "- Charges financières \n"
                                      "- Résultat  net de l'exercice")
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['tcr_id'] = rec.id
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
            context['tcr_id'] = rec.id
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


class ImportTcrOcrLine(models.Model):
    _name = "import.ocr.tcr.line"
    _description = "Line de tcr importé"

    name = fields.Char(string="RUBRIQUES")
    mintop = fields.Integer(string='Rang')
    height = fields.Integer(string='Height')
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    rubrique = fields.Many2one('import.ocr.config', string='Rubriques confirmés', domain="[('type','=','tcr')]")
    tcr_id = fields.Many2one('import.ocr.tcr', string="TCR ID")


class ConfigRubrique(models.Model):
    _name = 'import.ocr.config'
    _description = 'Liste des rubriques'

    name = fields.Char(string='rubrique')
    type = fields.Selection([('tcr', 'TCR'),
                             ('actif', 'Actif'),
                             ('passif', 'Passif')], string='Type')
    sequence = fields.Integer(string="Sequence")

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


def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')


def pdf_page_to_base64(pdf_bytes, page_number):
    pdf_file = io.BytesIO(pdf_bytes)
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    page = pdf_reader.getPage(page_number)
    page_content = page.extractText()  # Obtenez le contenu de la page si nécessaire
    # Convertir la page PDF en image (vous pouvez utiliser n'importe quelle bibliothèque pour cela)
    # Ici, nous utilisons PyMuPDF
    pdf_image = page.render()
    image = Image.open(io.BytesIO(pdf_image))
    # Convertir l'image en base64
    return image_to_base64(image.tobytes())