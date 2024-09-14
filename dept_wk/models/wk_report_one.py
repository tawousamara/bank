from odoo import models, fields, api, _


class ReportOne(models.Model):
    _name = 'wk.report.one'
    
    name = fields.Char(string='الاسم', compute='_compute_name', store=True)
    folder_number = fields.Many2one('wk.workflow.dashboard', string='رقم الملف')
    line_ids = fields.One2many('wk.report1.table', 'line', string='Les lignes')
    
    @api.depends('folder_number')
    def _compute_name(self):
        for record in self:
            if record.folder_number:
                record.name = f'{record.folder_number.name} تقرير الملف رقم'
            else:
                record.name = _('Test')

    @api.onchange('folder_number')
    def _onchange_folder_number(self):
        # dynamic UI updates
        if self.folder_number:
            self._compute_line_ids()

    @api.model
    def create(self, vals):
        record = super(ReportOne, self).create(vals)
        if record.folder_number:
            record._compute_line_ids()
        return record

    def write(self, vals):
        res = super(ReportOne, self).write(vals)
        if 'folder_number' in vals:
            self._compute_line_ids()
        return res

    def _compute_line_ids(self):
        workflow = self.folder_number
        if workflow:
            print('............... Clearing ................')
            self.line_ids = [(5, 0, 0)]

            branch = workflow.branche.name if workflow.branche else 'No Branch'
            nom_client = workflow.nom_client.name if workflow.nom_client else 'No Client'
            entry_date = workflow.date if workflow.date else 'No Date'
            self.line_ids = [(0, 0, {
                'customer_name': workflow.nom_client.id,
                'branch': workflow.branche.id,
                'entry_date': entry_date,
            })]

class Table(models.Model):
    _name = 'wk.report1.table'

    customer_name = fields.Many2one('res.partner', string=' اسم المتعامل')
    branch = fields.Many2one('wk.agence', string='الفرع')
    entry_date = fields.Date(string='تاريخ الادخال ')
    date_num_branch = fields.Integer(string='عدد الأيام في الفرع', compute="_compute_date_num_branch", store=True)
    date_num_finance = fields.Integer(string='عدد الأيام في التمويل', compute="_compute_date_num_finance", store=True)
    date_num_risk = fields.Integer(string='عدد الأيام في المخاطر', compute="_compute_date_num_risk", store=True)
    date_num_commercial = fields.Integer(string='عدد الأيام في التجارية', compute="_compute_date_num_commercial", store=True)

    line = fields.Many2one('wk.report.one', ondelete="cascade")
    
    @api.depends('line.folder_number')
    def _compute_date_num_branch(self):
        print("Computes the number of days the workflow spent in the branch states (branch_1 to branch_4)")
        for record in self:
            workflow = record.line.folder_number
            if workflow:
                tracking_records = self.env['wk.tracking'].search([('workflow_id', '=', workflow.id)])
                branch_states = ['branch_1', 'branch_2', 'branch_3', 'branch_4']
                date_num_branch = 0
                current_start_date = None

                for track in tracking_records:
                    if track.state in branch_states:
                        print("entering a branch state ### mark the start date")
                        if not current_start_date:
                            current_start_date = track.date_debut
                            print(current_start_date)
                    else:
                        print("Duration Calculation")
                        if current_start_date:
                            if track.date_debut:
                                date_num_branch += (track.date_debut - current_start_date).days
                                print(date_num_branch)
                            current_start_date = None

                    if track.state.startswith('finance'):
                        break
                if current_start_date and workflow.date:
                    date_num_branch += (fields.Date.today() - current_start_date).days

                record.date_num_branch = date_num_branch
                
    @api.depends('line.folder_number')
    def _compute_date_num_finance(self):
        for record in self:
            workflow = record.line.folder_number
            if workflow:
                tracking_records = self.env['wk.tracking'].search([('workflow_id', '=', workflow.id)])
                finance_states = ['finance_1', 'finance_2', 'finance_3', 'finance_4', 'finance_5', 'finance_6', 'finance_7']
                date_num_finance = 0
                current_start_date = None
                found_finance_state = False

                for track in tracking_records:
                    if track.state == 'finance_1':
                        current_start_date = track.date_debut
                        found_finance_state = True
                    elif track.state in finance_states:
                        if not current_start_date:
                            current_start_date = track.date_debut
                    else:
                        if track.state == 'commercial_1' and current_start_date:
                            if track.date_debut:
                                date_num_finance += (track.date_debut - current_start_date).days
                            current_start_date = None
                            break 
                    if track.state.startswith('commercial'):
                        break
                if current_start_date and workflow.date:
                    date_num_finance += (fields.Date.today() - current_start_date).days
                record.date_num_finance = date_num_finance            
    
    @api.depends('line.folder_number')
    def _compute_date_num_commercial(self):
        for record in self:
            workflow = record.line.folder_number
            if workflow:
                tracking_records = self.env['wk.tracking'].search([('workflow_id', '=', workflow.id)])
                commercial_states = ['commercial_1', 'commercial_2', 'commercial_3']
                date_num_commercial = 0
                current_start_date = None

                for track in tracking_records:
                    if track.state == 'commercial_1':
                        current_start_date = track.date_debut
                    elif track.state in commercial_states:
                        if not current_start_date:
                            current_start_date = track.date_debut
                    else:
                        if track.state == 'risque_1' and current_start_date:
                            if track.date_debut:
                                date_num_commercial += (track.date_debut - current_start_date).days
                            current_start_date = None
                            break
                        
                    if track.state.startswith('risque'):
                        break

                if current_start_date and workflow.date:
                    date_num_commercial += (fields.Date.today() - current_start_date).days

                record.date_num_commercial = date_num_commercial            
    
    @api.depends('line.folder_number')
    def _compute_date_num_risk(self):
        for record in self:
            workflow = record.line.folder_number
            if workflow:
                tracking_records = self.env['wk.tracking'].search([('workflow_id', '=', workflow.id)])
                risk_states = ['risque_1', 'risque_3', 'risque_4']
                date_num_risk = 0
                current_start_date = None

                for track in tracking_records:
                    if track.state == 'risque_1':
                        current_start_date = track.date_debut
                    elif track.state in risk_states:
                        if not current_start_date:
                            current_start_date = track.date_debut
                    else:
                        if current_start_date and track.date_debut:
                            date_num_risk += (track.date_debut - current_start_date).days
                            current_start_date = None

                    if not track.state.startswith('risque'):
                        break
                if current_start_date and workflow.date:
                    date_num_risk += (fields.Date.today() - current_start_date).days

                record.date_num_risk = date_num_risk