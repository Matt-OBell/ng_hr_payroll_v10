# -*- encoding: utf-8 -*-

from odoo import _, api, models, fields


class Increment(models.TransientModel):
    """Manage increments for employees"""

    _name = 'employee.increment'
    _description = "Employee Increment"

    employee_ids = fields.Many2many('hr.employee', string="Employees")
    dept_sector = fields.Many2one('department.sector', string="Department Sector")
    period_increment = fields.Selection([('1', "January"), ('7', "July")], string="Period", help="""
    Select the month for which increment should be run. This does increment for employees with the specified month 
    marked on their contracts""")

    @api.multi
    def get_all_emp(self):
        """Fetch the employee record"""
        all_employees = self.env['hr.employee'].search([])
        employees = all_employees.filtered(lambda emp: emp.month_increment == self.period_increment and
                emp.department_sector_id == self.dept_sector and emp.company_id == self.env.user.company_id)
        self.employee_ids = employees.ids
        return self.do_reopen_form()

    @api.multi
    def do_reopen_form(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,  # this model
            'res_id': self.id,  # the current wizard record
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def do_increment(self):
        """Run the increment for all employees in the system"""
        for employee in self.employee_ids:
            employee_step = employee.step_id
            all_steps = employee.grade_id.step_ids

            if all_steps:
                if employee_step['sequence'] < max(all_steps.mapped('sequence')):
                    next_sequence = employee_step.sequence + 1
                    next_step = all_steps.filtered(lambda step: step.sequence == next_sequence)
                    employee.write({
                        'step_id': next_step.id,
                    })

                    new_contract = self.env['hr.contract'].search([
                        ('department_sector_id', '=', employee.department_sector_id.id),
                        ('grade_id', '=', employee.grade_id.id),
                        ('step_id', '=', next_step.id),
                        ], limit=1)

                    if new_contract:
                        new_contract.write({'employee_id': employee.id})
        return True
