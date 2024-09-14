from odoo import models, fields, api, _
from odoo.tools import format_date

class ReportTwo(models.Model):
    _name = 'wk.report.two'
    
    name = fields.Char(string='الاسم', compute='_compute_name', store=True)
    date_debut = fields.Date(string='من')
    date_fin = fields.Date(string='الى')
    line_ids = fields.One2many('wk.report2.table', 'line', string='Les lignes')
    
    @api.depends('date_debut', 'date_fin')
    def _compute_name(self):
        for record in self:
            if record.date_debut and record.date_fin:
                date_debut_str = format_date(self.env, record.date_debut, date_format='dd-MM-yyyy')
                date_fin_str = format_date(self.env, record.date_fin, date_format='dd-MM-yyyy')
                record.name = f'{date_fin_str} الى {date_debut_str} التقرير من'
            else:
                record.name = _('Test')

    @api.onchange('date_debut', 'date_fin')
    def _onchange_date_range(self):
        if self.date_debut and self.date_fin:
            self._compute_line_ids()

    @api.model
    def create(self, vals):
        record = super(ReportTwo, self).create(vals)
        if record.date_debut and record.date_fin:
            record._compute_line_ids()
        return record

    def write(self, vals):
        res = super(ReportTwo, self).write(vals)
        if 'date_debut' in vals or 'date_fin' in vals:
            self._compute_line_ids()
        return res

    def _compute_line_ids(self):
        self.line_ids = [(5, 0, 0)]

        workflows = self.env['wk.workflow.dashboard'].search([
            ('date', '>=', self.date_debut),
            ('date', '<=', self.date_fin)
        ])
        users = self.env['res.users'].search([])

        report_lines = []

        for user in users:
            processed_finance_num = 0
            processed_agence_num = 0
            processed_commercial_num = 0
            processed_risque_num = 0

            processed_finance_prg = 0
            processed_agence_prg = 0
            processed_commercial_prg = 0
            processed_risque_prg = 0

            for workflow in workflows:
                for state in workflow.states:
                    # Finance processing logic
                    if state.state_finance in ['finance_1','finance_2','finance_3','finance_5','finance_6','finance_7','finance_4']:  
                        if workflow.assigned_to_finance == user:
                            if state.state_compute < 1:  
                                processed_finance_prg += 1
                            else:
                                processed_finance_num += 1

                    # Branch processing logic
                    if state.state_branch in ['branch_1', 'branch_2', 'branch_3', 'branch_4','branch_5']:  
                        if workflow.assigned_to_agence == user:
                            if state.state_compute < 1:  
                                processed_agence_prg += 1
                            else:
                                processed_agence_num += 1

                    # Commercial processing logic
                    if state.state_commercial in ['commercial_1', 'commercial_2', 'commercial_3', 'commercial_4']:  
                        if workflow.assigned_to_commercial == user:
                            if state.state_compute < 1:
                                processed_commercial_prg += 1
                            else:
                                processed_commercial_num += 1
                    
                    # Risk processing logic
                    if state.state_risque in ['risque_1', 'risque_2', 'risque_3', 'risque_4']:              
                        if workflow.assigned_to_risque == user:
                            if state.state_compute < 1:
                                processed_risque_prg += 1
                            else:
                                processed_risque_num += 1

            if processed_finance_num > 0 or processed_finance_prg > 0:
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'مديرية التمويلات',
                    'processed_file_num': processed_finance_num,
                    'processed_file_prg': processed_finance_prg,
                }))
            if processed_agence_num > 0 or processed_agence_prg > 0:
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'الفرع',
                    'processed_file_num': processed_agence_num,
                    'processed_file_prg': processed_agence_prg,
                }))
            if processed_commercial_num > 0 or processed_commercial_prg > 0:
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'مديرية الاعمال التجارية',
                    'processed_file_num': processed_commercial_num,
                    'processed_file_prg': processed_commercial_prg,
                }))
            if processed_risque_num > 0 or processed_risque_prg > 0:
                report_lines.append((0, 0, {
                    'employee_name': user.id,
                    'management': 'ادارة المخاطر',
                    'processed_file_num': processed_risque_num,
                    'processed_file_prg': processed_risque_prg,
                }))

        self.write({'line_ids': report_lines})


class Table(models.Model):
    _name = 'wk.report2.table'

    management = fields.Char(string='الإدارة')
    employee_name = fields.Many2one('res.users', string='اسم الموظف')
    processed_file_num = fields.Integer(string='عدد الملفات المعالجة')
    processed_file_avrg = fields.Integer(string='متوسط مدة المعالجة')
    processed_file_prg = fields.Integer(string='عدد الملفات جاري المعالجة ')

    line = fields.Many2one('wk.report.two', ondelete="cascade")
