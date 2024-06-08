from odoo import models, fields, api, _
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import base64
from datetime import datetime
from arabic_reshaper import reshape
from bidi.algorithm import get_display

from odoo.exceptions import ValidationError
list_fisc = [
    'السنة',
    'حقوق الملكية',
    'مجموع الديون',
    'نسبة المديونية leverage',
    'نسبة الالتزامات تجاه البنوك /Gearing',
    'رقم الاعمال',
    'EBIDTA',
    'صافي الربح',
    'راس المال العامل',
    'احتياجات راس المال العامل'
]

list_critere = [
    ('مؤشرات الهيكل المال', 200),
    ('مؤشرات السيولة', 75),
    ('مؤشرات النشاط', 95),
    ('مؤشرات المردودية', 30),
    ('الاجمالي', 400)
]


class Scoring(models.Model):
    _name = 'risk.scoring'
    _description = 'Main Risk Scoring'

    name = fields.Char(related='parent_id.name', string='Reference')
    date = fields.Date(string='تاريخ', default=datetime.today())
    is_initial = fields.Boolean(string='Is initial')
    parent_id = fields.Many2one('wk.workflow.dashboard', default=lambda self: self._context.get('parent_id'))
    etape_id = fields.Many2one('wk.etape' )
    partner_id = fields.Many2one('res.partner',  store=True, string='العميل')
    secteur = fields.Many2one('wk.activite', related='partner_id.activite', store=True)
    groupe = fields.Many2one('res.partner', related='partner_id.groupe', store=True, string='المجموعة')
    branche = fields.Many2one('wk.agence', related='partner_id.branche', store=True, string='الفرع')
    num_compte = fields.Char(related='partner_id.num_compte', store=True, string='رقم الحساب')
    taille = fields.Selection([('tpe', 'جد صغيرة'),
                               ('pe', 'صغيرة'),
                               ('me', 'متوسطة'),
                               ('ge', 'كبيرة')], string='حجم الشركة')
    critere_qual = fields.Many2one('risk.critere.qualitatif', string='Critères Qualitatifs', default=1)
    critere_quant = fields.Many2one('risk.critere.quantitatif', string='Critères Quantitatifs', default=1)

    tcr_id = fields.Many2one('import.ocr.tcr', string='TCR')
    passif_id = fields.Many2one('import.ocr.passif', string='Passif')
    actif_id = fields.Many2one('import.ocr.actif', string='Actif')

    original_capital = fields.Many2one('risk.original.capital', string='أصل رأس المال', domain="[('critere', '=', 1)]")
    comment_origin = fields.Text(string='تفسير/تعليق')
    actionnariat = fields.Many2one('risk.actionnariat', string='المساهمات', domain="[('critere', '=', 1)]")
    comment_actionnariat = fields.Text(string='تفسير/تعليق')
    forme_jur = fields.Many2one('risk.forme.jur', string='الشكل القانوني', domain="[('critere', '=', 1)]")
    comment_forme_jur = fields.Text(string='تفسير/تعليق')
    remp_succession = fields.Many2one('risk.remplacement.succession', string='الخلافة', domain="[('critere', '=', 1)]")
    comment_remp_succession = fields.Text(string='تفسير/تعليق')
    competence = fields.Many2one('risk.competence', string='الكفاءة', domain="[('critere', '=', 1)]")
    comment_competence = fields.Text(string='تفسير/تعليق')
    experience = fields.Many2one('risk.experience', string='الخبرة المهنية', domain="[('critere', '=', 1)]")
    comment_experience = fields.Text(string='تفسير/تعليق')
    soutien_etatic = fields.Many2one('risk.soutien.etatique', string='دعم الدولة', domain="[('critere', '=', 1)]")
    comment_soutien_etatic = fields.Text(string='تفسير/تعليق')
    activite = fields.Many2one('risk.activite', string='النشاط', domain="[('critere', '=', 1)]")
    comment_activite = fields.Text(string='تفسير/تعليق')
    influence_tech = fields.Many2one('risk.influence.tech', string='التكنولوجيا المستعملة', domain="[('critere', '=', 1)]")
    comment_influence_tech = fields.Text(string='تفسير/تعليق')
    anciennete = fields.Many2one('risk.anciennete', string='الأقدمية', domain="[('critere', '=', 1)]")
    comment_anciennete = fields.Text(string='تفسير/تعليق')
    concurrence = fields.Many2one('risk.concurrence', string='المنافسة', domain="[('critere', '=', 1)]")
    comment_concurrence = fields.Text(string='تفسير/تعليق')
    source_appro = fields.Many2one('risk.source.appro', string='الموردون', domain="[('critere', '=', 1)]")
    comment_source_appro = fields.Text(string='تفسير/تعليق')
    produit = fields.Many2one('risk.produit', string='المنتوج', domain="[('critere', '=', 1)]")
    comment_produit = fields.Text(string='تفسير/تعليق')
    flexibilite = fields.Many2one('risk.flexibilite', string='المرونة', domain="[('critere', '=', 1)]")
    comment_flexibilite= fields.Text(string='تفسير/تعليق')
    sollicitude = fields.Many2one('risk.sollicitude', string='طلب القروض لدى البنوك الزميلة', domain="[('critere', '=', 1)]")
    comment_sollicitude = fields.Text(string='تفسير/تعليق')
    situation = fields.Many2one('risk.situation', string='الأملاك العقارية للشركاء/المساهمين', domain="[('critere', '=', 1)]")
    comment_situation = fields.Text(string='تفسير/تعليق')
    mouvement = fields.Many2one('risk.mouvement', string='الإيداعات المتوقعة', domain="[('critere', '=', 1)]")
    comment_mouvement = fields.Text(string='تفسير/تعليق')
    garanties = fields.Many2one('risk.garanties', string='الضمانات المقترحة', domain="[('critere', '=', 1)]")
    comment_garantie = fields.Text(string='تفسير/تعليق')
    incident = fields.Many2one('risk.incident', string='التعثرات', domain="[('critere', '=', 1)]")
    comment_incident = fields.Text(string='تفسير/تعليق')
    conduite = fields.Many2one('risk.conduite', string='سيرة المتعامل', domain="[('critere', '=', 1)]")
    comment_conduite = fields.Text(string='تفسير/تعليق')
    dette_fisc = fields.Many2one('risk.dette.fisc', string='الضرائب', domain="[('critere', '=', 1)]")
    comment_dette_fisc = fields.Text(string='تفسير/تعليق')
    dette_parafisc = fields.Many2one('risk.dette.parafisc', string='الضمان الاجتماعي', domain="[('critere', '=', 1)]")
    comment_dette_parafisc = fields.Text(string='تفسير/تعليق')
    position_admin = fields.Many2one('risk.position.admin', string='إدارات أخرى', domain="[('critere', '=', 1)]")
    comment_position_admin = fields.Text(string='تفسير/تعليق')
    source_remb = fields.Many2one('risk.source.remb', string='مصادر التسديد', domain="[('critere', '=', 1)]")
    comment_source_remb = fields.Text(string='تفسير/تعليق')
    part_profil = fields.Many2one('risk.part.profil',
                                  string='ربحية المصرف من التمويلات الممنوحة', domain="[('critere', '=', 1)]")
    comment_part_profil = fields.Text(string='تفسير/تعليق')
    quant_1 = fields.Float(string='RS1 - FP / TB')
    quant_2 = fields.Float(string='RS2 - FP / Capitaux permanents *100')
    quant_3 = fields.Float(string='RS3 - FRN / Actif circulants hors tréso.')
    quant_4 = fields.Float(string='RS4 - DLMT / CAF')
    quant_17 = fields.Float(string='RS5 - Signes de la Trésorerie et le BFR')
    quant_5 = fields.Float(string='RL1 - Actif circulants / DCT *100')
    quant_6 = fields.Float(string='RL2 - Disponibilité / DCT *100')
    quant_7 = fields.Float(string='RA1 - Stock en jours Achats')
    quant_8 = fields.Float(string='RA2 - Créances clients en jours CA')
    quant_9 = fields.Float(string='RA3 - FRN rn jours CA')
    quant_10 = fields.Float(string='RA4 - BFR en jours CA')
    quant_11 = fields.Float(string='RA5 - Stock en jours CA')
    quant_12 = fields.Float(string='RR1 - VA / CA')
    quant_13 = fields.Float(string='RR2 - EBE / (Immo. + BFR)')
    quant_14 = fields.Float(string='RR3 - Résultat d`exploitation / FP')
    quant_15 = fields.Float(string='RR4 - RN / TB')
    quant_16 = fields.Float(string='RR5 - CAF / TB')
    res_quant_1 = fields.Integer(string='Resultat Pondération')
    res_quant_2 = fields.Integer(string='Resultat Pondération')
    res_quant_3 = fields.Integer(string='Resultat Pondération')
    res_quant_4 = fields.Integer(string='Resultat Pondération')
    res_quant_17 = fields.Integer(string='Resultat Pondération')
    res_quant_5 = fields.Integer(string='Resultat Pondération')
    res_quant_6 = fields.Integer(string='Resultat Pondération')
    res_quant_7 = fields.Integer(string='Resultat Pondération')
    res_quant_8 = fields.Integer(string='Resultat Pondération')
    res_quant_9 = fields.Integer(string='Resultat Pondération')
    res_quant_10 = fields.Integer(string='Resultat Pondération')
    res_quant_11 = fields.Integer(string='Resultat Pondération')
    res_quant_12 = fields.Integer(string='Resultat Pondération')
    res_quant_13 = fields.Integer(string='Resultat Pondération')
    res_quant_14 = fields.Integer(string='Resultat Pondération')
    res_quant_15 = fields.Integer(string='Resultat Pondération')
    res_quant_16 = fields.Integer(string='Resultat Pondération')
    resultat_scor = fields.Integer(string='مجموع النقاط')
    resultat_scoring = fields.Integer(string='مجموع النقاط')
    critere_ids = fields.One2many('wk.scoring.detail', 'risk', string='المعايير الكمية')
    max_limit = fields.Float(string='الحد الاقصى للتمويل')
    limit_expo = fields.Float(string='حد التعرض')
    chiffre_affaire = fields.Float(string='رقم الاعمال')
    ca_banque = fields.Float(string='الاموال الخاصة للمصرف')
    niveau_risque = fields.Char(string='مستوى المخاطر')
    classif = fields.Integer(string='تصنيف')
    pourcentage = fields.Float(string='تحديد نسبة السقف من الاموال الخاصة')
    limit_25 = fields.Float(string='25% من الاموال الخاصة')
    case_25 = fields.Float(string='حالة تجاوز 25%')
    annee_fiscal = fields.Integer(string='السنة المالية N', compute='compute_annee')
    configuration_ca = fields.Many2one('configuration.risque')
    vis1 = fields.Binary(string='Vis')
    vis2 = fields.Binary(string='Vis')
    vis3 = fields.Binary(string='Vis')
    vis4 = fields.Binary(string='Vis')
    vis5 = fields.Binary(string='Vis')
    scoring_qualitatif = fields.Integer(string='اجمالي المعايير النوعية')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    company_ids = fields.Integer(string='', compute="_compute_company_fisc")
    scoring_group_ids = fields.One2many('risk.scoring', 'scoring_id', domain="[('is_initial', '=', False)]")
    facilite_ids = fields.One2many('facilite.risk', 'scoring_id')
    engagement_ids = fields.One2many('engagement.risk', 'scoring_id')
    scoring_id = fields.Many2one('risk.scoring')
    companies_fisc = fields.One2many('wk.companies.fisc', 'scoring_id')
    weakness_ids = fields.One2many('wk.swot.weakness', 'risk_id')
    strength_ids = fields.One2many('wk.swot.strength', 'risk_id')
    threat_ids = fields.One2many('wk.swot.threat', 'risk_id')
    opportunitie_ids = fields.One2many('wk.swot.opportunitie', 'risk_id')
    is_branch = fields.Boolean(string='Est dans l\'agence', compute='compute_level')
    classif_risque = fields.Selection([('1', 'ديون فعالة'),
                                       ('2', 'ديون مصنفة')], string='تصنيف المخاطر')
    directeur = fields.Many2one('res.users', string='Directeur', compute='_compute_directeur')
    analyste = fields.Many2one('res.users', string='Directeur')

    def import_data_group(self):
        for rec in self:
            if rec.tcr_id.state not in ['valide', 'modified'] or rec.actif_id.state not in ['valide', 'modified'] or rec.passif_id.state not in ['valide', 'modified']:
                raise ValidationError("Vous devriez d'abord valider les bilans")
            else:
                if not rec.companies_fisc:
                    count = 0
                    for item in list_fisc:
                        line = self.env['wk.companies.fisc'].create({'declaration': item,
                                                                     'sequence': count,
                                                                     'etape_id': rec.etape_id.id,
                                                                     'scoring_id': rec.id})
                        count += 1
                else:
                    for item in rec.companies_fisc:
                        item.write({'scoring_id': rec.id})
                bilan_1 = rec.companies_fisc.filtered(lambda r: r.sequence == 1)
                # total I حقوق الملكية
                passif_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                bilan_1.write({'year_4': passif_1.montant_n,
                               'year_3': passif_1.montant_n1})

                bilan_2 = rec.companies_fisc.filtered(lambda r: r.sequence == 2)
                # مجموع الديون
                passif_2 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                bilan_2.write({'year_4': passif_2.montant_n + passif_3.montant_n,
                               'year_3': passif_2.montant_n1 + passif_3.montant_n1})
                #سبة المديونية leverage
                bilan_3 = rec.companies_fisc.filtered(lambda r: r.sequence == 3)
                actif_1 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif_6 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                bilan_3.write({'year_4': (passif_6.montant_n + passif_5.montant_n - actif_1.montant_n) / passif_1.montant_n if passif_1.montant_n != 0 else 0,
                                'year_3': (passif_6.montant_n1 + passif_5.montant_n1 - actif_1.montant_n1) / passif_1.montant_n1 if passif_1.montant_n1 != 0 else 0})

                #Gearing
                bilan_4 = rec.companies_fisc.filtered(lambda r: r.sequence == 4)
                bilan_4.write({'year_4': ((passif_6.montant_n + passif_5.montant_n) / passif_1.montant_n) * 100 if passif_1.montant_n != 0 else 0,
                                'year_3': ((passif_6.montant_n1 + passif_5.montant_n1) / passif_1.montant_n1) * 100 if passif_1.montant_n1 != 0 else 0})

                #رقم الاعمال
                bilan_5 = rec.companies_fisc.filtered(lambda r: r.sequence == 5)
                tcr_1 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                bilan_5.write({'year_4': tcr_1.montant_n,
                                'year_3': tcr_1.montant_n1,
                                })
                # EBIDTA
                tcr_2 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                bilan_6 = rec.companies_fisc.filtered(lambda r: r.sequence == 6)
                bilan_6.write({'year_4': tcr_2.montant_n,
                                'year_3': tcr_2.montant_n1})

                #صافي الربح
                bilan_7 = rec.companies_fisc.filtered(lambda r: r.sequence == 7)
                tcr_3 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                bilan_7.write({'year_4': tcr_3.montant_n,
                               'year_3': tcr_3.montant_n1,})

                # راس المال العامل
                bilan_8 = rec.companies_fisc.filtered(lambda r: r.sequence == 8)
                actif_2 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
                passif_18 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                bilan_8.write({'year_4': passif_1.montant_n - actif_2.montant_n,
                                'year_3': passif_1.montant_n1 - actif_2.montant_n1
                                })

                #احتياجات راس المال العامل
                bilan_9 = rec.companies_fisc.filtered(lambda r: r.sequence == 9)
                passif_4_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                passif_20 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif_18 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif_20 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                bilan_9.write({'year_4': actif_18.montant_n + actif_20.montant_n - passif_20.montant_n,
                               'year_3': actif_18.montant_n1 + actif_20.montant_n1 - passif_20.montant_n1
                                })

    def compute_level(self):
        for rec in self:
            if not rec.etape_id:
                state = rec.parent_id.states.filtered(lambda l: l.sequence == 2)
                if state:
                    rec.etape_id = state
            if not self.env.user.has_group('dept_wk.dept_wk_group_responsable_credit'):
                rec.is_branch = True
            else:
                rec.is_branch = False

    def _compute_directeur(self):
        for rec in self:
            rec.directeur = self.env['res.groups'].search(
                [('id', '=', self.env.ref('dept_wk.dept_wk_group_responsable_risque').id)]).users[0]
            state = rec.parent_id.states.filtered(lambda l: l.sequence == 4)
            print('state', rec.parent_id.assigned_to_risque)
            rec.analyste = rec.parent_id.assigned_to_risque

    def compute_annee(self):
        for rec in self:
            etape = rec.parent_id.states.filtered(lambda l: l.sequence == 2)
            rec.annee_fiscal = etape.annee_fiscal

    def _critere_qual_domain(self):
        for rec in self:
            return [('critere', '=', rec.critere_qual.id)]

    @api.model
    def create(self, vals):
        res = super(Scoring, self).create(vals)
        print(self.env.context)
        if self.env.context.get('parent_id'):
            res.passif_id = self.env.context.get('passif_id')
            res.actif_id = self.env.context.get('actif_id')
            res.tcr_id = self.env.context.get('tcr_id')
            res.parent_id = self.env.context.get('parent_id')
            res.partner_id = res.parent_id.nom_client.id
            res.parent_id.risk_scoring = res.id
            etape_1 = res.parent_id.states.filtered(lambda l: l.etape.sequence == 1)
            if etape_1:
                etape_1.risk_scoring = res.id
            """
            elif self.env.context.get('active_model') == 'wk.etape':
                etape_exist = self.env['risk.scoring'].search([('etape_id', '=', self.env.context.get('active_id')),
                                                               ('scoring_id', '=', False)], limit=1)
                state2 = etape_exist.parent_id.states.filtered(lambda self:self.sequence == 2)
                if etape_exist:
                    res.scoring_id = etape_exist.id
                    res.etape_id = state2.id
                etape_exists = self.env['risk.scoring'].search([('etape_id', '=', state2.id),
                                                                ('id', '!=', etape_exist.id),
                                                                ('partner_id', '!=', state2.workflow.nom_client.id)
                                                                ])
            print(etape_exists)
            for item in etape_exists:
                item.scoring_id = etape_exist.id
                item.parent_id = state2.workflow.id"""
        for item in list_critere:
            self.env['wk.scoring.detail'].create({
                'risk': res.id,
                'name': item[0],
                'critere': item[1]
            })
        self.env['wk.hist'].create({'workflow': res.parent_id.id,
                                    'date': res.parent_id.date,
                                    'nom_client': res.parent_id.nom_client.id})
        print('res', res)
        return res

    def calcul_scoring(self):
        for rec in self:
            print('rec.scoring_id', rec.scoring_id)
            print('rec.scoring_id == rec', rec.scoring_id == rec)
            if rec.scoring_id == rec:
                print('yes')
                rec.is_initial = True
            if not rec.tcr_id:
                etape = rec.parent_id.states.filtered(lambda l: l.etape.sequence == 2)
                rec.tcr_id = etape.tcr_id.id
                rec.actif_id = etape.actif_id.id
                rec.passif_id = etape.passif_id.id
            result_quant = 0
            count_quant = 0
            passif_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
            passif_2 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
            rec.quant_1 = (passif_1.montant_n / passif_2.montant_n) * 100 if passif_2.montant_n !=0 else 0
            for r in rec.critere_quant.quant_1:
                if r.du < rec.quant_1 <= r.au:
                    rec.res_quant_1 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            passif_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
            passif1_2 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 2)
            rec.quant_2 = (passif1_2.montant_n / passif_1.montant_n) * 100 if passif_1.montant_n != 0 else 0
            for r in rec.critere_quant.quant_2:
                if r.du < rec.quant_2 <= r.au:
                    rec.res_quant_2 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            actif_1 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
            actif_2 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
            actif_3 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
            passif_12 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
            passif_18 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
            rec.quant_3 = ((passif_12.montant_n + passif_18.montant_n - actif_2.montant_n) / (
                    actif_1.montant_n - actif_3.montant_n)) * 100 if (
                    actif_1.montant_n - actif_3.montant_n) != 0 else 0
            for r in rec.critere_quant.quant_3:
                if r.du < rec.quant_3 <= r.au:
                    rec.res_quant_3 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            tcr_1 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
            tcr_2 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
            rec.quant_4 = passif_3.montant_n / (tcr_1.montant_n + tcr_2.montant_n) if (tcr_1.montant_n + tcr_2.montant_n) != 0 else 0
            for r in rec.critere_quant.quant_4:
                if r.du < rec.quant_4 <= r.au:
                    rec.res_quant_4 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1
            passif_24 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
            passif_4 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
            rec.quant_5 = (actif_1.montant_n / passif_24.montant_n) * 100 if passif_24.montant_n != 0 else 0.001
            for r in rec.critere_quant.quant_5:
                if r.du < rec.quant_5 <= r.au:
                    rec.res_quant_5 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            rec.quant_6 = (actif_3.montant_n / passif_24.montant_n) * 100 if passif_24.montant_n != 0 else 0.001
            for r in rec.critere_quant.quant_6:
                if r.du < rec.quant_6 <= r.au:
                    rec.res_quant_6 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            actif_4 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
            actif_19 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 19)
            passif1_20 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
            passif_21 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
            tcr_3 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
            tcr_4 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
            rec.quant_7 = (actif_4.montant_n * 360) / (tcr_3.montant_n * 1.19) if tcr_3.montant_n != 0 else 0
            for r in rec.critere_quant.quant_7:
                if r.du < rec.quant_7 <= r.au:
                    rec.res_quant_7 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            actif_5 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
            tcr_5 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
            rec.quant_8 = (actif_5.montant_n * 360) / (tcr_5.montant_n * 1.19)if tcr_5.montant_n != 0 else 0
            for r in rec.critere_quant.quant_8:
                if r.du < rec.quant_8 <= r.au:
                    rec.res_quant_8 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            rec.quant_9 = ((passif_1.montant_n + passif_3.montant_n - actif_2.montant_n) * 360) / tcr_5.montant_n if tcr_5.montant_n != 0 else 0
            for r in rec.critere_quant.quant_9:
                if r.du < rec.quant_9 <= r.au:
                    rec.res_quant_9 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            actif_16 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
            passif_24 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
            passif_23 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
            passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
            passif_22 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 22)
            bfr = actif_16.montant_n - actif_3.montant_n - (passif_24.montant_n - passif_23.montant_n)
            rec.quant_10 = bfr * 360 / tcr_5.montant_n if tcr_5.montant_n != 0 else 0
            print('bfr', bfr)
            print(rec.quant_10)
            for r in rec.critere_quant.quant_10:
                if r == rec.critere_quant.quant_10[0]:
                    if r.du <= rec.quant_10 <= r.au:
                        rec.res_quant_10 = r.ponderation
                        result_quant += r.ponderation
                        count_quant += 1
                else:
                    if r.du < rec.quant_10 <= r.au:
                        rec.res_quant_10 = r.ponderation
                        result_quant += r.ponderation
                        count_quant += 1

            rec.quant_11 = (actif_4.montant_n * 360) / tcr_5.montant_n if tcr_5.montant_n != 0 else 0
            for r in rec.critere_quant.quant_11:
                if r.du < rec.quant_11 <= r.au:
                    rec.res_quant_11 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            tcr_6 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 30)
            rec.quant_12 = (tcr_6.montant_n / tcr_5.montant_n) * 100 if tcr_5.montant_n != 0 else 0
            for r in rec.critere_quant.quant_12:
                if r.du < rec.quant_12 <= r.au:
                    rec.res_quant_12 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1
            bfr = actif_16.montant_n - actif_3.montant_n - (passif_24.montant_n - passif_23.montant_n)

            tcr_7 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
            rec.quant_13 = (tcr_7.montant_n / (bfr +
                    actif_2.montant_n)) * 100 if (bfr +
                    actif_2.montant_n) != 0 else 0
            for r in rec.critere_quant.quant_13:
                if r.du < rec.quant_13 <= r.au:
                    rec.res_quant_13 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            tcr_33 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
            rec.quant_14 = (tcr_2.montant_n / passif_12.montant_n) * 100 if passif_12.montant_n != 0 else 0
            for r in rec.critere_quant.quant_14:
                if r.du < rec.quant_14 <= r.au:
                    rec.res_quant_14 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            rec.quant_15 = (tcr_2.montant_n / passif_2.montant_n) * 100 if passif_2.montant_n != 0 else 0
            for r in rec.critere_quant.quant_15:
                if r.du < rec.quant_15 <= r.au:
                    rec.res_quant_15 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1

            rec.quant_16 = ((tcr_1.montant_n + tcr_2.montant_n) / passif_2.montant_n) * 100 if passif_2.montant_n != 0 else 0
            for r in rec.critere_quant.quant_16:
                if r.du < rec.quant_16 <= r.au:
                    rec.res_quant_16 = r.ponderation
                    result_quant += r.ponderation
                    count_quant += 1
            tres = actif_3.montant_n - passif_4.montant_n
            bfr = actif_4.montant_n + actif_19.montant_n - passif1_20.montant_n - passif_21.montant_n - passif_22.montant_n
            if tres <= 0 and bfr > 0:
                rec.res_quant_17 = rec.critere_quant.quant_17[0].ponderation
                result_quant += rec.res_quant_17
                count_quant += 1
            elif tres <= 0 and bfr <= 0:
                rec.res_quant_17 = rec.critere_quant.quant_17[1].ponderation
                result_quant += rec.res_quant_17
                count_quant += 1
            elif tres > 0 and bfr > 0:
                rec.res_quant_17 = rec.critere_quant.quant_17[2].ponderation
                result_quant += rec.res_quant_17
                count_quant += 1
            elif tres > 0 and bfr <= 0:
                rec.res_quant_17 = rec.critere_quant.quant_17[3].ponderation
                result_quant += rec.res_quant_17
                count_quant += 1

            result_qual = rec.original_capital.ponderation + rec.actionnariat.ponderation + \
                            rec.forme_jur.ponderation + rec.remp_succession.ponderation +\
                            rec.competence.ponderation + rec.experience.ponderation +\
                            rec.soutien_etatic.ponderation + rec.activite.ponderation +\
                            rec.influence_tech.ponderation + rec.anciennete.ponderation + \
                            rec.concurrence.ponderation + rec.source_appro.ponderation +\
                            rec.produit.ponderation + rec.flexibilite.ponderation + \
                            rec.sollicitude.ponderation + rec.situation.ponderation +\
                            rec.mouvement.ponderation + rec.garanties.ponderation +\
                            rec.incident.ponderation + rec.conduite.ponderation + \
                            rec.dette_fisc.ponderation + rec.dette_parafisc.ponderation + \
                            rec.position_admin.ponderation + rec.source_remb.ponderation +\
                            rec.part_profil.ponderation

            rec.scoring_qualitatif = result_qual
            rec.resultat_scor = result_quant + result_qual
            rec.resultat_scoring = result_quant + result_qual
            cat1 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات الهيكل المال')
            cat1.resultat = rec.res_quant_1 + rec.res_quant_2 + rec.res_quant_3 + rec.res_quant_4 + rec.res_quant_17

            cat2 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات السيولة')
            cat2.resultat = rec.res_quant_5 + rec.res_quant_6

            cat3 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات النشاط')
            cat3.resultat = rec.res_quant_7 + rec.res_quant_8 + rec.res_quant_9 + rec.res_quant_10 + rec.res_quant_11

            cat4 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات المردودية')
            cat4.resultat = rec.res_quant_12 + rec.res_quant_13 + rec.res_quant_14 + rec.res_quant_15 + rec.res_quant_16
            cat5 = rec.critere_ids.filtered(lambda r: r.name == 'الاجمالي')
            cat_total = cat1.resultat + cat2.resultat + cat3.resultat + cat4.resultat
            if not cat5:
                rec.critere_ids.create({'name': list_critere[-1][0],
                                        'critere': list_critere[-1][1],
                                        'risk': rec.id,
                                        'resultat': cat_total})
            else:
                cat5.resultat = cat_total
            rec.chiffre_affaire = tcr_5.montant_n
            rec.max_limit = tcr_5.montant_n * (rec.resultat_scor / 1000)
            if 1 <= rec.date.month < 4:
                trimestre = '1'
            elif 4 <= rec.date.month < 7:
                trimestre = '2'
            elif 7 <= rec.date.month < 9:
                trimestre = '3'
            else:
                trimestre = '4'
            configuration = self.env['configuration.risque'].search([('annee', '=', rec.date.year),
                                                                     ('trimestre', '=', trimestre)], limit=1)
            rec.configuration_ca = configuration.id
            rec.ca_banque = configuration.montant
            if 300 <= rec.resultat_scoring <= 450:
                rec.niveau_risque = 'ارباح غير مؤكدة'
                rec.classif = 7
                rec.pourcentage = 1/100
            elif 450 <= rec.resultat_scoring <= 550:
                rec.niveau_risque = 'كاف (الحد الفاصل)'
                rec.classif = 6
                rec.pourcentage = 5/100
            elif 550 <= rec.resultat_scoring <= 650:
                rec.niveau_risque = 'مرضي (مخاطر متوسطة)'
                rec.classif = 5
                rec.pourcentage = 20/100
            elif 650 <= rec.resultat_scoring <= 750:
                rec.niveau_risque = 'جيد (مخاطر فوق متوسطة)'
                rec.classif = 4
                rec.pourcentage = 22/100
            elif 750 <= rec.resultat_scoring <= 850:
                rec.niveau_risque = 'متقدم (مخاطر معتدلة)'
                rec.classif = 3
                rec.pourcentage = 23/100
            elif 850 <= rec.resultat_scoring <= 950:
                rec.niveau_risque = 'ممتاز (حد ادنى من المخاطرة)'
                rec.classif = 2
                rec.pourcentage = 24/100
            elif 950 <= rec.resultat_scoring <= 1000:
                rec.niveau_risque = 'استثنائي (خالي من المخاطر)'
                rec.classif = 1
                rec.pourcentage = 25/100
            self.create_graphs()
            rec.company_id = self.env.company

    def create_file_tcr(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'score_id': rec.id, 'year': 1}
            }

    def create_file_actif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'score_id': rec.id, 'year': 1,}
            }

    def create_file_passif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'score_id': rec.id, 'year': 1, }
            }

    def _compute_company_fisc(self):
        print('hiii')
        for rec in self:
            rec.company_ids = len(rec.scoring_group_ids)
            print(rec.id)
            etape1 = rec.parent_id.states.filtered(lambda l: l.sequence == 1)
            etape2 = rec.parent_id.states.filtered(lambda l: l.sequence == 2)
            scoring = etape1.risk_scoring
            for company in rec.scoring_group_ids:
                print('company != scoring', company != scoring)
                if company != scoring:
                    company.etape_id = etape2.id
                    company.parent_id = rec.parent_id.id
                else:
                    company.scoring_id = False
                    company.etape_id = False
                    company.is_initial = True

    def calcul_limit(self):
        for rec in self:
            rec.limit_expo = rec.pourcentage * rec.ca_banque
            rec.limit_25 = rec.ca_banque * (25 / 100)
            if rec.max_limit >= rec.limit_25:
                if 300 <= rec.resultat_scoring <= 450:
                    rec.case_25 = rec.ca_banque * (1 / 100)
                elif 450 <= rec.resultat_scoring <= 550:
                    rec.case_25 = rec.ca_banque * (5 / 100)
                elif 550 <= rec.resultat_scoring <= 650:
                    rec.case_25 = rec.ca_banque * (20 / 100)
                elif 650 <= rec.resultat_scoring <= 750:
                    rec.case_25 = rec.ca_banque * (22 / 100)
                elif 750 <= rec.resultat_scoring <= 850:
                    rec.case_25 = rec.ca_banque * (23 / 100)
                elif 850 <= rec.resultat_scoring <= 950:
                    rec.case_25 = rec.ca_banque * (24 / 100)
                elif 950 <= rec.resultat_scoring <= 1000:
                    rec.case_25 = rec.ca_banque * (25 / 100)
    def open_file(self):
        for rec in self:
            view_id = self.env.ref('dept_wk.view_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.tcr_id.file_import
            context['pdf_2'] = rec.tcr_id.file_import2
            wizard = self.env['view.bilan.wizard'].create({'pdf_1': rec.tcr_id.file_import,
                                                  'pdf_2': rec.tcr_id.file_import2})
            return {
                'name': 'TCR',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'view.bilan.wizard',
                'res_id': wizard.id,
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
    def open_file_passif(self):
        for rec in self:
            view_id = self.env.ref('dept_wk.view_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.passif_id.file_import
            wizard = self.env['view.bilan.wizard'].create({'pdf_1': rec.passif_id.file_import})
            return {
                'name': 'Passif',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'view.bilan.wizard',
                'res_id': wizard.id,
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }

    def open_file_actif(self):
        for rec in self:
            view_id = self.env.ref('dept_wk.view_bilan_wizard_form').id
            context = dict(self.env.context or {})
            context['pdf_1'] = rec.actif_id.file_import
            wizard = self.env['view.bilan.wizard'].create({'pdf_1': rec.actif_id.file_import})
            return {
                'name': 'Actif',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'view.bilan.wizard',
                'res_id': wizard.id,
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
    def create_graphs(self):
        for rec in self:
            data = {'RS1': rec.res_quant_1 / 150,
                    'RS2': rec.res_quant_2 / 150,
                    'RS3': rec.res_quant_3 / 150,
                    'RS4': rec.res_quant_4 / 150,
                    'RS5': rec.res_quant_17 / 150}
            group_data = list(data.values())
            group_names = list(data.keys())
            group_mean = np.mean(group_data)
            # Ajustement de la taille de la figure
            fig, ax = plt.subplots(figsize=(6, 3))  # Largeur x Hauteur

            # Création des barres avec des couleurs spécifiques et réduction de la largeur
            bars = ax.barh(group_names, group_data, color=['green'], height=0.4)  # Spécifiez vos couleurs ici

            # Ajout des pourcentages sur les barres
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - 0.03  # Position de base de l'étiquette
                # Positionnement du texte en fonction de la longueur de la barre
                if width < 0.5:  # Si la barre est courte, placez le texte à gauche
                    label_x_pos = width + 0.03
                ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                        '{:.1%}'.format(width), va='center')

            # Masquer l'axe des x
            ax.get_xaxis().set_visible(False)

            # Supprimer le cadre autour du graphique
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.vis1 = base64.b64encode(buf.getvalue())
            buf.close()

            data = {
                'RL1': rec.res_quant_5 / 75,
                'RL2': rec.res_quant_6 / 75,
            }

            # Création du graphique avec des couleurs spécifiques
            group_data = list(data.values())
            group_names = list(data.keys())
            group_mean = np.mean(group_data)

            # Ajustement de la taille de la figure
            fig, ax = plt.subplots(figsize=(6, 1))  # Largeur x Hauteur

            # Création des barres avec des couleurs spécifiques et réduction de la largeur
            bars = ax.barh(group_names, group_data, color=['green'], height=0.4)  # Spécifiez vos couleurs ici

            # Ajout des pourcentages sur les barres
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - 0.03  # Position de base de l'étiquette
                # Positionnement du texte en fonction de la longueur de la barre
                if width < 0.5:  # Si la barre est courte, placez le texte à gauche
                    label_x_pos = width + 0.03
                ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                        '{:.1%}'.format(width), va='center')

            # Masquer l'axe des x
            ax.get_xaxis().set_visible(False)

            # Supprimer le cadre autour du graphique
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            # Ajustement du graphique et sauvegarde de l'image
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.vis2 = base64.b64encode(buf.getvalue())
            buf.close()

            data = {'RA1': rec.res_quant_7 / 75,
                    'RA2': rec.res_quant_8 / 75,
                    'RA3': rec.res_quant_9 / 75,
                    'RA4': rec.res_quant_10 / 75,
                    'RA5': rec.res_quant_11 / 75,}
            group_data = list(data.values())
            group_names = list(data.keys())
            group_mean = np.mean(group_data)

            # Ajustement de la taille de la figure
            fig, ax = plt.subplots(figsize=(6, 3))  # Largeur x Hauteur

            # Création des barres avec des couleurs spécifiques et réduction de la largeur
            bars = ax.barh(group_names, group_data, color=['green'], height=0.4)  # Spécifiez vos couleurs ici

            # Ajout des pourcentages sur les barres
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - 0.03  # Position de base de l'étiquette
                # Positionnement du texte en fonction de la longueur de la barre
                if width < 0.5:  # Si la barre est courte, placez le texte à gauche
                    label_x_pos = width + 0.03
                ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                        '{:.1%}'.format(width), va='center')

            # Masquer l'axe des x
            ax.get_xaxis().set_visible(False)

            # Supprimer le cadre autour du graphique
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.vis3 = base64.b64encode(buf.getvalue())
            buf.close()

            data = {'RR1': rec.res_quant_12 / 100,
                    'RR2': rec.res_quant_13 / 100,
                    'RR3': rec.res_quant_14 / 100,
                    'RR4': rec.res_quant_15 / 100,
                    'RR5': rec.res_quant_16 / 100}
            group_data = list(data.values())
            group_names = list(data.keys())
            group_mean = np.mean(group_data)

            # Ajustement de la taille de la figure
            fig, ax = plt.subplots(figsize=(6, 3))  # Largeur x Hauteur

            # Création des barres avec des couleurs spécifiques et réduction de la largeur
            bars = ax.barh(group_names, group_data, color=['green'], height=0.4)  # Spécifiez vos couleurs ici

            # Ajout des pourcentages sur les barres
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - 0.03  # Position de base de l'étiquette
                # Positionnement du texte en fonction de la longueur de la barre
                if width < 0.5:  # Si la barre est courte, placez le texte à gauche
                    label_x_pos = width + 0.03
                ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                        '{:.1%}'.format(width), va='center')

            # Masquer l'axe des x
            ax.get_xaxis().set_visible(False)

            # Supprimer le cadre autour du graphique
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.vis4 = base64.b64encode(buf.getvalue())
            buf.close()
            cat1 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات الهيكل المال')
            cat2 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات السيولة')
            cat3 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات النشاط')
            cat4 = rec.critere_ids.filtered(lambda r: r.name == 'مؤشرات المردودية')
            data = {
                'مؤشرات الهيكل المال': cat1.resultat / cat1.critere,
                'مؤشرات السيولة': cat2.resultat / cat2.critere,
                'مؤشرات النشاط': cat3.resultat / cat3.critere,
                'مؤشرات المردودية': cat4.resultat / cat4.critere
            }

            # Reformater les noms de données arabes
            reshaped_names = [get_display(reshape(name)) for name in data.keys()]

            # Création du graphique avec des couleurs spécifiques
            group_data = list(data.values())
            group_mean = np.mean(group_data)

            # Ajustement de la taille de la figure
            fig, ax = plt.subplots(figsize=(6, 3))  # Largeur x Hauteur

            # Création des barres avec des couleurs spécifiques et réduction de la largeur
            bars = ax.barh(reshaped_names, group_data, color=['green'], height=0.4)  # Spécifiez vos couleurs ici

            # Ajout des pourcentages sur les barres
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - 0.03  # Position de base de l'étiquette
                # Positionnement du texte en fonction de la longueur de la barre
                if width < 0.5:  # Si la barre est courte, placez le texte à gauche
                    label_x_pos = width + 0.03
                ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                        '{:.1%}'.format(width), va='center')
            # Masquer l'axe des x
            ax.get_xaxis().set_visible(False)

            # Supprimer le cadre autour du graphique
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.vis5 = base64.b64encode(buf.getvalue())
            buf.close()


