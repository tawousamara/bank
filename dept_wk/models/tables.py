from odoo import models, fields, api, _


class Apropos(models.Model):
    _name = 'wk.apropos'
    _description = 'Apropos du client'

    #partenaire = fields.One2many('wk.partenaire', 'apropos', string='الشركاء')


class Partenaire(models.Model):
    _name = 'wk.partenaire'
    _description = 'Partenaire du client'

    nom_partenaire = fields.Char(string='اسم الشريك/المالك')
    age = fields.Date(string='تاريخ التاسيس/الميلاد')
    pourcentage = fields.Float(string='نسبة الحصة')
    statut_partenaire = fields.Char(string='صفة الشريك')
    nationalite = fields.Many2one('res.country', string='الجنسية', default=lambda self: self.env['res.country'].search([('code', '=', 'DZ')], limit=1))
    etape_id = fields.Many2one('wk.etape')


class Kyc(models.Model):
    _name = 'wk.kyc'
    _description = 'kyc'

    def get_values(self):
        List_items = ['هل العميل شخص مقرب سياسيا؟',
              'هل أحد الشركاء/المساهمين/مسير مقرب سياسيا؟',
              'هل العميل أو أحد الشركاء/المساهمين/مسير مقرب من البنك؟',
              'هل للعميل شركات زميلة / مجموعة؟',
              'المتعامل / أحد الشركاء مدرج ضمن القوائم السوداء',
              'المتعامل / أحد الشركاء مدرج ضمن قائمة الزبائن المتعثرين بمركزية المخاطر لبنك الجزائر']
        list_ids = []
        for item in List_items:
            line = self.env['wk.kyc.details'].create({'info': item})
            list_ids.append(line.id)
        return self.env['wk.kyc.details'].browse(list_ids)
    #line_ids = fields.One2many('wk.kyc.details', 'kyc', default=get_values)


class KycDetail(models.Model):
    _name = 'wk.kyc.details'
    _description = 'Line KYC'

    info = fields.Char(string='معلومات إضافية عن العميل')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    detail = fields.Char(string='التفاصيل')
    etape_id = fields.Many2one('wk.etape')


class FaciliteAccorde(models.Model):
    _name = 'wk.facilite.accorde'
    _description = 'Détails des facilités accordées'


    etape_id = fields.Many2one('wk.etape')
    montant_da_actuel = fields.Float(string='الحالي')
    montant_dollar_actuel = fields.Float(string='K/$', compute='compute_dollar_actuel')
    montant_da_demande = fields.Float(string='المطلوبة')
    montant_dollar_demande = fields.Float(string='K/$', compute='compute_dollar_demande')
    montant_da_total = fields.Float(string='الاجمالي الصافي')
    montant_dollar_total = fields.Float(string='K/$', compute='compute_total')

    date = fields.Date(string='تاريخ الرخصة')
    type_facilite = fields.Many2one('wk.product', string='نوع التسهيلات')
    type_demande_ids = fields.Many2many('wk.product', string='نوع التسهيلات')
    garantie_montant = fields.Float(string='التأمين النقدي')
    credit = fields.Float(string='الرصيد')
    remarques = fields.Text(string='ملاحظات')
    compute_exist = fields.Boolean(compute='compute_products')

    def compute_products(self):
        for rec in self:
            if rec.type_facilite:
                values = self.env['wk.product'].browse(rec.type_facilite.id)
                rec.type_demande_ids |= values
                rec.compute_exist = True
            else:
                rec.compute_exist = False

    @api.depends('montant_da_actuel')
    def compute_dollar_actuel(self):
        for rec in self:
            rec.montant_dollar_actuel = rec.montant_da_actuel / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0

    @api.depends('montant_da_demande')
    def compute_dollar_demande(self):
        for rec in self:
            rec.montant_dollar_demande = rec.montant_da_demande / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0

    @api.depends('montant_da_total')
    def compute_total(self):
        for rec in self:
            rec.montant_dollar_total = rec.montant_da_total / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0


