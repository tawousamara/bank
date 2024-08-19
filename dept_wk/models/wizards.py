from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class RevoirState(models.TransientModel):
    _name = "wk.wizard.retour"

    etape_id = fields.Many2one("wk.etape", string="Request")
    etat = fields.Selection([('1', 'الفرع'),
                              ('2', 'مديرية التمويلات'),
                              ('3', 'مديرية الاعمال التجارية'),
                              ('4', 'ادارة المخاطر'),
                              ('10', 'رئيس قطاع الخزينة'),
                              ('5', 'نائب المدير العام')], string='الرجوع ل:')
    raison = fields.Text(string="Reason")
    one_step = fields.Boolean(string='الى مدير التمويلات')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def send(self):
        self.ensure_one()
        demande = self.env['wk.etape'].search([('id', 'in', self.env.context.get('active_ids'))])
        print(demande._fields['state_branch'])
        if self.env.context.get('refus') and self.raison:
            demande.workflow.raison_refus = self.raison
            demande.reject_request_function()
        elif self.raison:
            if not self.etat:
                demande.a_revoir(self.one_step)
            else:
                print(int(demande.workflow.state))
                print(int(self.etat))
                if int(demande.sequence) >= int(self.etat):
                    demande.a_revoir_2(self.etat, self.raison)
                else:
                    raise UserError('يجب اختيار وجهة اخرى')
            if demande.etape.sequence == 2 and demande.state_finance == 'finance_1':
                step_1 = demande.workflow.states.filtered(lambda l: l.etape.sequence == 1)
                if step_1.state_branch == 'branch_4':
                    step_1.write({'raison_a_revoir': self.raison})
            elif demande.etape.sequence == 5 and demande.state_vice == 'vice_1':
                step_1 = demande.workflow.states.filtered(lambda l: l.etape.sequence == 2)
                if step_1.state_finance == 'finance_3':
                    step_1.write({'raison_a_revoir': self.raison})
            elif demande.etape.sequence == 4 and demande.state_risque == 'risque_1':
                step_1 = demande.workflow.states.filtered(lambda l: l.etape.sequence == 2)
                if step_1.state_finance == 'finance_3':
                    step_1.write({'raison_a_revoir': self.raison})
            else:
                demande.write({'raison_a_revoir': self.raison})
            try:
                email_template = self.env.ref('dept_wk.notification_revoir_mail_template')
                email_values = {
                    'email_to': demande.get_mail_to_revoir(),
                }
                email_template.send_mail(demande.id, force_send=True, email_values=email_values)
            except:
                print('hi')
            '''last_track = self.env['wk.tracking'].search([('workflow_id', '=', demande.workflow.id)])
            last_track[-1].write({'date_fin': datetime.today()})
            state = dict(demande._fields['state_branch'].selection).get(demande.state_branch)
            if demande.etape.sequence == 1:
                state = dict(demande._fields['state_branch'].selection).get(demande.state_branch)
            elif demande.etape.sequence == 2:
                state = dict(demande._fields['state_finance'].selection).get(demande.state_finance)
            elif demande.etape.sequence == 3:
                state = dict(demande._fields['state_commercial'].selection).get(demande.state_commercial)
            elif demande.etape.sequence == 4:
                state = dict(demande._fields['state_risque'].selection).get(demande.state_risque)
            elif demande.etape.sequence == 5:
                state = dict(demande._fields['state_vice'].selection).get(demande.state_vice)
            elif demande.etape.sequence == 6:
                state = dict(demande._fields['state_comite'].selection).get(demande.state_comite)
            print(state)
            self.env['wk.tracking'].create({'workflow_id': demande.workflow.id,
                                            'date_debut': datetime.today(),
                                            'state1': state,
                                            'is_revision': True,
                                            'comment': self.raison})'''
            return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError("Vous devriez saisir la raison")


class AvanceState(models.TransientModel):
    _name = "wk.wizard.path"

    state = fields.Many2one('wk.state')
    commentaire = fields.Text(string="Comment")

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def send(self):
        for rec in self:
            '''demande = self.env['wk.workflow'].search([('id', 'in', self.env.context.get('active_ids'))])
            if self.state:
                demande.write({'state': self.state.sequence,
                               'commentaire': self.commentaire,
                               'raison_a_revoir': False})
                last_track = self.env['wk.tracking'].search([('workflow', '=', demande.id)])
                last_track[-1].write({'date_fin': datetime.today()})
                self.env['wk.tracking'].create({'workflow': demande.id,
                                                'date_debut': datetime.today(),
                                                'state': self.state.sequence,
                                                'comment': self.commentaire})
                print(demande.state)
                return {'type': 'ir.actions.act_window_close'}
            else:'''
            raise ValueError("Vous devriez saisir la destination")