class Detail(models.Model):
    _name = 'wk.scoring.detail'
    _description = 'Detail par categorie'

    name = fields.Char(string='المعايير الكمية')
    critere = fields.Integer(string='المعيار')
    resultat = fields.Float(string='العلامة')
    risk = fields.Many2one('risk.scoring', string='risk')
    computed_total = fields.Boolean(compute='compute_total')

    def compute_total(self):
        for rec in self:
            if rec.name == 'الاجمالي':
                others = self.env['wk.scoring.detail'].search([('risk', '=', rec.risk.id),
                                                               ('name', '!=', 'الاجمالي')])
                rec.critere = sum(others.mapped('critere'))
                rec.resultat = sum(others.mapped('resultat'))
                rec.computed_total = True
            else:
                rec.computed_total = False


class FaciliteRisk(models.Model):
    _name = 'facilite.risk'

    name = fields.Char()
    product_ids = fields.Many2many('wk.product', string='نوع التسهيلات')
    actuel_brut = fields.Float(string='الحالي الخام')
    assurance = fields.Float(string='التأمين النقدي')
    actuel_net = fields.Float(string='الحالي الصافي')
    bilan = fields.Float(string='الرصيد')
    request_net = fields.Float(string='المطلوب الصافي')
    proposed_net = fields.Float(string='المقترح الصافي')
    ratio_request_net = fields.Float(string='المطلوب/ممنوح المرجح')
    ratio_propose_net = fields.Float(string='المقترح/ممنوح المرجح')
    scoring_id = fields.Many2one('risk.scoring')


class EngagementRisk(models.Model):
    _name = 'engagement.risk'

    name = fields.Char()
    company = fields.Many2one('res.partner', string='الشركة', domain="[('is_client', '=', True)]")
    limit = fields.Float(string='السقف')
    ratio_request_net = fields.Float(string='المطلوب/ممنوح المرجح')
    ratio_propose_net = fields.Float(string='المقترح/ممنوح المرجح')
    scoring_id = fields.Many2one('risk.scoring')
