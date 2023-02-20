from odoo import _, api, fields, models


class SlideChannelPartner(models.Model):
    _inherit = "slide.channel.partner"

    slide_slide_partner_ids = fields.One2many(
        comodel_name='slide.slide.partner', 
        inverse_name='channel_id', 
        string="Slides"
    )


class SlideSlidePartner(models.Model):
    _inherit = "slide.slide.partner"

    slide_category_id = fields.Many2one(
        comodel_name='slide.slide',
        related='slide_id.category_id',
        store=True,  
        string="Slide Category"
    )

    slide_sequence = fields.Integer(
        related='slide_id.sequence',
        store=True,  
        string="Slide Sequence"
    )

    def make_as_completed(self):
        self.write({
            "completed": True
        })
    
    def make_as_incompleted(self):
        self.write({
            "completed": False
        })