class CommiteState(models.TransientModel):
    _name = "wk.wizard.path.choice"

    state = fields.Many2many('wk.state', domain="[('sequence', 'in', ['8', '9'])]")
    commentaire = fields.Text(string="Comment")
    branche = fields.Many2one('wk.agence', string='Branche')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def send(self):
        for rec in self:
            '''demande = self.env['wk.workflow'].search([('id', 'in', self.env.context.get('active_ids'))])
            if self.state and self.branche:
                if len(self.state) == 1:
                    demande.write({'state': self.state.sequence,
                                   'commentaire': self.commentaire,
                                   'branche_notif': self.branche.id,
                                   'raison_a_revoir': False})
                    last_track = self.env['wk.tracking'].search([('workflow', '=', demande.id)])
                    last_track[-1].write({'date_fin': datetime.today()})
                    self.env['wk.tracking'].create({'workflow': demande.id,
                                                    'date_debut': datetime.today(),
                                                    'state': self.state.sequence,
                                                    'comment': self.commentaire})
                else:
                    demande.write({'state': self.state[0].sequence,
                                   'commentaire': self.commentaire,
                                   'raison_a_revoir': False})
                    last_track = self.env['wk.tracking'].search([('workflow', '=', demande.id)])
                    last_track[-1].write({'date_fin': datetime.today()})
                    for s in self.state:
                        self.env['wk.tracking'].create({'workflow': demande.id,
                                                    'date_debut': datetime.today(),
                                                    'state': s.sequence,
                                                    'comment': self.commentaire})
                return {'type': 'ir.actions.act_window_close'}
            else:'''
            raise ValueError("Vous devriez saisir la destination")


class State(models.Model):
    _name = 'wk.state'

    name = fields.Char()
    sequence = fields.Char()


class Confirmation(models.TransientModel):
    _name = 'etape.wizard'
    _description = 'Confirmation of verification wizard'

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def confirm(self):
        print("send")
        print(self.env.context.get('active_ids')[0])
        print(self.env.context)
        model = self.env['bus.bus']
        if self.env.context.get('verrouiller'):
            etape = self.env['wk.etape'].search([('id', '=', self.env.context.get('etape'))])
            if etape:
                etape.write({'dossier_verouiller': self.env.context.get('verrouiller')})
                etape.verrouiller_dossier_function()
        elif self.env.context.get('to_validate'):
            etape = self.env['wk.etape'].search([('id', '=', self.env.context.get('etape'))])
            if etape.sequence == 1:
                if etape.state_branch == 'branch_1':
                    if not etape.gerant:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اختيار المسير",
                            'sticky': True, })
                    else:
                        etape.validate_information_function()
                elif etape.state_branch == 'branch_2':
                    not_assign = True
                    for doc in etape.documents:
                        if doc.document and not doc.answer:
                            filename = doc.filename if doc.filename else doc.list_doc
                            model._sendone(self.env.user.partner_id, 'simple_notification', {
                                'type': 'danger',
                                'message':  "يجب تاكيد الملف %s" % filename,
                                'sticky': True, })
                            not_assign = False
                            break
                    if not_assign:
                        etape.validate_information_function()
                elif etape.state_branch == 'branch_3':
                    if etape.documents.filtered(lambda  l:l.list_document == '15'):
                        list_validation = ['1', '2', '7', '8', '12', '13', '15', '16']
                    else:
                        list_validation = ['1', '2', '7', '8', '12', '13']
                    bloquants = etape.documents.filtered(
                        lambda l: l.list_document in list_validation and l.document != False).mapped(
                        'list_document')
                    print(bloquants)
                    if not etape.apropos:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء توزيع راس مال الشركة",
                            'sticky': True, })
                    elif not etape.gestion:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء فريق التسيير",
                            'sticky': True, })
                    elif not etape.tailles:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء حجم و هيكل التمويلات المطلوبة",
                            'sticky': True, })
                    elif not etape.fournisseur:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء الموردين",
                            'sticky': True, })
                    elif not etape.client:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء الزبائن",
                            'sticky': True, })
                    elif not etape.risk_scoring:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملأ بطاقة المعايير النوعية",
                            'sticky': True, })
                    elif not set(list_validation).issubset(set(bloquants)):
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يوجد ملفات غير مرفقة",
                            'sticky': True, })
                    elif not etape.recommendation_visit:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة توصية الفرع",
                            'sticky': True, })
                    elif not etape.risk_scoring.original_capital:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة أصل رأس المال في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.actionnariat:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة المساهمات في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.forme_jur:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الشكل القانوني في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.remp_succession:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الخلافة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.competence:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الكفاءة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.experience:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الخبرة المهنية في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.soutien_etatic:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة دعم الدولة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.activite:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة النشاط في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.influence_tech:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة التكنولوجيا المستعملة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.anciennete:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الأقدمية في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.concurrence:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة المنافسة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.source_appro:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الموردون في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.produit:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة المنتوج في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.flexibilite:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة المرونة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.sollicitude:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة طلب القروض لدى البنوك الزميلة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.situation:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة  الأملاك العقارية للشركاء/المساهمين في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.garanties:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الضمانات المقترحة في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.incident:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة التعثرات في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.conduite:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة سيرة المتعامل في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.dette_fisc:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة طلب الضرائب في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.dette_parafisc:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة الضمان الاجتماعي في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.position_admin:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة إدارات أخرى في المعايير النوعية",
                            'sticky': True, })
                    elif not etape.risk_scoring.source_remb:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة مصادر التسديد في المعايير النوعية",
                            'sticky': True, })
                    else:
                        etape.validate_information_function()
                elif etape.state_branch == 'branch_4':
                    not_assign = True
                    for doc in etape.documents:
                        if doc.document and not doc.answer:
                            filename = doc.filename if doc.filename else doc.list_doc
                            model._sendone(self.env.user.partner_id, 'simple_notification', {
                                'type': 'danger',
                                'message':  "يجب تاكيد الملف %s" % filename,
                                'sticky': True, })
                            not_assign = False
                            break
                    if not etape.recommendation_responsable_agence:
                        model._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب اضافة توصية مدير الفرع",
                            'sticky': True, })
                        not_assign = False
                    if not_assign:
                        etape.validate_information_function()
                else:
                    etape.validate_information_function()
            else:
                etape.validate_information_function()


