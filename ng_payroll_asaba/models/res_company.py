# -*- encoding: utf-8 -*-
from odoo import api, _, fields, models


class Company(models.Model):

    _inherit = 'res.company'

    email_hr_manager = fields.Char("HR Manager's Email")
    email_board_manager = fields.Char("Board Manager's Email")
    days_retirement_reminder = fields.Integer("Days Before Retirement Reminder")
