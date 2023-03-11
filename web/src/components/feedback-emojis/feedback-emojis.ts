import { LitElement, html } from "lit";
import { customElement, property } from "lit/decorators.js";
import {
  newsService,
  personalizationService,
  userService,
} from "../../services";
import { TranslationController } from "@veryan/lit-spa";
import { FeedbackType } from "../../models";
import { styles } from "./feedback-emojis.styles";

import "@veryan/lit-spa";

@customElement("feedback-emojis")
class FeedbackEmojiComponent extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this, "home");

  @property({ type: String })
  story_id: string;

  constructor() {
    super();
  }

  render() {
    return html` <div class="feedback-container text-center">
        <fieldset class="stars">
          <ul class="feedback">
            <lit-spa-tooltip text="${this.i18n.t("home:angry")}" position="top">
              <li
                class="angry"
                id="${"angry-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(FeedbackType.angry, true)}"
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
            </lit-spa-tooltip>
            <lit-spa-tooltip text="${this.i18n.t("home:sad")}" position="top">
              <li
                class="sad"
                id="${"cry-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(FeedbackType.cry, true)}"
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
            </lit-spa-tooltip>
            <lit-spa-tooltip text="${this.i18n.t("home:ok")}" position="top">
              <li
                class="ok"
                id="${"neutral-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(FeedbackType.neutral, true)}"
              >
                <div></div>
              </li>
            </lit-spa-tooltip>
            <lit-spa-tooltip text="${this.i18n.t("home:smile")}" position="top">
              <li
                class="good"
                id="${"smile-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(FeedbackType.smile, true)}"
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
            </lit-spa-tooltip>
            <lit-spa-tooltip text="${this.i18n.t("home:happy")}" position="top">
              <li
                class="happy"
                id="${"happy-" + this.story_id}"
                @click="${(e: Event) => this.onFeedbackClick(FeedbackType.happy, true)}"
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
            </lit-spa-tooltip>
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

  onFeedbackClick(feedbackType: FeedbackType, isEmoji = false) {
    personalizationService.postFeedback("*", this.story_id, feedbackType);
    if (isEmoji) {
      const articleEl = this.renderRoot.querySelector(
        `#${feedbackType + "-" + this.story_id}`
      )!;
      articleEl.classList.add("active");
      newsService.getSingleArticle(userService.getUser(), this.story_id).then(() => articleEl.classList.remove("active"));
    }
  }
}
