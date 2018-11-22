# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class hr_contract(models.Model):
    """Employee contract allows to add different values in fields.

    Fields are used in salary rule computation.
    """

    _inherit = 'hr.contract'
    _description = 'HR Contract'

    leave_allow_day = fields.Float(string='Earned Leave Allowance (Amount)',
                                   help='Please specify Earned leave allowance per day for employee which will be use while deducting from salary for unapproved leaves.')
    pension_company = fields.Float(string='Pension Company Contribution (%)',
                                   help='Please give % between 0-100 for Pension from Company Contribution.', default=7.5)
    pension_employee = fields.Float(string='Pension Employee Contribution (%)',
                                    help='Employee Contribution for Pension in % between 0-100.', default=7.5)
    hra = fields.Float(string='House Rent Allowance (%)', digits=dp.get_precision(
        'Payroll'), help="HRA is an allowance given by the employer to the employee for taking care of his rental or accommodation expenses, Please specify % between 0-100 for HRA given to Employee.", default=75.0)