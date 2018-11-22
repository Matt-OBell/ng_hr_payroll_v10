# -*-encoding: utf-8 -*-

from odoo import models, fields, api, _


class hr_holidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'Leave'

    carry_fw = fields.Boolean(string='Carry Forward', readonly=True,
                              help='Tick if you want to include this types of leave to carry forward next year. Only legal leaves can be carried forward.')
    carry_fw_ded = fields.Boolean(string='Carry forward deduction',
                                  help='This field is when you carry forward leaves legal leaves need to set zero for that we need to create leave request for that to set it zero..', default=False)
    carry_fw_allocation = fields.Boolean(string='Is Carry Forwarded?', default=False)  # see help in xml file .

    policy = fields.Selection(selection=[('earned', 'Deduct From Earned Leaves'),
                                         ('payslip', 'Deduct From Salary')], string='Leave Deduction', required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, help="Deduct from salary allows you put leaves amount deduction on salary while Deduct from Earned leaves will simple use your earned leaves or allocated leaves.", default='earned')


class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'
    _description = 'Leave Type'

    @api.multi
    def get_days(self, employee_id):
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in self.ids)
        holiday_ids = self.env['hr.holidays'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids),
            ('carry_fw_ded', '=', False),
            ('carry_fw_allocation', '=', False),
        ])
        for holiday in holiday_ids:  # self.env['hr.holidays'].browse(holiday_ids):
            carry_fw_add = 0.0
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.carry_fw:
                    carry_fw_add += holiday.number_of_days_temp
                status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

    is_payslip = fields.Boolean(string='Include in Payslip/Salary',
                                help='Tick if you want to include this type of leaves in salary or payslips.', default=False)
    can_carryfw = fields.Boolean(string='Carry Forward',
                                 help='Tick if you want to include this type of leaves to carry forward next year.')
    is_legal = fields.Boolean(string='Legal Leave?',
                              help='Tick if you want to set this type of leaves as legal leaves.', default=False)
    can_cash = fields.Boolean(string='Cash Reimbursement',
                              help='Tick if you want to include this type of leave as cash to your employee for his/her pending leaves at end of year.')
