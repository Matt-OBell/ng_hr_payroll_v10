# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class EmployeeSchool(models.Model):
    """Employee Schools

    This class holds all the records of schools for LEA employees

    """

    _name = "employee.school"
    _description = "Employee Schools"
    _order = "name ASC"

    name = fields.Char('Name')
    address = fields.Char("Address")
