# -*- encoding: utf-8 -*-
from odoo import _, api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    # Boolean Fields
    capture = fields.Boolean("Capture")
    due_for_retirement = fields.Boolean(string="Due for retirement", default=False)
    # Char Fields
    auto_staff_id = fields.Char(string="Automated Staff ID", readonly=True)
    identification_id = fields.Char(string="Staff ID")
    # below add the month to run the increment for this employee
    month_increment = fields.Selection([('1', "January"), ('7', "July")], string='Compute Increment in: ', help="""
        This field is to specify when the increment should be done for this particular employee""")
    # Relational Fields
    department_sector_id = fields.Many2one('department.sector', string="Department Sector")
    grade_id = fields.Many2one(comodel_name="emp.grade", string="Grade",
                               # domain="[('dept_sector_id', '=', department_sector_id)]"
                               )
    step_id = fields.Many2one(comodel_name="emp.step", string="Step")
    # Date fields
    date_appointment = fields.Date("Appointment Date")
    date_retirement = fields.Date(string="Date of Retirement", compute="_compute_date_of_retirement")
    date_present_appointment = fields.Date(string="Present Appointment Date")
    # birthday = fields.Date(required=True)

    @api.depends('birthday', 'date_appointment')
    @api.one
    def _compute_date_of_retirement(self):
        """Compute the date of retirement for each and every employee"""
        # self.send_retirement_email()
        birthday = fields.Date.from_string(self.birthday) or ''
        appointment = fields.Date.from_string(self.date_appointment) or ''
        if self.birthday and self.date_appointment:
            self.date_retirement = fields.Date.to_string(birthday.replace(year=birthday.year + 60)) if \
                (birthday.replace(year=birthday.year + 60)) < (appointment.replace(year=appointment.year + 35)) else \
                fields.Date.to_string(appointment.replace(year=appointment.year + 35))
        elif self.birthday and not self.date_appointment:
            self.date_retirement = fields.Date.to_string(birthday.replace(year=birthday.year + 60))
        elif self.date_appointment and not self.birthday:
            self.date_retirement = fields.Date.to_string(appointment.replace(year=appointment.year + 35))
        else:
            self.date_retirement = ''

    def get_retire(self):
        """Notify the human resources managers of the retirement of the employees"""

        employees_to_retire = self.env['hr.employee'].search([]).filtered(lambda emp: fields.Date.from_string(emp.date_retirement) == fields.date.today())
        email_template = self.env.ref('ng_payroll_asaba.notification_employee_retirement')
        ctx = self.env.context.copy()
        if employees_to_retire:
            for employee in employees_to_retire:
                ctx.update({
                    'employee_name': employee.name,
                    'birthday': employee.birthday,
                    'date_appointment': employee.date_appointment,
                    'recipient_email': 'oebabawale@rocketmail.com',
                    'recipient_name': "Olalekan Babawale",
                })
                try:
                    email_template.with_context(ctx).send_mail(self.id, force_send=True)
                except Exception as e:
                    raise e
                employee.due_for_retirement = not employee.due_for_retirement

    @api.model
    def create(self, values):
        values['auto_staff_id'] = self.env['ir.sequence'].next_by_code('seq.employee.id')
        return super(Employee, self).create(values)

    def do_increment(self):
        """open the wizard for increment"""
        return {
            "type": "ir.actions.act_window",
            "res_model": 'employee.increment',
            "views": [[False, "form"]],
            "target": "new",
        }
