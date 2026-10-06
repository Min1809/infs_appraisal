# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    appraisal_template_id = fields.Many2one(
        'appraisal.template',
        string='Appraisal Template',
        compute='_compute_appraisal_template_id',
        store=True,
        readonly=False,
        tracking=True,
        help='Appraisal template loaded based on the employee contract or default company settings.'
    )

    @api.depends('employee_id', 'employee_id.contract_id', 'company_id')
    def _compute_appraisal_template_id(self):
        for appraisal in self:
            if not appraisal.employee_id:
                appraisal.appraisal_template_id = False
                continue
            contract = (
                appraisal.employee_id.contract_id
                or appraisal.employee_id.contract_ids.filtered(lambda c: c.state == 'open')[:1]
                or appraisal.employee_id.contract_ids[:1]
            )
            if contract and contract.appraisal_template_id:
                appraisal.appraisal_template_id = contract.appraisal_template_id
            elif appraisal.company_id.default_appraisal_template_id:
                appraisal.appraisal_template_id = appraisal.company_id.default_appraisal_template_id
            else:
                appraisal.appraisal_template_id = False

    @api.depends('department_id', 'company_id', 'appraisal_template_id')
    def _compute_feedback_templates(self):
        for appraisal in self:
            if appraisal.appraisal_template_id and appraisal.appraisal_template_id.template:
                appraisal.employee_feedback_template = appraisal.appraisal_template_id.template
            elif appraisal.department_id.custom_appraisal_templates and appraisal.department_id.employee_feedback_template:
                appraisal.employee_feedback_template = appraisal.department_id.employee_feedback_template
            else:
                appraisal.employee_feedback_template = appraisal.company_id.appraisal_employee_feedback_template

            if appraisal.appraisal_template_id and appraisal.appraisal_template_id.manager_feedback_template:
                appraisal.manager_feedback_template = appraisal.appraisal_template_id.manager_feedback_template
            elif appraisal.department_id.custom_appraisal_templates and appraisal.department_id.manager_feedback_template:
                appraisal.manager_feedback_template = appraisal.department_id.manager_feedback_template
            else:
                appraisal.manager_feedback_template = appraisal.company_id.appraisal_manager_feedback_template

    @api.depends('department_id', 'appraisal_template_id')
    def _compute_employee_feedback(self):
        for appraisal in self.filtered(lambda a: a.state in ['new', 'pending']):
            if appraisal.appraisal_template_id and appraisal.appraisal_template_id.template:
                template = appraisal.appraisal_template_id.template
            elif appraisal.department_id.custom_appraisal_templates and appraisal.department_id.employee_feedback_template:
                template = appraisal.department_id.employee_feedback_template
            else:
                template = appraisal.company_id.appraisal_employee_feedback_template

            if appraisal.state == 'new':
                appraisal.employee_feedback = template
            else:
                appraisal.employee_feedback = appraisal.employee_feedback or template

    @api.depends('department_id', 'appraisal_template_id')
    def _compute_manager_feedback(self):
        for appraisal in self.filtered(lambda a: a.state in ['new', 'pending']):
            if appraisal.appraisal_template_id and appraisal.appraisal_template_id.manager_feedback_template:
                template = appraisal.appraisal_template_id.manager_feedback_template
            elif appraisal.department_id.custom_appraisal_templates and appraisal.department_id.manager_feedback_template:
                template = appraisal.department_id.manager_feedback_template
            else:
                template = appraisal.company_id.appraisal_manager_feedback_template

            if appraisal.state == 'new':
                appraisal.manager_feedback = template
            else:
                appraisal.manager_feedback = appraisal.manager_feedback or template

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super()._onchange_employee_id()
        if self.employee_id:
            contract = (
                self.employee_id.contract_id
                or self.employee_id.contract_ids.filtered(lambda c: c.state == 'open')[:1]
                or self.employee_id.contract_ids[:1]
            )
            if contract and contract.appraisal_template_id:
                self.appraisal_template_id = contract.appraisal_template_id
            elif self.company_id.default_appraisal_template_id:
                self.appraisal_template_id = self.company_id.default_appraisal_template_id
            else:
                self.appraisal_template_id = False
            self._apply_template_to_feedback()

    @api.onchange('appraisal_template_id')
    def _onchange_appraisal_template_id(self):
        self._apply_template_to_feedback()

    def _apply_template_to_feedback(self):
        for appraisal in self:
            if appraisal.appraisal_template_id:
                if appraisal.appraisal_template_id.template:
                    appraisal.employee_feedback = appraisal.appraisal_template_id.template
                    appraisal.employee_feedback_template = appraisal.appraisal_template_id.template
                if appraisal.appraisal_template_id.manager_feedback_template:
                    appraisal.manager_feedback = appraisal.appraisal_template_id.manager_feedback_template
                    appraisal.manager_feedback_template = appraisal.appraisal_template_id.manager_feedback_template

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'employee_id' in vals and not vals.get('appraisal_template_id'):
                employee = self.env['hr.employee'].browse(vals['employee_id'])
                contract = (
                    employee.contract_id
                    or employee.contract_ids.filtered(lambda c: c.state == 'open')[:1]
                    or employee.contract_ids[:1]
                )
                template = False
                if contract and contract.appraisal_template_id:
                    template = contract.appraisal_template_id
                elif employee.company_id.default_appraisal_template_id:
                    template = employee.company_id.default_appraisal_template_id

                if template:
                    vals['appraisal_template_id'] = template.id
                    if 'employee_feedback' not in vals and template.template:
                        vals['employee_feedback'] = template.template
                    if 'manager_feedback' not in vals and template.manager_feedback_template:
                        vals['manager_feedback'] = template.manager_feedback_template

        return super().create(vals_list)
