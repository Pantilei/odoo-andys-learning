from odoo import api, models, fields, _


class SlideSlide(models.Model):
    _inherit = "slide.slide"

    def _post_publication(self):
        """Override: Do not send any email! Ignore 'publish_template_id' channel field."""
        return True

    def _send_share_email(self, email, fullscreen):
        """Do not send share email!"""
        return []
