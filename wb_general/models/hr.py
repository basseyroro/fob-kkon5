from odoo import fields, models, api, _
from datetime import datetime, timedelta

GLOBAL_FIELDS_NAME = ["basic_amt_total",
    "annual_gross_amt_total",
    "allowance_amt_total",
    "tlt_annual_earning_amt_total",
    "annual_gross_cra_amt_total",
    "taxable_income_amt_total",
    "annual_paye_amt_total",
    "monthly_gross_income_amt_total",
    "monthly_paye_amt_total",
    "surcharge_amt_total",
    "loan_deduction_amt_total",
    "gross_amt_total",
    "net_salary_amt_total"]

GLOBAL_LABELS_NAME = {"Basic Salary":"basic_amt_total",
                       "Annual Gross":"annual_gross_amt_total",
                       "Allowance":"allowance_amt_total", "Total Annual Earnings":"tlt_annual_earning_amt_total",
                       "Annual Gross of CRA":"annual_gross_cra_amt_total",
                      "TAXABLE INCOME":"taxable_income_amt_total", "Annual PAYE":"annual_paye_amt_total",
                       "Monthly Gross Income":"monthly_gross_income_amt_total", "Monthly PAYE":"monthly_paye_amt_total",
                       "Surcharge":"surcharge_amt_total",
                      "Loan deduction":"loan_deduction_amt_total", "Gross":"gross_amt_total",
                       "Net Salary":"net_salary_amt_total"}


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    basic_amt_total = fields.Float("Basic", compute="_wb_computation_total", default=0.0)
    annual_gross_amt_total = fields.Float("Annual Gross", compute="_wb_computation_total", default=0.0)
    allowance_amt_total = fields.Float("Allowance", compute="_wb_computation_total", default=0.0)
    tlt_annual_earning_amt_total = fields.Float("Total Annual Earning", compute="_wb_computation_total", default=0.0)
    annual_gross_cra_amt_total = fields.Float("Annual Gross CRA", compute="_wb_computation_total", default=0.0)
    taxable_income_amt_total = fields.Float("Taxable Income", compute="_wb_computation_total", default=0.0)
    annual_paye_amt_total = fields.Float("Annual Paye", compute="_wb_computation_total", default=0.0)
    monthly_gross_income_amt_total = fields.Float("Monthly Gross Income", compute="_wb_computation_total", default=0.0)
    monthly_paye_amt_total = fields.Float("Monthly Paye", compute="_wb_computation_total", default=0.0)
    surcharge_amt_total = fields.Float("Surcharge", compute="_wb_computation_total", default=0.0)
    loan_deduction_amt_total = fields.Float("Loan Deduction", compute="_wb_computation_total", default=0.0)
    gross_amt_total = fields.Float("Gross", compute="_wb_computation_total", default=0.0)
    net_salary_amt_total = fields.Float("Net Salary", compute="_wb_computation_total", default=0.0)

    def _wb_computation_total(self):
        for rec in self:
            labels = GLOBAL_LABELS_NAME.keys()
            prepare_vals = {}
            for line in rec.line_ids:
                if line.name in labels:
                    prepare_vals[GLOBAL_LABELS_NAME.get(line.name)] = line.total
            if prepare_vals:
                rec.write(prepare_vals)
            prepare_vals = {}
            for line in GLOBAL_LABELS_NAME.values():
                if not rec[line]:
                    prepare_vals[line] = 0
            if prepare_vals:
                rec.write(prepare_vals)


class Tickets(models.Model):
    _inherit = "helpdesk.ticket"

    exp_finish_date = fields.Datetime(string="~Expected Finish Date", compute="_onchange_sla_status_ids")

    @api.onchange("sla_status_ids")
    def _onchange_sla_status_ids(self):
        for rec in self:
            today = rec.create_date
            for sla in rec.sla_status_ids:
                if sla.sla_id.time:
                    today += timedelta(hours=sla.sla_id.time)
            rec.exp_finish_date = today


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
            if rec.amount_total > amount:
                rec.is_approval_by_ceo = True

    def approved_by_ceo(self):
        for rec in self:
            rec.x_studio_selection_field_m7jU2 = "Approved"

    def approved_by_manager(self):
        for rec in self:
            rec.x_studio_selection_field_m7jU2 = "Approved"

# class payroll_approval(models.Model):
#     _inherit = "x_payroll_approval"
#
#     # allowance_amt_total = fields.Float("Total Allowance")
#     # deduction_amt_total = fields.Float("Total Deduction")
#
#     @api.onchange("x_studio_many2one_field_KhLwi")
#     def onchange_x_studio_many2one_field_KhLwi(self):
#         for rec in self:
#             allowance_amt_total, deduction_amt_total = 0, 0
#             x_studio_value = 0
#             x_studio_total_paye = 0
#             x_studio_total_pension = 0
#             if rec.x_studio_many2one_field_KhLwi and rec.x_studio_many2one_field_KhLwi.slip_ids:
#                 allowance_amt_total += rec.x_studio_many2one_field_KhLwi.allowance_amt_total
#                 deduction_amt_total += rec.x_studio_many2one_field_KhLwi.loan_deduction_amt_total
#                 x_studio_value += rec.x_studio_many2one_field_KhLwi.net_salary_amt_total
#                 x_studio_total_paye += rec.x_studio_many2one_field_KhLwi.monthly_paye_amt_total
#                 x_studio_total_pension += rec.x_studio_many2one_field_KhLwi.x_studio_total_pension
#
#             rec.update({'x_studio_total_allowance':allowance_amt_total,'x_studio_total_deduction':deduction_amt_total,
#                         'x_studio_value':x_studio_value, 'x_studio_total_paye':x_studio_total_paye,
#                         'x_studio_total_pension':x_studio_total_pension})

