/** @odoo-module **/
import publicWidget from "web.public.widget";
import Fullscreen from "@website_slides/js/slides_course_fullscreen_player";
import { Quiz } from "@website_slides/js/slides_course_quiz";
import { qweb as QWeb, _t } from "web.core";

var VideoPlayer = publicWidget.Widget.extend({
  template: "website.slides.fullscreen.video",
  youtubeUrl: "https://www.youtube.com/iframe_api",

  init: function (parent, slide) {
    this.slide = slide;
    return this._super.apply(this, arguments);
  },
  start: function () {
    var self = this;
    return Promise.all([
      this._super.apply(this, arguments),
      this._loadYoutubeAPI(),
    ]).then(function () {
      self._setupYoutubePlayer();
    });
  },
  _loadYoutubeAPI: function () {
    var self = this;
    var prom = new Promise(function (resolve, reject) {
      if (
        $(document).find('script[src="' + self.youtubeUrl + '"]').length === 0
      ) {
        var $youtubeElement = $("<script/>", { src: self.youtubeUrl });
        $(document.head).append($youtubeElement);

        // function called when the Youtube asset is loaded
        // see https://developers.google.com/youtube/iframe_api_reference#Requirements
        window.onYouTubeIframeAPIReady = function () {
          resolve();
        };
      } else {
        resolve();
      }
    });
    return prom;
  },
  /**
   * Links the youtube api to the iframe present in the template
   *
   * @private
   */
  _setupYoutubePlayer: function () {
    this.player = new YT.Player("youtube-player" + this.slide.id, {
      playerVars: {
        autoplay: 1,
        origin: window.location.origin,
      },
      events: {
        onStateChange: this._onPlayerStateChange.bind(this),
      },
    });
  },
  /**
   * Specific method of the youtube api.
   * Whenever the player starts playing/pausing/buffering/..., a setinterval is created.
   * This setinterval is used to check te user's progress in the video.
   * Once the user reaches a particular time in the video (30s before end), the slide will be considered as completed
   * if the video doesn't have a mini-quiz.
   * This method also allows to automatically go to the next slide (or the quiz associated to the current
   * video) once the video is over
   *
   * @private
   * @param {*} event
   */
  _onPlayerStateChange: function (event) {
    var self = this;
    if (event.data !== YT.PlayerState.ENDED) {
      if (self.slide.completed) {
        return;
      }
      if (!event.target.getCurrentTime) {
        return;
      }

      if (self.tid) {
        clearInterval(self.tid);
      }

      self.currentVideoTime = event.target.getCurrentTime();
      self.totalVideoTime = event.target.getDuration();
      self.tid = setInterval(function () {
        self.currentVideoTime += 1;
        if (
          self.totalVideoTime &&
          self.currentVideoTime > self.totalVideoTime - 10
        ) {
          clearInterval(self.tid);
          if (!self.slide.hasQuestion && !self.slide.completed) {
            self.trigger_up("slide_to_complete", self.slide);
          }
        }
      }, 1000);
    } else {
      if (self.tid) {
        clearInterval(self.tid);
      }
      this.player = undefined;
      if (this.slide.hasNext) {
        this.trigger_up("slide_go_next", {
          currentCategoryId: this.slide.categoryId,
          currentSlideID: this.slide.id,
        });
      }
    }
  },
});

Object.assign(Fullscreen.prototype, {
  _renderSlide: function () {
    var slide = this.get("slide");
    var $content = this.$(".o_wslides_fs_content");
    $content.empty();

    // display quiz slide, or quiz attached to a slide
    if (slide.type === "quiz" || slide.isQuiz) {
      $content.addClass("bg-white");
      var QuizWidget = new Quiz(this, slide, this.channel);
      return QuizWidget.appendTo($content);
    }

    // render slide content
    if (_.contains(["document", "presentation", "infographic"], slide.type)) {
      $content.html(
        QWeb.render("website.slides.fullscreen.content", { widget: this })
      );
    } else if (slide.type === "video") {
      this.videoPlayer = new VideoPlayer(this, slide);
      return this.videoPlayer.appendTo($content);
    } else if (slide.type === "webpage") {
      var $wpContainer = $("<div>").addClass(
        "o_wslide_fs_webpage_content bg-white block w-100 overflow-auto"
      );
      $(slide.htmlContent).appendTo($wpContainer);
      $content.append($wpContainer);
      this.trigger_up("widgets_start_request", {
        $target: $content,
      });
    }
    return Promise.resolve();
  },

  _onSlideGoToNext: function (ev) {
    let currentSlideIndex = this.slides.findIndex(
      (slide) => slide.id == ev.data.currentSlideID
    );
    if (this.slides.length > currentSlideIndex + 1) {
      let nextSlide = this.slides[currentSlideIndex + 1];

      if (nextSlide.categoryId === ev.data.currentCategoryId) {
        this.sidebar.goNext();
      }
    }
  },
});
