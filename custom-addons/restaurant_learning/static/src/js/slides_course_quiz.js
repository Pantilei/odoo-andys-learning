/** @odoo-module **/

import { Quiz } from "@website_slides/js/slides_course_quiz";
import { Markup } from "web.utils";

Object.assign(Quiz.prototype, {
  /**
   * Submit a quiz and get the correction. It will display messages
   * according to quiz result.
   *
   * @overide
   */
  async _submitQuiz() {
    const data = await this._rpc({
      route: "/slides/slide/quiz/submit",
      params: {
        slide_id: this.slide.id,
        answer_ids: this._getQuizAnswers(),
      },
    });
    if (data.error) {
      this._alertShow(data.error);
      return;
    }
    Object.assign(this.quiz, data);
    const {
      rankProgress,
      completed,
      channel_completion: completion,
    } = this.quiz;
    // two of the rankProgress properties are HTML messages, mark if set
    if ("description" in rankProgress) {
      rankProgress["description"] = Markup(rankProgress["description"] || "");
      rankProgress["previous_rank"]["motivational"] = Markup(
        rankProgress["previous_rank"]["motivational"] || ""
      );
    }
    if (completed) {
      this._disableAnswers();
      this.slide.completed = true;
      this.trigger_up("slide_completed", { slide: this.slide, completion });
    }
    this._hideEditOptions();
    this._renderAnswersHighlightingAndComments();
    this._renderValidationInfo();
  },
});
