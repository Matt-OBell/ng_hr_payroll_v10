# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class DepartmentSector(models.Model):
    """Department Sector Class"""

    _name = 'department.sector'

    name = fields.Char("Sector")
    grade_ids = fields.Many2many('emp.grade', string='Grades')
