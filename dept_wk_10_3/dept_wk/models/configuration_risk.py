import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
original = [
    ['مختلط أو ينتمي لمجمع', 10],
    ['محلي', 7],
    ['خارجي', 6]
]

forme = [
    ['شركة تضامن', 10],
    ['شركة ذات أسهم', 8],
    ['شركة ذات مسؤولية محدودة', 6],
    ['شركة ذات مسؤولية محدودة للشخص الوحيد', 6],
    ['شخص طبيعي', 10]
]

actiona = [
    ['عائلية', 15],
    ['أخرى', 10]
]

bool_list = [
    ['مضمونة',5],
    ['غير مضمونة',0]
]

comp_list = [
    ['عالية', 15],
    ['متوسطة', 8],
    ['ضعيفة', 0]
]
exp_list = [
    ['جيدة', 15],
    ['متوسطة', 8],
    ['ضعيفة', 3]
]

activite_list = [
    ['تطور', 30],
    ['تراجع ', 5],
    ['ركود', 10]
]

influence_list = [
    ['تأثيرها على المنتوج ضعيفة', 15],
    ['تأثيرها على المنتوج متوسطة', 8],
    ['تأثيرها على المنتوج عالية', 5]
]

anciente_list = [
    ['أكثر من 10 سنوات', 20],
    ['بين 5 و 10 سنوات', 15],
    ['بين 2 و 5 سنوات', 10],
    ['أقل من سنتين', 5]
]

concurrence_list = [
    ['ضعيفة', 20],
    ['متوسطة', 10],
    ['قوية', 5]
]

source_appro_list = [
    ['متنوع', 15],
    ['مركز', 5]
]

produit_list = [
    ['متنوع', 10],
    ['مركز', 5]
]

flexibilite_list = [
    ['حقيقية', 15],
    ['ممكنة', 5],
    ['غير ممكنة', 0]
]
solicitude_list = [
    ['قبول جيد', 30],
    ['متوسطة', 15],
    ['منعم', 5]
]
situation_list = [
    ['جيدة', 30],
    ['متوسطة', 15],
    ['ضعيفة', 5]
]

mouv_list = [
    ['أقل من 10%', 5],
    ['من 10% إلى 25%', 20],
    ['من 25% إلى 40%', 30],
    ['من 40% إلى 60%', 40],
    ['أكثر من 60%', 60]
]

garanties_list = [
    ['لا توجد', 0],
    ['كفالة', 25],
    ['عقارية درجة الأولى / مالية', 50],
    ['عقارية درجة الثانية/الثالثة', 45],
    ['بنكية/شركة ضمان تمويل', 40]
]

incident_list = [
    ['منعدمة', 30],
    ['مرة في السنة', 20],
    ['مرتين في السنة', 15],
    ['ثلاث مرات في السنة', 10],
    ['متعددة', 0]
]

conduite_list = [
    ['جد محترم', 30],
    ['محترم', 20],
    ['غير محترم', 0]
]

dette_fisc = [
    ['محين', 40],
    ['بجدول سداد محترم', 20],
    ['بجدول سداد غير محترم', 5],
    ['غير محين', 0]
]
dette_parafisc = [
    ['محين', 30],
    ['بجدول سداد محترم', 20],
    ['بجدول سداد غير محترم', 5],
    ['غير محين', 0]
]
position_list = [
    ['متوافق', 30],
    ['في صراع و بدون تأثير على النشاط', 10],
    ['في صراع بتأثير على النشاط', 0]

]

source_remb = [
    ['من نشاط الشركة', 40],
    ['من غير نشاط الشركة', 20],
    ['تفعيل ضمان', 5]
]

part_profit = [
    ['أقل من 0,01%', 15],
    ['من 0,01% إلى 0,1%', 20],
    ['من 0,1% إلى 0,5%', 25],
    ['أكثر من 0,5%', 30],
    ['متعامل جديد', 25]
]


