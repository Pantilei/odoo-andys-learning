from odoo import api, models, fields, _


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    scoring_type = fields.Selection([
        ('no_scoring', 'No scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end')],
        string="Scoring", required=True, default='scoring_without_answers')

    certification = fields.Boolean('Is a Certification', compute='_compute_certification',
                                   readonly=False, store=True, default=True)
