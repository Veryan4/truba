import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { TranslationController } from "@veryan/lit-spa";
import { userService } from "../../services/user.service";
import { styles } from "./unsubscribe.styles";
import "@veryan/lit-spa";
@customElement("auth-unsubscribe")
class Unsubscribe extends LitElement {
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
    if (email) {
      userService.unsubscribeEmail(email).then((result: boolean) => {
        this._isSuccessful = result;
        this._isLoading = false;
      });
    }
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
          ${this.i18n.t("auth.unsubscribe.success")}
        </div>`
      : html`<div class="card-title">
          ${this.i18n.t("auth.unsubscribe.error")}
        </div>`;
  }
}
