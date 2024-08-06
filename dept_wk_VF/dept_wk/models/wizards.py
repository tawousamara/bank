from odoo import models, fields, api, _
from datetime import datetime


class RevoirState(models.TransientModel):
    _name = "wk.wizard.retour"

    etape_id = fields.Many2one("wk.etape", string="Request")
    state = fields.Many2one('wk.state')
    raison = fields.Text(string="Reason", required=True)

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def send(self):
        for rec in self:
            print("send")
            print(self.env.context)
            demande = self.env['wk.etape'].search([('id', 'in', self.env.context.get('active_ids'))])
            print(demande._fields['state_branch'])
            print(self.env.context.get('actual_state'))
            if self.raison:
                demande.write({'raison_a_revoir': self.raison})
                demande.a_revoir()
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


class Mail(models.Model):
    _inherit ='mail.message'

    parent_res_id = fields.Char(default=lambda self: str(self._context.get('active_id')))
    parent_res_model = fields.Char(default=lambda self: self._context.get('active_model'))





