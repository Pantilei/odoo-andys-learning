# -*- coding: utf-8 -*-
{
    'name': "Restaurant E-Learning",

    'summary': """Restaurant E-Learning""",

    'description': """
        Restaurant E-Learning
    """,

    'author': "Pantilei Ianulov",
    'website': "http://www.yourcompany.com",

    'category': 'Technical',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'muk_web_theme', 'website_slides', 'website_slides_survey'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/slides_security.xml',

        'views/website_slides_templates_homepage_inherit.xml',
        'views/website_profile.xml',
        'views/webclient_templates.xml',
        'views/res_users.xml',
        'views/slide_channel.xml',
        'views/slide_channel_partner.xml',
        'views/survey_survey.xml',
        'views/slide_slide.xml',
        'views/contacts.xml',
        'views/portal_templates.xml',
        'views/website_slides_templates_course.xml',

        'views/menu_items.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [
            'restaurant_learning/static/src/js/slides_course_slides.js',
        ],
        'web.assets_tests': [],
        'web.qunit_suite_tests': [],
        'web.report_assets_common': [],
        'web.assets_qweb': [],
    },
    'license': 'LGPL-3',
}
