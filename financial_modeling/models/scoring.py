from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

import base64
from io import BytesIO
import matplotlib.pyplot as plt

LIST_KPI = [('1', 'MB / CA   (%)'),
            ('2', 'EBE / CA   (%)'),
            ('3', 'RNC / CA   (%)'),
            ('4', 'FF / EBE   (%)'),
            ('5', 'Stock en jours Achats (jours)'),
            ('6', 'Client en jours CA    (jours)'),
            ('7', 'Fournisseurs en jours Achats (jours)'),
            ('8', 'FP / TB   (%)'),
            ('9', 'Liquidité Rapide'),
            ('10', 'Endettement levier'), ]


class ScoringAnalyse(models.Model):
    _name = "scoring.kpi"
    _description = 'Defini les KPI norme par l\'utilisateur'

    name = fields.Char(string='Réf')
    date = fields.Date(string='Date', default=datetime.today())

    tcr_id = fields.Many2one('import.ocr.tcr', string="TCR", required=True, domain="[('state', '=', 'valide')]")
    actif_id = fields.Many2one('import.ocr.actif', string="Actif", required=True, domain="[('state', '=', 'valide')]")
    passif_id = fields.Many2one('import.ocr.passif', string="Passif", required=True, domain="[('state', '=', 'valide')]")

    secteur = fields.Many2one('scoring.kpi.secteur', string="Secteur")
    domaine = fields.Many2one('scoring.kpi.secteur.domaine', string="Activité")

    norme_ids = fields.One2many('scoring.kpi.norme.line', 'kpi_id', string="Lines")
    ratio_ids = fields.One2many('scoring.kpi.reel.line', 'kpi_id', string="Lines")
    ponderation_ids = fields.One2many('scoring.kpi.ponderation.line', 'kpi_id', string="Lines")
    score_ids = fields.One2many('scoring.kpi.score.line', 'kpi_id', string="Lines")

    graph_pie1_n = fields.Binary(string='Graph')
    graph_pie1_n1 = fields.Binary(string='Graph')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('scoring.kpi.seq')

        res = super(ScoringAnalyse, self).create(vals)
        for index, val in enumerate(LIST_KPI):
            line = self.env['scoring.kpi.norme.line'].create({'kpi_id': res.id,
                                                              'kpi': val[0]})
            line = self.env['scoring.kpi.reel.line'].create({'kpi_id': res.id,
                                                             'kpi': val[0]})
            line = self.env['scoring.kpi.ponderation.line'].create({'kpi_id': res.id,
                                                                    'kpi': val[0]})
            line = self.env['scoring.kpi.score.line'].create({'kpi_id': res.id,
                                                              'kpi': val[0]})
        return res

    def action_calcul_ratio(self):
        for rec in self:
            count = 0
            for i in rec.norme_ids:
                if i.valeur == 0:
                    count += 1
            if count > 0:
                raise ValidationError("Une des valeurs norme manquante")
            else:
                ca = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                achat_vendu = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                matiere_premiere = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
                autre_appro = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 14)
                print(ca)
                # Calcul 1
                ratio_1 = rec.ratio_ids.filtered(lambda r: r.kpi == '1')
                pond_1 = rec.ponderation_ids.filtered(lambda r: r.kpi == '1')
                pond_1.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '1').valeur
                if ca and achat_vendu and autre_appro and matiere_premiere:
                    ratio_1.n_reel = ((ca.montant_n - achat_vendu.montant_n - matiere_premiere.montant_n - autre_appro.montant_n) / ca.montant_n) * 100 if ca.montant_n != 0 else 0
                    ratio_1.n1_reel = ((ca.montant_n1 - achat_vendu.montant_n1 - matiere_premiere.montant_n1 - autre_appro.montant_n1) / ca.montant_n1) * 100 if ca.montant_n1 != 0 else 0
                    ratio_1.n_norme = ratio_1.n1_norme = pond_1.valeur
                    ratio_1.n_ecart = 'favorable' if ratio_1.n_reel > ratio_1.n_norme else 'defavorable'
                    ratio_1.n1_ecart = 'favorable' if ratio_1.n1_reel > ratio_1.n1_norme else 'defavorable'

                # Calcul 2
                ratio_2 = rec.ratio_ids.filtered(lambda r: r.kpi == '2')
                pond_2 = rec.ponderation_ids.filtered(lambda r: r.kpi == '2')
                pond_2.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '2').valeur
                ebe = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                if ebe and ca:
                    ratio_2.n_reel = (ebe.montant_n / ca.montant_n) * 100 if ca.montant_n != 0 else 0
                    ratio_2.n1_reel = (ebe.montant_n1 / ca.montant_n1) * 100 if ca.montant_n1 != 0 else 0
                    ratio_2.n_norme = ratio_2.n1_norme = pond_2.valeur
                    ratio_2.n_ecart = 'favorable' if ratio_2.n_reel > ratio_2.n_norme else 'defavorable'
                    ratio_2.n1_ecart = 'favorable' if ratio_2.n1_reel > ratio_2.n1_norme else 'defavorable'

                # Calcul 3
                ratio_3 = rec.ratio_ids.filtered(lambda r: r.kpi == '3')
                pond_3 = rec.ponderation_ids.filtered(lambda r: r.kpi == '3')
                pond_3.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '3').valeur
                resultat_net = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                print(resultat_net)
                print(ca)
                if resultat_net and ca:
                    print('here')
                    ratio_3.n_reel = (resultat_net.montant_n / ca.montant_n) * 100 if ca.montant_n != 0 else 0
                    ratio_3.n1_reel = (resultat_net.montant_n1 / ca.montant_n1) * 100 if ca.montant_n1 != 0 else 0
                    ratio_3.n_norme = ratio_3.n1_norme = pond_3.valeur
                    ratio_3.n_ecart = 'favorable' if ratio_3.n_reel > ratio_3.n_norme else 'defavorable'
                    ratio_3.n1_ecart = 'favorable' if ratio_3.n1_reel > ratio_3.n1_norme else 'defavorable'

                # Calcul 4
                ratio_4 = rec.ratio_ids.filtered(lambda r: r.kpi == '4')
                pond_4 = rec.ponderation_ids.filtered(lambda r: r.kpi == '4')
                pond_4.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '4').valeur
                charge_financiere = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 42)
                if charge_financiere and ebe:
                    ratio_4.n_reel = (charge_financiere.montant_n / ebe.montant_n) * 100 if ebe.montant_n != 0 else 0
                    ratio_4.n1_reel = (charge_financiere.montant_n1 / ebe.montant_n1) * 100 if ebe.montant_n1 != 0 else 0
                    ratio_4.n_norme = ratio_4.n1_norme = pond_4.valeur
                    ratio_4.n_ecart = 'favorable' if ratio_4.n_reel <= ratio_4.n_norme else 'defavorable'
                    ratio_4.n1_ecart = 'favorable' if ratio_4.n1_reel <= ratio_4.n1_norme else 'defavorable'

                # Calcul 5
                ratio_5 = rec.ratio_ids.filtered(lambda r: r.kpi == '5')
                pond_5 = rec.ponderation_ids.filtered(lambda r: r.kpi == '5')
                pond_5.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '5').valeur
                stock = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)

                if stock and achat_vendu and autre_appro and matiere_premiere:
                    ratio_5.n_reel = ((stock.montant_n * 360) / (achat_vendu.montant_n + autre_appro.montant_n + matiere_premiere.montant_n)) if (achat_vendu.montant_n + autre_appro.montant_n + matiere_premiere.montant_n) != 0 else 0
                    ratio_5.n1_reel = ((stock.montant_n1 * 360) / (achat_vendu.montant_n1 + autre_appro.montant_n1 + matiere_premiere.montant_n1)) if (achat_vendu.montant_n1 + autre_appro.montant_n1 + matiere_premiere.montant_n1) != 0 else 0
                    ratio_5.n_norme = ratio_5.n1_norme = pond_5.valeur
                    ratio_5.n_ecart = 'favorable' if ratio_5.n_reel <= ratio_5.n_norme else 'defavorable'
                    ratio_5.n1_ecart = 'favorable' if ratio_5.n1_reel <= ratio_5.n1_norme else 'defavorable'

                # Calcul 6
                ratio_6 = rec.ratio_ids.filtered(lambda r: r.kpi == '6')
                pond_6 = rec.ponderation_ids.filtered(lambda r: r.kpi == '6')
                pond_6.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '6').valeur
                client = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                if client and ca:
                    ratio_6.n_reel = (client.montant_n * 360) / ca.montant_n if ca.montant_n != 0 else 0
                    ratio_6.n1_reel = (client.montant_n1 * 360) / ca.montant_n1 if ca.montant_n1 != 0 else 0
                    ratio_6.n_norme = ratio_6.n1_norme = pond_6.valeur
                    ratio_6.n_ecart = 'favorable' if ratio_6.n_reel <= ratio_6.n_norme else 'defavorable'
                    ratio_6.n1_ecart = 'favorable' if ratio_6.n1_reel <= ratio_6.n1_norme else 'defavorable'

                # Calcul 7
                ratio_7 = rec.ratio_ids.filtered(lambda r: r.kpi == '7')
                pond_7 = rec.ponderation_ids.filtered(lambda r: r.kpi == '7')
                pond_7.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '7').valeur
                fournisseur = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                if fournisseur and achat_vendu and autre_appro and matiere_premiere:
                    ratio_7.n_reel = ((fournisseur.montant_n * 360) / (achat_vendu.montant_n + autre_appro.montant_n + matiere_premiere.montant_n)) if (achat_vendu.montant_n + autre_appro.montant_n + matiere_premiere.montant_n) != 0 else 0
                    ratio_7.n1_reel = ((fournisseur.montant_n1 * 360) / (achat_vendu.montant_n1 + autre_appro.montant_n1 + matiere_premiere.montant_n1)) if (achat_vendu.montant_n + autre_appro.montant_n + matiere_premiere.montant_n) != 0 else 0
                    ratio_7.n_norme = ratio_7.n1_norme = pond_7.valeur
                    ratio_7.n_ecart = 'favorable' if ratio_7.n_reel <= ratio_7.n_norme else 'defavorable'
                    ratio_7.n1_ecart = 'favorable' if ratio_7.n1_reel <= ratio_7.n1_norme else 'defavorable'

                # Calcul 8
                ratio_8 = rec.ratio_ids.filtered(lambda r: r.kpi == '8')
                pond_8 = rec.ponderation_ids.filtered(lambda r: r.kpi == '8')
                pond_8.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '8').valeur
                total_I = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                total_gnrl = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                if total_I and total_gnrl:
                    ratio_8.n_reel = (total_I.montant_n / total_gnrl.montant_n) * 100 if total_gnrl.montant_n != 0 else 0
                    ratio_8.n1_reel = (total_I.montant_n1 / total_gnrl.montant_n1) * 100 if total_gnrl.montant_n1 != 0 else 0
                    ratio_8.n_norme = ratio_8.n1_norme = pond_8.valeur
                    ratio_8.n_ecart = 'favorable' if ratio_8.n_reel >= ratio_8.n_norme else 'defavorable'
                    ratio_8.n1_ecart = 'favorable' if ratio_8.n1_reel >= ratio_8.n1_norme else 'defavorable'

                # Calcul 9
                ratio_9 = rec.ratio_ids.filtered(lambda r: r.kpi == '9')
                pond_9 = rec.ponderation_ids.filtered(lambda r: r.kpi == '9')
                pond_9.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '9').valeur
                total_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                tresorerie = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                if total_3 and tresorerie and client:
                    ratio_9.n_reel = ((client.montant_n + tresorerie.montant_n) / total_3.montant_n) if total_3.montant_n != 0 else 0
                    ratio_9.n1_reel = ((client.montant_n1 + tresorerie.montant_n1) / total_3.montant_n1) if total_3.montant_n1 != 0 else 0
                    ratio_9.n_norme = ratio_9.n1_norme = pond_9.valeur
                    ratio_9.n_ecart = 'favorable' if ratio_9.n_reel >= ratio_9.n_norme else 'defavorable'
                    ratio_9.n1_ecart = 'favorable' if ratio_9.n1_reel >= ratio_9.n1_norme else 'defavorable'

                # Calcul 10
                ratio_10 = rec.ratio_ids.filtered(lambda r: r.kpi == '10')
                pond_10 = rec.ponderation_ids.filtered(lambda r: r.kpi == '10')
                pond_10.valeur = rec.norme_ids.filtered(lambda r: r.kpi == '10').valeur
                emprunt = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                tresorerie_passif = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                if emprunt and tresorerie_passif and tresorerie and total_I:
                    ratio_10.n_reel = ((emprunt.montant_n + tresorerie_passif.montant_n - tresorerie.montant_n) / total_I.montant_n) if total_I.montant_n != 0 else 0
                    ratio_10.n1_reel = ((emprunt.montant_n1 + tresorerie_passif.montant_n1 - tresorerie.montant_n1) / total_I.montant_n1) if total_I.montant_n1 != 0 else 0
                    ratio_10.n_norme = ratio_10.n1_norme = pond_10.valeur
                    ratio_10.n_ecart = 'favorable' if ratio_10.n_reel <= ratio_10.n_norme else 'defavorable'
                    ratio_10.n1_ecart = 'favorable' if ratio_10.n1_reel <= ratio_10.n1_norme else 'defavorable'

                rec.graph_pie1_n = create_pie([stock, fournisseur, client], type=1)
                rec.graph_pie1_n1 = create_pie([stock, fournisseur, client], type=0)

    def write(self, vals):
        res = super(ScoringAnalyse, self).write(vals)
        for rec in self:
            if 'ponderation_ids' in vals:
                total = 0
                for line in rec.ponderation_ids:
                    total += line.ponderation
                print(total)
                if total != 100:
                    raise ValidationError("La somme des points n'equal pas à 100")
        return res

    def action_calcul_score(self):
        for rec in self:
            up = ['1', '2', '3', '8', '9']
            for line in rec.score_ids:
                line.n_norme = line.n1_norme = rec.norme_ids.filtered(lambda r: r.kpi == line.kpi).valeur
                line.n_ponderation = line.n1_ponderation = rec.ponderation_ids.filtered(lambda r: r.kpi == line.kpi).ponderation
                line.n_reel = rec.ratio_ids.filtered(lambda r: r.kpi == line.kpi).n_reel
                line.n1_reel = rec.ratio_ids.filtered(lambda r: r.kpi == line.kpi).n1_reel
                if line.kpi in up:
                    print('up')
                    line.n_ecart = (line.n_reel - line.n_norme) / line.n_norme
                    line.n1_ecart = (line.n1_reel - line.n1_norme) / line.n1_norme
                else:
                    print('down')
                    line.n_ecart = (line.n_norme - line.n_reel) / line.n_norme
                    line.n1_ecart = (line.n1_norme - line.n1_reel) / line.n1_norme
                line.n_score = (1 + line.n_ecart) * line.n_ponderation if line.n_ecart < 0 else line.n_ponderation
                line.n1_score = (1 + line.n1_ecart) * line.n1_ponderation if line.n1_ecart < 0 else line.n1_ponderation

    def import_values(self):
        for rec in self:
            if rec.secteur:
                record = self.env['scoring.configuration.data'].search([('name', '=', rec.secteur.id)])
                for line in rec.norme_ids:
                    line.valeur = record.norme.filtered(lambda l: l.kpi == line.kpi).valeur
            else:
                raise ValidationError("Secteur d'activité non défini")

    def import_suggested_values(self):
        for rec in self:
            if rec.secteur:
                record = self.env['scoring.configuration.data'].search([('name', '=', rec.secteur.id)])
                for line in rec.norme_ids:
                    line.valeur = record.norme.filtered(lambda l: l.kpi == line.kpi).valeur_suggested
            else:
                raise ValidationError("Secteur d'activité non défini")


