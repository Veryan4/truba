import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { classMap } from "lit-html/directives/class-map.js";
import { UserController } from "../../controllers";
import { TranslationController } from "@veryan/lit-spa";
import { Article } from "../../models";
import {
  buttonStyles,
  scrollBarStyles,
  iconButtonStyles,
  cardStyles,
} from "../../styles";
import { styles } from "./news-card.styles";

import "../feedback-emojis/feedback-emojis";
import "../favorite-chips/favorite-chips";
import "@veryan/lit-spa";
import "@material/mwc-button";

@customElement("news-card")
class NewsCard extends LitElement {
  static styles = [
    styles,
    cardStyles,
    iconButtonStyles,
    scrollBarStyles,
    buttonStyles,
  ];

  private user = new UserController(this);
  private i18n = new TranslationController(this, "home");

  @state()
  private _isFlipped = false;

  @property({ type: Object })
  article: Article;

  render() {
    const classes = { user: !!this.user.value };
    return !this._isFlipped
      ? html` <div class="mdc-card demo-card ${classMap(classes)}">
          <div
            class="mdc-card__primary-action demo-card__primary-action"
            tabindex="0"
          >
            <div
              class="mdc-card__media mdc-card__media--16-9 demo-card__media"
              style='background-image: url("${this.article.image}");'
            ></div>
            <div class="demo-card__primary">
              <h3
                class="demo-card__title mdc-typography mdc-typography--headline6"
              >
                ${this.article.shortTitle}
              </h3>
              <h4
                class="demo-card__subtitle mdc-typography mdc-typography--subtitle2"
              >
                ${this.article.source.value}
              </h4>
            </div>
            ${this.createFeedbackEmojis()}
          </div>
          ${this.createBottomRow()}
        </div>`
      : html`<div class="mdc-card demo-card ${classMap(classes)}">
          <div
            class="mdc-card__primary-action demo-card__primary-action flipped"
            tabindex="0"
          >
            <div class="demo-card__primary">
              <favorite-chips
                .favorite_items=${this.article.favorite_source
                  ? [this.article.favorite_source]
                  : []}
                type="source"
              ></favorite-chips>
              <favorite-chips
                .favorite_items=${this.article.favorite_author
                  ? [this.article.favorite_author]
                  : []}
                type="author"
              ></favorite-chips>
              <favorite-chips
                .favorite_items=${this.article.favorite_entities}
                type="entity"
              ></favorite-chips>
              <favorite-chips
                .favorite_items=${this.article.favorite_keywords}
                type="keyword"
              ></favorite-chips>
            </div>
          </div>
          ${this.createBottomRow()}
        </div> `;
  }

  private createBottomRow() {
    return html` <div class="mdc-card__actions">
      <div class="mdc-card__action-buttons">
        <mwc-button
          dense
          label=${"Read"}
          @click="${this.openInNewTab}"
        ></mwc-button>
      </div>
      <div class="mdc-card__action-icons">
        ${this.createShareButton()} ${this.createUserButtons()}
      </div>
    </div>`;
  }

  private createShareButton() {
    if (!(navigator as any).canShare) return "";
    return html`<button
      class="mdc-icon-button material-icons mdc-card__action mdc-card__action--icon--unbounded"
      title="Share"
      data-mdc-ripple-is-unbounded="true"
      @click="${this.socialShare}"
    >
      share
    </button>`;
  }

  private createUserButtons() {
    if (!this.user.value) return "";
    return html`<lit-spa-tooltip
      text="${this._isFlipped
        ? this.i18n.t("home:article")
        : this.i18n.t("home:favorites")}"
      position="top"
      ><button
        class="mdc-icon-button material-icons mdc-card__action mdc-card__action--icon--unbounded"
        title="More options"
        data-mdc-ripple-is-unbounded="true"
        @click="${(e: Event) => (this._isFlipped = !this._isFlipped)}"
      >
        more_vert
      </button></lit-spa-tooltip
    >`;
  }

  private createFeedbackEmojis() {
    if (!this.user.value) return "";
    return html`
      <div class="demo-card__secondary">
        <feedback-emojis story_id=${this.article.story_id}></feedback-emojis>
      </div>
    `;
  }

  openInNewTab() {
    window.open(this.article.url, "_blank", "noreferrer");
  }

  socialShare() {
    navigator.share({
      url: this.article.url,
      title: this.article.shortTitle,
    });
  }
}
