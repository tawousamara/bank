from odoo import models, fields, api, _


class ScoringConfirmed(models.Model):
    _name = 'wk.state.four'
    _description = "Données du scoring"

    workflow = fields.Many2one('wk.workflow', string='Demande')
    date = fields.Date(string='Date', related='workflow.date')
    name = fields.Char(string='Name', default='ادارة المخاطر')

    critere_qual = fields.Many2one('risk.critere.qualitatif', string='Qualitative criteria', related="workflow.risk_scoring.critere_qual")
    critere_quant = fields.Many2one('risk.critere.quantitatif', string='Quantitative criteria', related="workflow.risk_scoring.critere_quant")

    tcr_id = fields.Many2one('import.ocr.tcr', string='P&L Statement',
                             related="workflow.risk_scoring.tcr_id")
    passif_id = fields.Many2one('import.ocr.passif', string='Liabilities',
                                related="workflow.risk_scoring.passif_id")
    actif_id = fields.Many2one('import.ocr.actif', string='Assets',
                               related="workflow.risk_scoring.actif_id")

    original_capital = fields.Many2one('risk.original.capital', string='Original du capital',
                                       related="workflow.risk_scoring.original_capital")
    actionnariat = fields.Many2one('risk.actionnariat', string='Actionnariat',
                                   related="workflow.risk_scoring.actionnariat")
    forme_jur = fields.Many2one('risk.forme.jur', string='Forme juridique',
                                related="workflow.risk_scoring.forme_jur")
    remp_succession = fields.Many2one('risk.remplacement.succession',
                                      string='Remplacement et succession',
                                      related="workflow.risk_scoring.remp_succession")
    competence = fields.Many2one('risk.competence', string='Competence',
                                 related="workflow.risk_scoring.competence")
    experience = fields.Many2one('risk.experience', string='Expérience',
                                 related="workflow.risk_scoring.experience")
    soutien_etatic = fields.Many2one('risk.soutien.etatique', string='Soutien étatique',
                                     related="workflow.risk_scoring.soutien_etatic")
    activite = fields.Many2one('risk.activite', string='Activité',
                               related="workflow.risk_scoring.activite")
    influence_tech = fields.Many2one('risk.influence.tech', string='Influence technologique',
                                     related="workflow.risk_scoring.influence_tech")
    anciennete = fields.Many2one('risk.anciennete', string='Ancienneté',
                                 related="workflow.risk_scoring.anciennete")
    concurrence = fields.Many2one('risk.concurrence', string='Concurrence',
                                  related="workflow.risk_scoring.concurrence")
    source_appro = fields.Many2one('risk.source.appro', string='Sources d’approvisionnement',
                                   related="workflow.risk_scoring.source_appro")
    produit = fields.Many2one('risk.produit', string='Produit de l’entreprise',
                              related="workflow.risk_scoring.produit")
    flexibilite = fields.Many2one('risk.flexibilite', string='Flexibilité',
                                  related="workflow.risk_scoring.flexibilite")
    sollicitude = fields.Many2one('risk.sollicitude', string='Sollicitude des confrères',
                                  related="workflow.risk_scoring.sollicitude")
    situation = fields.Many2one('risk.situation', string='Situation patrimoniale des actionnaires',
                                related="workflow.risk_scoring.situation")
    mouvement = fields.Many2one('risk.mouvement', string='Mouvements confiés',
                                related="workflow.risk_scoring.mouvement")
    garanties = fields.Many2one('risk.garanties', string='Garanties proposées',
                                related="workflow.risk_scoring.garanties")
    incident = fields.Many2one('risk.incident', string='Incidents de paiement',
                               related="workflow.risk_scoring.incident")
    conduite = fields.Many2one('risk.conduite', string='Conduite du client',
                               related="workflow.risk_scoring.conduite")
    dette_fisc = fields.Many2one('risk.dette.fisc', string='Dette fiscale',
                                 related="workflow.risk_scoring.dette_fisc")
    dette_parafisc = fields.Many2one('risk.dette.parafisc', string='Dette parafiscale',
                                     related="workflow.risk_scoring.dette_parafisc")
    position_admin = fields.Many2one('risk.position.admin', string='Position envers autres administrations',
                                     related="workflow.risk_scoring.position_admin")
    source_remb = fields.Many2one('risk.source.remb', string='Sources de remboursement', related="workflow.risk_scoring.source_remb")
    part_profil = fields.Many2one('risk.part.profil',
                                  string='Part du profit de la contrepartie au total PNB', related="workflow.risk_scoring.part_profil")

    quant_1 = fields.Float(string='RS1 - FP / TB', related="workflow.risk_scoring.quant_1")
    quant_2 = fields.Float(string='RS2 - FP / Capitaux permanents *100', related="workflow.risk_scoring.quant_2")
    quant_3 = fields.Float(string='RS3 - FRN / Actif circulants hors tréso.', related="workflow.risk_scoring.quant_3")
    quant_4 = fields.Float(string='RS4 - DLMT / CAF', related="workflow.risk_scoring.quant_4")
    quant_5 = fields.Float(string='RL1 - Actif circulants / DCT *100', related="workflow.risk_scoring.quant_5")
    quant_6 = fields.Float(string='RL2 - Disponibilité / DCT *100', related="workflow.risk_scoring.quant_6")
    quant_7 = fields.Float(string='RA1 - Stock en jours Achats', related="workflow.risk_scoring.quant_7")
    quant_8 = fields.Float(string='RA2 - Créances clients en jours CA', related="workflow.risk_scoring.quant_8")
    quant_9 = fields.Float(string='RA3 - FRN rn jours CA', related="workflow.risk_scoring.quant_9")
    quant_10 = fields.Float(string='RA4 - BFR en jours CA', related="workflow.risk_scoring.quant_10")
    quant_11 = fields.Float(string='RA5 - Stock en jours CA', related="workflow.risk_scoring.quant_11")
    quant_12 = fields.Float(string='RR1 - VA / CA', related="workflow.risk_scoring.quant_12")
    quant_13 = fields.Float(string='RR2 - EBE / (Immo. + BFR)', related="workflow.risk_scoring.quant_13")
    quant_14 = fields.Float(string='RR3 - Résultat d`exploitation / FP', related="workflow.risk_scoring.quant_14")
    quant_15 = fields.Float(string='RR4 - RN / TB', related="workflow.risk_scoring.quant_15")
    quant_16 = fields.Float(string='RR5 - CAF / TB', related="workflow.risk_scoring.quant_16")
    res_quant_1 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_1")
    res_quant_2 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_2")
    res_quant_3 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_3")
    res_quant_4 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_4")
    res_quant_5 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_5")
    res_quant_6 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_6")
    res_quant_7 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_7")
    res_quant_8 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_8")
    res_quant_9 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_9")
    res_quant_10 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_10")
    res_quant_11 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_11")
    res_quant_12 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_12")
    res_quant_13 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_13")
    res_quant_14 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_14")
    res_quant_15 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_15")
    res_quant_16 = fields.Integer(string='Result Weighting', related="workflow.risk_scoring.res_quant_16")
    resultat_scoring = fields.Integer(string='Scoring Result ', related="workflow.risk_scoring.resultat_scoring")
