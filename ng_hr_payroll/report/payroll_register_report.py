# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mattobell (<http://www.mattobell.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import time
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class payroll_register_report(models.AbstractModel):
    _name = "report.ng_hr_payroll.payroll_register_report"

    # Additional fields requested to be added to the report
    ADDITIONAL_HR_FIELDS = [
        ('auto_staff_id', 'Staff ID'),
        ('lga_id', 'Local Government'),
        ('school_id', 'School'),
        ('job_id', 'Designation'),
        ('grade_id', 'Grade'),
        ('step_id', 'Step'),
        ('template_id', 'Salary Template')
    ]

    mnths = []
    mnths_total = []
    rules = []
    rules_data = []
    
    total = 0.0

    def get_periods(self, form, additional_fields=None):
        mnth_name = []
        rules = []
        rule_ids = form.get('rule_ids', [])
        if rule_ids:
            for r in self.env['hr.salary.rule'].browse(rule_ids):
                mnth_name.append(r.name)
                rules.append(r.id)
        self.rules = rules
        if additional_fields is None:
            additional_fields = self.ADDITIONAL_HR_FIELDS
        additional_headers = [field_name for (_, field_name) in additional_fields]
        self.rules_data = additional_headers + mnth_name if additional_fields and isinstance(additional_fields, list) \
            else mnth_name
        return [additional_headers + mnth_name] if additional_fields else [mnth_name]

    def append_additional_fields(self, primary_list, additional_fields):
        if not (isinstance(primary_list, list) and isinstance(additional_fields, list)):
            raise ValidationError("A list is required")
        employee = self.env['hr.employee'].search([('name', 'ilike', primary_list[0])], limit=1)
        for field, field_string in additional_fields:
            if field in employee._fields:
                if type(employee[field]) not in ['int', 'str', 'float']:
                    try:
                        primary_list.append(employee[field].name or '')
                    except AttributeError:
                        primary_list.append('')
                else:
                    try:
                        primary_list.append(employee[field])
                    except AttributeError:
                        primary_list.append('')
            else:
                contract = self.env['hr.contract'].search([('employee_id','=', employee.id)], limit=1)
                template = contract.template_id.name
                template = template or ''
                primary_list.append(template)
        return primary_list

    def get_salary(self, form, emp_id, emp_salary, total_mnths):
        total = 0.0
        cnt = 0
        flag = 0
        for r in self.env['hr.salary.rule'].browse(self.rules):
            self._cr.execute("select pl.name as name ,pl.total \
                                 from hr_payslip_line as pl \
                                 left join hr_payslip as p on pl.slip_id = p.id \
                                 left join hr_employee as emp on emp.id = p.employee_id \
                                 left join resource_resource as r on r.id = emp.resource_id  \
                                where p.employee_id = %s and pl.salary_rule_id = %s \
                                and (p.date_from >= %s) AND (p.date_to <= %s) \
                                group by pl.total,r.name, pl.name,emp.id",(emp_id, r.id, form.get('start_date', False), form.get('end_date', False),))
            sal = self._cr.fetchall()
            salary = dict(sal)
            cnt += 1
            flag += 1
            if flag > 8:
                continue
            if r.name in salary:
                emp_salary.append(salary[r.name])
                total += salary[r.name]
                total_mnths[cnt] = total_mnths[cnt] + salary[r.name]
            else:
                emp_salary.append('')

        if len(self.rules) < 8:
            diff = 8 - len(self.rules)
            for x in range(0,diff):
                emp_salary.append('')
        return emp_salary, total, total_mnths

    def get_salary1(self, form, emp_id, emp_salary, total_mnths):
        total = 0.0
        cnt = 0
        flag = 0
        for r in self.env['hr.salary.rule'].browse(self.rules):
            self._cr.execute("select pl.name as name ,pl.total \
                                 from hr_payslip_line as pl \
                                 left join hr_payslip as p on pl.slip_id = p.id \
                                 left join hr_employee as emp on emp.id = p.employee_id \
                                 left join resource_resource as r on r.id = emp.resource_id  \
                                where p.employee_id = %s and pl.salary_rule_id = %s \
                                and (p.date_from >= %s) AND (p.date_to <= %s) \
                                group by pl.total,r.name, pl.name,emp.id", (emp_id, r.id, form.get('start_date', False),
                                                                            form.get('end_date', False),))

            sal = self._cr.fetchall()
            salary = dict(sal)
            cnt += 1
            flag += 1
            if r.name in salary:
                emp_salary.append(salary[r.name])
                total += salary[r.name]
                total_mnths[cnt] = total_mnths[cnt] + salary[r.name]
            else:
                emp_salary.append('')
        return emp_salary, total, total_mnths

    def get_employee(self, form, excel=False, additional_fields=None):
        emp_salary = []
        salary_list = []
        total_mnths = ['Total', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # only for pdf report!
        emp_obj = self.env['hr.employee']
        emp_ids = form.get('employee_ids', [])
        
        total_excel_months = ['Total']  # for excel report
        for r in range(0, len(self.rules)):
            total_excel_months.append(0)
        employees = emp_obj.browse(emp_ids)
        for emp_id in employees:
            emp_salary.append(emp_id.name)
            if not additional_fields:
                additional_fields = self.ADDITIONAL_HR_FIELDS
            if additional_fields:
                self.append_additional_fields(emp_salary, additional_fields)
            if excel:
                emp_salary, total, total_mnths = self.get_salary1(form, emp_id.id, emp_salary, total_mnths=total_excel_months)
            else:
                emp_salary, total, total_mnths = self.get_salary(form, emp_id.id, emp_salary, total_mnths)
            emp_salary.append(total)
            salary_list.append(emp_salary)
            emp_salary = []
        self.mnths_total.append(total_mnths)
        return salary_list

    def get_months_tol(self):
        return self.mnths_total

    def get_total(self):
        for item in self.mnths_total:
            for count in range(1, len(item)):
              if item[count] == '':
                  continue
              self.total += item[count]
        return self.total

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['hr.employee'].browse(data['form']['employee_ids'])
        docargs ={
            'time': time,
            'get_employee': self.get_employee,
            'get_periods': self.get_periods,
            'get_months_tol': self.get_months_tol,
            'get_total': self.get_total,
            'doc_ids': data['form']['employee_ids'],
            'doc_model': 'hr.employee',
            'docs': docs,
            'data': data,
            'company': self.env.user.company_id
        }
        return self.env['report'].render('ng_hr_payroll.payroll_register_report', values=docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
