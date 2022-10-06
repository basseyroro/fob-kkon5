from odoo import api, fields, models, _


class PayrollApproval(models.Model):
    _name = "wb.payroll.approval"
    _description = "Payroll Approval"

    name = fields.Char("Name", required=True)
    approval_line = fields.One2many("wb.payroll.approval.line","approval_id", "Details")
    state = fields.Many2one("wb.payroll.approval.state", "State")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", "Company")
    currency_id = fields.Many2one("res.currency", "Currency")
    payslip_id = fields.Many2one("hr.payslip.run", "Payslip")
    doc_status = fields.Selection([("New","New"),
                                   ("Awaiting HR Manager Approval","Awaiting HR Manager Approval"),
                                   ("Awaiting MD Approval","Awaiting MD Approval"),
                                   ("Approved","Approved")], default="New")
    hr_manager_id = fields.Many2one("hr.employee", "HR Manager")
    hr_manager_email = fields.Char("HR Manager Email", related="hr_manager_id.work_email")
    md_id = fields.Many2one("hr.employee", "MD")
    md_email = fields.Char("MD Email", related="md_id.work_email")
    note = fields.Html("Notes")
    priority = fields.Boolean("High Priority")
    sequence = fields.Integer("Priority")
    tag_ids = fields.Many2many("wb.payroll.approval.tags", string="Tags")
    total_paye = fields.Float("Total PAYE")
    total_allowance = fields.Float("Total Allowance")
    total_deduction = fields.Float("Total Deduction")
    total_net_salary = fields.Float("Total Net Salary")
    total_pension = fields.Float("Total Pension")
    kanban_state = fields.Selection([('normal','In Progress'),
                                     ('done','Ready'),
                                     ('blocked','Blocked')], default="normal", copy=False, required=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['company_id'] = self.env.company.id
        defaults['currency_id'] = self.env.company.currency_id.id
        return defaults

    def submit(self):
        self.doc_status = 'Awaiting HR Manager Approval'

    def hr_manager_approval(self):
        self.doc_status = 'Awaiting MD Approval'
        self.state = self.env.ref("wb_general.wb_pas_2")

    def md_approval(self):
        self.doc_status = 'Approved'
        self.state = self.env.ref("wb_general.wb_pas_3")

    def reject(self):
        self.doc_status = 'New'
        self.state = self.env.ref("wb_general.wb_pas_4")


class PayrollApprovalStage(models.Model):
    _name = "wb.payroll.approval.state"
    _order = "sequence"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Priority")
    active = fields.Boolean(default=True)


class PayrollApprovalLine(models.Model):
    _name = "wb.payroll.approval.line"
    _description = "Payroll Approval Line"

    name = fields.Char("Name", required=True)
    approval_id = fields.Many2one("wb.payroll.approval", string="Approval")


class PayrollHRTags(models.Model):
    _name = "wb.payroll.approval.tags"
    _description = "Payroll Approval Tags"

    name = fields.Char("Name")
    active = fields.Boolean(default=True)