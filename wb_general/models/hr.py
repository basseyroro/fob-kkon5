from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

GLOBAL_FIELDS_NAME = ["Basic Salary", "Housing", "Annual Gross", "Transport Allowance", "Allowance",
                      "Utility Allowance", "Total Annual Earnings", "Leave Allowance", "PIT",
                      "Transport & Comm Allowance (Sales Only)", "Hazard Allowance",
                      "Employee Pension Contribution", "Employer Pension Contribution",
                      "Annual Gross of CRA", "Total Pension", "TAXABLE INCOME", "Annual Pension",
                      "Annual PAYE", "Monthly PAYE", "Monthly Gross Income", "Surcharge", "Loan deduction",
                      "Gross", "Attachment of Salary", "Assignment of Salary", "Child Support", "Deduction",
                      "Reimbursement", "Net Salary"]

GLOBAL_LABELS_NAME = {"Basic Salary":"amt_total_basic_salary", "Housing":"amt_total_housing",
                      "Annual Gross":"amt_total_annual_gross", "Transport Allowance":"amt_total_transport_allowance",
                      "Allowance":"amt_total_allowance", "Utility Allowance":"amt_total_utility_allowance",
                         "Total Annual Earnings":"amt_total_total_annual_earnings", "Leave Allowance":"amt_total_leave_allowance",
                         "PIT":"amt_total_pit", "Transport & Comm Allowance (Sales Only)":"amt_total_transport_comm_allowance",
                         "Hazard Allowance":"amt_total_hazard_allowance",
                         "Employee Pension Contribution":"amt_total_employee_pension_contribution",
                         "Employer Pension Contribution":"amt_total_employer_pension_contribution",
                         "Annual Gross of CRA":"amt_total_annual_gross_of_cra", "Total Pension":"amt_total_total_pension",
                         "TAXABLE INCOME":"amt_total_taxable_income", "Annual Pension":"amt_total_annual_pension",
                         "Annual PAYE":"amt_total_annual_paye", "Monthly PAYE":"amt_total_monthly_paye",
                         "Monthly Gross Income":"amt_total_monthly_gross_income", "Surcharge":"amt_total_surcharge",
                         "Loan deduction":"amt_total_load_deduction", "Gross":"amt_total_gross",
                         "Attachment of Salary":"amt_total_attachment_salary", "Assignment of Salary":"amt_total_assignment_salary",
                         "Child Support":"amt_total_child_support", "Deduction":"amt_total_deduction",
                         "Reimbursement":"amt_total_reimbursement", "Net Salary":"amt_total_net_salary"}


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    amt_total_basic_salary = fields.Float("Basic Salary", compute="_wb_computation_total")
    amt_total_housing = fields.Float("Housing", compute="_wb_computation_total")
    amt_total_annual_gross = fields.Float("Annual Gross", compute="_wb_computation_total")
    amt_total_transport_allowance = fields.Float("Transport Allowance", compute="_wb_computation_total")
    amt_total_allowance = fields.Float("Allowance", compute="_wb_computation_total")
    amt_total_utility_allowance = fields.Float("Utility Allowance", compute="_wb_computation_total")
    amt_total_total_annual_earnings = fields.Float("Total Annual Earnings", compute="_wb_computation_total")
    amt_total_leave_allowance = fields.Float("Leave Allowance", compute="_wb_computation_total")
    amt_total_pit = fields.Float("PIT", compute="_wb_computation_total")
    amt_total_transport_comm_allowance = fields.Float("Transport & Comm Allowance (Sales Only)",
                                                        compute="_wb_computation_total")
    amt_total_hazard_allowance = fields.Float("Hazard Allowance", compute="_wb_computation_total")
    amt_total_employee_pension_contribution = fields.Float("Employee Pension Contribution",
                                                             compute="_wb_computation_total")
    amt_total_employer_pension_contribution = fields.Float("Employer Pension Contribution",
                                                             compute="_wb_computation_total")
    amt_total_annual_gross_of_cra = fields.Float("Annual Gross of CRA", compute="_wb_computation_total")
    amt_total_total_pension = fields.Float("Total Pension", compute="_wb_computation_total")
    amt_total_taxable_income = fields.Float("TAXABLE INCOME", compute="_wb_computation_total")
    amt_total_annual_pension = fields.Float("Annual Pension", compute="_wb_computation_total")
    amt_total_annual_paye = fields.Float("Annual PAYE", compute="_wb_computation_total")
    amt_total_monthly_paye = fields.Float("Monthly PAYE", compute="_wb_computation_total")
    amt_total_monthly_gross_income = fields.Float("Monthly Gross Income", compute="_wb_computation_total")
    amt_total_surcharge = fields.Float("Surcharge", compute="_wb_computation_total")
    amt_total_load_deduction = fields.Float("Loan deduction", compute="_wb_computation_total")
    amt_total_gross = fields.Float("Gross", compute="_wb_computation_total")
    amt_total_attachment_salary = fields.Float("Attachment of Salary", compute="_wb_computation_total")
    amt_total_assignment_salary = fields.Float("Assignment of Salary", compute="_wb_computation_total")
    amt_total_child_support = fields.Float("Child Support", compute="_wb_computation_total")
    amt_total_deduction = fields.Float("Deduction", compute="_wb_computation_total")
    amt_total_reimbursement = fields.Float("Reimbursement", compute="_wb_computation_total")
    amt_total_net_salary = fields.Float("Net Salary", compute="_wb_computation_total")
    
    def _wb_computation_total(self):
        for rec in self:
            labels = GLOBAL_LABELS_NAME.keys()
            prepare_vals = {}
            for line in GLOBAL_LABELS_NAME.values():
                if not rec[line]:
                    prepare_vals[line] = 0
            for line in rec.line_ids:
                if line.name in labels:
                    if prepare_vals.get(line.name, 0):
                        prepare_vals[GLOBAL_LABELS_NAME.get(line.name)] += line.total
                    else:
                        prepare_vals[GLOBAL_LABELS_NAME.get(line.name)] = line.total
            if prepare_vals:
                rec.write(prepare_vals)


