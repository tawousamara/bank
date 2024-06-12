from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TCR(models.Model):
    _inherit = 'import.ocr.tcr'

    parent_id = fields.Many2one('wk.etape', string='Workflow')

    @api.model
    def create(self, vals):
        print(self.env.context)
        vals['parent_id'] = self.env.context.get('parent_id')
        res = super(TCR, self).create(vals)
        year = self.env.context.get('year')
        group = self.env.context.get('is_group') or False
        if res.parent_id:
            if year != 2 and not group:
                res.parent_id.tcr_id = res.id
            elif year == 2 and not group:
                res.parent_id.tcr1_id = res.id
            else:
                res.parent_id.tcr_group = res.id
        if self.env.context.get('score_id'):
            score = self.env['risk.scoring'].browse(self.env.context.get('score_id'))
            score.tcr_id = res.id
        return res

    def action_validation_wk(self):
        for rec in self:
            list_validation = [7, 33, 50, 36, 12, 13, 14, 30]
            tcr = rec.tcr_lines.mapped('rubrique.sequence')
            if not set(list_validation).issubset(set(tcr)):
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n "
                                      "- Chiffre d'affaires net des rabais, Remises, Ristournes \n"
                                      "- Excédent brut de l'exploitation \n"
                                      "- Résultat  net de l'exercice \n"
                                      "- Dotations aux amortissements \n"
                                      "- Matières premieres \n"
                                      "- Valeur Ajoutée d'exploitation \n"
                                      "- Achats de marchandises vendues \n"
                                      "- Valeur ajoutée d'exploitation (I-II) \n"
                                      )
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['tcr_id'] = rec.id
            context['state'] = 'valide'
            print(context)
            if not self._context.get('warning'):
                return {
                    'name': 'Validation',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.ocr.wizard',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': context,
                }



class Actif(models.Model):
    _inherit = 'import.ocr.actif'

    parent_id = fields.Many2one('wk.etape', string='Workflow')

    @api.model
    def create(self, vals):
        print(self.env.context)
        vals['parent_id'] = self.env.context.get('parent_id')
        print(vals['parent_id'])
        year = self.env.context.get('year')
        group = self.env.context.get('is_group') or False
        res = super(Actif, self).create(vals)
        if res.parent_id:
            if year != 2 and not group:
                res.parent_id.actif_id = res.id
            elif year == 2 and not group:
                res.parent_id.actif1_id = res.id
            else:
                res.parent_id.actif_group = res.id
        if self.env.context.get('score_id'):
            score = self.env['risk.scoring'].browse(self.env.context.get('score_id'))
            score.actif_id = res.id
        return res

    def action_validation_wk(self):
        for rec in self:
            list_validation = [4, 7, 16, 27, 18, 19, 20, 24, 26]
            actifs = rec.actif_lines.mapped('rubrique.sequence')
            print(actifs)
            print(set(list_validation).issubset(set(actifs)))
            print(set(list_validation) != set(actifs))
            if not set(list_validation).issubset(set(actifs)):
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n"
                                      "- Immobilisations corporelles \n"
                                      "- Autres immobilisations corporelles \n"
                                      "- Total actif non courant \n"
                                      "- Stocks et encours \n"
                                      "- Clients \n"
                                      "- Créances et emplois assimilés \n"
                                      "- Disponibilité et assimilés \n"
                                      "- Trésorerie \n"
                                      "- Total Actif courant \n"
                                      )
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['actif_id'] = rec.id
            context['state'] = 'valide'

            if not self._context.get('warning'):
                return {
                    'name': 'Validation',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.ocr.wizard',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': context,
                }


class Passif(models.Model):
    _inherit = 'import.ocr.passif'

    parent_id = fields.Many2one('wk.etape', string='Workflow')

    @api.model
    def create(self, vals):
        print(self.env.context)
        vals['parent_id'] = self.env.context.get('parent_id')
        year = self.env.context.get('year')
        group = self.env.context.get('is_group') or False
        res = super(Passif, self).create(vals)
        if res.parent_id:
            if year != 2 and not group:
                res.parent_id.passif_id = res.id
            elif year == 2 and not group:
                res.parent_id.passif1_id = res.id
            else:
                res.parent_id.passif_group = res.id
        if self.env.context.get('score_id'):
            score = self.env['risk.scoring'].browse(self.env.context.get('score_id'))
            score.passif_id = res.id
        return res

    def action_validation_wk(self):
        for rec in self:
            list_validation = [2, 4, 8, 12, 14, 18, 20, 21, 22, 23, 24, 25]
            passifs = rec.passif_lines.mapped('rubrique.sequence')
            if not set(list_validation).issubset(set(passifs)):
                raise ValidationError("Vous devriez confirmer les valeurs suivantes: \n"
                                      "- Capital émis \n"
                                      "- Primes et reserves \n"
                                      "- Autres capitaux propres - Report à nouveau \n"
                                      "- Total I \n"
                                      "- Emprunts et dettes financières \n"
                                      "- Total II \n"
                                      "- Fournisseurs et comptes rattachés \n"
                                      "- Impots \n"
                                      "- Autres dettes \n"
                                      "- Trésorerie passifs \n"
                                      "- Total III \n"
                                      "- Total General Passif (I+II+III)")
            '''for index in list_validation:
                passif = rec.passif_lines.filtered(lambda l: l.sequence == index)
                if len(passif) != 1:
                    raise ValidationError(_('Vous devriez supprimer les doublons de ce poste "'+ passif[0].name +' "'))'''
            view_id = self.env.ref('financial_modeling.confirmation_wizard_form')
            context = dict(self.env.context or {})
            context['passif_id'] = rec.id
            context['state'] = 'valide'
            print(context)
            if not self._context.get('warning'):
                return {
                    'name': 'Validation',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'import.ocr.wizard',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': context,
                }

class TCRInherit(models.Model):
    _inherit = 'tcr.analysis.import'

    parent_id = fields.Many2one('wk.etape', string='Workflow')

    @api.model
    def create(self, vals):
        print(self.env.context)
        vals['parent_id'] = self.env.context.get('parent_id')
        res = super(TCRInherit, self).create(vals)
        if res.parent_id:
            res.parent_id.invest_id = res.id
        return res
