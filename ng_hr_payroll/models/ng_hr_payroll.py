# -*- coding: utf-8 -*-

import time
from datetime import datetime

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError


DATETIME_FORMAT = "%Y-%m-%d"


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'  # For ordering do not remove please.


class hr_payroll_structure(models.Model):
    '''
    Approve Salary structure
    '''
    _inherit = 'hr.payroll.structure'
    _description = 'Salary Structure'

    state = fields.Selection(selection=[('draft', 'New'),
                                        ('approve', 'Approved'),
                                        ('cancel', 'Cancelled')], string='State', required=True, readonly=True, default='draft')

    @api.multi
    def button_done(self):
        self.write({'state': 'approve'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True


class work_shift(models.Model):
    '''
    Employee Work Shift
    '''
    _name = 'work.shift'
    _description = 'Work Shifts'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class working_time(models.Model):
    '''
    Employee Work Time
    '''
    _inherit = 'resource.calendar'
    _description = 'resource.calendar'

    @api.model
    def _get_shift(self):
        shift_ids = self.env['work.shift'].search([], limit=1)
        return shift_ids

    monday = fields.Boolean(string='Monday')
    tuesday = fields.Boolean(string='Tuesday')
    wednesday = fields.Boolean(string='Wednesday')
    thursday = fields.Boolean(string='Thursday')
    friday = fields.Boolean(string='Friday')
    saturday = fields.Boolean(string='Saturday', default=1)
    sunday = fields.Boolean(string='Sunday', default=1)
    shift_id = fields.Many2one('work.shift', string='Shift', default=_get_shift)

    @api.one
    @api.constrains('attendance_ids')
    def check_weekoff(self):
        weekoff = []
        if self.monday == 1:
            weekoff.append('0')
        if self.tuesday == 1:
            weekoff.append('1')
        if self.wednesday == 1:
            weekoff.append('2')
        if self.thursday == 1:
            weekoff.append('3')
        if self.friday == 1:
            weekoff.append('4')
        if self.saturday == 1:
            weekoff.append('5')
        if self.sunday == 1:
            weekoff.append('6')
        for w in self.attendance_ids:
            if w.dayofweek in weekoff:
                raise Warning(_('You can not create working time on week off day'))
        return True


class payroll_advice(models.Model):
    '''
    Bank Advice
    '''
    _name = 'hr.payroll.advice'
    _description = 'Bank Advice'

    name = fields.Char(string='Name', readonly=True, required=True, states={'draft': [('readonly', False)]},)
    note = fields.Text(string='Description',
                       default="Please make the payroll transfer from above account number to the below mentioned account numbers towards employee salaries:")
    date = fields.Date(string='Date', readonly=True, default=time.strftime('%Y-%m-%d'), required=True,
                       states={'draft': [('readonly', False)]}, help="Advice Date is used to search Payslips")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='State', index=True, readonly=True, default='draft')
    number = fields.Char(string='Reference')
    line_ids = fields.One2many('hr.payroll.advice.line', 'advice_id', string='Employee Salary',
                               states={'draft': [('readonly', False)]}, readonly=True)
    chaque_nos = fields.Char(string='Cheque Numbers')
    neft = fields.Boolean(string='NEFT Transaction',
                          help="Check this box if your company use online transfer for salary")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    bank_id = fields.Many2one('res.bank', string='Bank', readonly=True, states={'draft': [(
        'readonly', False)]}, help="Select the Bank from which the salary is going to be paid")
    bankaccount_id = fields.Many2one('res.partner.bank', string='Bank Account', readonly=True, states={
                                     'draft': [('readonly', False)]}, help="Select the Bank Account from which the salary is going to be paid")

    bank_account_no = fields.Char('Bank Account Number')
    batch_id = fields.Many2one('hr.payslip.run', string='Batch', readonly=True)

    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    def compute_advice(self):
        """
        Advice - Create Advice lines in Payment Advice and
        compute Advice lines.
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Advice’s IDs
        @return: Advice lines
        @param context: A standard dictionary for contextual values
        """
        payslip_pool = self.env['hr.payslip']
        advice_line_pool = self.env['hr.payroll.advice.line']
        payslip_line_pool = self.env['hr.payslip.line']

        for advice in self:
            old_line_ids = advice_line_pool.search([('advice_id', '=', advice.id)])
            if old_line_ids:
                old_line_ids.unlink()
            slip_ids = payslip_pool.search([('date_from', '<=', advice.date),
                                            ('date_to', '>=', advice.date), ('state', '=', ['draft', 'done'])])
            for slip in slip_ids:
                if not slip.employee_id.bank_account_id or not slip.employee_id.bank_account_id.acc_number:
                    raise Warning(_('Please define bank account for the %s employee') % (slip.employee_id.name))
                line_ids = payslip_line_pool.search([('slip_id', '=', slip.id), ('code', '=', 'NET')], limit=1)
                if line_ids:
                    advice_line = {
                        'advice_id': advice.id,
                        'name': slip.employee_id.bank_account_id.acc_number,
                        'employee_id': slip.employee_id.id,
                        'bysal': line_ids.total
                    }
                    advice_line_pool.create(advice_line)
                slip_ids.write({'advice_id': advice.id})
        return True

    @api.multi
    def confirm_sheet(self):
        """
        confirm Advice - confirmed Advice after computing Advice Lines..
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of confirm Advice’s IDs
        @return: confirmed Advice lines and set sequence of Advice.
        @param context: A standard dictionary for contextual values
        """
        seq_obj = self.env['ir.sequence']
        for advice in self:
            if not advice.line_ids:
                raise Warning(_('You can not confirm Payment advice without advice lines.'))
            advice_date = datetime.strptime(advice.date, DATETIME_FORMAT)
            advice_year = advice_date.strftime('%m') + '-' + advice_date.strftime('%Y')
            number = seq_obj.get('payment.advice')
            sequence_num = 'PAY' + '/' + advice_year + '/' + number
            advice.write({'number': sequence_num, 'state': 'confirm'})
        return True

    @api.multi
    def set_to_draft(self):
        """Resets Advice as draft.
        """
        return self.write({'state': 'draft'})

    @api.multi
    def cancel_sheet(self):
        """Marks Advice as cancelled.
        """
        return self.write({'state': 'cancel'})

    @api.multi
    def onchange_company_id(self, company_id=False):
        res = {}
        if company_id:
            company = self.env['res.company'].browse(company_id)
            if company.partner_id.bank_ids:
                res.update({'bank_id': company.partner_id.bank_ids[0].bank.id})
        return {
            'value': res
        }

    @api.multi
    def onchange_bankaccount_id(self, bankaccount_id=False):
        res = {}
        if bankaccount_id:
            bank = self.env['res.partner.bank'].browse(bankaccount_id)
            if bank:
                res.update({'bank_account_no': bank.acc_number})
        return {
            'value': res
        }


class payroll_advice_line(models.Model):
    '''
    Bank Advice Lines
    '''

    @api.multi
    def onchange_employee_id(self, employee_id=False):
        res = {}
        hr_obj = self.env['hr.employee']
        if not employee_id:
            return {'value': res}
        employee = hr_obj.browse(employee_id)
        res.update({'name': employee.bank_account_id.acc_number, 'ifsc_code': employee.bank_account_id.bank_bic or ''})
        return {'value': res}

    _name = 'hr.payroll.advice.line'
    _description = 'Bank Advice Lines'

    advice_id = fields.Many2one('hr.payroll.advice', string='Bank Advice')
    name = fields.Char(string='Bank Account No.', required=True)
    ifsc_code = fields.Char(string='IFSC Code')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    bank_account_id = fields.Many2one(related='employee_id.bank_account_id',
                                      relation='res.partner.bank', string='Bank Account', store=True)
    bank_id = fields.Many2one(related='bank_account_id.bank_id', relation='res.bank', string='Bank', store=True)
    bank_name = fields.Char(related='bank_id.name', string='Bank Name', store=True)
    bysal = fields.Float(string='By Salary', digits=dp.get_precision('Payroll'))
    debit_credit = fields.Char(string='C/D', required=False, default='C')
    company_id = fields.Many2one(related='advice_id.company_id', string='Company', store=True)
    ifsc = fields.Boolean(related='advice_id.neft', string='IFSC')
