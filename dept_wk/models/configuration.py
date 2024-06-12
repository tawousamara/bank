from odoo import models, fields, api, _


class Agence(models.Model):
    _name = 'wk.agence'
    _description = "Liste des agences de la banque"
    _rec_name = 'ref'
    name = fields.Char(string='رمز الفرع', size=5)
    wilaya = fields.Char(string='الولاية')
    ref = fields.Char(string='الولاية', )
    commune = fields.Char(string="المجلس الشعبي البلدي")
    wilaya_id = fields.Many2one('wk.wilaya',compute='compute_ref')

    def compute_ref(self):
        for rec in self:
            wilaya = self.env['wk.wilaya'].search([('name', '=', rec.wilaya)])
            commune = self.env['wk.commune'].search([('name', '=', rec.commune),
                                                     ('domaine', '=', rec.wilaya)])
            print(wilaya)
            print(commune)
            print(commune.description)
            if wilaya:

                rec.wilaya_id = wilaya.id
            else:
                rec.wilaya_id = False
            if commune:
                print(commune.description)
                if not rec.ref:
                    rec.ref = rec.name + '-' + commune.description

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
    wilaya_arabe = fields.Char(string='اسم الولاية بالعربية')


class Commune(models.Model):
    _name = 'wk.commune'
    _rec_name = 'description'

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
    for_branch = fields.Boolean(string='للفرع')


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

import logging
from odoo.exceptions import AccessError, ValidationError
_logger = logging.getLogger(__name__)
class IRRule(models.Model):
    _inherit = 'ir.rule'

    def _make_access_error(self, operation, records):
        _logger.info('Access Denied by record rules for operation: %s on record ids: %r, uid: %s, model: %s', operation, records.ids[:6], self._uid, records._name)
        self = self.with_context(self.env.user.context_get())

        model = records._name
        description = self.env['ir.model']._get(model).name or model
        operations = {
            'read':  _("read"),
            'write': _("write"),
            'create': _("create"),
            'unlink': _("unlink"),
        }
        user_description = f"{self.env.user.name} (id={self.env.user.id})"
        operation_error = _("Vous ne pouvez pas acceder %s n'a pas access a %s", user_description, operations[operation])
        failing_model = _("- %s (%s)", description, model)

        resolution_info = _("يمكنكم الاتصال بالفريق التقني")

        if not self.user_has_groups('base.group_no_one') or not self.env.user.has_group('base.group_user'):
            records.invalidate_recordset()
            return AccessError(f"{operation_error}\n{failing_model}\n\n{resolution_info}")

        # This extended AccessError is only displayed in debug mode.
        # Note that by default, public and portal users do not have
        # the group "base.group_no_one", even if debug mode is enabled,
        # so it is relatively safe here to include the list of rules and record names.
        rules = self._get_failing(records, mode=operation).sudo()

        records_sudo = records[:6].sudo()
        company_related = any('company_id' in (r.domain_force or '') for r in rules)

        def get_record_description(rec):
            # If the user has access to the company of the record, add this
            # information in the description to help them to change company
            if company_related and 'company_id' in rec and rec.company_id in self.env.user.company_ids:
                return f'{description}, {rec.display_name} ({model}: {rec.id}, company={rec.company_id.display_name})'
            return f'{description}, {rec.display_name} ({model}: {rec.id})'

        failing_records = '\n '.join(f'- {get_record_description(rec)}' for rec in records_sudo)

        rules_description = '\n'.join(f'- {rule.name}' for rule in rules)
        failing_rules = _("A cause de :\n%s", rules_description)

        if company_related:
            failing_rules += "\n\n" + _('Note: this might be a multi-company issue. Switching company may help - in Odoo, not in real life!')

        # clean up the cache of records prefetched with display_name above
        records_sudo.invalidate_recordset()

        msg = f"{operation_error}\n{failing_records}\n\n{failing_rules}\n\n{resolution_info}"
        return AccessError(msg)