class BilanViewer(models.TransientModel):
    _name = 'view.bilan.wizard'
    _description = 'Viewing Files wizard'

    pdf_1 = fields.Binary(string='PDF')
    pdf_2 = fields.Binary(string='PDF')

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def confirm(self):
        """print("send")
        print(self.env.context.get('active_ids')[0])
        print(self.env.context)
        if self.env.context.get('tcr_id'):
            tcr_id = self.env['import.ocr.tcr'].search([('id', '=', self.env.context.get('tcr_id'))])
            self.pdf_1 = tcr_id.file_import
            self.pdf_2 = tcr_id.file_import2"""


class Wizard(models.TransientModel):
    _name = 'wk.periode.wizard'

    date_from = fields.Date(string='De')
    date_to = fields.Date(string='Au')

    def send(self):
        for rec in self:
            date_from = rec.date_from.replace(day=1)
            date_to = rec.date_to.replace(day=1)
            self.env['wk.line.stat.prod'].search([]).unlink()
            demandes = self.env['wk.workflow.dashboard'].search([('state', '!=', '1')])
            for demande in demandes:
                if not date_from and not date_to:
                    etape = demande.states.filtered(lambda l: l.sequence == 2)
                    print(etape)
                    analyste = self.env['wk.line.stat'].search([('analyste', '=', etape.assigned_to_finance.id)])
                    if not analyste:
                        analyste = self.env['wk.line.stat'].create({'analyste': etape.assigned_to_finance.id,
                                                                    'line': rec.id})
                    else:
                        analyste.line = rec.id
                    if etape.state_finance == 'finance_2':
                        analyste.actual_demande += 1
                    analyste.total_demande += 1
                    analyste.montant_demande += etape.montant_demande
                    analyste.montant_propose += etape.montant_propose

                else:
                    if (date_from.year < demande.date.year or
                        (date_from.year == demande.date.year and date_from.month <= demande.date.month)) and \
                            (demande.date.year < date_to.year or
                             (demande.date.year == date_to.year and demande.date.month <= date_to.month)):
                        etape = demande.states.filtered(lambda l: l.sequence == 2)
                        print(etape)
                        analyste = self.env['wk.line.stat'].search([('analyste', '=', etape.assigned_to_finance.id)])
                        if not analyste:
                            analyste = self.env['wk.line.stat'].create({'analyste': etape.assigned_to_finance.id,
                                                                        'line': rec.id})
                        else:
                            analyste.line = rec.id
                        if etape.state_finance == 'finance_2':
                            analyste.actual_demande += 1
                        analyste.total_demande += 1
                        analyste.montant_demande += etape.montant_demande
                        analyste.montant_propose += etape.montant_propose
                        etape = demande.states.filtered(lambda l: l.sequence == 1)
                        for taille in etape.tailles:
                            produit = self.env['wk.line.stat.prod'].search([('product', '=', taille.type_demande.id),
                                                                            ('line', '=', rec.id),
                                                                            ('agence', '=', etape.branche.id)])
                            if not produit:
                                self.env['wk.line.stat.prod'].create({'line': rec.id,
                                                                      'product': taille.type_demande.id,
                                                                      'montant_demande': taille.montant,
                                                                      'agence': etape.branche.id})
                            else:
                                produit.montant_demande += taille.montant

        view_id = self.env.ref('dept_wk.wk_line_stat_prod_view_pivot').id
        return {'type': 'ir.actions.act_window',
                'name': 'جدول موجز',
                    'res_model': 'wk.line.stat.prod',
                    'view_mode': 'pivot',
                    'view_id': view_id,
                    }


    def cancel(self):
        pass


class Mail(models.Model):
    _inherit ='mail.message'

    parent_res_id = fields.Char(default=lambda self: str(self._context.get('active_id')))
    parent_res_model = fields.Char(default=lambda self: self._context.get('active_model'))





