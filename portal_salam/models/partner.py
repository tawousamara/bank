from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')


class Partenaire(models.Model):
    _inherit = 'wk.partenaire'
    _description = 'Partenaire du client'

    lead_id = fields.Many2one('crm.lead')


class EquipeGestion(models.Model):
    _inherit = 'wk.gestion'
    _description = 'Equipe de gestion'

    lead_id = fields.Many2one('crm.lead')


class Taillefin(models.Model):
    _inherit = 'wk.taille'

    lead_id = fields.Many2one('crm.lead')


class SituationBancaire(models.Model):
    _inherit = 'wk.situation'

    lead_id = fields.Many2one('crm.lead')


class SituationFin(models.Model):
    _inherit = 'wk.situation.fin'

    lead_id = fields.Many2one('crm.lead')




class Fournisseur(models.Model):
    _inherit = 'wk.fournisseur'

    lead_id = fields.Many2one('crm.lead')


class Client(models.Model):
    _inherit = 'wk.client'

    lead_id = fields.Many2one('crm.lead')


class KycDetail(models.Model):
    _inherit = 'wk.kyc.details'

    lead_id = fields.Many2one('crm.lead')


class Companies(models.Model):
    _inherit = 'wk.companies'

    lead_id = fields.Many2one('crm.lead')


class DocChecker(models.Model):
    _inherit = 'wk.document.check'

    lead_id = fields.Many2one('crm.lead')
