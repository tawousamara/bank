import uuid

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError, UserError
from collections import defaultdict

class IrAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'mail.thread']
    
    folder_id = fields.Many2one('documents.folders', string='Directory', ondelete='cascade')
    tag_ids = fields.Many2many('documents.tags', 'attachment_tags_rel','attachment_id', 'tag_id', string='Tags')
    color = fields.Integer('Color Index', default=0)    
    version = fields.Integer('Version', default=0, readonly=True)
    code = fields.Char('Coder', default=lambda self: _('New'), copy=False, readonly=True, tracking=True)
    access_token = fields.Char('Token', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", tracking=True)
    shared_user_ids = fields.Many2many('res.users', string="Shared Users",help="If you choose users, it will only be viewable to those individuals.")
    is_personal_directory = fields.Boolean(related="folder_id.is_personal_directory", string="Is Personal Document", store=True)
    is_portal_directory = fields.Boolean(related="folder_id.is_portal_directory", string="Is Portal Document", store=True)
    is_shared_file = fields.Boolean(compute='_compute_is_shared_file',string="Is a Shared File", default=False)
    allow_shared_download = fields.Boolean('Allow viewing of shared files')
    doc = fields.Many2one('wk.document.check', string='الملف')

    @api.constrains("folder_id")
    def check_folder_id_permission(self):
        user_id = self.env.ref("documents_portal_management.group_document_user").id or self.env.ref("documents_portal_management.group_document_manager")
        if (user_id not in self.env.user.groups_id.ids):
            raise AccessError(_("Sorry, You are not authorized to change the folder."))

    @api.depends('shared_user_ids')
    def _compute_is_shared_file(self):
        user = self.env.uid
        for rec in self:
            if user in rec.shared_user_ids.ids and user != rec.create_uid.id:
                rec.is_shared_file = True
            else:
                rec.is_shared_file = False
        
    def _ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token
        
    @api.model
    def create(self,vals):
    
        model = vals.get('res_model',False)
        name = vals.get('name',False)
        res_id = vals.get('res_id',False)

        folder = self.env['documents.folders'].sudo().search([('model_id.model', '=', model)])
        if folder:
            vals.update({
                'folder_id': folder.id,
            })                
        
        if name:
            attachments = self.env['ir.attachment'].search([('name', '=', name),('res_model','=',model),('res_id','=',res_id)], order="id desc")
            version =  False
            if attachments:
                last_attachment = self.env['ir.attachment'].browse(max(attachments.ids))                
                version = last_attachment.version + 1
            else:                
                version = 1
            
            vals.update({
                'version': version
            })

        code = self.env['ir.sequence'].next_by_code('ir.attachment.code')
        if code:
            vals.update({
                'code' : code,
            })
        return super(IrAttachment, self).create(vals)
    
    def _find_mail_template(self):
        template_id = False
        if not template_id:
            template_id = self.env['ir.model.data']._xmlid_to_res_id('documents_portal_management.email_template_attachments', raise_if_not_found=False)
        return template_id
    
    def action_attachment_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False

        ctx = {
            'default_model': 'ir.attachment',
            'active_model': 'ir.attachment',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'custom_layout': "mail.mail_notification_light",
            'default_attachment_ids': [(6, 0, [self.id])]
        }

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def _read_group_allowed_fields(self):
        return ['folder_id', 'type', 'company_id', 'res_id', 'create_date', 'create_uid', 'name', 'mimetype', 'id', 'url', 'res_field', 'res_model']
    
    @api.model
    def default_get(self, fields):
        vals = super(IrAttachment, self).default_get(fields)
        is_personal_directory = self.env.context.get('default_is_personal_directory')
        if is_personal_directory:
            personal_folder = self.env.ref('documents_portal_management.personal_folder')
            vals['folder_id'] = personal_folder.id
        return vals
    
    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to a attachment
        if not (self.env.is_admin() or self.env.user._is_internal() \
            or self.env.user.has_group('base.group_portal')):
            raise AccessError(_("Sorry, you are not allowed to access this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)            # {model_name: set(ids)}
        if self:
            # DLE P173: `test_01_portal_attachment`
            self.env['ir.attachment'].flush_model(['res_model', 'res_id', 'create_uid', 'public', 'allow_shared_download', 'res_field'])
            self._cr.execute('SELECT res_model, res_id, create_uid, public, allow_shared_download, res_field FROM ir_attachment WHERE id IN %s', [tuple(self.ids)])
            for res_model, res_id, create_uid, public, allow_shared_download, res_field in self._cr.fetchall():
                if allow_shared_download:
                    continue
                if public and mode == 'read':
                    continue
                if not self.env.is_system() and res_field:
                    raise AccessError(_("Sorry, you are not allowed to access this document."))
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list of writeable fields
                # e.g. in the case of a user inserting an image into his image signature
                # we need to bypass this check which would needlessly throw us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)