class Tickets(models.Model):
    _inherit = "helpdesk.ticket"

    exp_finish_date = fields.Datetime(string="~Expected Finish Date", compute="_onchange_sla_status_ids")
    exp_finish_sla_date = fields.Datetime(string="~Expected Finish Date2", compute="_onchange_sla_status_ids")

    @api.onchange("sla_status_ids")
    def _onchange_sla_status_ids(self):
        for rec in self:
            today = rec.create_date
            for sla in rec.sla_status_ids:
                if sla.sla_id.time:
                    today += timedelta(hours=sla.sla_id.time)
            rec.exp_finish_sla_date = today
            today = rec.create_date
            if rec.ticket_type_id:
                working_days = rec.ticket_type_id.time / 24
                # today += timedelta(hours=rec.ticket_type_id.time)
                today = self.date_by_adding_working_days(rec.create_date, working_days)
            rec.exp_finish_date = today

    def date_by_adding_working_days(self, from_date, add_days):
        import datetime
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday = 6
                continue
            business_days_to_add -= 1
        return current_date


class TicketType(models.Model):
    _inherit = "helpdesk.ticket.type"

    time = fields.Float('In', help='Time to reach given stage based on ticket creation date', default=0, required=True)


class HRExpense(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approved_manager', 'Approved By Manager'),
        ('interal_audit', 'Internal Audit'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused')
    ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='draft',
        required=True, help='Expense Report State')

    def _do_approve(self):
        self._check_can_approve()

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['submit', 'draft', 'approved_manager', 'interal_audit'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({'state': 'approve', 'user_id': sheet.user_id.id or self.env.user.id})
        notification['params'].update({
            'title': _('The expense reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        self.activity_update()
        return notification

    def action_manager_approve(self):
        for rec in self:
            if rec.state == "submit":
                rec.state = "approved_manager"

    def action_audit_manager_approve(self):
        for rec in self:
            if rec.state == "approved_manager":
                rec.state = "interal_audit"


class Purchase(models.Model):
    _inherit = "purchase.order"

    is_approval_by_ceo = fields.Boolean(string="Approval by CEO?", compute="_is_approval_by_ceo")

    def _is_approval_by_ceo(self):
        amount = float(self.env['ir.config_parameter'].sudo().get_param('po_approval_config', '0'))
        for rec in self:
            rec.is_approval_by_ceo = False
            if rec.amount_total < amount:
                rec.is_approval_by_ceo = True

    def approved_by_ceo(self):
        for rec in self:
            amount = float(self.env['ir.config_parameter'].sudo().get_param('po_approval_config', '0'))
            if rec.amount_total < amount:
                rec.x_studio_selection_field_m7jU2 = "Approved"
            else:
                rec.x_studio_selection_field_m7jU2 = "Awaiting MD Approval"

    def approved_by_manager(self):
        for rec in self:
            rec.x_studio_selection_field_m7jU2 = "Approved"

    def checkWritablePermission(self):
        not_editable = False
        if self.x_studio_selection_field_m7jU2 in ("Awaiting CFO Approval","Awaiting MD Approval","Approved") \
                and not self.env.user.has_group('wb_general.po_editor_group'):
            not_editable = True
        if not_editable:
            raise ValidationError(_("You don't have access rights to edit purchase order."))

    def write(self, vals):
        for rec in self:
            rec.checkWritablePermission()
        return super(Purchase, self).write(vals)


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = ['|',('name',operator, name), ('x_studio_customer_id', operator, name)]
            name = ''
        return super(Partner, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)