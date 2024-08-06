import datetime
from babel.dates import format_date, format_datetime, format_time
from odoo import models, fields, api, _

from odoo.exceptions import UserError


class Historique(models.Model):
    _name = 'wk.historique'
    _description = 'Hisotorique du client'

    type = fields.Many2one('wk.type.demande', string='نوع التسهيلات الممنوحة')
    date = fields.Date(string='تاريخ الرخصة')
    date_fin = fields.Date(string='صالحة لغاية')
    montant = fields.Float(string='المبلغ')
    garanties = fields.Many2one('wk.garanties', string='الشروط و الضمانات')


class EquipeGestion(models.Model):
    _name = 'wk.gestion'
    _description = 'Equipe de gestion'

    name = fields.Char(string='السيد(ة)')
    job = fields.Char(string='المهنة')
    niveau_etude = fields.Char(string='المستوى الدراسي')
    age = fields.Integer(string='السن')
    experience = fields.Integer(string='الخبرة المهنية')
    etape_id = fields.Many2one('wk.etape')


class Poste(models.Model):
    _name = 'wk.nombre.employee'
    _description = 'Nombre employee'

    name = fields.Char(string=' ')
    poste_permanent = fields.Integer(string='مناصب دائمة')
    poste_non_permanent = fields.Integer(string='غير دائمة')
    etape_id = fields.Many2one('wk.etape')


class SiegeSocial(models.Model):
    _name = 'wk.siege'
    _description = 'Nombre employee'

    name = fields.Char(string=' ')
    adresse = fields.Char(string='العنوان')
    nature = fields.Many2one('wk.nature.juridique', string='الطبيعة القانونية')
    etape_id = fields.Many2one('wk.etape')


class Taillefin(models.Model):
    _name = 'wk.taille'
    _description = 'La taille et la structure du financement requis'

    type_demande = fields.Many2one('wk.product', string='نوع التسهيلات')
    montant = fields.Float(string='المبلغ المطلوب')
    raison = fields.Char(string='الغرض من التمويل')
    garanties = fields.Many2many('wk.garanties', string='الضمانات المقترحة')
    etape_id = fields.Many2one('wk.etape')


class FinancementBanque(models.Model):
    _name = 'wk.fin.banque'
    _description = 'autres type de financement'

    name = fields.Char(string='نوع التمويل')


class SituationBancaire(models.Model):
    _name = 'wk.situation'
    _description = 'Situation bancaire et obligations envers autrui'

    banque = fields.Many2one('wk.banque', string='البنك')
    type_fin = fields.Many2one('wk.fin.banque', string='نوع التمويل')
    montant = fields.Float(string='المبلغ بالمليون دج')
    garanties = fields.Text(string='الضمانات الممنوحة')
    etape_id = fields.Many2one('wk.etape')


class Banque(models.Model):
    _name = 'wk.banque'

    name = fields.Char(string='Désignation', required=True, copy=False)
    code = fields.Char(string='Code', required=True, copy=False)


class SituationFinanciere(models.Model):
    _name = 'wk.situation.fin'
    _description = 'Situation financière'

    type = fields.Char(string='السنة')
    sequence = fields.Integer(string='Sequence')
    year1 = fields.Float(string='N')
    year2 = fields.Float(string='N-1')
    year3 = fields.Float(string='N-2')
    etape_id = fields.Many2one('wk.etape')


class Docs(models.Model):
    _name = 'wk.document'
    _description = 'documents'

    document = fields.Binary(string='الملف')

    @api.model
    def create(self, vals):
        res = super(Docs, self).create(vals)
        doc_checker = self.env['wk.document.check'].create({'workflow': res.workflow.id,
                                                            'document_id': res.id})
        return res

LIST = [('1', 'طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة'),
          ('2', 'الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس'),
          ('3',
           ' الميزانية الافتتاحية و الميزانية المتوقعة للسنة المراد تمويلها موقعة من طرف الشركة (حديثة النشأة)'),
          ('4', 'مخطط تمويل الاستغلال مقسم الى أرباع السنة للسنة المراد تمويلها'),
          ('5',
           ' المستندات و الوثائق المتعلقة بنشاط الشركة ( عقود، صفقات ،  طلبيات ، ... )'),
          ('6', 'محاضر الجمعيات العادية و الغير العادية للأشخاص المعنويين'),
          ('7', 'نسخة مصادق عليها من السجل التجاري'),
          ('8', 'نسخة مصادق عليها من القانون الأساسي للشركة'),
          ('9', 'مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية'),
          ('10', 'نسخة مصادق عليها من النشرة الرسمية للإعلانات القانونية'),
          ('11', 'نسخة طبق الأصل لعقد ملكية أو استئجار المحلات ذات الاستعمال المهني'),
          ('12',
           ' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)'),
          ('13', 'استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)'),
          ('14', 'آخر تقرير مدقق الحسابات'),
          ('15', 'ملف اخر'),
          ]

