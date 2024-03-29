from odoo import _, api, fields, models


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    slide_ids = fields.One2many(
        comodel_name='slide.slide', 
        inverse_name='channel_id', 
        string="Slides and categories",
        copy=True
    )

    enroll = fields.Selection([
        ('public', 'Public'), ('invite', 'On Invitation')],
        default='invite', string='Enroll Policy', required=True,
        help='Condition to enroll: everyone, on invite, on payment (sale bridge).')

    visibility = fields.Selection([
        ('public', 'Public'), ('members', 'Members Only')],
        default='members', string='Visibility', required=True,
        help='Applied directly as ACLs. Allow to hide channels and their content for non members.')

    scoring_type = fields.Selection([
        ('no_scoring', 'No scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end')],
        string="Scoring", required=True, default='scoring_without_answers')

    def publish_course(self):
        for record in self:
            record.is_published = True

    def publish_all_contents(self):
        for record in self:
            record.slide_ids.write({
                "is_published": True
            })

    @api.model
    def create_assign_user_to_course(self, username, login, password, slide_channel_id, image_1920):
        Users = self.env["res.users"]
        SlideChannelPartner = self.env['slide.channel.partner']
        user_id = Users.with_context({"active_test": False}).search([
            ("login", "=", login)], limit=1)
        if not user_id:
            user_id = Users.create({
                "name": username,
                "image_1920": image_1920,
                "email": login,
                "login": login,
                "password": password,
                "active": True,
                "groups_id": [(6, 0, [self.env.ref("base.group_public").id])]
            })
        else:
            update_body = {
                "name": username,
                "email": login,
                "active": True,
                "groups_id": [(6, 0, [self.env.ref("base.group_public").id])]
            }
            if password:
                update_body.update({
                    "password": password,
                })
            user_id.write(update_body)
        # self.env.ref("base.group_public").users += user_id
        partner_id = user_id.partner_id
        slide_channel_partner_id = SlideChannelPartner.with_context({"active_test": False}).search([
            ("channel_id", "=", slide_channel_id),
            ("partner_id", "=", partner_id.id)
        ])
        if not slide_channel_partner_id:
            slide_channel_partner_id = SlideChannelPartner.create({
                "channel_id": slide_channel_id,
                "partner_id": partner_id.id
            })
        return {
            "course_id": slide_channel_id,
            "user_id": user_id.id,
            "partner_id": partner_id.id,
        }

    def assign_course(self):
        return {
            "name": _("Assign the Course"),
            "type": "ir.actions.act_window",
            "res_model": "slide.channel.partner",
            "views": [[self.env.ref('restaurant_learning.slide_channel_partner_view_form').id, "form"]],
            "context": {
                "default_channel_id": self.id,
            },
            "target": "current",
        }

    @api.model
    def get_user_scores_of_survey_of_slide_channel(self, slide_channel_id):
        channel_id = self.env["slide.channel"].search([("id", "=", slide_channel_id)])
        if not channel_id:
            return []

        if cert_slide_ids := channel_id.slide_ids.filtered(lambda r: r.slide_type == "certification"):
            certification_id = cert_slide_ids[-1].survey_id
            user_input_ids = self.env["survey.user_input"].search([
                ["survey_id", "=", certification_id.id],
                ["state", "=", "done"],
                ["test_entry", "=", False],
            ], sort="create_date asc")

            return [{
                "slide_channel_id": self.id,
                "partner_id": user_input_id.partner_id.id,
                "scoring_percentage": user_input_id.scoring_percentage
            } for user_input_id in user_input_ids]

        return []
    
    @api.model
    def get_partner_scores_by_slide_channel(self, partner_id):
        
        user_input_ids = self.env["survey.user_input"].search([
            ["partner_id", "=", partner_id],
            ["state", "=", "done"],
            ["test_entry", "=", False],
        ], sort="create_date asc")

        return [{
            "slide_channel_id": self.id,
            "partner_id": user_input_id.partner_id.id,
            "scoring_percentage": user_input_id.scoring_percentage
        } for user_input_id in user_input_ids]