class CritereQualitatif(models.Model):
    _name = 'risk.critere.qualitatif'

    name = fields.Char()
    date = fields.Date(string='Date')
    original_capital = fields.One2many('risk.original.capital', 'critere', string='Original du capital')
    actionnariat = fields.One2many('risk.actionnariat', 'critere', string='Actionnariat')
    forme_jur = fields.One2many('risk.forme.jur', 'critere', string='Forme juridique')
    remp_succession = fields.One2many('risk.remplacement.succession', 'critere', string='Remplacement et succession')
    competence = fields.One2many('risk.competence', 'critere', string='Competence')
    experience = fields.One2many('risk.experience', 'critere', string='Expérience')
    soutien_etatic = fields.One2many('risk.soutien.etatique', 'critere', string='Soutien étatique')
    activite = fields.One2many('risk.activite', 'critere', string='Activité')
    influence_tech = fields.One2many('risk.influence.tech', 'critere', string='Influence technologique')
    anciennete = fields.One2many('risk.anciennete', 'critere', string='Ancienneté')
    concurrence = fields.One2many('risk.concurrence', 'critere', string='Concurrence')
    source_appro = fields.One2many('risk.source.appro', 'critere', string='Sources d’approvisionnement')
    produit = fields.One2many('risk.produit', 'critere', string='Produit de l’entreprise')
    flexibilite = fields.One2many('risk.flexibilite', 'critere', string='Flexibilité')
    sollicitude = fields.One2many('risk.sollicitude', 'critere', string='Sollicitude des confrères')
    situation = fields.One2many('risk.situation', 'critere', string='Situation patrimoniale des actionnaires ')
    mouvement = fields.One2many('risk.mouvement', 'critere', string='Mouvements confiés')
    garanties = fields.One2many('risk.garanties', 'critere', string='Garanties proposées')
    incident = fields.One2many('risk.incident', 'critere', string='Incidents de paiement')
    conduite = fields.One2many('risk.conduite', 'critere', string='Conduite du client')
    dette_fisc = fields.One2many('risk.dette.fisc', 'critere', string='Dette fiscale')
    dette_parafisc = fields.One2many('risk.dette.parafisc', 'critere', string='Dette parafiscale')
    position_admin = fields.One2many('risk.position.admin', 'critere', string='Position envers autres administrations')
    source_remb = fields.One2many('risk.source.remb', 'critere', string='Sources de remboursement')
    part_profil = fields.One2many('risk.part.profil', 'critere', string='Part du profit de la contrepartie au total PNB')

    @api.model
    def create(self, vals):
        res = super(CritereQualitatif, self).create(vals)
        for item in original:
            self.env['risk.original.capital'].create({'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in forme:
            self.env['risk.forme.jur'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in actiona:
            self.env['risk.actionnariat'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in bool_list:
            self.env['risk.remplacement.succession'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
            self.env['risk.soutien.etatique'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in comp_list:
            self.env['risk.competence'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in exp_list:
            self.env['risk.experience'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in activite_list:
            self.env['risk.activite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in influence_list:
            self.env['risk.influence.tech'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in anciente_list:
            self.env['risk.anciennete'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in concurrence_list:
            self.env['risk.concurrence'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in source_appro_list:
            self.env['risk.source.appro'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in produit_list:
            self.env['risk.produit'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in flexibilite_list:
            self.env['risk.flexibilite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in solicitude_list:
            self.env['risk.sollicitude'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in situation_list:
            self.env['risk.situation'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in mouv_list:
            self.env['risk.mouvement'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in garanties_list:
            self.env['risk.garanties'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in incident_list:
            self.env['risk.incident'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in conduite_list:
            self.env['risk.conduite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in dette_fisc:
            self.env['risk.dette.fisc'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
            self.env['risk.dette.parafisc'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in position_list:
            self.env['risk.position.admin'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in source_remb:
            self.env['risk.source.remb'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in part_profit:
            self.env['risk.part.profil'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        return res


list_quant_1 = [
    [0, 20, 10],
    [20, 25, 25],
    [25, 30, 40],
    [30, 40, 55],
    [40, 50, 60],
    [50, 60, 65],
    [60, 100, 70],
]
list_quant_2 = [
    [0, 20, 5],
    [20, 30, 15],
    [30, 50, 20],
    [50, 60, 23],
    [60, 70, 25],
    [70, 80, 30],
    [80, 100, 40],
]
list_quant_3 = [
    [-100, 0, 1],
    [0, 20, 5],
    [20, 30, 10],
    [30, 40, 20],
    [40, 50, 25],
    [50, 70, 32],
    [70, 100, 40],
]
list_quant_4 = [
    [0, 1, 25],
    [1, 2, 20],
    [2, 3, 15],
    [3, 4, 10],
    [4, 5, 6],
    [5, 6, 3],
    [6, 100, 1],
]
list_quant_5 = [
    [0, 20,1],
    [20, 30,2],
    [30, 50,5],
    [50, 70,10],
    [70, 90,15],
    [90, 100,40],
]
list_quant_6 = [
    [0, 10,2],
    [10, 20,7],
    [20, 30,11],
    [30, 50,14],
    [50, 70,21],
    [70, 90,28],
    [90, 100,35],
]
list_quant_7 = [
    [0, 30, 5],
    [30, 45, 7],
    [45, 60, 10],
    [60, 75, 12],
    [75, 90, 14],
    [90, 120, 18],
    [120, 600, 24],
]
list_quant_8 = [
    [0, 30, 24],
    [30, 45, 18],
    [45, 60, 14],
    [60, 75, 12],
    [75, 90, 10],
    [90, 120, 7],
    [120, 600, 5],
]
list_quant_9 = [
    [0, 15, 0],
    [15, 30, 6],
    [30, 60, 13],
    [60, 100, 19],
]
list_quant_10 = [
    [0, 15, 14],
    [15, 30, 10],
    [30, 60, 6],
    [60, 100, 0],
]
list_quant_11 = [
    [0, 30, 3],
    [30, 45, 4],
    [45, 60, 6],
    [60, 75, 7],
    [75, 90, 8],
    [90, 120, 10],
    [120, 600, 14],
]
list_quant_12 = [
    [0, 20, 1],
    [20, 30, 2],
    [30, 50, 4],
    [50, 100, 6],
]
list_quant_13 = [
    [0, 3, 1],
    [3, 5, 2],
    [5, 8, 4],
    [8, 10, 5],
    [10, 100, 6],
]
list_quant_14 = [
    [0, 10, 1],
    [10, 15, 3],
    [15, 20, 4],
    [20, 30, 5],
    [30, 100, 6],
]
list_quant_15 = [
    [0, 10, 1],
    [10, 20, 3],
    [20, 30, 5],
    [30, 100, 6],
]
list_quant_16 = [
    [0, 10, 1],
    [10, 20, 2],
    [20, 30, 3],
    [30, 100, 6],
]


class CritereQuantitatif(models.Model):
    _name = 'risk.critere.quantitatif'
    _description = 'Configuration Critere Quantitatif'

    name = fields.Char(string='Nom')
    date = fields.Date(string='Date')
    quant_1 = fields.One2many('risk.quant.1', 'critere', string='RS1 - FP / TB')
    quant_2 = fields.One2many('risk.quant.2', 'critere', string='RS2 - FP / Capitaux permanents *100')
    quant_3 = fields.One2many('risk.quant.3', 'critere', string='RS3 - FRN / Actif circulants hors tréso.')
    quant_4 = fields.One2many('risk.quant.4', 'critere', string='RS4 - DLMT / CAF')
    quant_5 = fields.One2many('risk.quant.5', 'critere', string='RL1 - Actif circulants / DCT *100')
    quant_6 = fields.One2many('risk.quant.6', 'critere', string='RL2 - Disponibilité / DCT *100')
    quant_7 = fields.One2many('risk.quant.7', 'critere', string='RA1 - Stock en jours Achats')
    quant_8 = fields.One2many('risk.quant.8', 'critere', string='RA2 - Créances clients en jours CA')
    quant_9 = fields.One2many('risk.quant.9', 'critere', string='RA3 - FRN rn jours CA')
    quant_10 = fields.One2many('risk.quant.10', 'critere', string='RA4 - BFR en jours CA')
    quant_11 = fields.One2many('risk.quant.11', 'critere', string='RA5 - Stock en jours CA')
    quant_12 = fields.One2many('risk.quant.12', 'critere', string='RR1 - VA / CA')
    quant_13 = fields.One2many('risk.quant.13', 'critere', string='RR2 - EBE / (Immo. + BFR)')
    quant_14 = fields.One2many('risk.quant.14', 'critere', string='RR3 - Résultat d`exploitation / FP')
    quant_15 = fields.One2many('risk.quant.15', 'critere', string='RR4 - RN / TB')
    quant_16 = fields.One2many('risk.quant.16', 'critere', string='RR5 - CAF / TB')

    @api.model
    def create(self, vals):
        res = super(CritereQuantitatif, self).create(vals)

        for item in list_quant_1:
            self.env['risk.quant.1'].create({'du': item[0],
                                             'au': item[1],
                                             'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_2:
            self.env['risk.quant.2'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_3:
            self.env['risk.quant.3'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_4:
            self.env['risk.quant.4'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_6:
            self.env['risk.quant.6'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_7:
            self.env['risk.quant.7'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_8:
            self.env['risk.quant.8'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_11:
            self.env['risk.quant.11'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_10:
            self.env['risk.quant.10'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_9:
            self.env['risk.quant.9'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_12:
            self.env['risk.quant.12'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_13:
            self.env['risk.quant.13'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_14:
            self.env['risk.quant.14'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_15:
            self.env['risk.quant.15'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        for item in list_quant_16:
            self.env['risk.quant.16'].create({'du': item[0],
                                             'au': item[1],'ponderation': item[2],
                                             'critere': res.id})
        return res


class Hist(models.Model):
    _name = 'wk.hist'
    _description = 'fffff'

    workflow = fields.Many2one('wk.workflow.dashboard', string='Demande')
    date = fields.Date(string='Date')
    name = fields.Char(string='Name')
    nom_client = fields.Many2one('res.partner', string='اسم المتعامل')
    resultat_scoring = fields.Integer(string='التنقيط الاجمالي', compute='resultat')
    plafond = fields.Float(string='Plafond de crédit')

    def resultat(self):
        for rec in self:
            rec.resultat_scoring = rec.workflow.risk_scoring.resultat_scoring


class ChiffreBank(models.Model):
    _name = 'configuration.risque'

    date_from = fields.Date(string='من')
    date_to = fields.Date(string='الى')
    montant = fields.Float(string='المبلغ')

