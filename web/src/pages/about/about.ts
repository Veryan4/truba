import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { classMap } from "lit-html/directives/class-map.js";
import { TranslationController } from "@veryan/lit-spa";
import { styles } from "./about.styles";

import "../../material-web"

@customElement("app-about")
class About extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this, "about");

  @state()
  emojis = [false, false, false, false, false];

  render() {
    const classes = [
      { active: this.emojis[0] },
      { active: this.emojis[1] },
      { active: this.emojis[2] },
      { active: this.emojis[3] },
      { active: this.emojis[4] },
    ];
    return html`
      <div class="about-container">
        <div class="about-wrap">
          <div class="about-title">${this.i18n.t("about.title")}</div>
          <span class="about-item"> ${this.i18n.t("about.subtitle")} </span>
          <div class="about-title">${this.i18n.t("about.switch")}</div>
          <div class="example-row">
            <div class="example-col">
              <h5>${this.i18n.t("about.random")}</h5>
              <div class="example-wrap">
                <md-switch .selected=${false} .disabled=${true}></md-switch>
              </div>
            </div>
            <div class="example-col">
              <h5>${this.i18n.t("about.personalized")}</h5>
              <div class="example-wrap">
                <md-switch .selected=${true} .disabled=${true}></md-switch>
              </div>
            </div>
          </div>
          <span class="about-item">
            ${this.i18n.t("about.toggle.1")}<strong
              >${this.i18n.t("about.random")}</strong
            >
            ${this.i18n.t("about.toggle.2")}<strong
              >${this.i18n.t("about.personalized")}</strong
            >
            ${this.i18n.t("about.toggle.3")}
            <br />
            ${this.i18n.t("about.toggle.4")}<strong
              >${this.i18n.t("about.random")}</strong
            >
            ${this.i18n.t("about.toggle.5")}
            <a href="https://airtable.com/shrZcJZKB2w545AsW">
              ${this.i18n.t("about.toggle.6")} </a
            >.
            <br />
            ${this.i18n.t("about.toggle.7")}${this.i18n.t("about.email")}
            <br />
            ${this.i18n.t("about.toggle.8")}<strong
              >${this.i18n.t("about.personalized")}</strong
            >
            ${this.i18n.t("about.toggle.9")}
          </span>
          <div class="about-title">${this.i18n.t("about.train")}</div>
          <ul class="feedback">
            <li
              class="angry ${classMap(classes[0])}"
              @click="${(e: any) => this.onFeedbackClick(0)}"
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
            <li
              class="sad ${classMap(classes[1])}"
              @click="${(e: any) => this.onFeedbackClick(1)}"
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
            <li
              class="ok ${classMap(classes[2])}"
              @click="${(e: any) => this.onFeedbackClick(2)}"
            >
              <div></div>
            </li>
            <li
              class="good ${classMap(classes[3])}"
              @click="${(e: any) => this.onFeedbackClick(3)}"
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
            <li
              class="happy ${classMap(classes[4])}"
              @click="${(e: any) => this.onFeedbackClick(4)}"
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
          </ul>
          <span class="about-item">
            ${this.i18n.t("about.emojis")}
            <br />
            <!---	If you find your algorithm has gone off course, you can always modify key variables it uses for recommendations.
    			In the <a href="/settings">settings page</a>, you can add/remove Keywords, Entities, and Sources.
    		  --->
          </span>

          <div class="about-title">${this.i18n.t("about.features.title")}</div>
          <span class="about-item">
            ${this.i18n.t("about.features.1")}<mat-icon class="info-icon"
              >info</mat-icon
            >${this.i18n.t("about.features.2")}
            <br />
            ${this.i18n.t("about.features.3")}
            <br />
            ${this.i18n.t("about.features.4")}
            <br />
            <br />
            <div class="mat-chip">${this.i18n.t("about.features.fork")}</div>
            <div class="mat-chip selected">
              ${this.i18n.t("about.features.york")}
            </div>
            <br />
            <br />
            ${this.i18n.t("about.features.5")}
            <br />
            ${this.i18n.t("about.features.5")}
          </span>
          <div class="about-title">${this.i18n.t("about.open_source")}</div>
          <span class="about-item">
            <ul>
              <li>
                <a href="https://github.com/Veryan4/truba" target="_blank"
                  >https://github.com/Veryan4/truba</a
                >
              </li>
            </ul>
          </span>
          <div class="about-title">${this.i18n.t("about.other")}</div>
          <span class="about-item">
            <ul>
              <li>
                <a href="/privacy">${this.i18n.t("privacy.title")}</a>
              </li>
              <li>
                <a href="/terms">${this.i18n.t("terms.title")}</a>
              </li>
            </ul>
          </span>
        </div>
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
      </svg>
    `;
  }

  onFeedbackClick(index: number) {
    this.emojis = [false, false, false, false, false];
    this.emojis[index] = true;
  }


  renderFundMe() {
    return html`<div class="about-title">${this.i18n.t("about.fund")}</div>
    <span class="about-item">
      ${this.i18n.t("about.free_1")}<strong
        >${this.i18n.t("about.email")}</strong
      >
      ${this.i18n.t("about.free_2")}
      <br />
      <br />
      <form
        action="https://www.paypal.com/donate"
        method="POST"
        target="_top"
      >
        <input
          type="hidden"
          name="hosted_button_id"
          value="KY23TS7UL2VA6"
        />
        <input
          type="image"
          src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif"
          border="0"
          name="submit"
          title="PayPal - The safer, easier way to pay online!"
          alt="Donate with PayPal button"
        />
        <img
          alt=""
          border="0"
          src="https://www.paypal.com/en_CA/i/scr/pixel.gif"
          width="1"
          height="1"
        />
      </form>
    </span>`
  }
}