class DetailGarantiePropose(models.Model):
    _name = 'wk.detail.garantie.propose'
    _description = 'Detail Garantie'


    etape_id = fields.Many2one('wk.etape')
    type_garantie = fields.Many2one('wk.garanties', string='نوعية الضمان')
    type_garant = fields.Char(string='نوعية الضمان')
    type_contrat = fields.Many2one('wk.contrat', string='نوعية العقد')
    montant = fields.Float(string='القيمة')
    date = fields.Date(string='تاريخ التقييم')
    recouvrement = fields.Float(string='التغطية')
    niveau = fields.Selection([('1', 'عالي'),
                               ('2', 'متوسط'),
                               ('3', 'منخفض')], string='كفاية الضمانات قابلية التنفيذ عليها')


class DetailGarantieActuel(models.Model):
    _name = 'wk.detail.garantie.actuel'
    _description = 'Detail Garantie'


    etape_id = fields.Many2one('wk.etape')
    type_garantie = fields.Many2one('wk.garanties', string='نوعية الضمان')
    type_contrat = fields.Many2one('wk.contrat', string='نوعية العقد')
    montant = fields.Float(string='القيمة')
    date = fields.Date(string='تاريخ التقييم')
    recouvrement = fields.Float(string='التغطية')
    niveau = fields.Selection([('1', 'عالي'),
                               ('2', 'متوسط'),
                               ('3', 'منخفض')], string='كفاية الضمانات قابلية التنفيذ عليها')


class Detail(models.Model):
    _name = 'wk.detail.garantie'
    _description = 'Detail Garantie'

    etape_id = fields.Many2one('wk.etape')
    type_garantie = fields.Many2one('wk.garanties', string='نوعية الضمان')
    type_contrat = fields.Many2one('wk.contrat', string='نوعية العقد')
    montant = fields.Float(string='القيمة')
    date = fields.Date(string='تاريخ التقييم')
    recouvrement = fields.Float(string='التغطية')
    niveau = fields.Selection([('1', 'عالي'),
                               ('2', 'متوسط'),
                               ('3', 'منخفض')], string='كفاية الضمانات قابلية التنفيذ عليها')


class Contrat(models.Model):
    _name = 'wk.contrat'

    name = fields.Char(string='Nom')


class Ganrantie(models.Model):
    _name = 'wk.garantie.conf'

    info = fields.Char(string='الشروط السابقة و المقترحة')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    detail = fields.Char(string='التعليق')


    etape_id = fields.Many2one('wk.etape')


class GanrantieFin(models.Model):
    _name = 'wk.garantie.fin'

    info = fields.Char(string='الشروط السابقة و المقترحة')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    detail = fields.Char(string='التعليق')

    etape_id = fields.Many2one('wk.etape')


class GanrantieAutre(models.Model):
    _name = 'wk.garantie.autres'

    info = fields.Char(string='الشروط السابقة و المقترحة')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    detail = fields.Char(string='التعليق')


    etape_id = fields.Many2one('wk.etape')


class Risque(models.Model):
    _name = 'wk.risque.line'
    _description = 'Risque'


    etape_id = fields.Many2one('wk.etape')
    declaration = fields.Char(string='البيان')
    montant_esalam_dz_donne = fields.Float(string='السلام:الممنوح', default=0)
    montant_esalam_dollar_donne = fields.Float(string='K/$', compute='compute_salam_dollar_donne')
    montant_esalam_dz_used = fields.Float(string='السلام:المستغل', default=0)
    montant_esalam_dollar_used = fields.Float(string='K/$',  compute='compute_salam_dollar_donne')

    montant_other_dz_donne = fields.Float(string='اخرى :الممنوحة', default=0)
    montant_other_dollar_donne = fields.Float(string='K/$', compute='compute_other_dollar_donne')
    montant_other_dz_used = fields.Float(string='اخرى :المستغل', default=0)
    montant_other_dollar_used = fields.Float(string='K/$', compute='compute_other_dollar_donne')

    montant_total_dz_donne = fields.Float(string='الاجمالي:الممنوحة', compute='compute_total')
    montant_total_dollar_donne = fields.Float(string='K/$', compute='compute_total')
    montant_total_dz_used = fields.Float(string='الاجمالي:المستغل', compute='compute_total')
    montant_total_dollar_used = fields.Float(string='K/$', compute='compute_total')

    @api.onchange('montant_other_dollar_used',
                  'montant_other_dz_used',
                  'montant_other_dollar_donne',
                  'montant_other_dz_donne',
                  'montant_esalam_dollar_used',
                  'montant_esalam_dz_used',
                  'montant_esalam_dollar_donne',
                  'montant_esalam_dz_donne')
    def compute_total(self):
        for rec in self:
            rec.montant_total_dz_used = rec.montant_esalam_dz_used + rec.montant_other_dz_used
            rec.montant_total_dz_donne = rec.montant_esalam_dz_donne + rec.montant_other_dz_donne
            rec.montant_total_dollar_used = rec.montant_total_dz_used / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            rec.montant_total_dollar_donne = rec.montant_total_dz_donne / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0

    @api.depends('montant_esalam_dz_donne', 'montant_esalam_dz_used')
    def compute_salam_dollar_donne(self):
        for rec in self:
            rec.montant_esalam_dollar_donne = rec.montant_esalam_dz_donne / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            rec.montant_esalam_dollar_used = rec.montant_esalam_dz_used / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0

    @api.depends('montant_other_dz_used', 'montant_other_dz_donne')
    def compute_other_dollar_donne(self):
        for rec in self:
            rec.montant_other_dollar_donne = rec.montant_other_dz_donne / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            rec.montant_other_dollar_used = rec.montant_other_dz_used / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0


