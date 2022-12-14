from odoo.http import request, Controller, route
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.osv import expression


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

    @route('/slides', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_home(self, **post):
        """ Home page for eLearning platform. Is mainly a container page, does not allow search / filter. """

        user_id = request.env['res.users'].sudo().browse(request.session.uid)
        domain = [("partner_id", "=", user_id.partner_id.id)]
        channels = request.env["slide.channel.partner"].sudo().search(
            domain).mapped("channel_id")

        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].search(domain) & channels
        if not request.env.user._is_public():
            channels_all = channels_all.filtered(
                lambda channel: channel.user_id.id == request.session.uid)
            # If a course is completed, we don't want to see it in first position but in last
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted(
                lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel']
        channels_popular = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest = channels_all.sorted('create_date', reverse=True)[:3]

        achievements = request.env['gamification.badge.user'].sudo().search(
            [('badge_id.is_published', '=', True)], limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        values = self._prepare_user_values(**post)
        values.update({
            'channels_my': channels_my,
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag'],
            'slide_query_url': QueryURL('/slides/all', ['tag']),
            'slugify_tags': self._slugify_tags,
        })

        return request.render('website_slides.courses_home', values)

    @route(['/slides/all', '/slides/all/tag/<string:slug_tags>'], type='http', auth="public", website=True, sitemap=True)
    def slides_channel_all(self, slide_type=None, slug_tags=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param string slug_tags: if provided, filter the slide.channels having
            the tag(s) (in comma separated slugified form);
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
        """

        if slug_tags and request.httprequest.method == 'GET':
            # Redirect `tag-1,tag-2` to `tag-1` to disallow multi tags
            # in GET request for proper bot indexation;
            # if the search term is available, do not remove any existing
            # tags because it is user who provided search term with GET
            # request and so clearly it's not SEO bot.
            tag_list = slug_tags.split(',')
            if len(tag_list) > 1 and not post.get('search'):
                url = QueryURL(
                    '/slides/all', ['tag'], tag=tag_list[0], my=my, slide_type=slide_type)()
                return request.redirect(url, code=302)

        # if not request.env.user.sudo()._is_public() and not my:
        #     url = QueryURL('/slides/all', ['tag'], my=1, slide_type=slide_type)()
        #     return request.redirect(url, code=302)

        options = {
            'displayDescription': True,
            'displayDetail': False,
            'displayExtraDetail': False,
            'displayExtraLink': False,
            'displayImage': False,
            'allowFuzzy': not post.get('noFuzzy'),
            'my': my,
            'tag': slug_tags or post.get('tag'),
            'slide_type': slide_type,
        }
        search = post.get('search')
        order = self._channel_order_by_criterion.get(post.get('sorting'))
        _, details, fuzzy_search_term = request.website._search_with_fuzzy("slide_channels_only", search,
                                                                           limit=1000, order=order, options=options)
        channels = details[0].get('results', request.env['slide.channel'])

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        if slug_tags:
            search_tags = self._channel_search_tags_slug(slug_tags)
        elif post.get('tags'):
            search_tags = self._channel_search_tags_ids(post['tags'])
        else:
            search_tags = request.env['slide.channel.tag']

        values = self._prepare_user_values(**post)

        user_id = values["user"]
        domain = [("partner_id", "=", user_id.partner_id.id)]
        if search or fuzzy_search_term:
            domain = expression.AND([
                domain,
                [("channel_id.name", "ilike", search or fuzzy_search_term)],
            ])

        for search_tag in search_tags:
            domain = expression.AND([
                domain,
                [("channel_id.tag_ids", "in", [search_tag.id])]
            ])

        if my:
            domain = expression.AND([
                domain,
                [("channel_id.user_id", "=", user_id.id)]
            ])
        channels = request.env["slide.channel.partner"].sudo().search(
            domain).mapped("channel_id")

        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'top3_users': self._get_top3_users(),
            'slugify_tags': self._slugify_tags,
            'slide_query_url': QueryURL('/slides/all', ['tag']),
        })

        return request.render('website_slides.courses_all', values)


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
