from odoo import models, fields, api, _
from odoo.tools import format_date


class ReportTwo(models.Model):
    _name = 'wk.report.two'

    name = fields.Char(string='الاسم', compute='_compute_name', store=True)
    date_debut = fields.Date(string='من')
    date_fin = fields.Date(string='الى')
    code = fields.Many2one('wk.agence', string='الفرع')

    line_ids = fields.One2many('wk.report2.table', 'line', string='Les lignes')

    @api.depends('date_debut', 'date_fin', 'code')
    def _compute_name(self):
        for record in self:
            if record.date_debut and record.date_fin:
                date_debut_str = format_date(self.env, record.date_debut, date_format='dd-MM-yyyy')
                date_fin_str = format_date(self.env, record.date_fin, date_format='dd-MM-yyyy')
                code_str = record.code.name if record.code else _('Unknown Code')
                record.name = f'تقرير الفرع {code_str} من {date_debut_str} الى {date_fin_str}'
            else:
                record.name = _('Test')


    @api.onchange('date_debut', 'date_fin', 'code')
    def _onchange_date_range(self):
        if self.date_debut and self.date_fin and self.code:
            self._compute_line_ids()

    @api.model
    def create(self, vals):
        record = super(ReportTwo, self).create(vals)
        if record.date_debut and record.date_fin and record.code:
            record._compute_line_ids()
        return record

    def write(self, vals):
        res = super(ReportTwo, self).write(vals)
        if 'date_debut' in vals or 'date_fin' in vals or 'code' in vals:
            self._compute_line_ids()
        return res

    def _compute_line_ids(self):
        self.line_ids = [(5, 0, 0)]
        workflows = self.env['wk.workflow.dashboard'].search([
            ('date', '>=', self.date_debut),
            ('date', '<=', self.date_fin),
            ('branche', '=', self.code.id) 
        ])
        users = self.env['res.users'].search([])

        report_lines = []

        for user in users:
            processed_finance_num = processed_agence_num = processed_commercial_num = processed_risque_num = 0
            processed_finance_prg = processed_agence_prg = processed_commercial_prg = processed_risque_prg = 0
            finance_duration = agence_duration = commercial_duration = risque_duration = 0

            for workflow in workflows:
                for state in workflow.states:
                    # Finance processing logic
                    if state.state_finance in ['finance_1', 'finance_2', 'finance_3', 'finance_5', 'finance_6', 'finance_7', 'finance_4']:
                        if workflow.assigned_to_finance == user:
                            tracking_records = self._get_tracking_records_finance(workflow, state)
                            if state.state_compute < 1:
                                processed_finance_prg += 1
                            else:
                                processed_finance_num += 1
                                finance_duration += sum(tracking.difference for tracking in tracking_records)

                    # Branch processing logic
                    if state.state_branch in ['branch_1', 'branch_2', 'branch_3', 'branch_4', 'branch_5']:
                        if workflow.assigned_to_agence == user:
                            tracking_records = self._get_tracking_records_branch(workflow, state)
                            if state.state_compute < 1:
                                processed_agence_prg += 1
                            else:
                                processed_agence_num += 1
                                agence_duration += sum(tracking.difference for tracking in tracking_records)

                    # Commercial processing logic
                    if state.state_commercial in ['commercial_1', 'commercial_2', 'commercial_3', 'commercial_4']:
                        if workflow.assigned_to_commercial == user:
                            tracking_records = self._get_tracking_records_commercial(workflow, state)
                            if state.state_compute < 1:
                                processed_commercial_prg += 1
                            else:
                                processed_commercial_num += 1
                                commercial_duration += sum(tracking.difference for tracking in tracking_records)

                    # Risk processing logic
                    if state.state_risque in ['risque_1', 'risque_2', 'risque_3', 'risque_4']:
                        if workflow.assigned_to_risque == user:
                            tracking_records = self._get_tracking_records_risque(workflow, state)
                            if state.state_compute < 1:
                                processed_risque_prg += 1
                            else:
                                processed_risque_num += 1
                                risque_duration += sum(tracking.difference for tracking in tracking_records)

            if processed_finance_num > 0 or processed_finance_prg > 0:
                avg_duration = finance_duration / processed_finance_num if processed_finance_num > 0 else 0
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'مديرية التمويلات',
                    'processed_file_num': processed_finance_num,
                    'processed_file_prg': processed_finance_prg,
                    'processed_file_avrg': avg_duration
                }))
            if processed_agence_num > 0 or processed_agence_prg > 0:
                avg_duration = agence_duration / processed_agence_num if processed_agence_num > 0 else 0
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'الفرع',
                    'code': self.code.name,
                    'processed_file_num': processed_agence_num,
                    'processed_file_prg': processed_agence_prg,
                    'processed_file_avrg': avg_duration,
                }))
            if processed_commercial_num > 0 or processed_commercial_prg > 0:
                avg_duration = commercial_duration / processed_commercial_num if processed_commercial_num > 0 else 0
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'مديرية الاعمال التجارية',
                    'processed_file_num': processed_commercial_num,
                    'processed_file_prg': processed_commercial_prg,
                    'processed_file_avrg': avg_duration
                }))
            if processed_risque_num > 0 or processed_risque_prg > 0:
                avg_duration = risque_duration / processed_risque_num if processed_risque_num > 0 else 0
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'ادارة المخاطر',
                    'processed_file_num': processed_risque_num,
                    'processed_file_prg': processed_risque_prg,
                    'processed_file_avrg': avg_duration
                }))

        self.write({'line_ids': report_lines})

    
    def _get_tracking_records_finance(self, workflow, state):
        return self.env['wk.tracking'].search([
            ('workflow_id', '=', workflow.id),
            ('etape_id', '=', state.id),
            ('state', 'in', ['finance_1', 'finance_2', 'finance_3', 'finance_5', 'finance_6', 'finance_7'])
        ])

    def _get_tracking_records_branch(self, workflow, state):
        return self.env['wk.tracking'].search([
            ('workflow_id', '=', workflow.id),
            ('etape_id', '=', state.id),
            ('state', 'in', ['branch_1', 'branch_2', 'branch_3', 'branch_4'])
        ])

    def _get_tracking_records_commercial(self, workflow, state):
        return self.env['wk.tracking'].search([
            ('workflow_id', '=', workflow.id),
            ('etape_id', '=', state.id),
            ('state', 'in', ['commercial_1', 'commercial_2', 'commercial_3'])
        ])

    def _get_tracking_records_risque(self, workflow, state):
        return self.env['wk.tracking'].search([
            ('workflow_id', '=', workflow.id),
            ('etape_id', '=', state.id),
            ('state', 'in', ['risque_1', 'risque_3', 'risque_4'])
        ])

class Table(models.Model):
    _name = 'wk.report2.table'

    management = fields.Char(string='الإدارة')
    employee_name = fields.Many2one('res.users', string='اسم الموظف')
    processed_file_num = fields.Integer(string='عدد الملفات المعالجة')
    processed_file_avrg = fields.Integer(string='متوسط مدة المعالجة')
    processed_file_prg = fields.Integer(string='عدد الملفات جاري المعالجة ')
    code = fields.Char(string='رمز الفرع') 

    line = fields.Many2one('wk.report.two', ondelete="cascade")
