from odoo import models, fields, api, _
import datetime


class Workflow(models.Model):
    _name = 'wk.workflow.dashboard'
    _description = 'Workflow de demande de financement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='تاريخ البدء', default=fields.Date.today)
    date_fin = fields.Date(string='تاريخ الانتهاء')
    name = fields.Char(string='Réference')
    state = fields.Selection([('1', 'الفرع'),
                              ('2', 'مديرية التمويلات'),
                              ('3', 'مديرية الاعمال التجارية'),
                              ('4', 'ادارة المخاطر'),
                              ('10', 'رئيس قطاع الخزينة'),
                              ('5', 'نائب المدير العام'),
                              ('9', 'المدير العام'),
                              ('6', 'لجنة التسهيلات'),
                              ('7', 'طور تبليغ المتعامل'),
                              ('8', 'ملف مرفوض')], default='1', string='وضعية الملف')
    nom_client = fields.Many2one('res.partner', string='اسم المتعامل', required=True)
    branche = fields.Many2one('wk.agence', string='الفرع', related='nom_client.branche', store=True)
    num_compte = fields.Char(string='رقم الحساب', related='nom_client.num_compte', store=True)
    demande = fields.Many2one('wk.type.demande', string='الطلب', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    chiffre_affaire = fields.Monetary(string='راس المال الشركة', currency_field='currency_id',related='nom_client.chiffre_affaire')
    montant_demande = fields.Float(string='المبلغ المطلوب')
    active = fields.Boolean(default=True)
    risk_scoring = fields.Many2one('risk.scoring', string='إدارة المخاطر')
    workflow_old = fields.Many2one('wk.workflow.dashboard', string='ملف سابق',)
    explanation = fields.Text(string='الغرض من الطلب')
    assigned_to_finance = fields.Many2one('res.users', string='المحلل المالي', )
    assigned_to_agence = fields.Many2one('res.users', string='المكلف بالملف', )
    assigned_to_commercial = fields.Many2one('res.users', string='المكلف بالاعمال التجارية')
    assigned_to_risque = fields.Many2one('res.users', string='المكلف بادارة المخاطر')
    states = fields.One2many('wk.etape', 'workflow', string='المديريات', domain=lambda self: [('etape', '!=', self.env.ref('dept_wk.princip_8').id)])
    lanced = fields.Boolean(string='Traitement lancé', compute='compute_visible_states')
    is_new = fields.Boolean(string='is new', compute='compute_type_demande')
    is_renew = fields.Boolean(string='is renew', compute='compute_type_demande')
    is_modify = fields.Boolean(string='is modify', compute='compute_type_demande')
    is_delete = fields.Boolean(string='is delete', compute='compute_type_demande')
    is_condition = fields.Boolean(string='is condition', compute='compute_type_demande')
    is_same_branche = fields.Boolean(compute='is_same_compute')
    is_same = fields.Boolean()
    raison_refus = fields.Text(string='سبب طلب المراجعة')
    is_in_financial = fields.Boolean(string='is financial state')
    classification = fields.Many2one('wk.classification',
                                     string='تصنيف الشركة',
                                     related='nom_client.classification')
    is_in_risk = fields.Boolean(string='is risk state', compute='compute_state', store=True)
    is_in_comm = fields.Boolean(string='is risk state', compute='compute_state_comm', store=True)
    is_in_dga = fields.Boolean(string='is dga state', compute='compute_state_dga', store=True)
    state_risque = fields.Selection([('risque_1', 'مدير المخاطر'),
                                     ('risque_3', 'المكلف بادارة المخاطر'),
                                     ('risque_4', 'مدير المخاطر'),
                                     ('risque_2', 'انتهاء التحليل'),
                                     ], string='وضعية الملف (في ادارة المخاطر)')
    state_commercial = fields.Selection([('commercial_1', 'مدير الاعمال التجارية'),
                                         ('commercial_2', 'مديرية الاعمال التجارية'),
                                         ('commercial_3', 'مدير الاعمال التجارية'),
                                         ('commercial_4', 'انتهاء التحليل'),
                                         ], string='وضعية الملف (في ادارة الاعمال التجارية)')

    def open_report_risk(self):
        for rec in self:
            if rec.risk_scoring:
                return self.env.ref('dept_wk.scoring_report').report_action(rec.risk_scoring, config=False)
            else:
                return False

    @api.depends('states')
    def compute_state(self):
        print('exec')
        for rec in self:
            exist = rec.states.filtered(lambda l:l.sequence == 4)
            if exist:
                rec.is_in_risk = True
            else:
                rec.is_in_risk = False

    @api.depends('states')
    def compute_state_comm(self):
        print('exec')
        for rec in self:
            exist = rec.states.filtered(lambda l:l.sequence == 3)
            if exist:
                rec.is_in_comm = True
            else:
                rec.is_in_comm = False

    @api.depends('states')
    def compute_state_dga(self):
        print('exec')
        for rec in self:
            exist = rec.states.filtered(lambda l:l.sequence == 5)
            if exist:
                rec.is_in_dga = True
            else:
                rec.is_in_dga = False

    def is_same_compute(self):
        for rec in self:
            exist = rec.states.filtered(lambda l: l.sequence == 5)
            if exist:
                rec.is_in_dga = True
            else:
                rec.is_in_dga = False
            if self.env.user.partner_id.branche:
                if self.env.user.partner_id.branche == rec.branche:
                    print(True)
                    rec.is_same = True
                    rec.is_same_branche = True
                else:
                    rec.is_same = False
                    rec.is_same_branche = False
            else:
                rec.is_same = False
                rec.is_same_branche = False


    def compute_type_demande(self):
        for rec in self:
            self.is_same_compute()
            if rec.demande.name == 'تسهيلات جديدة':
                rec.is_new = True
                rec.is_renew = rec.is_modify = rec.is_delete = rec.is_condition = False
            elif rec.demande.name == 'تجديد التسهيلات':
                rec.is_renew = True
                rec.is_new = rec.is_modify = rec.is_delete = rec.is_condition = False
            elif rec.demande.name == 'تعديل التسهيلات':
                rec.is_modify = True
                rec.is_new = rec.is_renew = rec.is_delete = rec.is_condition = False
            elif rec.demande.name == 'الغاء تسهيلات':
                rec.is_delete = True
                rec.is_new = rec.is_modify = rec.is_renew = rec.is_condition = False
            elif rec.demande.name == 'تعديل الشروط':
                rec.is_condition = True
                rec.is_new = rec.is_modify = rec.is_delete = rec.is_renew = False
            else:
                rec.is_new = rec.is_condition = rec.is_modify = rec.is_delete = rec.is_renew = False

    def compute_visible_states(self):
        for rec in self:
            print('not scoring')
            print(rec.risk_scoring)
            if not rec.risk_scoring:
                print('not scoring')
                rec.risk_scoring = rec.states.filtered(lambda l:l.sequence == 1).risk_scoring
            if rec.state == '2':
                rec.is_in_financial = True
            else:
                rec.is_in_financial = False
            if rec.states:
                rec.lanced = True
            else:
                rec.lanced = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('wk.credit.corporate') or _('New')
        res = super(Workflow, self).create(vals)
        return res


    def write(self, vals):
        if self.name == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('wk.credit.corporate') or _('New')
        res = super(Workflow, self).write(vals)
        return res

    def open_messages(self):
        for rec in self:
            view_id = self.env.ref('mail.view_message_tree').id
            return {
                'name': "Messages",
                'res_model': 'mail.message',
                'view_mode': 'tree',
                'view_id': view_id,
                'domain': [('res_id', 'in', rec.states.ids + [rec.id]),
                           ('message_type', '=', 'comment'),
                           ('model', 'in', ['wk.etape', 'wk.workflow.dashboard'])],
                'type': 'ir.actions.act_window',
            }

    def force_final(self):
        for rec in self:
            rec.state = '7'

    def force_comite(self):
        for rec in self:
            rec.state = '6'
            etape_fin = rec.states.filtered(lambda l: l.etape.sequence == 2)
            etape_comm = rec.states.filtered(lambda l: l.etape.sequence == 3)
            etape_risk = rec.states.filtered(lambda l: l.etape.sequence == 4)
            etape_1 = rec.states.filtered(lambda l: l.etape.sequence == 1)
            etape = rec.states.filtered(lambda l: l.etape.sequence == 6)
            vals = {'workflow': rec.id,
                    'etape': self.env.ref('dept_wk.princip_6').id,
                    'state_comite': 'comite_1',
                    'nom_client': etape_1.nom_client.id,
                    'gerant': etape_1.gerant.id,
                    'recommendation_visit': etape_1.recommendation_visit,
                    'recommendation_responsable_agence': etape_1.recommendation_responsable_agence,
                    'analyse_concurrence': etape_comm.analyse_concurrence,
                    'ampleur_benefice': etape_comm.ampleur_benefice,
                    'analyse_relation': etape_comm.analyse_relation,
                    'recommendation_dir_commercial': etape_comm.recommendation_dir_commercial,
                    'recommendation_commercial': etape_comm.recommendation_commercial,
                    'risk_scoring': etape_risk.risk_scoring.id,
                    'recommandation_dir_risque': etape_risk.recommandation_dir_risque,
                    'recommandation_analyste_fin': etape_fin.recommandation_analyste_fin,
                    'garantie_ids': etape_fin.garantie_ids.ids,
                    'exception_ids': etape_fin.exception_ids.ids,
                    'comite': etape_fin.comite.id,
                    'recommandation_dir_fin': etape_fin.recommandation_dir_fin,
                    'recommandation_vice_dir_fin': etape_fin.recommandation_vice_dir_fin,
                    }
            if not etape:
                etape = self.env['wk.etape'].create(vals)
            else:
                etape.write(vals)
            etape.facilite_propose.unlink()
            for fac in etape_fin.facilite_propose:
                self.env['wk.facilite.propose'].create({
                    'type_facilite': fac.type_facilite.id,
                    'type_demande_ids': fac.type_demande_ids.ids,
                    'montant_dz': fac.montant_dz,
                    'preg': fac.preg,
                    'duree': fac.duree,
                    'condition': fac.condition,
                    'etape_id': etape.id})


    def action_start(self):
        for rec in self:
            print('here')
            if rec.demande == self.env.ref('dept_wk.type_demande_1'):
                etape = self.env['wk.etape'].create({'workflow': rec.id,
                                             'etape': self.env.ref('dept_wk.princip_1').id,
                                             'state_branch': 'branch_1'})
            elif rec.demande in [self.env.ref('dept_wk.type_demande_2'), self.env.ref('dept_wk.type_demande_3')] and not rec.workflow_old:
                etape = self.env['wk.etape'].create({'workflow': rec.id,
                                                     'etape': self.env.ref('dept_wk.princip_1').id,
                                                     'state_branch': 'branch_1'})
            elif rec.demande in [self.env.ref('dept_wk.type_demande_2'), self.env.ref('dept_wk.type_demande_3')] and rec.workflow_old:
                print(rec.workflow_old.states)
                for etape in rec.workflow_old.states:
                    vals = get_values(rec, etape)
                    print(vals)
                    etape_new = self.env['wk.etape'].create(vals)
                    get_lists(self, etape_new, etape)
            '''state = 'الفرع'
            self.env['wk.tracking'].create({'workflow_id': rec.id,
                                            'state1': state,
                                            'date_debut': datetime.datetime.today()})'''

    def open_tracking(self):
        self.ensure_one()
        view_id = self.env.ref('dept_wk.view_wk_tracking_tree').id
        return {
                'name': "تتبع",
                'res_model': 'wk.tracking',
                'view_mode': 'tree',
                'view_id': view_id,
                'domain': [('workflow_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'create': False,
                            'edit': False,
                            'delete': False},
            }


def get_values(workflow, etape):
    values = {}
    if etape.sequence == 1:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_branch': 'branch_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'num_compte': etape.num_compte,
            'demande': etape.demande.id,
            'gerant': etape.gerant.id,
            'unit_prod': etape.unit_prod,
            'stock': etape.stock,
            'prod_company': etape.prod_company,
            'politique_comm': etape.politique_comm,
            'cycle_exploit': etape.cycle_exploit,
            'concurrence': etape.concurrence,
            'program_invest': etape.program_invest,
            'annee_fiscal_list' : etape.annee_fiscal_list.id,
            'result_visit': etape.result_visit,
            'description_company': etape.description_company,
            'recommendation_visit': etape.recommendation_visit,
            'recommendation_responsable_agence': etape.recommendation_responsable_agence,
            'risk_scoring': etape.risk_scoring.id,
        }
    elif etape.sequence == 2:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_finance': 'finance_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'taux_change': etape.taux_change,
            'annee_fiscal': etape.annee_fiscal,
            'risque_date': etape.risque_date,
            'nbr_banque': etape.nbr_banque,
            'comment_risk_central': etape.comment_risk_central,
            'capture_filename': etape.capture_filename,
            'risk_capture': etape.risk_capture,
            'actif_group': etape.actif_group.id,
            'passif_group': etape.passif_group.id,
            'tcr_group': etape.tcr_group.id,
            'visualisation2': etape.visualisation2,
            'annee_fiscal_list': etape.annee_fiscal_list.id,
            'visualisation1': etape.visualisation1,
            'description_prjt_invest': etape.description_prjt_invest,
            'actif_invest': etape.actif_invest,
            'pays_prod': etape.pays_prod.ids,
            'valeur_total': etape.valeur_total,
            'auto_financement': etape.auto_financement,
            'financement_demande': etape.financement_demande,
            'duree_financement': etape.duree_financement,
            'avis_invest': etape.avis_invest,
            'invest_id': etape.invest_id.id,
            'recommandation_analyste_fin': etape.recommandation_analyste_fin,
            'garantie_ids': etape.garantie_ids.ids,
            'comite': etape.comite.id,
            'recommandation_dir_fin': etape.recommandation_dir_fin,
        }
    elif etape.sequence == 3:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_commercial': 'commercial_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'analyse_secteur_act': etape.analyse_secteur_act,
            'analyse_concurrence': etape.analyse_concurrence,
            'ampleur_benefice': etape.ampleur_benefice,
            'analyse_relation': etape.analyse_relation,
            'recommendation_dir_commercial': etape.recommendation_dir_commercial,
            'recommendation_commercial': etape.recommendation_commercial,
        }
    elif etape.sequence == 4:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_risque': 'risque_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'recommandation_dir_risque': etape.recommandation_dir_risque,
        }
    elif etape.sequence == 5:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_vice': 'vice_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'gerant': etape.gerant.id,
            'unit_prod': etape.unit_prod,
            'stock': etape.stock,
            'prod_company': etape.prod_company,
            'annee_fiscal_list': etape.annee_fiscal_list.id,
            'politique_comm': etape.politique_comm,
            'cycle_exploit': etape.cycle_exploit,
            'concurrence': etape.concurrence,
            'program_invest': etape.program_invest,
            'result_visit': etape.result_visit,
            'description_company': etape.description_company,
            'recommendation_visit': etape.recommendation_visit,
            'recommendation_responsable_agence': etape.recommendation_responsable_agence,
            'analyse_secteur_act': etape.analyse_secteur_act,
            'analyse_concurrence': etape.analyse_concurrence,
            'ampleur_benefice': etape.ampleur_benefice,
            'analyse_relation': etape.analyse_relation,
            'recommendation_dir_commercial': etape.recommendation_dir_commercial,
            'recommendation_commercial': etape.recommendation_commercial,
            'recommandation_analyste_fin': etape.recommandation_analyste_fin,
            'garantie_ids': etape.garantie_ids.ids,
            'comite': etape.comite.id,
            'recommandation_dir_fin': etape.recommandation_dir_fin,
            'recommandation_vice_dir_fin': etape.recommandation_vice_dir_fin,
        }
    elif etape.sequence == 6:
        values = {
            'etape': etape.etape.id,
            'workflow': workflow.id,
            'state_comite': 'comite_1',
            'nom_client': etape.nom_client.id,
            'branche': etape.branche.id,
            'gerant': etape.gerant.id,
            'annee_fiscal_list': etape.annee_fiscal_list.id,
            'recommendation_visit': etape.recommendation_visit,
            'recommendation_responsable_agence': etape.recommendation_responsable_agence,
            'recommendation_dir_commercial': etape.recommendation_dir_commercial,
            'recommendation_commercial': etape.recommendation_commercial,
            'recommandation_analyste_fin': etape.recommandation_analyste_fin,
            'garantie_ids': etape.garantie_ids.ids,
            'comite': etape.comite.id,
            'recommandation_dir_fin': etape.recommandation_dir_fin,
            'recommandation_vice_dir_fin': etape.recommandation_vice_dir_fin,
            'recommandation_fin_comite': etape.recommandation_fin_comite,
        }
    return values