class MouvementAction(models.Model):
    _name = 'wk.mouvement'
    _description = 'Mouvement et Action'


    etape_id = fields.Many2one('wk.etape')
    mouvement = fields.Char(string='الحركة')
    sequence = fields.Integer(string='Sequence')
    n3_dz = fields.Float(string='KDA:N-3')
    n3_dollar = fields.Float(string='N-3:K/$', compute='compute_dollar')

    n2_dz = fields.Float(string='N-2:KDA')
    n2_dollar = fields.Float(string='N-2:K/$', compute='compute_dollar')

    n1_dz = fields.Float(string='N-1:KDA')
    n1_dollar = fields.Float(string='N-1:K/$', compute='compute_dollar')

    n_dz = fields.Float(string='N:KDA')
    n_dollar = fields.Float(string='N:K/$', compute='compute_dollar')
    remarques = fields.Char(string='ملاحظات')

    def compute_dollar(self):
        for rec in self:
            if rec.sequence != 0:
                rec.n_dollar = rec.n_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.n1_dollar = rec.n1_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.n2_dollar = rec.n2_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.n3_dollar = rec.n3_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.n_dollar = 0
                rec.n1_dollar = 0
                rec.n2_dollar = 0
                rec.n3_dollar = 0



class MouvementGroupe(models.Model):
    _name = 'wk.mouvement.group'
    _description = 'Mouvement et Action'


    etape_id = fields.Many2one('wk.etape')
    company = fields.Char(string='الشركة')
    sequence = fields.Integer(string='Sequence')
    n2_dz = fields.Float(string='N-2')
    n2_dollar = fields.Float(string='N-2:K/$', compute='compute_dollar')

    n1_dz = fields.Float(string='N-1')
    n1_dollar = fields.Float(string='N-1:K/$', compute='compute_dollar')

    n_dz = fields.Float(string='N')
    n_dollar = fields.Float(string='N:K/$', compute='compute_dollar')
    remarques = fields.Char(string='ملاحظات')

    @api.depends('n2_dz', 'n1_dz', 'n_dz')
    def compute_dollar(self):
        for rec in self:
            if rec.company != 'السنة':
                rec.n_dollar = rec.n_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.n1_dollar = rec.n1_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.n2_dollar = rec.n2_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.n_dollar = rec.n1_dollar = rec.n2_dollar = 0


class PositionTax(models.Model):
    _name = 'wk.position'
    _description = 'Position taxonomique'


    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='  ')
    adversite = fields.Boolean(string='محينة')
    non_adversite = fields.Boolean(string='غير محينة')
    compute_adversite = fields.Boolean(string='غير محينة', compute='compute_adversite')
    notes = fields.Char(string='ملاحظات')

    @api.onchange('adversite')
    def compute_adversite(self):
        for rec in self:
            if rec.adversite:
                rec.non_adversite = False
            else:
                rec.non_adversite = True
    @api.onchange('non_adversite')
    def compute_non_adversite(self):
        for rec in self:
            if rec.non_adversite:
                rec.adversite = False
            else:
                rec.adversite = True


