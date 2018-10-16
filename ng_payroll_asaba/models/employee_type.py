# -*- encoding: utf-8 -*-

from odoo import fields, models, api


class EmploymentType(models.Model):
    """Employee Type For Use in Salary Template"""

    _name = 'employment.type'
    _description = "Employment Type"
    _order = 'name asc'

    name = fields.Char("Name")
