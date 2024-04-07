from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class RevoirState(models.TransientModel):
    _name = "wk.wizard.retour"

    etape_id = fields.Many2one("wk.etape", string="Request")
    state = fields.Many2one('wk.state')
    raison = fields.Text(string="Reason")

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def send(self):
        for rec in self:
            print("send")
            print(self.env.context)
            demande = self.env['wk.etape'].search([('id', 'in', self.env.context.get('active_ids'))])
            print(demande._fields['state_branch'])
            if self.env.context.get('refus') and self.raison:
                demande.workflow.raison_refus = self.raison
                demande.reject_request_function()
            elif self.raison:
                demande.write({'raison_a_revoir': self.raison})
                demande.a_revoir()
                email_template = self.env.ref('dept_wk.notification_revoir_mail_template')
                email_values = {
                    'email_to': demande.get_mail_to_revoir(),
                }
                email_template.send_mail(demande.id, force_send=True, email_values=email_values)
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
                raise ValueError("Vous devriez saisir la raison")


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
        if self.env.context.get('verrouiller'):
            etape = self.env['wk.etape'].search([('id', '=', self.env.context.get('etape'))])
            if etape:
                etape.write({'dossier_verouiller': self.env.context.get('verrouiller')})
                print('1')
        elif self.env.context.get('to_validate'):
            etape = self.env['wk.etape'].search([('id', '=', self.env.context.get('etape'))])
            if etape.sequence == 1:
                if etape.state_branch == 'branch_3':
                    list_validation = ['1', '2', '7', '8', '12', '13']
                    bloquants = etape.documents.filtered(
                        lambda l: l.list_document in ['1', '2', '7', '8', '12', '13'] and l.document != False).mapped(
                        'list_document')
                    print(bloquants)
                    if not etape.apropos:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء توزيع راس مال الشركة",
                            'sticky': True, })
                    if not etape.gestion:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء فريق التسيير",
                            'sticky': True, })
                    if not etape.tailles:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء حجم و هيكل التمويلات المطلوبة",
                            'sticky': True, })
                    if not etape.fournisseur:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء الموردين",
                            'sticky': True, })
                    if not etape.client:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملء الزبائن",
                            'sticky': True, })
                    if not etape.risk_scoring:
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يجب ملأ بطاقة المعايير النوعية",
                            'sticky': True, })
                    if not set(list_validation).issubset(set(bloquants)):
                        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                            'type': 'danger',
                            'message': "يوجد ملفات غير مرفقة",
                            'sticky': True, })

                    all_valid = etape.client and etape.fournisseur and etape.risk_scoring and etape.tailles and etape.gestion and etape.apropos and set(list_validation).issubset(set(bloquants))
                    if all_valid:
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



class Mail(models.Model):
    _inherit ='mail.message'

    parent_res_id = fields.Char(default=lambda self: str(self._context.get('active_id')))
    parent_res_model = fields.Char(default=lambda self: self._context.get('active_model'))





