from odoo import models, fields, api, _


class Agence(models.Model):
    _name = 'wk.agence'
    _description = "Liste des agences de la banque"
    _rec_name = 'ref'
    name = fields.Char(string='رمز الفرع', size=5)
    wilaya = fields.Char(string='الولاية')
    ref = fields.Char(string='الولاية', compute='compute_ref', store=True)
    commune = fields.Char(string="المجلس الشعبي البلدي")
    wilaya_id = fields.Many2one('wk.wilaya')

    @api.depends('name', 'wilaya')
    def compute_ref(self):
        for rec in self:
            wilaya = self.env['wk.wilaya'].search([('name', '=', rec.wilaya)])
            if wilaya:
                rec.ref = rec.name + '-' + wilaya.domaine
                rec.wilaya_id = wilaya.id

    def create_folder(self):
        for rec in self:
            folder = self.env['documents.folders'].search([('branch', '=', rec.id), ('client', '=', False)])
            if not folder:
                folder = self.env['documents.folders'].create({'branch': rec.id,
                                                               'name': rec.ref})

            clients = self.env['res.partner'].search([('branche', '=', rec.id)])
            for client in clients:
                client_folder = self.env['documents.folders'].search([('parent_folder_id', '=', folder.id),
                                                                        ('client', '=', client.id)])
                if not client_folder:
                    client_folder = self.env['documents.folders'].create({'branch': rec.id,
                                                                   'name': client.num_compte,
                                                                   'parent_folder_id': folder.id,
                                                                   'client': client.id})


class Garanties(models.Model):
    _name = 'wk.garanties'

    name = fields.Char(string='الشروط و الضمانات')


class ExceptionsWk(models.Model):
    _name = 'wk.exception'

    name = fields.Char(string='الاستثناءات')


class Wilaya(models.Model):
    _name = 'wk.wilaya'
    _rec_name = 'domaine'
    name = fields.Char(string="الرمز")
    domaine = fields.Char(string='الولاية')
    description = fields.Char(string='الاسم')


class FormeJuridique(models.Model):
    _name = 'wk.forme.jur'
    _description = 'Lignes des formes juridiques'

    name = fields.Char(string='الشكل القانوني')


class Product(models.Model):
    _name = 'wk.product'
    _description = 'Liste des produits de la banque'

    name = fields.Char(string='منتجات المصرف')


class DecisionCell(models.Model):
    _name = 'wk.decision.cell'
    _description = 'Liste des cells de decision'

    name = fields.Char(string='سلطة القرار')


class TypeDemande(models.Model):
    _name = 'wk.type.demande'
    _description = 'Liste des types de demandes'

    name = fields.Char(string='نوع الطلب')


class Activity(models.Model):
    _name = 'wk.activite'
    _description = 'Liste des activités'
    _rec_name = 'domaine'

    name = fields.Char(string='الرمز')
    domaine = fields.Char(string='النشاط')
    description = fields.Char(string='Description')


class Secteur(models.Model):
    _name = 'wk.secteur'
    _description = 'Liste des secteurs'

    name = fields.Char(string='Secondary activity')
    activity = fields.Many2one('wk.activite', string='Main activity')


class TypePayment(models.Model):
    _name = 'wk.type.payment'
    _description = 'Type Payment'

    name = fields.Char(string='name')
    type = fields.Selection([('1', 'المورد'),
                             ('2', 'الزبون'),
                             ('3', 'الكل')])


class ClassificationEntreprise(models.Model):
    _name = 'wk.classification'
    _description = "Classification de l'entreprise"

    name = fields.Char(string='تصنيف الشركة')


class NatureJuridique(models.Model):
    _name = 'wk.nature.juridique'
    _description = "Nature juridique"

    name = fields.Char(string='الطبيعة القانونية للمقرات')


class TypeFin(models.Model):
    _name = 'wk.type.fin'
    _description = "Type de financement"

    name = fields.Char(string='نوع التمويل')


class TimeExpected(models.Model):
    _name = 'wk.time'
    _description = "Temps necessaire pour chaque tache"

    name = fields.Char(string='الحالة')
    state = fields.Selection([('branch_1', 'الفرع'),
                              ('branch_2', 'مدير الفرع'),
                              ('branch_3', ' الفرع'),
                              ('branch_4', 'مدير الفرع'),
                              ('finance_1', 'مدير التمويلات'),
                              ('finance_2', 'المحلل المالي'),
                              ('finance_3', 'مدير التمويلات'),
                              ('commercial_1', 'مدير الاعمال التجارية'),
                              ('commercial_2', 'مديرية الاعمال التجارية'),
                              ('commercial_3', 'مدير الاعمال التجارية'),
                              ('risque_1', 'ادارة المخاطر')])
    etape = fields.Many2one('wk.state.principal', string='الحالة')
    time = fields.Integer(string='الوقت اللازم')

