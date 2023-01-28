import { LitElement, html } from "lit";
import { customElement, property } from "lit/decorators.js";
import {
  newsService,
  personalizationService,
  userService,
} from "../../services";
import { TranslationController } from "../../controllers";
import { styles } from "./feedback-emojis.styles";

import "../tooltip/tooltip";

@customElement("feedback-emojis")
class FeedbackEmojiComponent extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this);

  @property({ type: String })
  story_id: string;

  constructor() {
    super();
  }

  render() {
    return html` <div class="feedback-container text-center">
        <fieldset class="stars">
          <ul class="feedback">
            <tool-tip text="${this.i18n.t("home:angry")}" position="top">
              <li
                class="angry"
                id="${"angry-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(31, true)}"
              >
                <div>
                  <svg class="eye left">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="eye right">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="mouth">
                    <use xlink:href="#mouth"></use>
                  </svg>
                </div>
              </li>
            </tool-tip>
            <tool-tip text="${this.i18n.t("home:sad")}" position="top">
              <li
                class="sad"
                id="${"sad-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(32, true)}"
              >
                <div>
                  <svg class="eye left">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="eye right">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="mouth">
                    <use xlink:href="#mouth"></use>
                  </svg>
                </div>
              </li>
            </tool-tip>
            <tool-tip text="${this.i18n.t("home:ok")}" position="top">
              <li
                class="ok"
                id="${"ok-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(33, true)}"
              >
                <div></div>
              </li>
            </tool-tip>
            <tool-tip text="${this.i18n.t("home:smile")}" position="top">
              <li
                class="good"
                id="${"good-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(34, true)}"
              >
                <div>
                  <svg class="eye left">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="eye right">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="mouth">
                    <use xlink:href="#mouth"></use>
                  </svg>
                </div>
              </li>
            </tool-tip>
            <tool-tip text="${this.i18n.t("home:happy")}" position="top">
              <li
                class="happy"
                id="${"happy-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(35, true)}"
              >
                <div>
                  <svg class="eye left">
                    <use xlink:href="#eye"></use>
                  </svg>
                  <svg class="eye right">
                    <use xlink:href="#eye"></use>
                  </svg>
                </div>
              </li>
            </tool-tip>
          </ul>
        </fieldset>
      </div>
      <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
        <symbol xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 4" id="eye">
          <path
            d="M1,1 C1.83333333,2.16666667 2.66666667,2.75 3.5,2.75 C4.33333333,2.75 5.16666667,2.16666667 6,1"
          ></path>
        </symbol>
        <symbol
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 18 7"
          id="mouth"
        >
          <path
            d="M1,5.5 C3.66666667,2.5 6.33333333,1 9,1 C11.6666667,1 14.3333333,2.5 17,5.5"
          ></path>
        </symbol>
      </svg>`;
  }

  onFeedbackClick(feedbackType: number, isEmoji = false) {
    personalizationService.postFeedback("*", this.story_id, feedbackType);
    if (isEmoji) {
      const emotions = ["angry", "sad", "ok", "good", "happy"];
      const articleEl = this.renderRoot.querySelector(
        `#${emotions[feedbackType - 31] + "-" + this.story_id}`
      )!;
      articleEl.classList.add("active");
      newsService.getSingleArticle(userService.getUser(), this.story_id).then(() => articleEl.classList.remove("active"));
    }
  }
}
