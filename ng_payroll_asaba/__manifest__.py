# -*- coding: utf-8 -*-
{
    'name': "Payroll Implementation Module",

    'summary': """
    Re-implement the payroll computation to reduce processing time and slowness experienced in the old system
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Matt O'Bell Ltd",
    'website': "http://www.mattobell.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/salary_template_view.xml',
        'views/hr_contract_view.xml',
        'views/res_company_view.xml',
        'views/hr_employees_view.xml',
        'views/department_sector_view.xml',
        'views/emp_grade_view.xml',
        'views/emp_step_view.xml',
        'data/employee_id_sequence.xml',
        'data/employee_retirement_email.xml',
        'wizard/increment_view.xml',
        'wizard/promotion_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
