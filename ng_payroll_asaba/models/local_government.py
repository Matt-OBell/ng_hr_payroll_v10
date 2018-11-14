# -*- encoding: utf-8 -*-

from odoo import models, fields


class LocalGovernment(models.Model):
    """Represents the class For the Local Government Areas.

        Each local government is used to logically group employees especially those who belong to the LEA department
        sector. We would have a group by feature on the employee page to display the employees who belong to certain
        local governments.

        Attributes:
            _name: A string that represents the business name for the class.
            _description: A string description of the class.
            _order: A string showing the field used to order our records as in ORDER BY.
            name: A string showing the name of the record when used in many2one fields.
            code: A short string representing each LGA.
        """

    _name = "local.government"
    _description = "Local Government Areas"
    _order = "name ASC"

    name = fields.Char("Name")
    code = fields.Char("Code")