class DocChecker(models.Model):
    _name = 'wk.document.check'
    _description = ' check documents'


    list_document = fields.Selection(selection=LIST, string='اسم الملف')
    document = fields.Binary(string='الملف',)
    filename = fields.Char(string='الاسم')
    answer = fields.Selection([('oui', 'نعم'),
                               ('non', 'لا')], string='نعم/ لا')
    note = fields.Text(string='التعليق')
    etape_id = fields.Many2one('wk.etape',  ondelete='cascade')
    checked = fields.Boolean(string='Checked', related='etape_id.doc_checked')

    @api.model
    def create(self, vals):
        for index, item in LIST:
            if index == vals['list_document']:
                vals['filename'] = item
        return super(DocChecker, self).create(vals)



class DemandeLeasing(models.Model):
    _name = 'wk.leasing'
    _description = 'Demande Leasing'

    achat = fields.Many2one('product.product', string='Leased equipment')
    fournisseur = fields.Many2one('res.partner', string='Supplier', domain="[('supplier_rank', '!=', 0)]")
    montant_euro = fields.Float(string='Value of the asset EUR')
    montant_da = fields.Float(string='value of the asset DZD')
    montant_dollar = fields.Float(string='value of the asset USD')


class RecommLeasing(models.Model):
    _name = 'wk.leasing.recom'
    _description = 'Recommandation Leasing'

    achat = fields.Many2one('product.product', string='Leased equipment')
    fournisseur = fields.Many2one('res.partner', string='Supplier', domain="[('supplier_rank', '!=', 0)]")
    montant_euro = fields.Float(string='Value of the asset EUR')
    montant_da = fields.Float(string='Value of the asset DZD')
    montant_dollar = fields.Float(string='Value of the asset USD')


class Partner(models.Model):
    _inherit = 'res.partner'

    is_client = fields.Boolean(string='هل هو عميل؟')
    nif = fields.Char(string='NIF')
    rc = fields.Char(string='RC')
    activity_code = fields.Char(string='رمز النشاط')
    activity_description = fields.Char(string='النشاط')
    branche = fields.Many2one('wk.agence', string='الفرع')
    num_compte = fields.Char(string='رقم الحساب')
    date_ouverture_compte = fields.Date(string='تاريخ فتح الحساب')
    demandes = fields.Many2many('wk.historique', string="تسهيلات الشركة")

    nom_groupe = fields.Char(string='اسم الشركة')
    groupe = fields.Many2one('res.partner', string='المجموعة')
    classification = fields.Many2one('wk.classification', string="تصنيف الشركة")
    adress_siege = fields.Char(string='عنوان المقر الاجتماعي')
    wilaya = fields.Many2one('wk.wilaya', string='الولاية', related='branche.wilaya_id')
    date_inscription = fields.Date(string='تاريخ القيد في السجل التجاري')
    date_debut_activite = fields.Date(string='تاريخ بداية النشاط')
    activite = fields.Many2one('wk.activite', string='النشاط')
    forme_jur = fields.Many2one('wk.forme.jur', string='الشكل القانوني')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    chiffre_affaire = fields.Monetary(string='راس المال الشركة', currency_field='currency_id',)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        print(res.parent_id)
        if res.parent_id:
            res.display_name = res.name
        return res

    @api.depends('num_compte')
    def open_contact_view(self):
        print('called')
        for rec in self:
            if self._context.get('params').get('model') == 'wk.workflow.dashboard':
                if not rec.num_compte:
                    return {
                        'name': _("Related Contacts"),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'view_id': self.env.ref('dept_wk.purchase_order_wk').id,
                        'res_model': 'res.partner',
                    }
                else:
                    return False
            else:
                return False


class States(models.Model):
    _name = 'wk.state.principal'

    name = fields.Char(string='Nom')
    sequence = fields.Integer(string='Nom')

    def action_get_view(self):
        for rec in self:
            if rec.sequence == 1:
                view_id = self.env.ref('dept_wk.view_wk_workflow_form').id
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('الفرع'),
                    'view_mode': 'form',
                    'res_model': 'wk.workflow.dashboard',
                    'target': 'new',
                    'views': [[view_id, 'form']],
                }