class KpiNormeLine(models.Model):
    _name = 'scoring.kpi.norme.line'
    _description = 'Detail des KPI norme defini par l\'utilisateur'

    kpi = fields.Selection(LIST_KPI, string='KPI')
    valeur = fields.Float(string='Valeur')
    kpi_id = fields.Many2one('scoring.kpi', string='KPI ID')


class KpiPonderationLine(models.Model):
    _name = 'scoring.kpi.ponderation.line'
    _description = 'Detail ponderation des KPI norme defini par l\'utilisateur'

    kpi = fields.Selection(LIST_KPI, string='KPI')
    valeur = fields.Float(string='Valeur')
    ponderation = fields.Integer(string='Ponderation')
    kpi_id = fields.Many2one('scoring.kpi', string='KPI ID')


class KpiReelLine(models.Model):
    _name = 'scoring.kpi.reel.line'
    _description = 'Detail des KPI reel calculé'

    kpi = fields.Selection(LIST_KPI, string='KPI')
    kpi_id = fields.Many2one('scoring.kpi', string='KPI ID')

    n_norme = fields.Float(string='N/ Norme')
    n_reel = fields.Float(string='N/ Réel')
    n_ecart = fields.Selection([('favorable', 'Favorable'), ('defavorable', 'Défavorable')], string='N/Ecart')
    n1_norme = fields.Float(string='N-1/ Norme')
    n1_reel = fields.Float(string='N-1/ Réel')
    n1_ecart = fields.Selection([('favorable', 'Favorable'), ('defavorable', 'Défavorable')], string='N-1/ Ecart')


