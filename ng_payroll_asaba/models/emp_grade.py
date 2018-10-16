# -*- coding: utf-8 -*-
from odoo import models, fields


class EmployeeGrade(models.Model):

    _name = 'emp.grade'
    _order = 'sequence,name'

    name = fields.Char(string='Grade', required=True)
    sequence = fields.Integer(string="Integer")
    step_ids = fields.Many2many('emp.step', string="Steps")
