from odoo import models, fields, api, _


class AgenceConfirmed(models.Model):
    _name = 'wk.state.one'
    _description = "Données saisi par l'agence"

    workflow = fields.Many2one('wk.workflow', string='الطلب')
    date = fields.Date(string='التاريخ')
    name = fields.Char(string='Name', default='الفرع')
    assigned_to_branch = fields.Many2one('res.users', string='تم تعيينه ل', domain=lambda self: [
        ('groups_id', 'in', self.env.ref('dept_wk.dept_wk_group_agent_agence').id)])
    nom_client = fields.Char(string='اسم المتعامل')
    branche = fields.Many2one('wk.agence', string='الفرع', related='workflow.branche')
    num_compte = fields.Char(string='رقم الحساب', related='workflow.num_compte')
    date_ouverture_compte = fields.Date(string='تاريخ فتح الحساب', related='workflow.date_ouverture_compte')
    demande = fields.Many2one('wk.type.demande', string='الطلب', related='workflow.demande')
    demandes = fields.One2many('wk.historique', string="تسهيلات الشركة", related='workflow.demandes')

    nom_groupe = fields.Char(string='اسم الشركة', related='workflow.nom_groupe')
    classification = fields.Many2one('wk.classification', string="تصنيف الشركة", related='workflow.classification')
    adress_siege = fields.Char(string='عنوان المقر الاجتماعي', related='workflow.adress_siege')
    wilaya = fields.Many2one('wk.wilaya', string='الولاية', related='workflow.wilaya')
    num_registre_commerce = fields.Char(string='رقم السجل التجاري', related='workflow.num_registre_commerce')
    date_inscription = fields.Date(string='تاريخ القيد في السجل التجاري', related='workflow.date_inscription')
    date_debut_activite = fields.Date(string='تاريخ بداية النشاط', related='workflow.date_debut_activite')
    activite = fields.Many2one('wk.activite', string='النشاط', related='workflow.activite')
    gerant = fields.Many2one('res.partner',string='المسير', related='workflow.gerant')
    phone = fields.Char(string='الهاتف', related='workflow.phone')
    email = fields.Char(string='البريد الإلكتروني', related='workflow.email')
    siteweb = fields.Char(string='الموقع الالكتروني للشركة', related='workflow.siteweb')

    unit_prod = fields.Text(string='وحدات الانتاج', related='workflow.unit_prod')
    stock = fields.Text(string='المخازن', related='workflow.stock')
    prod_company = fields.Text(string='منتوجات الشركة', related='workflow.prod_company')
    politique_comm = fields.Text(string='السياسة التسويقية', related='workflow.politique_comm')
    cycle_exploit = fields.Text(string='دورة الاستغلال', related='workflow.cycle_exploit')
    concurrence = fields.Text(string='المنافسة و دراسة السوق', related='workflow.concurrence')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    forme_jur = fields.Many2one('wk.forme.jur', string='الشكل القانوني', related='workflow.forme_jur')
    chiffre_affaire = fields.Monetary(string='راس المال الشركة', currency_field='currency_id', related='workflow.chiffre_affaire')

    #FIELDS IN THE NOTEBOOK
    kyc = fields.One2many('wk.kyc.details', related='workflow.kyc')
    apropos = fields.One2many('wk.partenaire', string='نبذة عن المتعامل', related='workflow.apropos')
    gestion = fields.One2many('wk.gestion',  string='فريق التسيير', related='workflow.gestion')
    employees = fields.One2many('wk.nombre.employee', string='عدد العمال (حسب الفئة المهنية)', related='workflow.employees')
    sieges = fields.One2many('wk.siege', string='مقرات تابعة للشركة', related='workflow.sieges')
    tailles = fields.One2many('wk.taille', string='حجم و هيكل التمويلات المطلوبة', related='workflow.tailles')
    situations = fields.One2many('wk.situation',  string='الوضعية المصرفية والتزامات لدى الغير', related='workflow.situations')
    situations_fin = fields.One2many('wk.situation.fin',
                                     string='البيانات المالية المدققة للثلاث سنوات الأخيرة', related='workflow.situations_fin')
    fournisseur = fields.One2many('wk.fournisseur',  related='workflow.fournisseur')
    client = fields.One2many('wk.client',  related='workflow.client')

    politique_vente = fields.Text(string='السياسة التسويقية /البيع', related='workflow.politique_vente')
    program_invest = fields.Text(string='البرنامج الاستثماري /المشاريع التطويرية', related='workflow.program_invest')
    result_visit = fields.Text(string='نتائج الزيارة', related='workflow.result_visit')
    recommendation_visit = fields.Text(string='توصية اعضاء الوفد المشرف على الزيارة', related='workflow.recommendation_visit')
    recommendation_responsable_agence = fields.Text(string='توصية مدير الفرع')
    images = fields.One2many('wk.documents', string='الصور المرفقة' , related='workflow.images')
    weakness_ids = fields.One2many('wk.swot.weakness', related='workflow.weakness_ids')
    strength_ids = fields.One2many('wk.swot.strength', related='workflow.strength_ids')
    threat_ids = fields.One2many('wk.swot.threat', related='workflow.threat_ids')
    opportunitie_ids = fields.One2many('wk.swot.opportunitie', related='workflow.opportunitie_ids')
    documents = fields.One2many('wk.document.check', string='التاكد من الوثائق المرفقة', related='workflow.documents')


class SWOT(models.Model):
    _name = 'wk.swot'
    _description = "SWOT"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    name = fields.Char(string='name', default='SWOT')
    weakness_ids = fields.One2many('wk.swot.weakness', related='workflow.weakness_ids')
    strength_ids = fields.One2many('wk.swot.strength', related='workflow.strength_ids')
    threat_ids = fields.One2many('wk.swot.threat', related='workflow.threat_ids')
    opportunitie_ids = fields.One2many('wk.swot.opportunitie', related='workflow.opportunitie_ids')