class KpiScoreLine(models.Model):
    _name = 'scoring.kpi.score.line'
    _description = 'Detail des KPI score calculé'

    kpi = fields.Selection(LIST_KPI, string='KPI')
    kpi_id = fields.Many2one('scoring.kpi', string='KPI ID')

    n_norme = fields.Float(string='N/ Norme')
    n_reel = fields.Float(string='N/ Réel')
    n_ponderation= fields.Integer(string='N/ Pondération')
    n_ecart = fields.Float(string='N/ Ecart')
    n_score = fields.Float(string='N/ Score')

    n1_norme = fields.Float(string='N-1/ Norme')
    n1_reel = fields.Float(string='N-1/ Réel')
    n1_ponderation = fields.Integer(string='N-1/ Pondération')
    n1_ecart = fields.Float(string='N-1/ Ecart')
    n1_score = fields.Float(string='N-1/ Score')


def create_pie(data, type=1):
    sizes = []
    labels = []

    for d in data:
        if type == 1:
            sizes.append(d.montant_n)
        else:
            sizes.append(d.montant_n1)
        labels.append(d.rubrique.name)
    print(labels)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%',pctdistance=0.8, startangle=90)
    ax1.axis('equal')
    ax1.legend(labels, loc="lower center", bbox_to_anchor=(0.5, -0.04), fontsize=6, ncol=2)
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.85)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='jpeg',dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    buf.close()
    return imageBase64


