# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    appraisal_template_id = fields.Many2one(
        'appraisal.template',
        string='Appraisal Template',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=True,
        help='Appraisal template used for appraisals generated for this contract. '
             'If left empty, the default template from Appraisal Settings will be used.'
    )
    frequency = fields.Integer(
        string='Appraisal Frequency (Months)',
        tracking=True,
        help='Frequency of next appraisals in months (e.g. 3, 6, 12). '
             'If left empty or 0, the default setting from Appraisal Settings will be used.'
    )

    @api.constrains('frequency')
    def _check_frequency(self):
        for contract in self:
            if contract.frequency and contract.frequency < 0:
                raise ValidationError(_("Appraisal frequency cannot be a negative number."))