class Remarks(models.Model):
    _name = 'wk.remark'
    _description = 'remarques'

    name = fields.Char(string='ملاحظات')


class Fournisseur(models.Model):
    _name = 'wk.fournisseur'
    _description = 'fournisseur'


    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='الاسم')
    country = fields.Many2one('res.country', string='البلد')
    type_payment = fields.Many2many('wk.type.payment', string='طريقة السداد')


class Client(models.Model):
    _name = 'wk.client'
    _description = 'clients'

    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='الاسم')
    country = fields.Many2one('res.country', string='البلد', default=lambda self: self.env['res.country'].search([('code', '=', 'DZ')], limit=1))
    type_payment = fields.Many2many('wk.type.payment', string='طريقة السداد')


class Companies(models.Model):
    _name = 'wk.companies'
    _description = 'Companies in relation'

    name = fields.Char(string='الشركة')
    date_creation = fields.Char(string='سنة التاسيس', size=4)
    activite = fields.Many2one('wk.activite', string='النشاط الرئيسي')
    chiffre_affaire = fields.Float(string='راس المال')
    n1_num_affaire = fields.Integer(string='رقم الاعمال N-1')
    n_num_affaire = fields.Integer(string='رقم الاعمال N')

    etape_id = fields.Many2one('wk.etape')


class DeclarationFisc(models.Model):
    _name = 'wk.companies.fisc'
    _description = 'Companies fisc'

    scoring_id = fields.Many2one('risk.scoring')

    etape_id = fields.Many2one('wk.etape')
    declaration = fields.Char(string='البيان')
    sequence = fields.Integer(string='Sequence')
    year_1 = fields.Float(string='المدققة N-3')
    year_2 = fields.Float(string='المدققة N-2')
    year_3 = fields.Float(string='المدققة N-1')
    year_4 = fields.Float(string='N')
    variante = fields.Float(string='N-1 - N-2 Δ')
    remark = fields.Text(string='التعليق')


class FaciliteExistante(models.Model):
    _name = 'wk.facilite.existante'
    _description = 'Facilités existantes avec la banque'

    etape_id = fields.Many2one('wk.etape')
    company = fields.Char(string='الشركة')
    facilite = fields.Many2one('wk.product', string='نوع التسهيلات')
    type_demande_ids = fields.Many2many('wk.product', string='نوع التسهيلات')
    brut_da = fields.Float(string='الخام الحالي:KDA')
    brut_dollar = fields.Float(string='K/$', compute='compute_dollar')
    net_da = fields.Float(string='الصافي الحالي:KDA')
    net_dollar = fields.Float(string='K/$', compute='compute_dollar')
    garanties = fields.Many2many('wk.garanties', string='الضمانات')
    compute_exist = fields.Boolean(compute='compute_products')

    def compute_products(self):
        for rec in self:
            if rec.facilite:
                values = self.env['wk.product'].browse(rec.facilite.id)
                rec.type_demande_ids |= values
                rec.compute_exist = True
            else:
                rec.compute_exist = False

    @api.depends('brut_da', 'net_da')
    def compute_dollar(self):
        for rec in self:
            rec.brut_dollar = rec.brut_da / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            rec.net_dollar = rec.net_da / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0