class Secteur(models.Model):
    _name = 'scoring.kpi.secteur'
    _description = 'SECTEUR D`ACTIVITE'

    name = fields.Char(string='Secteur d`activité')
    domaine = fields.One2many('scoring.kpi.secteur.domaine', 'secteur', string='domaines d`activité')


class Domaine(models.Model):
    _name = 'scoring.kpi.secteur.domaine'
    _description = 'ACTIVITE D`ENTREPRISE'

    name = fields.Char(string='Activité d`entreprise')
    secteur = fields.Many2one('scoring.kpi.secteur', string='secteur')


class DataCumule(models.Model):
    _name = 'scoring.configuration.data'
    _description = 'Configuration norme data'

    name = fields.Many2one('scoring.kpi.secteur', string='Secteur', required=True)
    norme = fields.One2many('scoring.kpi.cumule.line', 'cumule_id', string="Norme" , help="Valeur calculée à l'aide des anciennes valeurs défini par l'utilisateur")
    nbr_records = fields.Integer(string="Nombre d'enregistrements", compute="_compute_nbr_record")

    @api.model
    def create(self, vals):
        records = self.env['scoring.configuration.data'].search([('name', '=', int(vals['name']))])
        if records:
            raise ValidationError('Enregistrement existe déja')
        else:
            res = super(DataCumule, self).create(vals)
            for index, val in enumerate(LIST_KPI):
                line = self.env['scoring.kpi.cumule.line'].create({'cumule_id': res.id,
                                                                  'kpi': val[0]})
            return res

    def _compute_nbr_record(self):
        for rec in self:
            records = self.env['scoring.kpi'].search([('secteur', '=', rec.name.id)])
            if records:
                rec.nbr_records = len(records)
                for line in rec.norme:
                    sum = 0
                    for r in records:
                        if r.ratio_ids:
                            ratio = r.ratio_ids.filtered(lambda l: l.kpi == line.kpi)
                            val = (ratio.n_reel + ratio.n1_reel) / 2
                            sum += val
                    line.valeur_suggested = sum / len(records)
            else:
                rec.nbr_records = 0


class KpiCumuleLine(models.Model):
    _name = 'scoring.kpi.cumule.line'
    _description = 'Detail des KPI norme defini par l\'utilisateur'

    kpi = fields.Selection(LIST_KPI, string='KPI')
    valeur = fields.Float(string='Valeur')
    valeur_suggested = fields.Float(string='Valeur Suggérée')
    cumule_id = fields.Many2one('scoring.configuration.data', string='Cumule ID')
