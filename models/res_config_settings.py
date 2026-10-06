# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_appraisal_template_id = fields.Many2one(
        related='company_id.default_appraisal_template_id',
        string='Default Appraisal Template',
        readonly=False
    )
    default_appraisal_frequency = fields.Integer(
        related='company_id.default_appraisal_frequency',
        string='Default Appraisal Frequency (Months)',
        readonly=False
    )