def get_lists(self, etape_new, etape_old):
    if etape_new.sequence == 1:
        for doc in etape_old.documents:
            self.env['wk.document.check'].create({'list_document': doc.list_document,
                                                  'document': doc.document,
                                                  'answer': doc.answer,
                                                  'note': doc.note,
                                                  'filename': doc.filename,
                                                  'etape_id': etape_new.id})
        for image in etape_old.images:
            self.env['wk.documents'].create({'picture': image.picture,
                                             'name': image.name,
                                             'etape_id': etape_new.id})
        for kyc in etape_old.kyc:
            self.env['wk.kyc.details'].create({'info': kyc.info,
                                               'answer': kyc.answer,
                                               'detail': kyc.detail,
                                               'etape_id': etape_new.id})
        for a in etape_old.apropos:
            self.env['wk.partenaire'].create({'nom_partenaire': a.nom_partenaire,
                                              'age': a.age,
                                              'pourcentage': a.pourcentage,
                                              'statut_partenaire': a.statut_partenaire,
                                              'nationalite': a.nationalite.id,
                                              'etape_id': etape_new.id
                                              })
        for g in etape_old.gestion:
            self.env['wk.gestion'].create({
                'name': g.name,
                'job': g.job,
                'niveau_etude': g.niveau_etude,
                'age': g.age,
                'experience': g.experience,
                'etape_id': etape_new.id
            })
        for empl in etape_old.employees:
            self.env['wk.nombre.employee'].create({
                'name': empl.name,
                'poste_permanent': empl.poste_permanent,
                'poste_non_permanent': empl.poste_non_permanent,
                'etape_id': etape_new.id
            })
        for siege in etape_old.sieges:
            self.env['wk.siege'].create({
                'name': siege.name,
                'adresse': siege.adresse,
                'nature': siege.nature.id,
                'etape_id': etape_new.id
            })
        for taille in etape_old.tailles:
            self.env['wk.taille'].create({
                'type_demande': taille.type_demande.id,
                'montant': taille.montant,
                'raison': taille.raison,
                'etape_id': etape_new.id,
                'garanties': taille.garanties.ids})
        for sit in etape_old.situations:
            self.env['wk.situation'].create({
                'banque': sit.banque.id,
                'type_fin': sit.type_fin.id,
                'montant': sit.montant,
                'garanties': sit.garanties,
                'etape_id': etape_new.id
            })
        for sit in etape_old.situations_fin:
            self.env['wk.situation.fin'].create({
                'type': sit.type,
                'sequence': sit.sequence,
                'year1': sit.year1,
                'year2': sit.year2,
                'year3': sit.year3,
                'etape_id': etape_new.id
            })
        for client in etape_old.client:
            self.env['wk.client'].create({
                'name': client.name,
                'country': client.country.id,
                'type_payment': client.type_payment.ids,
                'etape_id': etape_new.id
            })
        for f in etape_old.fournisseur:
            self.env['wk.fournisseur'].create({
                'name': f.name,
                'country': f.country.id,
                'type_payment': f.type_payment.ids,
                'etape_id': etape_new.id
            })
    elif etape_new.sequence == 2:
        for doc in etape_old.documents:
            if doc.document:
                self.env['wk.document.check'].create({'list_document': doc.list_document,
                                                  'document': doc.document,
                                                  'answer': doc.answer,
                                                  'note': doc.note,
                                                  'filename': doc.filename,
                                                  'etape_id': etape_new.id})
        for doc in etape_old.facilite_accorde:
            self.env['wk.facilite.accorde'].create({'type_facilite': doc.type_facilite.id,
                  'date': doc.date,
                  'montant_da_actuel': doc.montant_da_actuel,
                  'montant_da_demande': doc.montant_da_demande,
                  'montant_da_total': doc.montant_da_total,
                  'garantie_montant': doc.garantie_montant,
                  'remarques': doc.remarques,
                  'etape_id': etape_new.id})
        for doc in etape_old.detail_garantie_actuel_ids:
            self.env['wk.detail.garantie'].create({'type_garantie': doc.type_garantie.id,
                  'type_contrat': doc.type_contrat.id,
                  'montant': doc.montant,
                  'date': doc.date,
                  'recouvrement': doc.recouvrement,
                  'niveau': doc.niveau,
                  'etape_id': etape_new.id})
        for doc in etape_old.detail_garantie_propose_ids:
            self.env['wk.detail.garantie.propose'].create({'type_garantie': doc.type_garantie.id,
                  'type_contrat': doc.type_contrat.id,
                  'montant': doc.montant,
                  'date': doc.date,
                  'recouvrement': doc.recouvrement,
                  'niveau': doc.niveau,
                  'etape_id': etape_new.id})
        for doc in etape_old.garantie_conf:
            self.env['wk.garantie.conf'].create({'info': doc.info,
                  'answer': doc.answer,
                  'detail': doc.detail,
                  'etape_id': etape_new.id})
        for doc in etape_old.garantie_fin:
            self.env['wk.garantie.fin'].create({'info': doc.info,
                  'answer': doc.answer,
                  'detail': doc.detail,
                  'etape_id': etape_new.id})
        for doc in etape_old.garantie_autres:
            self.env['wk.garantie.autres'].create({'info': doc.info,
                  'answer': doc.answer,
                  'detail': doc.detail,
                  'etape_id': etape_new.id})
        for doc in etape_old.risque_central:
            self.env['wk.risque.line'].create({'declaration': doc.declaration,
                  'montant_esalam_dz_donne': doc.montant_esalam_dz_donne,
                  'montant_esalam_dz_used': doc.montant_esalam_dz_used,
                  'montant_other_dz_donne': doc.montant_esalam_dz_used,
                  'montant_other_dz_used': doc.montant_esalam_dz_used,
                  'etape_id': etape_new.id})
        for doc in etape_old.position_tax:
            self.env['wk.position'].create({'name': doc.name,
                  'adversite': doc.adversite,
                  'non_adversite': doc.non_adversite,
                  'notes': doc.notes,
                  'etape_id': etape_new.id})
        for doc in etape_old.mouvement:
            self.env['wk.mouvement'].create({'mouvement': doc.mouvement,
                  'sequence': doc.sequence,
                  'n3_dz': doc.n3_dz,
                  'n2_dz': doc.n2_dz,
                  'n1_dz': doc.n1_dz,
                  'n_dz': doc.n_dz,
                  'remarques': doc.remarques,
                  'etape_id': etape_new.id})
        for doc in etape_old.companies:
            self.env['wk.companies'].create({'name': doc.name,
                  'date_creation': doc.date_creation,
                  'activite': doc.activite.id,
                  'chiffre_affaire': doc.chiffre_affaire,
                  'n1_num_affaire': doc.n1_num_affaire,
                  'n_num_affaire': doc.n_num_affaire,
                  'etape_id': etape_new.id})
        for doc in etape_old.companies_fisc:
            self.env['wk.companies.fisc'].create({'declaration': doc.declaration,
                  'sequence': doc.sequence,
                  'year_1': doc.year_1,
                  'year_2': doc.year_2,
                  'year_3': doc.year_3,
                  'year_4': doc.year_4,
                  'variante': doc.variante,
                  'remark': doc.remark,
                  'etape_id': etape_new.id})
        for doc in etape_old.facitlite_existante:
            self.env['wk.facilite.existante'].create({'company': doc.company,
                  'facilite': doc.facilite.id,
                  'brut_da': doc.brut_da,
                  'net_da': doc.net_da,
                  'garanties': doc.garanties.ids,
                  'etape_id': etape_new.id})
        for doc in etape_old.mouvement_group:
            self.env['wk.mouvement.group'].create({'company': doc.company,
                  'sequence': doc.sequence,
                  'n2_dz': doc.n2_dz,
                  'n1_dz': doc.n1_dz,
                  'n_dz': doc.n_dz,
                  'remarques': doc.remarques,
                  'etape_id': etape_new.id})
        for doc in etape_old.recap_ids:
            self.env['wk.recap'].create({'declaration': doc.declaration,
                  'sequence': doc.sequence,
                  'montant': doc.montant,
                  'etape_id': etape_new.id})
        for doc in etape_old.var_ids:
            self.env['wk.variable'].create({'var': doc.var,
                  'sequence': doc.sequence,
                  'montant': doc.montant,
                  'etape_id': etape_new.id})

        for doc in etape_old.weakness_ids:
            self.env['wk.swot.weakness'].create({'name': doc.name,
                  'etape_id': etape_new.id})
        for doc in etape_old.strength_ids:
            self.env['wk.swot.strength'].create({'name': doc.name,
                  'etape_id': etape_new.id})
        for doc in etape_old.threat_ids:
            self.env['wk.swot.threat'].create({'name': doc.name,
                  'etape_id': etape_new.id})
        for doc in etape_old.opportunitie_ids:
            self.env['wk.swot.opportunitie'].create({'name': doc.name,
                  'etape_id': etape_new.id})

        for doc in etape_old.facilite_propose:
            self.env['wk.facilite.propose'].create({'type_demande_ids': doc.type_demande_ids.ids,
                                                    'montant_dz': doc.montant_dz,
                                                    'condition': doc.condition,
                                                    'preg': doc.preg,
                                                    'duree': doc.duree,
                                                    'etape_id': etape_new.id})

        vals = {'etape_id': etape_new.id,
                'sequence': 0,
                'declaration': 'السنة',
                'year_1': etape_new.annee_fiscal - 3,
                'year_2': etape_new.annee_fiscal - 2,
                'year_3': etape_new.annee_fiscal - 1,
                'year_4': etape_new.annee_fiscal,
                }
        self.env['wk.bilan.cat1'].create(vals)
        self.env['wk.bilan.cat2'].create(vals)
        self.env['wk.bilan.cat3'].create(vals)
        self.env['wk.bilan.cat4'].create(vals)
        self.env['wk.bilan.cat5'].create(vals)
        for doc in etape_old.bilan_id:
            self.env['wk.bilan'].create({
                'etape_id': etape_new.id,
                'bilan_id': doc.id,
                'sequence': doc.sequence,
                'categorie': doc.categorie,
                'declaration': doc.declaration,
                'year_1': doc.year_1,
                'year_2': doc.year_2,
                'year_3': doc.year_3,
                'year_4': doc.year_4,
                'is_null_4': doc.is_null_4,
                'is_null_3': doc.is_null_3,
                'is_null_2': doc.is_null_2,
                'is_null_1': doc.is_null_1,
                'variante': doc.variante,
            })
