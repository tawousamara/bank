from odoo import models, fields, api, _


class FinancialConfirmed(models.Model):
    _name = 'wk.state.two'
    _description = "Données saisi par le service financier"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    date = fields.Date(string='Date')
    name = fields.Char(string='Name', default='مديرية التمويلات')

    analyseur = fields.Many2one('res.users')
    facilite_accorde = fields.One2many('wk.facilite.accorde', 'workflow'
                                       , related='workflow.facilite_accorde')
    detail_garantie_actuel_ids = fields.One2many('wk.detail.garantie', 'workflow', related='workflow.detail_garantie_actuel_ids')
    detail_garantie_propose_ids = fields.One2many('wk.detail.garantie.propose', 'workflow', related='workflow.detail_garantie_propose_ids')
    garantie_conf = fields.One2many('wk.garantie.conf', 'workflow',related='workflow.garantie_conf')
    garantie_fin = fields.One2many('wk.garantie.fin', 'workflow',  related='workflow.garantie_fin')
    garantie_autres = fields.One2many('wk.garantie.autres', 'workflow',  related='workflow.garantie_autres')

    risque_central = fields.One2many('wk.risque.line', 'workflow',  related='workflow.risque_central')
    risque_date = fields.Date(related='workflow.risque_date')
    nbr_banque = fields.Integer(related='workflow.nbr_banque')
    mouvement = fields.One2many('wk.mouvement', 'workflow', related='workflow.mouvement')
    administration = fields.Text( related='workflow.administration')
    definition_company = fields.Text(related='workflow.definition_company')
    analyse_secteur = fields.Text( related='workflow.analyse_secteur')
    relation = fields.Text(related='workflow.relation')
    position_tax = fields.One2many('wk.position', 'workflow', related='workflow.position_tax')
    companies = fields.One2many('wk.companies', 'workflow', related='workflow.companies')
    companies_fisc = fields.One2many('wk.companies.fisc', 'workflow', related='workflow.companies_fisc')
    visualisation2 = fields.Binary(string='visualisation', related='workflow.visualisation2')

    mouvement_group = fields.One2many('wk.mouvement.group', 'workflow',related='workflow.mouvement_group')
    visualisation1 = fields.Binary(string='visualisation', related='workflow.visualisation1')

    facitlite_existante = fields.One2many('wk.facilite.existante', 'workflow' , related='workflow.facitlite_existante')

    fin_max_ca = fields.Float(related='workflow.fin_max_ca')
    fin_max_bfr = fields.Float( related='workflow.fin_max_bfr')
    fin_max_caf = fields.Float( related='workflow.fin_max_caf')
    fin_achat = fields.Char(related='workflow.fin_achat')
    fin_collecte = fields.Char( related='workflow.fin_collecte')

    bilan_id = fields.One2many('wk.bilan', 'workflow', related='workflow.bilan_id')

    tcr_id = fields.Many2one('import.ocr.tcr',  related='workflow.tcr_id')
    passif_id = fields.Many2one('import.ocr.passif', related='workflow.passif_id')
    actif_id = fields.Many2one('import.ocr.actif',related='workflow.actif_id')

    tcr1_id = fields.Many2one('import.ocr.tcr', related='workflow.tcr1_id')
    passif1_id = fields.Many2one('import.ocr.passif', related='workflow.passif1_id')
    actif1_id = fields.Many2one('import.ocr.actif',  related='workflow.actif1_id')

    recap_ids = fields.One2many('wk.recap', 'workflow', related='workflow.recap_ids')
    var_ids = fields.One2many('wk.variable', 'workflow', related='workflow.var_ids')

    recommandation_analyste_fin = fields.Text(related='workflow.recommandation_analyste_fin')
    facilite_propose = fields.One2many('wk.facilite.propose', 'workflow', related='workflow.facilite_propose')
    garantie_ids = fields.Many2many('wk.garanties', related='workflow.garantie_ids')
    recommandation_dir_fin = fields.Text(related='workflow.recommandation_dir_fin')
