from odoo import models, fields, api, _

# critere qualitatif

class originalCapital(models.Model):
    _name = 'risk.original.capital'
    _description = 'original du capital et sa ponderation'

    name = fields.Char(string='أصل رأس المال')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')

class Actionnariat(models.Model):
    _name = 'risk.actionnariat'
    _description = 'actionnariat et sa ponderation'

    name = fields.Char(string='المساهمات')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')

class FormeJur(models.Model):
    _name = 'risk.forme.jur'
    _description = 'forme juridique et sa ponderation'

    name = fields.Char(string='الشكل القانوني')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class RempSuccession(models.Model):
    _name = 'risk.remplacement.succession'
    _description = 'Remplacement et succession et sa ponderation'

    name = fields.Char(string='الخلافة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Competence(models.Model):
    _name = 'risk.competence'
    _description = 'Compétence et sa ponderation'

    name = fields.Char(string='الكفاءة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Experience(models.Model):
    _name = 'risk.experience'
    _description = 'Expérience et sa ponderation'

    name = fields.Char(string='الخبرة المهنية')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class SoutienEtatique(models.Model):
    _name = 'risk.soutien.etatique'
    _description = 'Soutien étatique et sa ponderation'

    name = fields.Char(string='دعم الدولة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Activite(models.Model):
    _name = 'risk.activite'
    _description = 'Activité et sa ponderation'

    name = fields.Char(string='النشاط')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class InfluenceTech(models.Model):
    _name = 'risk.influence.tech'
    _description = 'Influence technologique et sa ponderation'

    name = fields.Char(string='التكنولوجيا المستعملة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Anciennete(models.Model):
    _name = 'risk.anciennete'
    _description = 'Ancienneté et sa ponderation'

    name = fields.Char(string='الأقدمية')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Concurrence(models.Model):
    _name = 'risk.concurrence'
    _description = 'Concurrence et sa ponderation'

    name = fields.Char(string='المنافسة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class SourceAppro(models.Model):
    _name = 'risk.source.appro'
    _description = 'Sources d’approvisionnement et sa ponderation'

    name = fields.Char(string='الموردون')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Produit(models.Model):
    _name = 'risk.produit'
    _description = 'Produit de l’entreprise et sa ponderation'

    name = fields.Char(string='المنتوج')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Flexibilite(models.Model):
    _name = 'risk.flexibilite'
    _description = 'Flexibilité et sa ponderation'

    name = fields.Char(string='المرونة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Sollicitude(models.Model):
    _name = 'risk.sollicitude'
    _description = 'Sollicitude des confrères et sa ponderation'

    name = fields.Char(string='طلب القروض لدى البنوك الزميلة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Situation(models.Model):
    _name = 'risk.situation'
    _description = 'Situation patrimoniale des actionnaires et sa ponderation'

    name = fields.Char(string='الأملاك العقارية للشركاء/المساهمين')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Mouvement(models.Model):
    _name = 'risk.mouvement'
    _description = 'Mouvements confiés et sa ponderation'

    name = fields.Char(string='الإيداعات')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class Garanties(models.Model):
    _name = 'risk.garanties'
    _description = 'Garanties proposées et sa ponderation'

    name = fields.Char(string='الضمانات المقترحة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class incident(models.Model):
    _name = 'risk.incident'
    _description = 'Incidents de paiement et sa ponderation'

    name = fields.Char(string='التعثرات')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class conduite(models.Model):
    _name = 'risk.conduite'
    _description = 'Conduite du client et sa ponderation'

    name = fields.Char(string='سيرة المتعامل')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class DetteFisc(models.Model):
    _name = 'risk.dette.fisc'
    _description = 'Dette fiscale et sa ponderation'

    name = fields.Char(string='الضرائب')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class DetteParafisc(models.Model):
    _name = 'risk.dette.parafisc'
    _description = 'Dette parafiscale et sa ponderation'

    name = fields.Char(string='الضمان الاجتماعي')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class PositionAdmin(models.Model):
    _name = 'risk.position.admin'
    _description = 'Position envers autres administrations et sa ponderation'

    name = fields.Char(string='إدارات أخرى')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class SourceRemb(models.Model):
    _name = 'risk.source.remb'
    _description = 'Sources de remboursement et sa ponderation'

    name = fields.Char(string='مصادر التسديد')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')


class PartProfil(models.Model):
    _name = 'risk.part.profil'
    _description = 'Part du profit de la contrepartie au total PNB et sa ponderation'

    name = fields.Char(string='ربحية المصرف من التمويلات الممنوحة')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere', ondelete='cascade')

# critere quantitatif


class Quant1(models.Model):
    _name = 'risk.quant.1'
    _description = 'Quantité 1 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant1, self).create(vals)
        return res
    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant1, self).write(vals)
        return res


class Quant2(models.Model):
    _name = 'risk.quant.2'
    _description = 'Quantité 2 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant2, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant2, self).write(vals)
        return res


class Quant3(models.Model):
    _name = 'risk.quant.3'
    _description = 'Quantité 3 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant3, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant3, self).write(vals)
        return res


class Quant4(models.Model):
    _name = 'risk.quant.4'
    _description = 'Quantité 4 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant4, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant4, self).write(vals)
        return res


class Quant5(models.Model):
    _name = 'risk.quant.5'
    _description = 'Quantité 5 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant5, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant5, self).write(vals)
        return res


class Quant6(models.Model):
    _name = 'risk.quant.6'
    _description = 'Quantité 6 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant6, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant6, self).write(vals)
        return res


class Quant7(models.Model):
    _name = 'risk.quant.7'
    _description = 'Quantité 7 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant7, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant7, self).write(vals)
        return res


class Quant8(models.Model):
    _name = 'risk.quant.8'
    _description = 'Quantité 8 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant8, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant8, self).write(vals)
        return res


class Quant9(models.Model):
    _name = 'risk.quant.9'
    _description = 'Quantité 9 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant9, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant9, self).write(vals)
        return res


class Quant10(models.Model):
    _name = 'risk.quant.10'
    _description = 'Quantité 10 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant10, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant10, self).write(vals)
        return res


class Quant11(models.Model):
    _name = 'risk.quant.11'
    _description = 'Quantité 11 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant11, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant11, self).write(vals)
        return res


class Quant12(models.Model):
    _name = 'risk.quant.12'
    _description = 'Quantité 12 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant12, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant12, self).write(vals)
        return res


class Quant13(models.Model):
    _name = 'risk.quant.13'
    _description = 'Quantité 13 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant13, self).create(vals)
        return res
    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant13, self).write(vals)
        return res


class Quant14(models.Model):
    _name = 'risk.quant.14'
    _description = 'Quantité 14 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant14, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant14, self).write(vals)
        return res


class Quant15(models.Model):
    _name = 'risk.quant.15'
    _description = 'Quantité 15 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant15, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant15, self).write(vals)
        return res


class Quant16(models.Model):
    _name = 'risk.quant.16'
    _description = 'Quantité 16 et sa ponderation'

    name = fields.Char(string='nom', readonly=True)
    du = fields.Integer(string='Du')
    au = fields.Integer(string='Au')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.quantitatif', string='critere', ondelete='cascade')

    @api.model
    def create(self, vals):
        vals['name'] = str(vals['du']) + '< X <=' + str(vals['au'])
        res = super(Quant16, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        for rec in self:
            if vals['du']:
                du = str(vals['du'])
            else:
                du = str(rec.du)
            if vals['au']:
                au = str(vals['au'])
            else:
                au = str(rec.au)
            vals['name'] = du + '< X <=' + au
        res = super(Quant16, self).write(vals)
        return res


