from odoo.http import request, Controller, route
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.addons.portal.controllers.portal import CustomerPortal


class WebsiteSlidesInherit(WebsiteSlides):
    def _get_channel_progress(self, channel, include_quiz=False):
        """ Replacement to user_progress. Both may exist in some transient state. """
        slides = request.env['slide.slide'].sudo().search(
            [('channel_id', '=', channel.id)])
        channel_progress = dict((sid, dict()) for sid in slides.ids)
        if channel.is_member:
            slide_partners = request.env['slide.slide.partner'].sudo().search([
                ('channel_id', '=', channel.id),
                ('partner_id', '=', request.env.user.partner_id.id),
                ('slide_id', 'in', slides.ids)
            ])
            for slide_partner in slide_partners:
                channel_progress[slide_partner.slide_id.id].update(
                    slide_partner.read()[0])
                if slide_partner.slide_id.question_ids:
                    gains = [slide_partner.slide_id.quiz_first_attempt_reward,
                             slide_partner.slide_id.quiz_second_attempt_reward,
                             slide_partner.slide_id.quiz_third_attempt_reward,
                             slide_partner.slide_id.quiz_fourth_attempt_reward]
                    channel_progress[slide_partner.slide_id.id]['quiz_gain'] = gains[slide_partner.quiz_attempts_count] if slide_partner.quiz_attempts_count < len(
                        gains) else gains[-1]

        if include_quiz:
            quiz_info = slides._compute_quiz_info(
                request.env.user.partner_id, quiz_done=False)
            for slide_id, slide_info in quiz_info.items():
                channel_progress[slide_id].update(slide_info)
        return channel_progress


class CustomerPortalInhert(CustomerPortal):

    @route('/my/security', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def security(self, **post):
        return request.redirect('/my/home')

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        return request.redirect('/my/home')

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user_id = partner = request.env.user.id
        return request.redirect(f"/profile/user/{user_id}")
