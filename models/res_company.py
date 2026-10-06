# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    default_appraisal_template_id = fields.Many2one(
        'appraisal.template',
        string='Default Appraisal Template',
        help='Default appraisal template applied when an employee contract does not specify a template.'
    )
    default_appraisal_frequency = fields.Integer(
        string='Default Appraisal Frequency (Months)',
        default=12,
        help='Default appraisal review interval in months when not specified on the employee contract.'
    )
