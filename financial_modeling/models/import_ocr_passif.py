from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import io
import pdfplumber
import ocrmypdf
import re


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
                with pdfplumber.open(io.BytesIO(base64.b64decode(rec.file_import))) as pdf:
                    page = pdf.pages[0]
                    text = page.extract_text()
                    input_file = io.BytesIO(base64.b64decode(rec.file_import))
                    output = io.BytesIO()
                    output.seek(0)
                    ocrmypdf.ocr(input_file, output)
                    passif = self.env['import.ocr.passif.line'].search([('passif_id', '=', rec.id)])
                    print(passif)
                    passif.unlink()

                    with pdfplumber.open(output) as pdfPage:
                        pages = pdfPage.pages
                        for page in pages:
                            text = ""
                            text += page.extract_text()
                            lines = text.split('\n')
                            first_item = 9
                            for line in lines:
                                if "Désignation" in line:
                                    rec.company = line[len("Désignation de l'entreprise:"):]
                                if "Exercice clos" in line:
                                    rec.annee = line[len("Exercice clos"):]
                                if "CAPITAUX PROPRES" in line:
                                    first_item = lines.index(line)
                            sublines = lines[first_item:]

                            for line in sublines:
                                name = ''
                                montant_n = 0
                                montant_n1 = 0

                                try:
                                    rubrique = re.search('\d', str(line))
                                    try:
                                        if_rubrique = re.findall("\(1\)",line)
                                    except:
                                        if_rubrique = []
                                    if len(if_rubrique) > 0:
                                        name = line[:(rubrique.start() + 2)]
                                    else:
                                        name = line[:rubrique.start()]
                                    if len(line) > len(name):
                                        if '1)' in name:
                                            chiffre = line[(rubrique.start()+2):]
                                        else:
                                            chiffre = line[rubrique.start():]
                                        print(chiffre)
                                        if '_' in chiffre:
                                            montant_n, montant_n1 = chiffre.split('_')

                                            montant_n = re.sub("[^0-9]", "", montant_n, 0)
                                            montant_n1 = re.sub("[^0-9]", "", montant_n1, 0)
                                        elif '|' in chiffre:
                                            montant_n, montant_n1 = chiffre.split('|')

                                            montant_n = re.sub("[^0-9]", "", montant_n, 0)
                                            montant_n1 = re.sub("[^0-9]", "", montant_n1, 0)
                                        elif '-' in chiffre:
                                            montant_n, montant_n1 = chiffre.split('-')

                                            montant_n = re.sub("[^0-9]", "", montant_n, 0)
                                            montant_n1 = - float(re.sub("[^0-9]", "", montant_n1, 0))
                                        else:
                                            demi = int(len(chiffre) / 2)
                                            montant_n = re.sub("[^0-9]", "", chiffre[:demi], 0)
                                            montant_n1 = re.sub("[^0-9]", "", chiffre[demi:], 0)
                                except:
                                    name = line

                                try:
                                    montant = float(montant_n)
                                except:
                                    montant = 0

                                try:
                                    if type(montant_n1) == str:
                                        montant_1 = float(montant_n1)
                                    else:
                                        montant_1 = montant_n1
                                except:
                                    montant_1 = 0
                                rec.env['import.ocr.passif.line'].create({'passif_id': rec.id,
                                                                       'name': name,
                                                                       'montant_n': montant,
                                                                       'montant_n1': montant_1})
                            print(sublines)
                    output.close()
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


class ImportPassifOcrLine(models.Model):
    _name = "import.ocr.passif.line"
    _description = "Line de bilan passif importé"

    name = fields.Char(string="RUBRIQUES")
    rubrique = fields.Many2one('import.ocr.config', string='Rubriques confirmés', domain="[('type','=','passif')]")
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    passif_id = fields.Many2one('import.ocr.passif', string="Passif ID")
