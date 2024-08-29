import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { TranslationController } from "@veryan/lit-spa";
import { userService } from "../../services/user.service";
import { styles } from "./email.styles";
import "@veryan/lit-spa";
@customElement("auth-email")
class Email extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this, {scope:"auth"});

  @state()
  private _isLoading = true;

  @state()
  private _isSuccessful = false;

  constructor() {
    super();
    const urlSearchParams = new URLSearchParams(location.search);
    const email = urlSearchParams.get("email");
    userService.confirmEmail().then((result: boolean) => {
      this._isSuccessful = true;
      this._isLoading = false;
    });
  }

  render() {
    return html` <div class="card">${this.renderResult()}</div> `;
  }

  renderResult() {
    return this._isLoading
      ? html`<lit-spa-loader .styleInfo=${{width: '10rem' }}></lit-spa-loader>`
      : html` <div>${this.renderMessage()}</div>`;
  }

  renderMessage() {
    return this._isSuccessful
      ? html`<div class="card-title">
          ${this.i18n.t("auth.email.success")}
        </div>`
      : html`<div class="card-title">
          ${this.i18n.t("auth.email.error")}
        </div>`;
  }
}
