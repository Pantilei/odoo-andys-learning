/** @odoo-module **/

import publicWidget from "web.public.widget";
import { _t } from "web.core";

publicWidget.registry.websiteSlidesCourseSlidesList =
  publicWidget.Widget.extend(
    publicWidget.registry.websiteSlidesCourseSlidesList.prototype,
    {
      /**
       * @override
       */
      _updateHref: function () {},
    }
  );

export default publicWidget.registry.websiteSlidesCourseSlidesList;
