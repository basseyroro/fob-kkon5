from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.osv import expression

GLOBAL_FIELDS_NAME = ["Basic",
    "Allowance","Gross","Deduction","Net",
    "Company Contribution","TCA","HZD Allowance","ANN PENSION",
    "Total Pen","GCRA","INCOME","EMP PAYE","surcharge","Loan",
    "gross income","Total Earning","PIT"]

GLOBAL_LABELS_NAME = {"Basic":"basic_amt_total",
    "Allowance":"allowance_amt_total","Gross":"gross_amt_total","Deduction":"deduction_amt_total","Net":"net_amt_total",
    "Company Contribution":"company_contribution_amt_total","TCA":"tca_amt_total","HZD Allowance":"hzd_allowance_amt_total",
                      "ANN PENSION":"ann_pension_amt_total",
    "Total Pen":"total_pen_amt_total","GCRA":"gcra_amt_total","INCOME":"income_amt_total",
                      "EMP PAYE":"emp_paye_amt_total","surcharge":"surcharge_amt_total","Loan":"loan_amt_total",
    "gross income":"gross_income_amt_total","Total Earning":"total_earning_amt_total","PIT":"pit_amt_total"}


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    basic_amt_total = fields.Float("Basic", compute="_wb_computation_total", default=0.0)
    allowance_amt_total = fields.Float("Allowance", compute="_wb_computation_total", default=0.0)
    gross_amt_total = fields.Float("Gross", compute="_wb_computation_total", default=0.0)
    deduction_amt_total = fields.Float("Deduction", default=0.0, compute="_wb_computation_total")
    net_amt_total = fields.Float("Net Salary", compute="_wb_computation_total", default=0.0)
    company_contribution_amt_total = fields.Float("Company Contribution", default=0.0)
    tca_amt_total = fields.Float("TCA", compute="_wb_computation_total", default=0.0)
    hzd_allowance_amt_total = fields.Float("HZD Allowance", compute="_wb_computation_total", default=0.0)
    ann_pension_amt_total = fields.Float("Ann Pension", compute="_wb_computation_total", default=0.0)
    total_pen_amt_total = fields.Float("Total Pen", compute="_wb_computation_total", default=0.0)
    gcra_amt_total = fields.Float("GCRA", compute="_wb_computation_total", default=0.0)
    income_amt_total = fields.Float("Income", compute="_wb_computation_total", default=0.0)
    emp_paye_amt_total = fields.Float("EMP Paye", compute="_wb_computation_total", default=0.0)
    surcharge_amt_total = fields.Float("Surcharge", compute="_wb_computation_total", default=0.0)
    loan_amt_total = fields.Float("Loan", compute="_wb_computation_total", default=0.0)
    gross_income_amt_total = fields.Float("Gross Income", compute="_wb_computation_total", default=0.0)
    total_earning_amt_total = fields.Float("Total Earning", compute="_wb_computation_total", default=0.0)
    pit_amt_total = fields.Float("PIT", compute="_wb_computation_total", default=0.0)

    def _wb_computation_total(self):
        for rec in self:
            labels = GLOBAL_LABELS_NAME.keys()
            prepare_vals = {}
            for line in GLOBAL_LABELS_NAME.values():
                if not rec[line]:
                    prepare_vals[line] = 0
            for line in rec.line_ids:
                if line.category_id.name in labels:
                    if prepare_vals.get(line.category_id.name, 0):
                        prepare_vals[GLOBAL_LABELS_NAME.get(line.category_id.name)] += line.total
                    else:
                        prepare_vals[GLOBAL_LABELS_NAME.get(line.category_id.name)] = line.total
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


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = ['|',('name',operator, name), ('x_studio_customer_id', operator, name)]
            name = ''
        return super(Partner, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)