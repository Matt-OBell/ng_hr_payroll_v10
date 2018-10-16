# -*- coding: utf-8 -*-
from odoo import models, fields


class EmployeeStep(models.Model):
    """Steps under certain Grades"""

    _name = 'emp.step'
    _order = 'sequence,name'

    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Step', required=True)
