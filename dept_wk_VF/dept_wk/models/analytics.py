from odoo import models, fields, api, _


class Recap(models.Model):
    _name = 'wk.analyse.performence'

    name = fields.Char(string='Nom', default='Performance')
    date_debut = fields.Date(string='من')
    date_fin = fields.Date(string='الى')
    line_ids = fields.One2many('wk.line.stat', 'line', string='الملفات')
    line_prod_ids = fields.One2many('wk.line.stat.prod', 'line', string='الملفات')

    def action_get_detail(self):
        for rec in self:
            self.line_ids.unlink()
            demandes = self.env['wk.workflow.dashboard'].search([('state', '!=', '1')])
            for demande in demandes:
                if not rec.date_debut and not rec.date_fin:
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
                    if (rec.date_debut.year < demande.date.year or
                        (rec.date_debut.year == demande.date.year and rec.date_debut.month <= demande.date.month)) and \
                            (demande.date.year < rec.date_fin.year or
                             (demande.date.year == rec.date_fin.year and demande.date.month <= rec.date_fin.month)):
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

                print(rec.line_ids)
                print(rec.line_prod_ids)


class Stat(models.Model):
    _name = 'wk.line.stat'

    analyste = fields.Many2one('res.users', string='المحلل المالي')
    montant_demande = fields.Float(string='المبلغ المطلوب')
    montant_propose = fields.Float(string='المبلغ المقترح')
    total_demande = fields.Integer(string='عدد الملفات')
    actual_demande = fields.Integer(string='عدد الملفات الحالية')
    avg_traitement = fields.Integer(string='متوسط دراسة الملف حسب المحلل')
    time = fields.Integer(string='اجل دراسة الملف', compute='compute_time')
    line = fields.Many2one('wk.analyse.performence', ondelete="cascade")

    def compute_time(self):
        for rec in self:
            time = self.env['wk.time'].search([('state', '=', 'finance_2')])
            rec.time = time.time
            tracking = self.env['wk.tracking'].search([('state', '=', 'finance_2')])
            somme = 0
            for track in tracking:
                if track.etape_id.assigned_to_finance == rec.analyste and track.difference:
                    somme += track.difference
            avg_traitement = somme / rec.total_demande
            rec.avg_traitement = avg_traitement


class StatProd(models.Model):
    _name = 'wk.line.stat.prod'

    product = fields.Many2one('wk.product', string='المنتج')
    agence = fields.Many2one('wk.agence', string='الفرع')
    montant_demande = fields.Float(string='المبلغ المطلوب')

    line = fields.Many2one('wk.analyse.performence', ondelete="cascade")

