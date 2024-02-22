
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import io
import pdfplumber
import ocrmypdf
import re


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
                              ("valide", "Validé")], string="Etat", default="get_data")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('import.ocr.actif.seq')
        return super(ImportActifOCR, self).create(vals)

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
                    actif = self.env['import.ocr.actif.line'].search([('actif_id', '=', rec.id)])
                    print(actif)
                    actif.unlink()

                    with pdfplumber.open(output) as pdfPage:
                        pages = pdfPage.pages
                        for page in pages:
                            text = ""
                            text += page.extract_text()
                            lines = text.split('\n')

                            first_item = 13
                            last_item = len(lines) - 1
                            for line in lines:
                                if "Désignation" in line:
                                    rec.company = line[len("Désignation de l'entreprise:"):]
                                if "Exercice" in line:
                                    rec.annee = line[len("Exercice clos"):]
                                if "ACTIFS NON COURANTS" in line:
                                    first_item = lines.index(line)
                                if "TOTAL GENERAL ACTIF" in line:
                                    last_item = lines.index(line) + 1
                            sublines = lines[first_item:last_item]
                            print(sublines)
                            for line in sublines:
                                print(line)
                                montant_1n = 0
                                montant_2n = 0
                                montant_n = 0
                                montant_n1 = 0

                                try:
                                    rubrique = re.search('\d', str(line))
                                    name = line[:rubrique.start()]
                                    print(name)
                                    if len(line) > len(name):
                                        chiffre = line[rubrique.start():]
                                        list_montant1 = chiffre.split('|')
                                        list_montant2 = chiffre.split('_')

                                        if len(list_montant1) == 4:
                                            montant_1n = re.sub("[^0-9]", "", list_montant1[0], 0)
                                            montant_2n = re.sub("[^0-9]", "", list_montant1[1], 0)
                                            montant_n = re.sub("[^0-9]", "", list_montant1[2], 0)
                                            montant_n1 = re.sub("[^0-9]", "", list_montant1[3], 0)
                                        elif len(list_montant2) == 4:
                                            montant_1n = re.sub("[^0-9]", "", list_montant2[0], 0)
                                            montant_2n = re.sub("[^0-9]", "", list_montant2[1], 0)
                                            montant_n = re.sub("[^0-9]", "", list_montant2[2], 0)
                                            montant_n1 = re.sub("[^0-9]", "", list_montant2[3], 0)
                                        else:
                                            chiffre_rep = re.sub("[^0-9]", "", chiffre, 0)
                                            length_montant = int(len(chiffre_rep)/4)
                                            if length_montant < 6:
                                                length_montant = int(len(chiffre_rep) / 3)
                                                if length_montant < 6:
                                                    length_montant = int(len(chiffre_rep) / 2)
                                            montant_1n = re.sub("[^0-9]", "", chiffre_rep[:length_montant], 0)
                                            montant_2n = re.sub("[^0-9]", "", chiffre_rep[length_montant:((len(chiffre_rep)- (2 * length_montant)))], 0)
                                            montant_n = re.sub("[^0-9]", "", chiffre_rep[((len(chiffre_rep)- (2 * length_montant))):(len(chiffre_rep)-length_montant)], 0)
                                            montant_n1 = re.sub("[^0-9]", "", chiffre_rep[len(chiffre_rep)-length_montant:], 0)
                                            if len(montant_2n) <= 4:
                                                montant_2n = 0
                                except:
                                    name = line
                                    print(name)
                                try:
                                    montant1 = float(montant_1n)
                                except:
                                    montant1 = 0
                                try:
                                    montant2 = float(montant_2n)
                                except:
                                    montant2 = 0
                                try:
                                    montant = float(montant_n)
                                except:
                                    montant = 0

                                try:
                                    montant_1 = float(montant_n1)
                                except:
                                    montant_1 = 0
                                rec.env['import.ocr.actif.line'].create({'actif_id': rec.id,
                                                                       'name': name,
                                                                         'montant_1n':montant1,
                                                                         'montant_2n': montant2,
                                                                       'montant_n': montant,
                                                                       'montant_n1': montant_1})
                    output.close()
                    rec.state = "validation"
            for line in rec.actif_lines:
                line.montant_1n = line.montant_1n / 1000
                line.montant_2n = line.montant_2n / 1000
                line.montant_n = line.montant_n / 1000
                line.montant_n1 = line.montant_n1 / 1000

    def action_validation(self):
        for rec in self:
            list_validation = [18, 20, 26]
            actifs = rec.actif_lines.filtered(lambda r: r.rubrique.sequence in list_validation)
            if len(actifs) != 3:
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
    rubrique = fields.Many2one('import.ocr.config', string='Rubriques confirmés', domain="[('type','=','actif')]")
    montant_1n = fields.Float(string="Montants Bruts")
    montant_2n = fields.Float(string="Amortissements provisions et pertes de valeurs")
    montant_n = fields.Float(string="N")
    montant_n1 = fields.Float(string="N-1")
    actif_id = fields.Many2one('import.ocr.actif', string="Actif ID")
