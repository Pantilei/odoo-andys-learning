from odoo import api, models, fields, _


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    @api.model
    def create_assign_user_to_course(self, username, login, password, slide_channel_id):
        Users = self.env["res.users"]
        SlideChannelPartner = self.env['slide.channel.partner']
        user_id = Users.with_context({"active_test": False}).search([
            ("login", "=", login)], limit=1)
        if not user_id:
            user_id = Users.create({
                "name": username,
                "email": login,
                "login": login,
                "password": password,
                "active": True,
                "groups_id": [(6, 0, [self.env.ref("base.group_public").id])]
            })
        else:
            user_id.write({
                "name": username,
                "email": login,
                "password": password,
                "active": True,
                "groups_id": [(6, 0, [self.env.ref("base.group_public").id])]
            })
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
