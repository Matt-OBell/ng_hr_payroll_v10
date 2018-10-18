# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalaryTemplate(models.Model):

    def action_confirm(self):
        """Confirm and send notification to Manager to approve template."""
        self.write({'state': 'confirm'})

    def action_approve(self):
        """Confirm and send notification to Manager to approve template."""
        self.write({'state': 'approve'})

    def reset_draft(self):
        """Reset the record to draft to allow changes to be applied."""
        self.write({'state': 'draft'})

    _name = 'salary.template'
    _description = 'Salary Template'

    name = fields.Char(string="Description")
    state = fields.Selection(selection=[
        ('draft', 'New'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved')], readonly=True, default='draft', help="""
    When a new record is created, the state is draft
    When the contract is confirmed, the state changes to confirm
    Contracts are only selectable from other models""")

    parent_id = fields.Many2one('salary.template', string='Parent Template', index=True)
    child_ids = fields.One2many('salary.template', 'parent_id', string=' Sub Template')

    # Float fields
    basic = fields.Float(string='Basic')
    housing = fields.Float(string='Housing',)
    transport = fields.Float(string='Transport',)
    leave_allowance = fields.Float(string='Leave Allowance',)
    utility = fields.Float(string='Utility',)
    meal = fields.Float(string='Meal',)
    furniture = fields.Float(string='Furniture',)
    domestic = fields.Float(string='Domestic',)
    travelling = fields.Float(string='Travelling',)
    others = fields.Float(string='Others',)
    extra = fields.Float(string='extra')

    # Newly added fields
    rural_posting = fields.Float(string='Rural Posting',)
    shift_allowance = fields.Float(string='Shift Allowance',)
    hazard = fields.Float(string='Hazard',)
    call_duty_all = fields.Float(string='Call Duty Allowance')
    extra_two = fields.Float(string='Extra 2')

    # Relational fields
    department_sector_id = fields.Many2one(comodel_name="department.sector", string="Department Sector")
    grade_id = fields.Many2one(comodel_name="emp.grade", string="Grade",
                               # domain=[('dept_sector_id', '=', department_sector_id)]
                               )
    step_id = fields.Many2one(comodel_name="emp.step", string="Step")
    employment_type_id = fields.Many2one('employment.type', string="Employment Type")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You can not create recursive parent tags.'))
        if self.child_ids:
            raise ValidationError(_("Error ! Parent Template can't have a parent"))
