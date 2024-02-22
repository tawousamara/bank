
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import io
import pdfplumber
import ocrmypdf
import re


class ImportTcrOCR(models.Model):
    _name = 'import.ocr.tcr'
    _description = "Import Tcr Data by OCR Functionality"

    name = fields.Char(string="Réf")
    date = fields.Date(string="Date d'importation", default=datetime.today())
    annee = fields.Char(string="Année de l'exercice")
    company = fields.Char(string="Désignation de l'entreprise")
    tcr_lines = fields.One2many("import.ocr.tcr.line", "tcr_id", string="Lignes")
    file_import = fields.Binary(string="Import de fichier")
    file_import_name = fields.Char(string="Fichier")
    state = fields.Selection([("get_data", "Import données"),
                              ("validation", "Validation"),
                              ("valide", "Validé")], string="Etat", default="get_data")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.tcr.seq')
        return super(ImportTcrOCR, self).create(vals)

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
                    tcr = self.env['import.ocr.tcr.line'].search([('tcr_id', '=', rec.id)])
                    print(tcr)
                    tcr.unlink()

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
                                if "Exercice du" in line:
                                    rec.annee = line[len("Exercice du"):]
                                if "Ventes de marchandises" in line:
                                    first_item = lines.index(line)
                                if "brut" in line or "produits opérationnels" in line:
                                    first_item = lines.index(line)
                            sublines = lines[first_item:]

                            for line in sublines:

                                montant_n = 0
                                montant_n1 = 0

                                try:
                                    rubrique = re.search('\d', str(line))
                                    name = line[:rubrique.start()]

                                    if len(line) > len(name):
                                        chiffre = line[rubrique.start():]
                                        if '_' in chiffre:
                                            montant_n, montant_n1 = chiffre.split('_')
                                            print(montant_n)
                                            montant_n = montant_n.replace(' ', '')
                                            montant_n1 = montant_n1.replace(' ', '')
                                        elif '|' in chiffre:
                                            montant_n, montant_n1 = chiffre.split('|')
                                            print(montant_n)
                                            montant_n = montant_n.replace(' ', '')
                                            montant_n1 = montant_n1.replace(' ', '')
                                        else:
                                            demi = int(len(chiffre) / 2)
                                            montant_n = chiffre[:demi].replace(' ', '')
                                            montant_n1 = chiffre[demi:].replace(' ', '')
                                except:
                                    name = line

                                try:
                                    montant = float(montant_n)
                                except:
                                    montant = 0

                                try:
                                    montant_1 = float(montant_n1)
                                except:
                                    montant_1 = 0
                                rec.env['import.ocr.tcr.line'].create({'tcr_id': rec.id,
                                                                       'name': name,
                                                                       'montant_n': montant,
                                                                       'montant_n1': montant_1})
                            print(sublines)
                    output.close()
                    rec.state = "validation"
                # old code is in read pdf.txt
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
