import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { TranslationController, routerService } from "@veryan/lit-spa";
import { userService } from "../../services";
import { User } from "../../models";
import { textFieldStyles, buttonStyles } from "../../styles";
import { styles } from "./password.styles";

import "@material/mwc-button";
import "@material/mwc-formfield";
import "@material/mwc-textfield";

@customElement("auth-password")
class Password extends LitElement {
  static styles = [styles, buttonStyles, textFieldStyles];

  private i18n = new TranslationController(this, "auth");

  @state()
  private _hasToken = false;

  @state()
  private _showMessage = false;

  @state()
  private _resetToken = "";

  @query("#email")
  emailInput: HTMLInputElement;

  @query("#password")
  passwordInput: HTMLInputElement;

  @query("#repeatPassword")
  repeatPasswordInput: HTMLInputElement;

  constructor() {
    super();
    const urlSearchParams = new URLSearchParams(location.search);
    const token = urlSearchParams.get("token");
    if (token) {
      this._resetToken = token;
      this._hasToken = true;
    }
  }

  render() {
    return html`
      <div class="card">
        ${this.renderTitle()} ${this.renderForm()}
        <div class="form-buttons">${this.renderButton()}</div>
        <br />
        ${this.renderMessage()}
      </div>
    `;
  }

  renderTitle() {
    return this._hasToken
      ? html`<div class="card-title">
          ${this.i18n.t("auth.password.reset.title")}
        </div>`
      : html`<div class="card-title">
          ${this.i18n.t("auth.password.submit.title")}
        </div>`;
  }

  renderForm() {
    return this._hasToken
      ? html` <form class="card-form">
          <mwc-textfield
            class="form-field"
            label="${this.i18n.t("auth.password.password")}"
            id="password"
            type="password"
            name="password"
            required
          ></mwc-textfield>
          <mwc-textfield
            class="form-field"
            label="${this.i18n.t("auth.password.repeat")}"
            id="repeatPassword"
            type="password"
            name="repeatPassword"
            validationMessage="${this.i18n.t("auth.password.mismatch")}"
            @validityTransform=${this.passwordsMatchValidator}
            required
          ></mwc-textfield>
        </form>`
      : html` <form class="card-form">
          <mwc-textfield
            class="form-field"
            label="${this.i18n.t("auth.password.email")}"
            id="email"
            type="email"
            name="email"
            required
          ></mwc-textfield>
        </form>`;
  }

  renderButton() {
    return this._hasToken
      ? html`<mwc-button
          dense
          unelevated
          @click=${this.resetPassword}
          label=${this.i18n.t("auth.password.reset.button")}
        ></mwc-button>`
      : html`<mwc-button
          dense
          unelevated
          @click=${this.forgotPassword}
          label=${this.i18n.t("auth.password.submit.button")}
        ></mwc-button>`;
  }

  renderMessage() {
    return this._showMessage && !this._hasToken
      ? html`<div>${this.i18n.t("auth.password.sent")}</div>`
      : "";
  }

  forgotPassword(): void {
    if (!this.emailInput.value) {
      return;
    }
    userService.forgotPassword(this.emailInput.value).then((user: User) => {
      this._showMessage = true;
    });
  }

  resetPassword() {
    if (!this.passwordInput.value || !this.repeatPasswordInput.value) {
      return;
    }
    if (!this.passwordInput.value !== !this.repeatPasswordInput.value) {
      return;
    }
    userService
      .resetPassword(this._resetToken, this.passwordInput.value)
      .then((data) => {
        routerService.navigate("/");
      });
  }

  passwordsMatchValidator(
    newValue: string,
    nativeValidity: ValidityState
  ): Partial<ValidityState> | null {
    if (nativeValidity.valid) {
      const isValid =
        (this.renderRoot?.querySelector("#password") as HTMLInputElement)
          .value === newValue;
      return {
        valid: isValid,
        customError: !isValid,
      };
    } else {
      return {};
    }
  }
}
