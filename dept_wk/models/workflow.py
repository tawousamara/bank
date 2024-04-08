import locale

from odoo import models, fields, api, _
import base64
import datetime
from io import BytesIO
import numpy as np
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import rcParams
from bidi.algorithm import get_display
from arabic_reshaper import reshape
from odoo.exceptions import ValidationError


List_items = ['هل العميل شخص مقرب سياسيا؟',
              'هل أحد الشركاء/المساهمين/مسير مقرب سياسيا؟',
              'هل العميل أو أحد الشركاء/المساهمين/مسير مقرب من البنك؟',
              'هل للعميل شركات زميلة / مجموعة؟',
              'المتعامل / أحد الشركاء مدرج ضمن القوائم السوداء',
              'المتعامل / أحد الشركاء مدرج ضمن قائمة الزبائن المتعثرين بمركزية المخاطر لبنك الجزائر']

List_risque = [
    'المباشرة قصيرة الأجل',
    'المباشرة متوسطة الأجل',
    'الغير المباشرة',
    'الاجمالي'
]
list_mouvement = [
    'الإيداعات (1)',
    'الإيرادات (2)',
    '(1)/(2)',
    'الربحية',
    'التوطين البنكي'
]
List_position = [
    'الوضعية الجبائية',
    'الوضعية الشبه جبائية',
    'الوضعية الشبه جبائية لغير الاجراء'
]
list_fisc = [
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

List_Bilan = [
    'حقوق الملكية',
    'رأس المال',
    'نتائج متراكمة',
    'مجموع المطلوبات',
    'التزامات بنكية قصيرة الأجل',
    'التزامات بنكية متوسطة الأجل',
    'تسهيلات الموردين',
    'مستحقات ضرائب',
    'مطلوبات أخرى متداولة',
    'Leverage',
    'مجموع الميزانية',
    'رقم الأعمال',
    'EBITDA',
    'صافي الأرباح',
    'صافي الأرباح/المبيعات',
    'قدرة التمويل الذاتي CAF',
    'صافي رأس المال العامل',
    'احتياجات رأس المال العامل',
    'نسبة التداول (السيولة)',
    'نسبة السيولة السريعة',
    'حقوق عند الزبائن',
    'المخزون',
    'متوسط دوران المخزون (يوم)',
    'متوسط فترة التحصيل (يوم)',
    'متوسط مدة تسهيلات الموردين (يوم)'
]
list_recap = [
    'فترة التحصيل بالأيام',
    'فترة دوران المخزون',
    'مدة تسهيلات الموردين',
    'فترة دوران رأس المال العامل',
    'المبلغ المستحق لتسهيلات قصيرة الأمد',
    'تسهيلات قصيرة الأمد مع البنوك الأخرى',
    'المبلغ المتبقي بعد خصم التسهيلات',
]
list_var = [
    'المبيعات',
    'كلفة المبيعات',
    'الذمم المدينة',
    'المخزون',
    'الذمم الدائنة',
]
list_garantie = [
    '',
    'وجود التأمين على العقارات والضمانات و صلاحيتها',
    'التعهد بتحويل الإيجارات في الحساب / توطين الصفقات في الحساب',
    'تقديم الحسابات المدققة للسنة الماضية في الآجال (خلال 6 أشهر)',
    'تغطية الضمانات تفوق 120%']
list_garantie_fisc = [
    'أقل مستوى لرأس المال',
    'خطاب التنازل عن حقوق سابقة',
    'هامش ضمان الجدية',
    'خطاب دمج الحسابات'
]
list_autre_term = [
    'رهن الحصص والاسهم',
    'رهن حسابات جارية/لأجل'
]
list_poste = [
    'الاطارات',
    'التقنيين',
    'التنفيذ'
]

list_siege = [
    'المقر الاجتماعي',
    'المقرات الثانوية 01',
    'المقرات الثانوية 02',
    'المقرات الثانوية 03'
]

list_situation = [
    'حقوق الملكية',
    'مجموع الميزانية',
    'رقم الأعمال',
    'صافي الارباح'
]

list_bilan = [
    ('1', 'حقوق الملكية'),
    ('1', 'رأس المال'),
    ('1', 'الاحتياطات'),
    ('1', 'الارباح المتراكمة (محتجزة+محققة)'),
    ('1', 'حقوق الملكية / مجموع الميزانية'),
    ('1', 'ACTIF NET IMMOBILISE CORPOREL'),
    ('1', 'الات ومعدات و عتاد نقل'),
    ('1', 'إهتلاكات المعدات'),
    ('1', 'اهتالكات / آلات و معدات و عتاد نقل'),
    ('1', 'صافي رأس المال العامل'),
    ('1', 'احتياجات رأس المال العامل'),
    ('1', 'FR/BFR'),
    ('2', 'مجموع المطلوبات (الديون)'),
    ('2', 'التزامات بنكية'),
    ('2', 'تسهيلات الموردين'),
    ('2', 'ضرائب مستحقة غير مدفوعة'),
    ('2', 'مطلوبات أخرى متداولة'),
    ('2', 'نسبة المديونية Leverage'),
    ('2', 'الالتزامات تجاه البنوك / حقوق'),
    ('3', 'مجموع الميزانية'),
    ('3', '(المبيعات، الايرادات)'),
    ('3', 'EBITDA'),
    ('3', 'صافي الارباح'),
    ('3', 'صافي الارباح/المبيعات ROS'),
    ('3', 'معدل العائد على الموجودات ROA'),
    ('3', 'معدل العائد على حقوق الملكية ROE'),
    ('4', 'التدفقات النقدية التشغيلية'),
    ('4', 'نسبة التداول (السيولة)'),
    ('4', 'نسبة السيولة السريعة'),
    ('5', 'حقوق عند الزبائن'),
    ('5', 'المخزون'),
    ('5', 'متوسط دوران المخزون (يوم)'),
    ('5', 'متوسط فترة التحصيل (يوم)'),
    ('5', 'متوسط مدة تسهيلات الموردين  (يوم)'),
]

class Workflow(models.Model):
    _name = 'wk.workflow'
    _description = 'Workflow de demande de financement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string='Date', default=datetime.datetime.today())
    name = fields.Char(string='Name')
    state = fields.Selection([('1', 'الفرع'),
                              ('2', 'مدير الفرع'),
                              ('3', 'مديرية التمويلات'),
                              ('4', 'مديرية الاعمال التجارية'),
                              ('5', 'ادارة المخاطر'),
                              ('6', 'نائب المدير العام'),
                              ('7', 'لجنة التسهيلات'),
                              ('8', 'انتهاء التحليل')], default='1')

    """******First state******"""

    nom_client = fields.Many2one('res.partner', string='اسم المتعامل', domain="[('is_client', '=', True)]")
    branche = fields.Many2one('wk.agence', string='الفرع', related='nom_client.branche')
    branche_related = fields.Many2one('wk.agence', string='الفرع', related='nom_client.branche')
    num_compte = fields.Char(string='رقم الحساب', related='nom_client.num_compte', store=True)
    num_compte_related = fields.Char(string='رقم الحساب', related='nom_client.num_compte')
    demande = fields.Many2one('wk.type.demande', string='الطلب')
    demande_related = fields.Many2one('wk.type.demande', string='الطلب', related='demande')
    demandes = fields.One2many('wk.historique', 'workflow', string="تسهيلات الشركة")
    show = fields.Boolean(string='show')
    nom_groupe = fields.Char(string='اسم الشركة', related='nom_client.nom_groupe')
    nom_groupe_related = fields.Char(string='اسم الشركة', related='nom_client.nom_groupe')
    classification = fields.Many2one('wk.classification', string="تصنيف الشركة", related='nom_client.classification')
    adress_siege = fields.Char(string='عنوان المقر الاجتماعي', related='nom_client.adress_siege')
    wilaya = fields.Many2one('wk.wilaya', string='الولاية', related='nom_client.wilaya')
    nif = fields.Char(string='NIF', related='nom_client.nif')
    num_registre_commerce = fields.Char(string='رقم السجل التجاري', related='nom_client.rc')
    date_inscription = fields.Date(string='تاريخ القيد في السجل التجاري', related='nom_client.date_inscription')
    date_debut_activite = fields.Date(string='تاريخ بداية النشاط', related='nom_client.date_debut_activite')
    activite = fields.Many2one('wk.activite', string='النشاط', related='nom_client.activite')
    gerant = fields.Many2one('res.partner', string='المسير', domain="[('parent_id', '=', nom_client),('is_company', '=', False)]")
    phone = fields.Char(string='الهاتف', related='nom_client.mobile')
    email = fields.Char(string='البريد الإلكتروني', related='nom_client.email')
    siteweb = fields.Char(string='الموقع الالكتروني للشركة', related='nom_client.website')

    unit_prod = fields.Text(string='وحدات الانتاج')
    stock = fields.Text(string='المخازن')
    prod_company = fields.Text(string='منتوجات الشركة')
    prod_company_related = fields.Text(string='منتوجات الشركة', related='prod_company')
    politique_comm = fields.Text(string='السياسة التسويقية')
    cycle_exploit = fields.Text(string='دورة الاستغلال')
    concurrence = fields.Text(string='المنافسة و دراسة السوق')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    forme_jur = fields.Many2one('wk.forme.jur', string='الشكل القانوني', related='nom_client.forme_jur')
    forme_jur_related = fields.Many2one('wk.forme.jur', string='الشكل القانوني', related='nom_client.forme_jur')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    chiffre_affaire = fields.Monetary(string='راس المال الشركة', currency_field='currency_id',related='nom_client.chiffre_affaire')
    chiffre_affaire_related = fields.Monetary(string='راس المال الشركة', currency_field='currency_id', related='nom_client.chiffre_affaire')
    kyc = fields.One2many('wk.kyc.details', 'workflow')
    apropos = fields.One2many('wk.partenaire', 'workflow', string='نبذة عن المتعامل')
    gestion = fields.One2many('wk.gestion', 'workflow', string='فريق التسيير')
    employees = fields.One2many('wk.nombre.employee', 'workflow', string='عدد العمال (حسب الفئة المهنية)')
    employees_related = fields.One2many('wk.nombre.employee', 'workflow', string='عدد العمال (حسب الفئة المهنية)', related='employees')
    sieges = fields.One2many('wk.siege', 'workflow', string='مقرات تابعة للشركة')
    tailles = fields.One2many('wk.taille', 'workflow', string='حجم و هيكل التمويلات المطلوبة')
    tailles_related = fields.One2many('wk.taille', 'workflow', string='حجم و هيكل التمويلات المطلوبة', related='tailles')
    situations = fields.One2many('wk.situation', 'workflow', string='الوضعية المصرفية والتزامات لدى الغير')
    situations_fin = fields.One2many('wk.situation.fin', 'workflow', string='البيانات المالية المدققة للثلاث سنوات الأخيرة')
    situations_fin_related = fields.One2many('wk.situation.fin', 'workflow', string='لبيانات المالية المدققة للثلاث سنوات الأخيرة', related='situations_fin')

    politique_vente = fields.Text(string='السياسة التسويقية /البيع')
    program_invest = fields.Text(string='البرنامج الاستثماري /المشاريع التطويرية')
    result_visit = fields.Text(string='نتائج الزيارة')
    recommendation_visit = fields.Text(string='توصية الفرع')
    recommendation_responsable_agence = fields.Text(string='توصية مدير الفرع')
    images = fields.One2many('wk.documents', 'workflow', string='الصور المرفقة')
    assigned_to_branch = fields.Many2one('res.users', string='تم تعيينه ل', domain=lambda self: [('groups_id', 'in', self.env.ref('dept_wk.dept_wk_group_agent_agence').id)])
    # documents a attacher
    doc_checked = fields.Boolean(string="أؤكد المستندات")
    doc_checked_vis = fields.Boolean(string="أؤكد المستندات", related='doc_checked')
    demande_facilite = fields.Binary(string='طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة')
    budget_3_ans = fields.Binary(string='الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس')
    budget_previsionnel = fields.Binary(string=' الميزانية الافتتاحية و الميزانية المتوقعة للسنة المراد تمويلها موقعة من طرف الشركة (حديثة النشأة)')
    schema_financement = fields.Binary(string='مخطط تمويل الاستغلال مقسم الى أرباع السنة للسنة المراد تمويلها')
    document_activite = fields.Binary(string=' المستندات و الوثائق المتعلقة بنشاط الشركة ( عقود، صفقات ،  طلبيات ، ... )' ,)
    proces_reg_irreg = fields.Binary(string='محاضر الجمعيات العادية و الغير العادية للأشخاص المعنويين', )
    copie_registre_commerce = fields.Binary(string='نسخة مصادق عليها من السجل التجاري')
    copie_statut = fields.Binary(string='نسخة مصادق عليها من القانون الأساسي للشركة')
    deliberation = fields.Binary(string='مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية')
    bulletin_officiel = fields.Binary(string='نسخة مصادق عليها من النشرة الرسمية للإعلانات القانونية')
    contrat_propriete = fields.Binary(string='نسخة طبق الأصل لعقد ملكية أو استئجار المحلات ذات الاستعمال المهني')
    attestation_fiscal = fields.Binary(string=' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)')
    declaration_central_risque = fields.Binary(string='استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)')
    autre_document = fields.Binary(string='ملف اخر')

    weakness_ids = fields.One2many('wk.swot.weakness', 'workflow')
    strength_ids = fields.One2many('wk.swot.strength', 'workflow')
    threat_ids = fields.One2many('wk.swot.threat', 'workflow')
    opportunitie_ids = fields.One2many('wk.swot.opportunitie', 'workflow')

    hide_documents = fields.Boolean(string='Hide documents')

    """******Second state******"""
    visualisation = fields.Binary(string='visualisation')
    visualisation1 = fields.Binary(string='visualisation')
    visualisation2 = fields.Binary(string='visualisation')

    analyse_secteur_act = fields.Text(string='تحليل قطاع عمل العميل')
    analyse_concurrence = fields.Text(string='تحليل المنافسة')
    ampleur_benefice = fields.Float(string='حجم الارباح PNB المتوقعة')
    ampleur_benefice_related = fields.Float(string='حجم الارباح PNB المتوقعة', related='ampleur_benefice')
    analyse_relation = fields.Text(string='تحليل اهمية العلاقة على المدى المتوسط')
    analyse_relation_related = fields.Text(string='تحليل اهمية العلاقة على المدى المتوسط', related='analyse_relation')

    documents = fields.One2many('wk.document.check', 'workflow', string='التاكد من الوثائق المرفقة')
    analyseur = fields.Many2one('res.users', string='المحلل المالي', domain=lambda self: [('groups_id', 'in', self.env.ref('dept_wk.dept_wk_group_analyste').id)])
    facilite_accorde = fields.One2many('wk.facilite.accorde', 'workflow',
                                       string='تفاصيل التسهيلات الممنوحة (بالمليون دج)')
    garantie_conf = fields.One2many('wk.garantie.conf', 'workflow',
                                    string='الشروط السابقة/المقترحة و الموافق عليها من لجان التمويل')
    garantie_fin = fields.One2many('wk.garantie.fin', 'workflow', string='الشروط المالية')
    garantie_autres = fields.One2many('wk.garantie.autres', 'workflow', string='الشروط الاخرى')

    detail_garantie_actuel_ids = fields.One2many('wk.detail.garantie', 'workflow', string='الضمانات العقارية الحالية')
    detail_garantie_propose_ids = fields.One2many('wk.detail.garantie.propose', 'workflow',
                                                  string='الضمانات العقارية المقترحة')

    risque_central = fields.One2many('wk.risque.line', 'workflow', string='مركزية المخاطر')
    compute_risque = fields.Float(string='compute field', compute='compute_risk')
    risque_date = fields.Date(string='مركزية المخاطر بتاريخ')
    nbr_banque = fields.Integer(string='عدد البنوك المصرحة')
    comment_risk_central = fields.Text(string='تعليق')
    capture_filename = fields.Char(default='صورة')
    risk_capture = fields.Binary(string='لقطة شاشة')

    @api.onchange('risque_central')
    def compute_risk(self):
        loc = locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
        for rec in self:
            print(self.env.company)
            if rec.risque_central:
                total = rec.risque_central.filtered(lambda r: r.declaration == 'الاجمالي')
                items = rec.risque_central.filtered(lambda r: r.declaration != 'الاجمالي')
                total.montant_esalam_dz_donne = sum(items.mapped('montant_esalam_dz_donne'))
                total.montant_esalam_dollar_donne = sum(items.mapped('montant_esalam_dollar_donne'))
                total.montant_esalam_dz_used = sum(items.mapped('montant_esalam_dz_used'))
                total.montant_esalam_dollar_used = sum(items.mapped('montant_esalam_dollar_used'))
                total.montant_other_dz_donne = sum(items.mapped('montant_other_dz_donne'))
                total.montant_other_dollar_donne = sum(items.mapped('montant_other_dollar_donne'))
                total.montant_other_dz_used = sum(items.mapped('montant_other_dz_used'))
                total.montant_other_dollar_used = sum(items.mapped('montant_other_dollar_used'))
                total.montant_total_dz_donne = sum(items.mapped('montant_total_dz_donne'))
                total.montant_total_dollar_donne = sum(items.mapped('montant_total_dollar_donne'))
                total.montant_total_dz_used = sum(items.mapped('montant_total_dz_used'))
                total.montant_total_dollar_used = sum(items.mapped('montant_total_dollar_used'))

    weakness1_ids = fields.One2many('wk.swot.weakness', 'workflow')
    strength1_ids = fields.One2many('wk.swot.strength', 'workflow')
    threat1_ids = fields.One2many('wk.swot.threat', 'workflow')
    opportunitie1_ids = fields.One2many('wk.swot.opportunitie', 'workflow')

    mouvement = fields.One2many('wk.mouvement', 'workflow',
                                string='الحركة والأعمال الجانبية للحساب مع مصرف السلام الجزائر (بالمليون دج)')

    administration = fields.Text(string='الادارة')
    definition_company = fields.Text(string='التعريف بالشركة')
    analyse_secteur = fields.Text(string='تحليل قطاع عمل العميل')
    relation = fields.Text(string='تاريخ العلاقة')

    position_tax = fields.One2many('wk.position', 'workflow', string='الوضعية الجبائية والشبه جبائية')

    fournisseur = fields.One2many('wk.fournisseur', 'workflow', string='الموردين')
    client = fields.One2many('wk.client', 'workflow', string='الزبائن')

    companies = fields.One2many('wk.companies', 'workflow')
    companies_fisc = fields.One2many('wk.companies.fisc', 'workflow')

    mouvement_group = fields.One2many('wk.mouvement.group', 'workflow',
                                      string='الحركة والأعمال الجانبية للمجموعة مع مصرف السلام الجزائر (بالمليون دج)')

    bilan_id = fields.One2many('wk.bilan', 'workflow')
    bilan1_id = fields.One2many('wk.bilan.cat1', 'workflow')
    comment_cat1 = fields.Text(string='تعليق')
    bilan2_id = fields.One2many('wk.bilan.cat2', 'workflow')
    comment_cat2 = fields.Text(string='تعليق')
    bilan3_id = fields.One2many('wk.bilan.cat3', 'workflow')
    comment_cat3 = fields.Text(string='تعليق')
    bilan4_id = fields.One2many('wk.bilan.cat4', 'workflow')
    comment_cat4 = fields.Text(string='تعليق')
    bilan5_id = fields.One2many('wk.bilan.cat5', 'workflow')
    comment_cat5 = fields.Text(string='تعليق')

    tcr_id = fields.Many2one('import.ocr.tcr', string='TCR')
    passif_id = fields.Many2one('import.ocr.passif', string='Passif')
    actif_id = fields.Many2one('import.ocr.actif', string='Actif')

    tcr1_id = fields.Many2one('import.ocr.tcr', string='TCR')
    passif1_id = fields.Many2one('import.ocr.passif', string='Passif')
    actif1_id = fields.Many2one('import.ocr.actif', string='Actif')

    tcr_group = fields.Many2one('import.ocr.tcr', string='TCR')
    passif_group = fields.Many2one('import.ocr.passif', string='Passif')
    actif_group = fields.Many2one('import.ocr.actif', string='Actif')

    recap_ids = fields.One2many('wk.recap', 'workflow')
    var_ids = fields.One2many('wk.variable', 'workflow')

    facitlite_existante = fields.One2many('wk.facilite.existante', 'workflow')

    fin_max_ca = fields.Float(string='الحد الاقصى لتمويل الاستغلال بناءا على رقم الاعمال')
    fin_max_bfr = fields.Float(string='الحد الاقصى لتمويل الاستغلال بناء على احتياجات راس المال العامل')
    fin_max_caf = fields.Float(string='الحد الاقصىي للتمويل متوسط الاجل بناءا على قدرة التمويل الذاتي')
    fin_achat = fields.Char(string='تمويل المشتريات')
    fin_collecte = fields.Char(string='تمويل فترة التحصيل')

    recommandation_analyste_fin = fields.Text(string='توصية المحلل المالي')
    recommandation_analyste_fin_related = fields.Text(string='توصية المحلل المالي', related='recommandation_analyste_fin')
    facilite_propose = fields.One2many('wk.facilite.propose', 'workflow', string='التسهيلات المقترحة')
    facilite_propose_related = fields.One2many('wk.facilite.propose', 'workflow', string='التسهيلات المقترحة', related='facilite_propose')
    garantie_ids = fields.Many2many('wk.garanties', string='الضمانات المقترحة')
    garantie_ids_related = fields.Many2many('wk.garanties', string='الضمانات المقترحة', related='garantie_ids')
    recommandation_dir_fin = fields.Text(string='راي مدير ادارة التمويلات')
    recommandation_dir_fin_related = fields.Text(string='راي مدير ادارة التمويلات', related='recommandation_dir_fin')

    """******THIRD STEP*****"""
    demandes_leasing = fields.One2many('wk.leasing', 'workflow', string='الطلب')
    description_achat = fields.Text(string='وصف العتاد')
    objet_demande = fields.Text(string='الغرض من الطلب')
    projet_client = fields.Text(string='نبذة عن مشروع المتعامل')
    avantage_projet = fields.Text(string='مزايا المشروع')
    etude_predict = fields.Text(string='معطيات الدراسة التنبؤية')

    recomm_leasing = fields.One2many('wk.leasing.recom', 'workflow', string='Recommendation of the rental approval cell')
    recomm_leasing_related = fields.One2many('wk.leasing.recom', 'workflow', string='Recommendation of the rental approval cell', related='recomm_leasing')
    garantie_leasing = fields.Many2many('wk.garanties', 'garantie_leasing_rel',  string='الضمانات المقترحة')
    garantie_leasing_related = fields.Many2many('wk.garanties', 'garantie_leasing_rel',  string='الضمانات المقترحة', related='garantie_leasing')
    tcr_leasing = fields.Many2one('tcr.analysis.import', string='TCR')
    bilan_leasing = fields.Many2one('bilan.general', string='Actif & Passif')
    # first step of the workflow

    chiffre_affaire_actuel = fields.Float(string='رأس المال الحالي')
    last_scoring = fields.Integer(string='التنقيط السابق')
    current_scoring = fields.Integer(string='التنقيط الحالي')
    date_ouverture_compte = fields.Date(string='تاريخ فتح الحساب',related='nom_client.date_ouverture_compte')
    interet_demande = fields.Char(string='الغرض من الطلب')
    product = fields.Many2many('wk.product', string='منتجات المصرف')
    # second step of the workflow
    rapport_dir_commercial = fields.Text(string='توصية مدير إدارة الاعمال التجارية')

    risk_scoring = fields.Many2one('risk.scoring', string='إدارة المخاطر')
    resultat_scoring = fields.Integer(string='التنقيط الاجمالي', related='risk_scoring.resultat_scoring')

    recommandation_vice_dir_fin = fields.Text(string='توصية نائب المدير العام')

    recommandation_fin_grp = fields.Text(string='توصية لجنة التمويلات')
    recommandation_fin_grp_related = fields.Text(string='توصية لجنة التمويلات', related='recommandation_fin_grp')

    doc_1 = fields.Binary(string='رهن حيازي على القاعدة التجارية')
    doc_2 = fields.Binary(string="امضاء شهادة التنازل في تمويل الذمم المدنية للعقد (LCAC Lettre de Cession d'Antériotité des Créances) في حدود التسهيلات الممنوحة")
    doc_3 = fields.Binary(string='الكفالة التضامنية للشركاء')
    doc_4 = fields.Binary(string='امضاء سفتجة باجمالي التسهيلات')
    doc_5 = fields.Binary(string='تجبير بوليصة التامين الشامل لصالح المصرف')
    doc_6 = fields.Binary(string='رهن عقاري من الدرجة الاولى يغطي 100% من صافي التسهيلات')
    doc_7 = fields.Binary(string='تقديم الحسابات المدققة للسنة الماضية في الاجال')
    doc_8 = fields.Binary(string='تقديم الحسابات المدققة للسنة الماضية في الاجال')

    validation_gar = fields.One2many('wk.garantie.validation', 'workflow', string='المصادقة على الضمانات')

    critere_ids = fields.One2many('wk.scoring.detail', 'risk', string='المعايير الكمية', related='risk_scoring.critere_ids')

    raison_a_revoir = fields.Text(string='سبب طلب المراجعة')
    commentaire = fields.Text(string='Comment')
    state1 = fields.Many2one('wk.state.one', string='state1')
    state2 = fields.Many2one('wk.state.two', string='state2')
    state3 = fields.Many2one('wk.state.three', string='state3')
    state4 = fields.Many2one('wk.state.four', string='state4')
    state5 = fields.Many2one('wk.state.five', string='state5')
    state6 = fields.Many2one('wk.state.six', string='state6')

    sale_id = fields.Many2one('purchase.order', string='Request')

    facilite_final_fin = fields.One2many('wk.facilite.final.fin', 'workflow', string='التسهيلات المقترحة')
    facilite_final_leasing = fields.One2many('wk.facilite.final.leasing', 'workflow', string='التسهيلات المقترحة')

    plafond = fields.Float(string='Plafond de crédit')
    branche_notif = fields.Many2one('wk.agence', string='الفرع')
    taux_change = fields.Float(string='1$ = ?DA: سعر الصرف', default=1)
    annee_fiscal = fields.Integer(string='السنة المالية', default=datetime.date.today().year)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('wk.credit.corporate') or _('New')
        res = super(Workflow, self).create(vals)
        list_ids = []
        for item in List_items:
            print(item)
            line = self.env['wk.kyc.details'].create({'info': item, 'workflow': res.id})
            list_ids.append(line.id)
        res.kyc = self.env['wk.kyc.details'].browse(list_ids)
        list_ids = []
        for item in list_garantie:
            line = self.env['wk.garantie.conf'].create({'info': item, 'workflow': res.id})
        for item in list_garantie_fisc:
            line = self.env['wk.garantie.fin'].create({'info': item, 'workflow': res.id})
        for item in list_autre_term:
            line = self.env['wk.garantie.autres'].create({'info': item, 'workflow': res.id})

        for item in List_risque:
            line = self.env['wk.risque.line'].create({'declaration': item, 'workflow': res.id})
            list_ids.append(line.id)
        res.risque_central = self.env['wk.risque.line'].browse(list_ids)
        list_ids = []
        for item in list_mouvement:
            line = self.env['wk.mouvement'].create({'mouvement': item, 'workflow': res.id})
            list_ids.append(line.id)
        res.mouvement = self.env['wk.mouvement'].browse(list_ids)
        list_ids = []
        for item in List_position:
            line = self.env['wk.position'].create({'name': item, 'workflow': res.id})
            list_ids.append(line.id)
        res.position_tax = self.env['wk.position'].browse(list_ids)
        list_ids = []
        for item in list_fisc:
            line = self.env['wk.companies.fisc'].create({'declaration': item, 'workflow': res.id})
            list_ids.append(line.id)
        res.companies_fisc = self.env['wk.companies.fisc'].browse(list_ids)
        list_ids = []
        count = 1
        for item in list_recap:
            line = self.env['wk.recap'].create({'declaration': item, 'workflow': res.id, 'sequence': count})
            list_ids.append(line.id)
            count += 1
        res.recap_ids = self.env['wk.recap'].browse(list_ids)
        list_ids = []
        count = 1
        for item in list_var:
            line = self.env['wk.variable'].create({'var': item, 'workflow': res.id, 'sequence': count})
            list_ids.append(line.id)
            count += 1
        res.var_ids = self.env['wk.variable'].browse(list_ids)
        list_ids = []
        count = 1
        for index, item in list_bilan:
            line = self.env['wk.bilan'].create({'declaration': item,
                                                'categorie': index,
                                                'workflow': res.id,
                                                'sequence': count})
            count += 1
            list_ids.append(line.id)
        res.bilan_id = self.env['wk.bilan'].browse(list_ids)
        list_ids = []
        for item in list_poste:
            line = self.env['wk.nombre.employee'].create({'name': item,
                                                          'workflow': res.id})
            list_ids.append(line.id)
        res.employees = self.env['wk.nombre.employee'].browse(list_ids)
        list_ids = []
        for item in list_siege:
            print(item)
            line = self.env['wk.siege'].create({'name': item,
                                                'workflow': res.id})
            list_ids.append(line.id)
        res.sieges = self.env['wk.siege'].browse(list_ids)
        list_ids = []
        for item in list_situation:
            print(item)
            line = self.env['wk.situation.fin'].create({'type': item,
                                                        'workflow': res.id})
            list_ids.append(line.id)
        res.situations_fin = self.env['wk.situation.fin'].browse(list_ids)
        self.env['wk.tracking'].create({'workflow': res.id,
                                        'date_debut': res.date,
                                        'state': '1', })
        return res

    def create_tcr_leasing(self):
        for rec in self:
            if not rec.tcr_leasing:
                view_id = self.env.ref('financial_modeling.tcr_analysis_import_view_form').id
                return {
                    'name': 'TCR',
                    'res_model': 'tcr.analysis.import',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'parent_id': rec.id},
                }

    def create_bilan_leasing(self):
        for rec in self:
            if not rec.bilan_leasing:
                view_id = self.env.ref('financial_modeling.bilan_general_view_form').id
                return {
                    'name': 'Bilan Generale',
                    'res_model': 'bilan.general',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'default_tcr_id': rec.tcr_leasing.id,
                                'parent_id': rec.id},
                }

    def create_viz(self):
        for rec in self:
            line1 = rec.situations_fin.filtered(lambda l: l.type == 'صافي الارباح')
            line2 = rec.situations_fin.filtered(lambda l: l.type == 'رقم الأعمال')
            data1 = [line1.year3, line1.year2, line1.year1]
            data2 = [line2.year3, line2.year2, line2.year1]
            rec.visualisation = view_viz(data1, data2)

    def get_historic(self):
        for rec in self:
            rec.show = True
            demandes = self.env['wk.workflow'].search([('nom_client', '=', rec.nom_client)])
            if demandes:
                rec.demandes = demandes

    def hide_docs(self):
        for rec in self:
            print(rec.hide_documents)
            rec.hide_documents = not rec.hide_documents

    def action_create_tcr(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }

    def action_create_tcr1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 2}
            }

    def action_create_actif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }

    def action_create_actif1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 2}
            }

    def action_create_passif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }

    def action_create_passif1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 2}
            }

    def create_tcr_group(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }

    def create_actif_group(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }

    def create_passif_group(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id, 'year': 1}
            }
    def import_data(self):
        for rec in self:
            if rec.tcr_id.state != 'valide' or rec.actif_id.state != 'valide' or rec.passif_id.state != 'valide':
                raise ValidationError("Vous devriez d'abord valider les bilans")
            else:
                bilan_1 = rec.bilan_id.filtered(lambda r: r.sequence == 1)
                # total I حقوق الملكية
                passif_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                passif1_1 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                bilan_1.write({'year_4': passif_1.montant_n,
                               'year_3': passif_1.montant_n1,
                               'year_2': passif1_1.montant_n,
                               'year_1': passif1_1.montant_n1})

                # capital emis رأس المال
                bilan_2 = rec.bilan_id.filtered(lambda r: r.sequence == 2)
                passif_2 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 2)
                passif1_2 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 2)
                bilan_2.write({'year_4': passif_2.montant_n,
                               'year_3': passif_2.montant_n1,
                               'year_2': passif1_2.montant_n,
                               'year_1': passif1_2.montant_n1,
                               })
                # Passif - Autres capitaux propres - report à nouveau نتائج متراكمة
                bilan_3 = rec.bilan_id.filtered(lambda r: r.sequence == 3)
                passif_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 8)
                passif1_3 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 8)
                bilan_3.write({'year_4': passif_3.montant_n,
                               'year_3': passif_3.montant_n1,
                               'year_2': passif1_3.montant_n,
                               'year_1': passif1_3.montant_n1})
                # Passif - Total II + Total III مجموع المطلوبات
                bilan_4 = rec.bilan_id.filtered(lambda r: r.sequence == 4)
                passif_4 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                passif1_4 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                passif_4_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                passif1_4_1 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                bilan_4.write({'year_4': (passif_4.montant_n + passif_4_1.montant_n),
                               'year_3': (passif_4.montant_n1 + passif_4_1.montant_n1),
                               'year_2': (passif1_4.montant_n + passif1_4_1.montant_n),
                               'year_1': (passif1_4.montant_n1 + passif1_4_1.montant_n1)})

                # Passif - Trésorerie passif التزامات بنكية قصيرة الأجل
                bilan_5 = rec.bilan_id.filtered(lambda r: r.sequence == 5)
                passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif1_5 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                bilan_5.write({'year_4': passif_5.montant_n,
                               'year_3': passif_5.montant_n1,
                               'year_2': passif1_5.montant_n,
                               'year_1': passif1_5.montant_n1})

                # Passif - Emprunts et dettes financières التزامات بنكية متوسطة الأجل
                bilan_6 = rec.bilan_id.filtered(lambda r: r.sequence == 6)
                passif_6 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif1_6 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                bilan_6.write({'year_4': passif_6.montant_n,
                               'year_3': passif_6.montant_n1,
                               'year_2': passif1_6.montant_n,
                               'year_1': passif1_6.montant_n1})

                # Passif - Fournisseurs et comptes rattachés تسهيلات الموردين
                bilan_7 = rec.bilan_id.filtered(lambda r: r.sequence == 7)
                passif_7 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                passif1_7 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                var_5 = rec.var_ids.filtered(lambda r: r.sequence == 5)
                bilan_7.write({'year_4': passif_7.montant_n,
                               'year_3': passif_7.montant_n1,
                               'year_2': passif1_7.montant_n,
                               'year_1': passif1_7.montant_n1})

                var_5.write({'montant': passif_7.montant_n})

                # Passif - Impôts مستحقات ضرائب
                bilan_8 = rec.bilan_id.filtered(lambda r: r.sequence == 8)
                passif_8 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                passif1_8 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                bilan_8.write({'year_4': passif_8.montant_n,
                               'year_3': passif_8.montant_n1,
                               'year_2': passif1_8.montant_n,
                               'year_1': passif1_8.montant_n1,
                               })
                # Passif - Autres dettes مطلوبات أخرى متداولة
                bilan_25 = rec.bilan_id.filtered(lambda r: r.sequence == 9)
                passif_8 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                passif1_8 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                bilan_25.write({'year_4': passif_8.montant_n,
                                   'year_3': passif_8.montant_n1,
                                   'year_2': passif1_8.montant_n1,
                                   'year_1': passif1_8.montant_n1,
                                })

                # (Emprunts et dettes financières passif + Trésorerie passif - Trésorerie coté actif ) / Total I coté passif نسبة المديونية Leverage

                bilan_9 = rec.bilan_id.filtered(lambda r: r.sequence == 10)
                actif_1 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                actif1_1 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                bilan_9.write({'year_4': (passif_6.montant_n + passif_5.montant_n - actif_1.montant_n) / passif_1.montant_n if passif_1.montant_n != 0 else 0,
                               'year_3': (passif_6.montant_n1 + passif_5.montant_n1 - actif_1.montant_n1) / passif_1.montant_n1 if passif_1.montant_n1 != 0 else 0,
                               'year_2': (passif1_6.montant_n + passif1_5.montant_n - actif1_1.montant_n) / passif1_1.montant_n if passif1_1.montant_n != 0 else 0,
                               'year_1': (passif1_6.montant_n1 + passif1_5.montant_n1 - actif1_1.montant_n1) / passif1_1.montant_n1 if passif1_1.montant_n1 != 0 else 0,
                               })

                # Passif - Total général passif I+II+III مجموع الميزانية

                passif_12 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                passif1_12 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                bilan_10 = rec.bilan_id.filtered(lambda r: r.sequence == 11)
                bilan_10.write({'year_4': passif_12.montant_n,
                                'year_3': passif_12.montant_n1,
                                'year_2': passif1_12.montant_n,
                                'year_1': passif1_12.montant_n1,
                                })

                # TCR - Chiffre d`affaire net رقم الأعمال
                tcr_1 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                tcr1_1 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                bilan_11 = rec.bilan_id.filtered(lambda r: r.sequence == 12)
                var_1 = rec.var_ids.filtered(lambda r: r.sequence == 1)
                bilan_11.write({'year_4': tcr_1.montant_n,
                                'year_3': tcr_1.montant_n1,
                                'year_2': tcr1_1.montant_n,
                                'year_1': tcr1_1.montant_n1})
                var_1.write({'montant': tcr_1.montant_n})

                # TCR- Excédent brut d`exploitation   EBITDA
                tcr_2 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                tcr1_2 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                bilan_12 = rec.bilan_id.filtered(lambda r: r.sequence == 13)
                bilan_12.write({'year_4': tcr_2.montant_n,
                               'year_3': tcr_2.montant_n1,
                               'year_2': tcr1_2.montant_n,
                               'year_1': tcr1_2.montant_n1})

                # TCR - Résultat net de l`exercice   صافي الأرباح
                bilan_13 = rec.bilan_id.filtered(lambda r: r.sequence == 14)
                tcr_3 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                tcr1_3 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                bilan_13.write({'year_4': tcr_3.montant_n,
                                'year_3': tcr_3.montant_n1,
                                'year_2': tcr1_3.montant_n1,
                                'year_1': tcr1_3.montant_n1})

                # TCR (Résultat net de l`exercice / Chiffre d`affaire net) * 100   صافي الأرباح/المبيعات
                bilan_14 = rec.bilan_id.filtered(lambda r: r.sequence == 15)
                bilan_14.write({'year_4': tcr_3.montant_n / tcr_1.montant_n if tcr_1.montant_n != 0 else 0,
                                'year_3': tcr_3.montant_n1 / tcr_1.montant_n1 if tcr_1.montant_n1 != 0 else 0,
                                'year_2': tcr1_3.montant_n / tcr1_1.montant_n if tcr1_1.montant_n != 0 else 0,
                                'year_1': tcr1_3.montant_n1 / tcr1_1.montant_n1 if tcr1_1.montant_n1 != 0 else 0})

                # TCR (Résultat net de l`exercice + dotations aux amortissements)   قدرة التمويل الذاتي CAF
                bilan_15 = rec.bilan_id.filtered(lambda r: r.sequence == 16)
                tcr_4 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
                tcr1_4 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
                bilan_15.write({'year_4': tcr_3.montant_n + tcr_4.montant_n,
                                'year_3': tcr_3.montant_n1 + tcr_4.montant_n1,
                                'year_2': tcr1_3.montant_n + tcr1_4.montant_n,
                                'year_1': tcr1_3.montant_n1 + tcr1_4.montant_n1,
                                })

                # Passif (Total I + Total II) - Total actif non courant   صافي رأس المال العامل
                actif_2 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
                actif1_2 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
                bilan_16 = rec.bilan_id.filtered(lambda r: r.sequence == 17)
                bilan_16.write({'year_4': (passif_1.montant_n + passif_1.montant_n) - actif_2.montant_n,
                                'year_3': (passif_1.montant_n1 + passif_1.montant_n1) - actif_2.montant_n1,
                                'year_2': (passif1_1.montant_n + passif1_1.montant_n) - actif1_2.montant_n,
                                'year_1': (passif1_1.montant_n1 + passif1_1.montant_n1) - actif1_2.montant_n1,
                                })

                # Total actif courant actif  - Total III passif   احتياجات رأس المال العامل
                bilan_17 = rec.bilan_id.filtered(lambda r: r.sequence == 18)
                actif_3 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
                actif1_3 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
                bilan_17.write({'year_4': actif_3.montant_n - passif_4_1.montant_n,
                                'year_3': actif_3.montant_n1 - passif_4_1.montant_n1,
                                'year_2': actif1_3.montant_n - passif1_4_1.montant_n,
                                'year_1': actif1_3.montant_n1 - passif1_4_1.montant_n1,
                                })
                bilan_17.unlink()
                # Total actif courant / Total III passif   نسبة التداول (السيولة)
                bilan_18 = rec.bilan_id.filtered(lambda r: r.sequence == 19)
                bilan_18.write({'year_4':  actif_3.montant_n / passif_4_1.montant_n if passif_4_1.montant_n != 0 else 0,
                                'year_3': actif_3.montant_n1 / passif_4_1.montant_n1 if passif_4_1.montant_n1 != 0 else 0,
                                'year_2': actif1_3.montant_n / passif1_4_1.montant_n if passif1_4_1.montant_n != 0 else 0,
                                'year_1': actif1_3.montant_n1 / passif1_4_1.montant_n1 if passif1_4_1.montant_n1 != 0 else 0})

                # (Total actif courant - stock et encours) / Total III passif نسبة السيولة السريعة
                actif_4 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif1_4 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                bilan_19 = rec.bilan_id.filtered(lambda r: r.sequence == 20)
                bilan_19.write({'year_4': (actif_3.montant_n - actif_4.montant_n) / passif_4_1.montant_n if passif_4_1.montant_n != 0 else 0,
                                'year_3': (actif_3.montant_n1 - actif_4.montant_n1) / passif_4_1.montant_n1 if passif_4_1.montant_n1 != 0 else 0,
                                'year_2': (actif1_3.montant_n - actif1_4.montant_n) / passif1_4_1.montant_n if passif1_4_1.montant_n != 0 else 0,
                                'year_1': (actif1_3.montant_n1 - actif1_4.montant_n1) / passif1_4_1.montant_n1 if passif1_4_1.montant_n1 != 0 else 0,
                                })


                # Actif - Clients حقوق عند الزبائن
                actif_5 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif1_5 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                bilan_20 = rec.bilan_id.filtered(lambda r: r.sequence == 21)
                var_3 = rec.var_ids.filtered(lambda r: r.sequence == 3)
                bilan_20.write({'year_4': actif_5.montant_n,
                                'year_3': actif_5.montant_n1,
                                'year_2': actif1_5.montant_n,
                                'year_1': actif1_5.montant_n1,
                                })
                var_3.write({'montant': actif_5.montant_n})

                # Actif - Stock et encours المخزون
                bilan_21 = rec.bilan_id.filtered(lambda r: r.sequence == 22)
                bilan_21.write({'year_4': actif_4.montant_n,
                                'year_3': actif_4.montant_n1,
                                'year_2': actif1_4.montant_n,
                                'year_1': actif1_4.montant_n1,
                                })
                var_4 = rec.var_ids.filtered(lambda r: r.sequence == 4)
                var_4.write({'montant': actif_4.montant_n})

                # Actif (Stock et encours * 360) / (achat de marchandises vendue + matières premières) TCR متوسط دوران المخزون (يوم)
                tcr_5 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                tcr1_5 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                tcr_6 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
                tcr1_6 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
                var_2 = rec.var_ids.filtered(lambda r: r.sequence == 2)
                bilan_22 = rec.bilan_id.filtered(lambda r: r.sequence == 23)
                bilan_22.write({'year_4': (actif_4.montant_n * 360) / (tcr_5.montant_n + tcr_6.montant_n) if (tcr_5.montant_n + tcr_6.montant_n) != 0 else 0,
                                'year_3': (actif_4.montant_n1 * 360) / (tcr_5.montant_n1 + tcr_6.montant_n1) if (tcr_5.montant_n1 + tcr_6.montant_n1) != 0 else 0,
                                'year_2': (actif1_4.montant_n * 360) / (tcr1_5.montant_n + tcr1_6.montant_n) if (tcr1_5.montant_n + tcr1_6.montant_n) != 0 else 0,
                                'year_1': (actif1_4.montant_n1 * 360) / (tcr1_5.montant_n1 + tcr1_6.montant_n1) if (tcr1_5.montant_n1 + tcr1_6.montant_n1) != 0 else 0,
                                })
                var_2.write({'montant': (tcr_5.montant_n + tcr_6.montant_n)})
                recap_2 = rec.recap_ids.filtered(lambda r: r.sequence == 2)
                recap_2.write({'montant': bilan_22.year_4})

                # Actif (Clients * 360) / Chiffre d`affaires net TCR متوسط فترة التحصيل (يوم)
                bilan_23 = rec.bilan_id.filtered(lambda r: r.sequence == 24)
                bilan_23.write({'year_4': (actif_5.montant_n * 360) / tcr_1.montant_n if tcr_1.montant_n != 0 else 0,
                                'year_3': (actif_5.montant_n1 * 360) / tcr_1.montant_n1 if tcr_1.montant_n1 != 0 else 0,
                                'year_2': (actif1_5.montant_n * 360) / tcr1_1.montant_n if tcr1_1.montant_n != 0 else 0,
                                'year_1': (actif1_5.montant_n1 * 360) / tcr1_1.montant_n1 if tcr1_1.montant_n1 != 0 else 0})

                recap_1 = rec.recap_ids.filtered(lambda r: r.sequence == 1)
                recap_1.write({'montant': bilan_23.year_4})

                # Passif (Fournisseurs et comptes rattachés * 360) / (achat de marchandises vendue + matières premières) TCR متوسط مدة تسهيلات الموردين (يوم)
                bilan_24 = rec.bilan_id.filtered(lambda r: r.sequence == 25)

                bilan_24.write({'year_4': (passif_7.montant_n * 360) / (tcr_5.montant_n + tcr_6.montant_n) if (tcr_5.montant_n + tcr_6.montant_n) != 0 else 0,
                                'year_3': (passif_7.montant_n1 * 360) / (tcr_5.montant_n1 + tcr_6.montant_n1) if (tcr_5.montant_n1 + tcr_6.montant_n1) != 0 else 0,
                                'year_2': (passif1_7.montant_n * 360) / (tcr1_5.montant_n + tcr1_6.montant_n) if (tcr1_5.montant_n + tcr1_6.montant_n) != 0 else 0,
                                'year_1': (passif1_7.montant_n1 * 360) / (tcr1_5.montant_n1 + tcr1_6.montant_n1) if (tcr1_5.montant_n1 + tcr1_6.montant_n1) != 0 else 0,
                                })

                recap_3 = rec.recap_ids.filtered(lambda r: r.sequence == 3)
                recap_3.write({'montant': bilan_24.year_4})
                recap_4 = rec.recap_ids.filtered(lambda r: r.sequence == 4)
                recap_4.write({'montant': (bilan_16.year_4 * 360) / tcr_1.montant_n if tcr_1.montant_n != 0 else 0})

    def action_create_risk(self):
        for rec in self:
            view_id = self.env.ref('dept_wk.view_risk_scoring_form').id
            return {
                'name': 'Risk Scoring',
                'domain': [('parent_id', '=', rec.id)],
                'res_model': 'risk.scoring',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'default_parent_id': rec.id,
                            'parent_id': rec.id,
                            'default_tcr_id': rec.tcr_id.id,
                            'default_actif_id': rec.actif_id.id,
                            'default_passif_id': rec.passif_id.id}
            }

    def create_viz2(self):
        for rec in self:
            line1 = rec.bilan_id.filtered(lambda l: l.declaration == 'صافي الارباح')
            line2 = rec.bilan_id.filtered(lambda l: l.declaration == 'رقم الأعمال')
            line3 = rec.bilan_id.filtered(lambda l: l.declaration == 'EBITDA')
            data1 = [line1.year_1, line1.year_2, line1.year_3, line1.year_4]
            data2 = [line2.year_1, line2.year_2, line2.year_3, line2.year_4]
            data3 = [line3.year_1, line3.year_2, line3.year_3, line3.year_4]

            label1 = 'Net profits'
            label2 = 'Turnover'
            year = ["N-3", "N-2", "N-1", "N"]
            fig, ax = plt.subplots()
            width = 0.12
            X_axis = np.arange(len(year))
            rects1 = ax.bar(X_axis - width, data1, width, color="yellow", label=label1)
            rects2 = ax.bar(X_axis, data2, width, color="orange", label=label2)
            rects3 = ax.bar(X_axis + width, data3, width, color="red", label="EBITDA")
            ax.set_ylabel('Montant')
            ax.set_title('Montant par année')
            ax.set_xticks(X_axis + width, year)
            ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.visualisation1 = base64.b64encode(buf.getvalue())
            buf.close()

    def create_viz3(self):
        for rec in self:
            line1 = rec.companies_fisc.filtered(lambda l: l.declaration == 'صافي الارباح')
            line2 = rec.companies_fisc.filtered(lambda l: l.declaration == 'رقم الأعمال')
            line3 = rec.companies_fisc.filtered(lambda l: l.declaration == 'EBIDTA')
            data1 = [line1.year_1, line1.year_2, line1.year_3, line1.year_4]
            data2 = [line2.year_1, line2.year_2, line2.year_3, line2.year_4]
            data3 = [line3.year_1, line3.year_2, line3.year_3, line3.year_4]
            label1 = "صافي الارباح"
            label2 = "رقم الأعمال"
            year = ["N-3", "N-2", "N-1", "N"]
            fig, ax = plt.subplots()
            width = 0.12
            X_axis = np.arange(len(year))
            rects1 = ax.bar(X_axis - width, data1, width, color="yellow", label=label1)
            rects2 = ax.bar(X_axis, data2, width, color="orange", label=label2)
            rects3 = ax.bar(X_axis + width, data3, width, color="red", label="EBITDA")
            ax.set_ylabel('Montant')
            ax.set_title('Montant par année')
            ax.set_xticks(X_axis + width, year)
            ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.visualisation2 = base64.b64encode(buf.getvalue())
            buf.close()

    def find_facil_prop(self):
        for rec in self:
            ca = rec.bilan_id.filtered(lambda r: r.sequence == 12)
            rec.fin_max_ca = ca.year_4 * 0.35
            bfr = rec.bilan_id.filtered(lambda r: r.sequence == 18)
            rec.fin_max_bfr = bfr.year_4 * 0.65
            caf = rec.bilan_id.filtered(lambda r: r.sequence == 16)
            rec.fin_max_caf = caf.year_4 * 0.33 * 5
            stock = rec.bilan_id.filtered(lambda r: r.sequence == 23)
            if stock.year_4 > 120:
                rec.fin_achat = 'يفضل عدم تمويل المشتريات (متوسط دوران المخزون)'
            else:
                rec.fin_achat = str(rec.var_ids.filtered(lambda r: r.sequence == 2).montant)
            collecte = rec.bilan_id.filtered(lambda r: r.sequence == 24)
            if collecte.year_4 < 60:
                rec.fin_collecte = 'الشركة لا تحتاج لتمويل فترة التحصيل'
            elif 119 >= collecte.year_4 >= 61:
                client = rec.bilan_id.filtered(lambda r: r.sequence == 21)
                rec.fin_collecte = str(client.year_4 * 0.35)
            elif 179 >= collecte.year_4 >= 120:
                client = rec.bilan_id.filtered(lambda r: r.sequence == 21)
                rec.fin_collecte = str(client.year_4 * 0.25)
            else:
                client = rec.bilan_id.filtered(lambda r: r.sequence == 21)
                rec.fin_collecte = str(client.year_4 * 0.2)

    def get_documents(self):
        for rec in self:
            document = self.env['wk.document.check']
            if rec.demande_facilite:
                doc = document.search([('filename', '=', 'طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة'),
                                       ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.demande_facilite,
                                 'filename': 'طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة'})
                else:
                    doc.write({'document': rec.demande_facilite})
            if rec.budget_3_ans:
                doc = document.search([('filename', '=', 'الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس'),
                                       ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.budget_3_ans,
                                 'filename': 'الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس'})
                else:
                    doc.write({'document': rec.budget_3_ans})
            if rec.budget_previsionnel:
                doc = document.search(
                    [('filename', '=', ' الميزانية الافتتاحية و الميزانية المتوقعة للسنة المراد تمويلها موقعة من طرف الشركة (حديثة النشأة)'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.budget_previsionnel,
                                 'filename': ' الميزانية الافتتاحية و الميزانية المتوقعة للسنة المراد تمويلها موقعة من طرف الشركة (حديثة النشأة)'})
                else:
                    doc.write({'document': rec.budget_previsionnel})
            if rec.schema_financement:
                doc = document.search(
                    [('filename', '=',
                      'مخطط تمويل الاستغلال مقسم الى أرباع السنة للسنة المراد تمويلها'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.schema_financement,
                                 'filename': 'مخطط تمويل الاستغلال مقسم الى أرباع السنة للسنة المراد تمويلها'})
                else:
                    doc.write({'document': rec.schema_financement})
            if rec.document_activite:
                doc = document.search(
                    [('filename', '=',
                      ' المستندات و الوثائق المتعلقة بنشاط الشركة ( عقود، صفقات ،  طلبيات ، ... )'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.document_activite,
                                 'filename': ' المستندات و الوثائق المتعلقة بنشاط الشركة ( عقود، صفقات ،  طلبيات ، ... )'})
                else:
                    doc.write({'document': rec.document_activite})
            if rec.proces_reg_irreg:
                doc = document.search(
                    [('filename', '=',
                      'محاضر الجمعيات العادية و الغير العادية للأشخاص المعنويين'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.proces_reg_irreg,
                                 'filename': 'محاضر الجمعيات العادية و الغير العادية للأشخاص المعنويين'})
                else:
                    doc.write({'document': rec.proces_reg_irreg })
            if rec.copie_registre_commerce:
                doc = document.search(
                    [('filename', '=',
                      'نسخة مصادق عليها من السجل التجاري'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.copie_registre_commerce,
                                 'filename': 'نسخة مصادق عليها من السجل التجاري'})
                else:
                    doc.write({'document': rec.copie_registre_commerce})
            if rec.copie_statut:
                document.create({'workflow': rec.id,
                                 'document': rec.copie_statut,
                                 'filename': 'نسخة مصادق عليها من القانون الأساسي للشركة'})
            if rec.deliberation:
                doc = document.search(
                    [('filename', '=',
                      'مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.deliberation,
                                 'filename': 'مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية'})

                else:
                    doc.write({'document': rec.copie_registre_commerce})
            if rec.bulletin_officiel:
                doc = document.search(
                    [('filename', '=',
                      'نسخة مصادق عليها من النشرة الرسمية للإعلانات القانونية'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.bulletin_officiel,
                                 'filename': 'نسخة مصادق عليها من النشرة الرسمية للإعلانات القانونية'})
                else:
                    doc.write({'document': rec.bulletin_officiel})
            if rec.contrat_propriete:
                doc = document.search(
                    [('filename', '=',
                      'نسخة طبق الأصل لعقد ملكية أو استئجار المحلات ذات الاستعمال المهني'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.contrat_propriete,
                                 'filename': 'نسخة طبق الأصل لعقد ملكية أو استئجار المحلات ذات الاستعمال المهني'})
                else:
                    doc.write({'document': rec.contrat_propriete})
            if rec.attestation_fiscal:
                doc = document.search(
                    [('filename', '=',
                      ' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.attestation_fiscal,
                                 'filename': ' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)'})
                else:
                    doc.write({'document': rec.attestation_fiscal})
            if rec.declaration_central_risque:
                doc = document.search(
                    [('filename', '=',
                      'استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.declaration_central_risque,
                                 'filename': 'استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)'})
                else:
                    doc.write({'document': rec.declaration_central_risque})
            if rec.autre_document:
                doc = document.search(
                    [('filename', '=',
                      'ملف اخر'),
                     ('workflow', '=', rec.id)])
                if not doc:
                    document.create({'workflow': rec.id,
                                 'document': rec.autre_document,
                                 'filename': 'ملف اخر'})
                else:
                    doc.write({'document': rec.autre_document})

    def action_retour(self):
        view_id = self.env.ref('dept_wk.retour_wizard_form').id
        return {
            'name': 'سبب طلب المراجعة',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wk.wizard.retour',
            'view_id': view_id,
            'target': 'new',
            'context': {'actual_state': int(self.state)}
        }

    def validate_agence(self):
        for rec in self:
            '''if not rec.demande_facilite:
                raise ValidationError('طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة')
            if not rec.budget_3_ans:
                raise ValidationError('الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس')
            if not rec.copie_registre_commerce:
                raise ValidationError('مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية')
            if not rec.copie_statut:
                raise ValidationError('نسخة مصادق عليها من القانون الأساسي للشركة')
            if not rec.deliberation:
                raise ValidationError('مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية')
            if not rec.attestation_fiscal:
                raise ValidationError(
                    ' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)')
            if not rec.declaration_central_risque:
                raise ValidationError('استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)')
            rec.get_documents()'''
            state1 = self.env['wk.state.one'].search([('workflow', '=', rec.id)])
            if not state1:
                state1 = self.env['wk.state.one'].create({'workflow': rec.id})
            else:
                state1.write({'workflow': rec.id})
            rec.state1 = state1
            rec.state = '2'
            rec.raison_a_revoir = False

    def validate_dir_agence(self):
        for rec in self:
            if self.env.user.has_group('dept_wk.dept_wk_group_responsable_agence'):
                rec.state = '3'
                rec.raison_a_revoir = False

    def open_state1(self):
        for rec in self:
            self.ensure_one()
            state1 = self.env['wk.state.one'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state1_form').id
            if state1:
                return {
                    'name': "الفرع",
                    'res_model': 'wk.state.one',
                    'res_id': state1.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def validate_commercial(self):
        for rec in self:
            state3 = self.env['wk.state.three'].search([('workflow', '=', rec.id)])
            if not state3:
                state3 = self.env['wk.state.three'].create({
                    'workflow': rec.id,
                    'date': rec.date,
                    'name': rec.name})
            else:
                state3.write({
                    'date': rec.date})
            rec.state3 = state3
            rec.state = '5'
            rec.raison_a_revoir = False


    def open_state2(self):
        for rec in self:
            self.ensure_one()
            state2 = self.env['wk.state.two'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state2_form').id
            if state2:
                return {
                    'name': "مديرية التمويلات",
                    'res_model': 'wk.state.two',
                    'res_id': state2.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def get_swot(self):
        for rec in self:
            swot = self.env['wk.swot'].search([('workflow', '=', rec.id)])
            if not swot:
                swot = self.env['wk.swot'].create({'workflow': rec.id})
            view_id = self.env.ref('dept_wk.view_wk_swot_form').id
            if not self._context.get('warning'):
                return {
                    'name': 'SWOT',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'wk.swot',
                    'res_id': swot.id,
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def validate_financial(self):
        for rec in self:
            print('Hi')
            state2 = self.env['wk.state.two'].search([('workflow', '=', rec.id)])
            if not state2:
                state2 = self.env['wk.state.two'].create({
                    'workflow': rec.id,
                    'date': rec.date,
                    'name': rec.name})
            else:
                state2.write({
                    'date': rec.date})
            rec.state2 = state2
            rec.state = '4'
            rec.raison_a_revoir = False


    def open_state3(self):
        for rec in self:
            self.ensure_one()
            state3 = self.env['wk.state.three'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state3_form').id
            if state3:
                return {
                    'name': "مديرية الاعمال التجارية",
                    'res_model': 'wk.state.three',
                    'res_id': state3.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def validate_scoring(self):
        for rec in self:
            state4 = self.env['wk.state.four'].search([('workflow', '=', rec.id)])
            if not state4:
                state4 = self.env['wk.state.four'].create({
                    'workflow': rec.id})
            rec.state4 = state4
            rec.state = '6'
            rec.raison_a_revoir = False

    def open_state4(self):
        for rec in self:
            self.ensure_one()
            state4 = self.env['wk.state.four'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state4_form').id
            if state4:
                return {
                    'name': "ادارة المخاطر",
                    'res_model': 'wk.state.four',
                    'res_id': state4.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def validate_vice(self):
        for rec in self:
            state5 = self.env['wk.state.five'].search([('workflow', '=', rec.id)])
            if not state5:
                state5 = self.env['wk.state.five'].create({
                    'workflow': rec.id})
            rec.state5 = state5
            rec.state = '7'
            rec.raison_a_revoir = False

    def open_state5(self):
        for rec in self:
            self.ensure_one()
            state4 = self.env['wk.state.five'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state5_form').id
            if state4:
                return {
                    'name': "نائب المدير العام",
                    'res_model': 'wk.state.five',
                    'res_id': state4.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }

    def validate_comite(self):
        for rec in self:
            state6 = self.env['wk.state.six'].search([('workflow', '=', rec.id)])
            if not state6:
                state6 = self.env['wk.state.six'].create({
                    'workflow': rec.id})
            rec.state6 = state6
            rec.state = '8'
            rec.raison_a_revoir = False

    def open_state6(self):
        for rec in self:
            self.ensure_one()
            state4 = self.env['wk.state.six'].search([('workflow', '=', rec.id)])
            view_id = self.env.ref('dept_wk.view_wk_state6_form').id
            if state4:
                return {
                    'name': "لجنة التسهيلات",
                    'res_model': 'wk.state.six',
                    'res_id': state4.id,
                    'view_mode': 'form',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'context': {'create': False,
                                'edit': False,
                                'delete': False},
                }


    def open_tracking(self):
        view_id = self.env.ref('dept_wk.view_wk_tracking_tree').id
        return {
                'name': "تتبع",
                'res_model': 'wk.tracking',
                'view_mode': 'tree',
                'view_id': view_id,
                'domain': [('workflow', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'create': False,
                            'edit': False,
                            'delete': False},
            }

    def open_sale(self):
        for rec in self:
            view_id = self.env.ref('purchase.purchase_order_form').id
            return {
                'name': "الطلب",
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'workflow_id': rec.id},
            }


class Purchase(models.Model):
    _inherit = 'purchase.order'

    workflow = fields.Many2one('wk.workflow', string='workflow')

    @api.model
    def create(self, vals):
        res = super(Purchase, self).create(vals)
        parent_id = self.env['wk.workflow'].search([('id', '=', self.env.context.get('workflow_id'))])
        if parent_id:
            parent_id.sale_id = res.id
            res.workflow = parent_id.id
        return res


def view_viz(data1, data2):
    year = ["N-2", "N-1", "N"]
    fig, ax = plt.subplots()
    width = 0.25
    print(data1, data2)
    X_axis = np.arange(len(year))
    label1 = "صافي الارباح"
    label2 = "رقم الأعمال"
    print(rcParams['font.family'])
    plt.rcParams['font.family'] = 'DejaVu Sans'
    print(rcParams['font.family'])
    rects1 = ax.bar(X_axis - (width / 2), data1, width, color="yellow", label=label1)
    rects2 = ax.bar(X_axis + (width / 2), data2, width, color="orange", label=label2)
    ax.set_ylabel('Montant')
    ax.set_title('Montant par année')
    ax.set_xticks(X_axis + width, year)
    ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))
    fig.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100)
    buf.seek(0)
    imageBase64 = base64.b64encode(buf.getvalue())
    buf.close()
    return imageBase64

