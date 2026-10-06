# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Alias for contract_id to support employee.hr_contract_id syntax
    hr_contract_id = fields.Many2one(
        'hr.contract',
        related='contract_id',
        string='Contract (Alias)',
        readonly=True
    )

    @api.depends(
        'ongoing_appraisal_count',
        'company_id.appraisal_plan',
        'company_id.duration_after_recruitment',
        'company_id.duration_first_appraisal',
        'company_id.duration_next_appraisal',
        'company_id.default_appraisal_frequency',
        'contract_id.frequency',
    )
    def _compute_next_appraisal_date(self):
        super()._compute_next_appraisal_date()

    def _upcoming_appraisal_creation_date(self):
        today = fields.Date.today()
        dates = {}
        for employee in self:
            contract = employee.contract_id or employee.contract_ids.filtered(lambda c: c.state == 'open')[:1] or employee.contract_ids[:1]
            if contract and contract.frequency:
                months = contract.frequency
            elif employee.company_id.default_appraisal_frequency:
                months = employee.company_id.default_appraisal_frequency
            elif employee.appraisal_count == 0:
                months = employee.company_id.duration_after_recruitment
            elif employee.appraisal_count == 1:
                months = employee.company_id.duration_first_appraisal
            else:
                months = employee.company_id.duration_next_appraisal

            if employee.appraisal_count == 0:
                starting_date = employee._get_appraisal_plan_starting_date() or today
            else:
                starting_date = employee.last_appraisal_date

            if starting_date:
                # In case proposed next_appraisal_date is in the past, start counting from now
                starting_date = starting_date.date() if isinstance(starting_date, datetime.datetime) else starting_date
                original_next_appraisal_date = starting_date + relativedelta(months=months)
                dates[employee.id] = original_next_appraisal_date if original_next_appraisal_date >= today else today + relativedelta(months=months)
            else:
                dates[employee.id] = today + relativedelta(months=months)
        return dates
