# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError


class EmployeePromotion(models.TransientModel):
    """Manage the promotion of Employees through an approval process"""

    _name = 'employee.promotion'
    _inherit = 'mail.thread'
    _description = "Promotion of Employees"

    def _get_department_sector(self):
        """Return the department sector of the logged in user"""
        session_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return session_employee.department_sector_id.id

    employee_ids = fields.Many2many('hr.employee', string="Employees", domain="[('department_sector_id','=',dept_sector_id)]")
    state = fields.Selection(selection=[
        ('draft', "New"),
        ('confirm', "Open"),
        ('approve', "Approved"),
        ('done', 'completed'),
        ('cancel', 'Cancelled'),
    ], string="State", default='draft', help="""When a new request is created, the state is set to draft\n When the record is 
    confirmed, the next approving officer is able to validate, confirm that all the selected employees can be 
    promoted\n In the approved state the promotion workflow can be carried out and the individual employees are moved 
    to the next salary grade""", track_visibility='always')
    dept_sector_id = fields.Many2one('department.sector', string="Department Sector", default=_get_department_sector)

    @api.multi
    def submit(self):
        """Submit the request for approval"""
        self.state = 'confirm'

    @api.multi
    def approve(self):
        """Validate that all employees can be promoted"""
        self.state = 'approve'

    @api.multi
    def cancel(self):
        """Cancel, the request perhaps because the employees should not be promoted"""
        self.state = 'cancel'

    @api.multi
    def set_draft(self):
        """Set to draft"""
        self.state = 'draft'

    @api.multi
    def do_promotion(self):
        """Run the promotion for all employees in the system"""
        if not self.state == 'approve':
            raise UserError("Request must be approved before action can be performed!")
        if not self.employee_ids:
            raise UserError("There are no employees selected fo promotion!")
        for employee in self.employee_ids:
            employee_grade = employee.grade_id
            all_grades = employee.department_sector_id.grade_ids

            if all_grades:
                if employee_grade['sequence'] < max(all_grades.mapped('sequence')):
                    next_sequence = employee_grade.sequence + 1
                    next_grade = all_grades.filtered(lambda grade: grade.sequence == next_sequence)
                    next_step = next_grade.step_ids.filtered(
                        lambda step: step.sequence == min(next_grade.step_ids.mapped('sequence')))
                    employee.write({
                        'grade_id': next_grade.id,
                        'step_id': next_step.id or 0,
                    })

                    new_contract = self.env['hr.contract'].search([
                        ('department_sector_id', '=', employee.department_sector_id.id),
                        ('grade_id', '=', next_grade.id),
                        ('step_id', '=', next_step.id),
                    ], limit=1)

                    if new_contract:
                        new_contract.write({'employee_id': employee.id})
        return self.write({'state': 'done'})
