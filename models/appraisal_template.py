# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AppraisalTemplate(models.Model):
    _name = 'appraisal.template'
    _table = 'appraisal_template'
    _description = 'Appraisal Template'
    _order = 'sequence, name'

    name = fields.Char(string='Template Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='Department to which this appraisal template applies. Leave blank for general company-wide use.'
    )
    template = fields.Html(
        string='Appraisal Form Template',
        translate=True,
        help='HTML content / questions for the employee self-assessment and feedback form.'
    )
    manager_feedback_template = fields.Html(
        string='Manager Feedback Template',
        translate=True,
        help='Optional template content specifically for manager evaluation and feedback.'
    )
    guide = fields.Html(
        string='Guide / Instructions',
        translate=True,
        help='Guidelines, instructions, and scoring criteria on how to fill out this appraisal form.'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    description = fields.Text(string='Description / Internal Notes')
