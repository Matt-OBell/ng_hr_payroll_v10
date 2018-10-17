# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmploymentType(models.Model):
    """Employee Type For Use in Salary Template"""

    _name = 'employment.type'
    _description = "Employment Type"
    _order = 'name asc'

    name = fields.Char("Name")
    base = fields.Boolean("Base for other types")

    _sql_constraints = [
        (
            'employment_type_name_uniq',
            'UNIQUE (name)',
            'Name must be unique!'
        )
    ]

    @api.constrains('base')
    def _check_base(self):
        """Check that base type is a singleton"""
        base = self.search([]).filtered(lambda x: x.base is True)
        if len(base) > 1:
            raise ValidationError(_("Only one type is allowed to be the base"))
