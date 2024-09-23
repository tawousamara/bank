from odoo import models, fields, api, _

class ReportOne(models.Model):
    _name = 'wk.report.one'

    name = fields.Char(string='الاسم', compute='_compute_name', store=True)
    folder_number = fields.Many2one('wk.workflow.dashboard', string='رقم الملف')
    customer_name = fields.Many2one('res.partner', string='اسم المتعامل')
    line_ids = fields.One2many('wk.report1.table', 'line', string='Les lignes')

    @api.depends('folder_number', 'customer_name')
    def _compute_name(self):
        for record in self:
            if record.folder_number:
                record.customer_name = False
                record.name = f'{record.folder_number.name} تقرير الملف رقم'
            elif record.customer_name:
                record.name = f'{record.customer_name.name} تقرير العميل'
            else:
                record.name = _('Test')

    @api.onchange('folder_number', 'customer_name')
    def _onchange_folder_number(self):
        self._compute_line_ids()

    @api.model
    def create(self, vals):
        record = super(ReportOne, self).create(vals)
        record._compute_line_ids() if record.folder_number or record.customer_name else None
        return record

    def write(self, vals):
        res = super(ReportOne, self).write(vals)
        if 'folder_number' in vals or 'customer_name' in vals:
            self._compute_line_ids()
        return res

    def _compute_line_ids(self):
        self.line_ids = [(5, 0, 0)]
        workflows = []
        
        if self.folder_number:
            workflows.append(self.folder_number)
        elif self.customer_name:
            workflows = self.env['wk.workflow.dashboard'].search([('nom_client', '=', self.customer_name.id)])

        for workflow in workflows:
            branch = workflow.branche.id if workflow.branche else False
            nom_client = workflow.nom_client.id if workflow.nom_client else False
            entry_date = workflow.date if workflow.date else False
            name = workflow.id if workflow.id else 'No Name'

            line_vals = {
                'folder_number': name,
                'customer_name': nom_client,
                'branch': branch,
                'entry_date': entry_date,
            }
            line = self.line_ids.new(line_vals)
            line.compute_dates(workflow)
            self.line_ids += line

class Table(models.Model):
    _name = 'wk.report1.table'

    folder_number = fields.Many2one('wk.workflow.dashboard', string='رقم الملف')
    customer_name = fields.Many2one('res.partner', string='اسم المتعامل')
    branch = fields.Many2one('wk.agence', string='الفرع')
    entry_date = fields.Date(string='تاريخ الادخال ')
    date_num_branch = fields.Integer(string='عدد الأيام في الفرع',  store=True)
    date_num_finance = fields.Integer(string='عدد الأيام في التمويل',  store=True)
    date_num_risk = fields.Integer(string='عدد الأيام في المخاطر', store=True)
    date_num_commercial = fields.Integer(string='عدد الأيام في التجارية',store=True)

    line = fields.Many2one('wk.report.one', ondelete="cascade")

    def compute_dates(self, workflow):
        self.date_num_branch = self._compute_days(workflow, ['branch_1', 'branch_2', 'branch_3', 'branch_4'])
        self.date_num_finance = self._compute_days(workflow, ['finance_1', 'finance_2', 'finance_3', 'finance_4', 'finance_5', 'finance_6', 'finance_7'])
        self.date_num_risk = self._compute_days(workflow, ['risque_1', 'risque_3', 'risque_4'])
        self.date_num_commercial = self._compute_days(workflow, ['commercial_1', 'commercial_2', 'commercial_3'])

    def _compute_days(self, workflow, state_list):
        total_days = 0
        tracking_records = self._get_tracking_records(workflow, state_list)
        total_days += sum(tracking.difference for tracking in tracking_records)
        return total_days

    def _get_tracking_records(self, workflow, state_list):
        return self.env['wk.tracking'].search([
            ('workflow_id', '=', workflow.id),
            ('state', 'in', state_list),
            ('difference', '!=', None)
        ])