class BilanFisc(models.Model):
    _name = 'wk.bilan'
    _description = 'Bilan fiscal'

    etape_id = fields.Many2one('wk.etape')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float( compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float( compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float( compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float( compute='compute_dollar')
    variante = fields.Float(string='الوضعية المحاسبية')
    remark = fields.Text(string='التعليق')
    bilan_id = fields.Many2one('wk.bilan', string='Bilan')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    @api.model
    def create(self, vals):
        res = super(BilanFisc, self).create(vals)
        if 'bilan_id' in vals:
            vals.pop('bilan_id')
        if 'etape_id' in vals:
            vals['bilan'] = res.id
            if res.categorie == '1':
                self.env['wk.bilan.cat1'].create(vals)
            if res.categorie == '2':
                self.env['wk.bilan.cat2'].create(vals)
            if res.categorie == '3':
                self.env['wk.bilan.cat3'].create(vals)
            if res.categorie == '4':
                self.env['wk.bilan.cat4'].create(vals)
            if res.categorie == '5':
                self.env['wk.bilan.cat5'].create(vals)
        return res

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4


class BilanCateg1(models.Model):
    _name = 'wk.bilan.cat1'

    etape_id = fields.Many2one('wk.etape')
    bilan = fields.Many2one('wk.bilan')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float(compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float(compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float(compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float(compute='compute_dollar')
    variante = fields.Float(string='التغير', compute='compute_variante')
    remark = fields.Text(string='التعليق')
    compute_field = fields.Boolean(string='compute', compute='compute_years')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    def compute_years(self):
        for rec in self:
            if not rec.bilan:
                rec.compute_field = False
            else:
                rec.year_1 = rec.bilan.year_1
                rec.year_2 = rec.bilan.year_2
                rec.year_3 = rec.bilan.year_3
                rec.year_4 = rec.bilan.year_4
                rec.is_null_4 = rec.bilan.is_null_4
                rec.is_null_3 = rec.bilan.is_null_3
                rec.is_null_2 = rec.bilan.is_null_2
                rec.is_null_1 = rec.bilan.is_null_1
                rec.compute_field = True

    def compute_variante(self):
        for rec in self:
            rec.variante = (rec.year_4 - rec.year_3) / rec.year_3 if rec.year_3 != 0 else 0

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4


class BilanCateg2(models.Model):
    _name = 'wk.bilan.cat2'

    etape_id = fields.Many2one('wk.etape')
    bilan = fields.Many2one('wk.bilan')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float(compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float(compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float(compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float(compute='compute_dollar')
    variante = fields.Float(string='التغير', compute='compute_variante')
    remark = fields.Text(string='التعليق')
    compute_field = fields.Boolean(string='compute', compute='compute_years')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    def compute_years(self):
        for rec in self:
            if not rec.bilan:
                rec.compute_field = False
            else:
                rec.year_1 = rec.bilan.year_1
                rec.year_2 = rec.bilan.year_2
                rec.year_3 = rec.bilan.year_3
                rec.year_4 = rec.bilan.year_4
                rec.is_null_4 = rec.bilan.is_null_4
                rec.is_null_3 = rec.bilan.is_null_3
                rec.is_null_2 = rec.bilan.is_null_2
                rec.is_null_1 = rec.bilan.is_null_1
                rec.compute_field = True

    def compute_variante(self):
        for rec in self:
            rec.variante = (rec.year_4 - rec.year_3) / rec.year_3 if rec.year_3 != 0 else 0

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4

class BilanCateg3(models.Model):
    _name = 'wk.bilan.cat3'

    etape_id = fields.Many2one('wk.etape')
    bilan = fields.Many2one('wk.bilan')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float(compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float(compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float(compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float(compute='compute_dollar')
    variante = fields.Float(string='التغير', compute='compute_variante')
    remark = fields.Text(string='التعليق')
    compute_field = fields.Boolean(string='compute', compute='compute_years')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4

    def compute_years(self):
        for rec in self:
            if not rec.bilan:
                rec.compute_field = False
            else:
                rec.year_1 = rec.bilan.year_1
                rec.year_2 = rec.bilan.year_2
                rec.year_3 = rec.bilan.year_3
                rec.year_4 = rec.bilan.year_4
                rec.is_null_4 = rec.bilan.is_null_4
                rec.is_null_3 = rec.bilan.is_null_3
                rec.is_null_2 = rec.bilan.is_null_2
                rec.is_null_1 = rec.bilan.is_null_1
                rec.compute_field = True

    def compute_variante(self):
        for rec in self:
            rec.variante = (rec.year_4 - rec.year_3) / rec.year_3 if rec.year_3 != 0 else 0


class BilanCateg4(models.Model):
    _name = 'wk.bilan.cat4'

    etape_id = fields.Many2one('wk.etape')
    bilan = fields.Many2one('wk.bilan')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float(compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float(compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float(compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float(compute='compute_dollar')
    variante = fields.Float(string='التغير', compute='compute_variante')
    remark = fields.Text(string='التعليق')
    compute_field = fields.Boolean(string='compute', compute='compute_years')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4

    def compute_years(self):
        for rec in self:
            if not rec.bilan:
                rec.compute_field = False
            else:
                rec.year_1 = rec.bilan.year_1
                rec.year_2 = rec.bilan.year_2
                rec.year_3 = rec.bilan.year_3
                rec.year_4 = rec.bilan.year_4
                rec.is_null_4 = rec.bilan.is_null_4
                rec.is_null_3 = rec.bilan.is_null_3
                rec.is_null_2 = rec.bilan.is_null_2
                rec.is_null_1 = rec.bilan.is_null_1
                rec.compute_field = True

    def compute_variante(self):
        for rec in self:
            rec.variante = (rec.year_4 - rec.year_3) / rec.year_3 if rec.year_3 != 0 else 0


class BilanCateg5(models.Model):
    _name = 'wk.bilan.cat5'

    etape_id = fields.Many2one('wk.etape')
    bilan = fields.Many2one('wk.bilan')
    sequence = fields.Integer(string='sequence')
    declaration = fields.Char(string='البيان')
    categorie = fields.Selection([('1', 'مؤشرات البنية المالية'),
                                  ('2', 'مؤشرات المديونية'),
                                  ('3', 'مؤشرات المردودية'),
                                  ('4', 'مؤشرات السيولة'),
                                  ('5', 'مؤشرات النشاط'),
                                  ])
    year_1 = fields.Float(string='المدققة N-3')
    year_1_d = fields.Float(compute='compute_dollar')
    year_2 = fields.Float(string='المدققة N-2')
    year_2_d = fields.Float(compute='compute_dollar')
    year_3 = fields.Float(string='المدققة N-1')
    year_3_d = fields.Float(compute='compute_dollar')
    year_4 = fields.Float(string='N')
    year_4_d = fields.Float(compute='compute_dollar')
    variante = fields.Float(string='التغير', compute='compute_variante')
    remark = fields.Text(string='التعليق')
    compute_field = fields.Boolean(string='compute', compute='compute_years')
    is_null_4 = fields.Boolean(string='Est null')
    is_null_3 = fields.Boolean(string='Est null')
    is_null_2 = fields.Boolean(string='Est null')
    is_null_1 = fields.Boolean(string='Est null')

    def compute_dollar(self):
        for rec in self:
            if rec.sequence not in [5, 9, 12, 18, 19, 24, 25, 26, 28, 29]:
                rec.year_1_d = rec.year_1 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_2_d = rec.year_2 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_3_d = rec.year_3 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
                rec.year_4_d = rec.year_4 / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0
            else:
                rec.year_1_d = rec.year_1
                rec.year_2_d = rec.year_2
                rec.year_3_d = rec.year_3
                rec.year_4_d = rec.year_4

    def compute_years(self):
        for rec in self:
            if not rec.bilan:
                rec.compute_field = False
            else:
                rec.year_1 = rec.bilan.year_1
                rec.year_2 = rec.bilan.year_2
                rec.year_3 = rec.bilan.year_3
                rec.year_4 = rec.bilan.year_4
                rec.is_null_4 = rec.bilan.is_null_4
                rec.is_null_3 = rec.bilan.is_null_3
                rec.is_null_2 = rec.bilan.is_null_2
                rec.is_null_1 = rec.bilan.is_null_1
                rec.compute_field = True

    def compute_variante(self):
        for rec in self:
            rec.variante = (rec.year_4 - rec.year_3) / rec.year_3 if rec.year_3 != 0 else 0


class Recap(models.Model):
    _name = 'wk.recap'
    _description = 'declaration'

    etape_id = fields.Many2one('wk.etape')
    declaration = fields.Char(string='البيان')
    sequence = fields.Integer(string='sequence')
    montant = fields.Float(string='المبلغ (دج)')


class Variables(models.Model):
    _name = 'wk.variable'
    _description = 'variables'


    etape_id = fields.Many2one('wk.etape')
    var = fields.Char(string='المتغيرات')
    sequence = fields.Integer(string='sequence')
    montant = fields.Float(string='المبلغ (دج)')


class TCR(models.Model):
    _name = 'wk.tcr'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class Actif(models.Model):
    _name = 'wk.actif'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class Passif(models.Model):
    _name = 'wk.passif'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class TCREstim(models.Model):
    _name = 'wk.tcr.estim'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class ActifEstim(models.Model):
    _name = 'wk.actif.estim'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class PassifEstim(models.Model):
    _name = 'wk.passif.estim'

    name = fields.Char(string='Poste comptable')
    name_ar = fields.Char(string='Poste comptable')
    sequence = fields.Integer(string='Sequence')
    valeur = fields.Float(string='المبلغ')
    valeur_dollar = fields.Float(string='المبلغ', compute="compute_dollar")
    etape_id = fields.Many2one('wk.etape')
    type = fields.Integer()

    def compute_dollar(self):
        for rec in self:
            rec.valeur_dollar = rec.valeur / rec.etape_id.taux_change


class SwotStrength(models.Model):
    _name = 'wk.swot.strength'
    _description = 'swot matrice'

    risk_id = fields.Many2one('risk.scoring')
    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='نقاط القوة')


class SwotWeakness(models.Model):
    _name = 'wk.swot.weakness'
    _description = 'swot matrice'


    risk_id = fields.Many2one('risk.scoring')
    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='نقاط الضعف')


class SwotOpportunities(models.Model):
    _name = 'wk.swot.opportunitie'
    _description = 'swot matrice'

    risk_id = fields.Many2one('risk.scoring')
    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='الفرص')


class SwotThreats(models.Model):
    _name = 'wk.swot.threat'
    _description = 'swot matrice'

    risk_id = fields.Many2one('risk.scoring')
    etape_id = fields.Many2one('wk.etape')
    name = fields.Char(string='التهديدات')


class FacilitePropose(models.Model):
    _name = 'wk.facilite.propose'
    _description = 'facilite propose'

    etape_id = fields.Many2one('wk.etape')
    type_facilite = fields.Many2one('wk.product', string='نوع التسهيلات')
    type_demande_ids = fields.Many2many('wk.product', string='نوع التسهيلات')
    montant_dz = fields.Float(string='المبلغ المقترح KDA')
    montant_dollar = fields.Float(string='K/$', compute='compute_montant_dollar')
    preg = fields.Float(string='التامين النقدي')
    duree = fields.Integer(string='المدة (الايام)')
    condition = fields.Char(string='الشروط')
    compute_exist = fields.Boolean(compute='compute_products')

    def compute_products(self):
        for rec in self:
            print('hiiiiiiioooooo')
            if rec.type_facilite:
                values = self.env['wk.product'].browse(rec.type_facilite.id)
                rec.type_demande_ids |= values
                rec.compute_exist = True
            else:
                rec.compute_exist = False

    @api.depends('montant_dz')
    def compute_montant_dollar(self):
        for rec in self:
            rec.montant_dollar = rec.montant_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0


class Facilitefinalfin(models.Model):
    _name = 'wk.facilite.final.fin'
    _description = 'facilite propose'


    type_facilite = fields.Many2one('wk.product', string='نوع التسهيلات')
    montant_dz = fields.Float(string='المبلغ المقترح KDA')
    montant_dollar = fields.Float(string='K/$', compute='compute_montant_dollar')
    condition = fields.Char(string='الشروط')

    @api.depends('montant_dz')
    def compute_montant_dollar(self):
        for rec in self:
            rec.montant_dollar = rec.montant_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0


class FaciliteFinalLeasing(models.Model):
    _name = 'wk.facilite.final.leasing'
    _description = 'facilite propose'


    type_facilite = fields.Many2one('wk.product', string='نوع التسهيلات')
    montant_dz = fields.Float(string='المبلغ المقترح KDA')
    montant_dollar = fields.Float(string='K/$', compute='compute_montant_dollar')
    condition = fields.Char(string='الشروط')

    @api.depends('montant_dz')
    def compute_montant_dollar(self):
        for rec in self:
            rec.montant_dollar = rec.montant_dz / rec.etape_id.taux_change if rec.etape_id.taux_change != 0 else 0


class ValidationGanrantie(models.Model):
    _name = 'wk.garantie.validation'

    info = fields.Char(string='الشروط السابقة و الممنوحة')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    detail = fields.Char(string='التعليق')


class Comite(models.Model):
    _name = 'wk.comite'

    name = fields.Char(string='اللجنة')
    pouvoir = fields.Char(string='الصلاحيات')
    alias = fields.Char(string='Alias')
