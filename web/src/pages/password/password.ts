import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { TranslationController, routerService } from "@veryan/lit-spa";
import { userService, formService } from "../../services";
import { User } from "../../models";
import { MdFilledTextField } from "../../material-web";
import { styles } from "./password.styles";

import "../../material-web"

@customElement("auth-password")
class Password extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this, {scope:"auth"});

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

  private debounceTimer = 0;

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
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.password.password")}"
            id="password"
            type="password"
            name="password"
            @change=${formService.checkInputValidity}
            required
          ></md-filled-text-field>
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.password.repeat")}"
            id="repeatPassword"
            type="password"
            name="repeatPassword"
            errorMessage="${this.i18n.t("auth.password.mismatch")}"
            @change=${this.passwordsMatchValidator}
            required
          ></md-filled-text-field>
        </form>`
      : html` <form class="card-form">
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.password.email")}"
            id="email"
            type="email"
            name="email"
            @change=${formService.checkInputValidity}
            required
          ></md-filled-text-field>
        </form>`;
  }

  renderButton() {
    return this._hasToken
      ? html`<md-filled-button
          @click=${this.resetPassword}
        >${this.i18n.t("auth.password.reset.button")}</md-filled-button>`
      : html`<md-filled-button
          @click=${this.forgotPassword}
        >${this.i18n.t("auth.password.submit.button")}</md-filled-button>`;
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
    e: Event
  ) {
    const input = e.target as MdFilledTextField;
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      input.error = this.passwordInput.value !== input.value;
    }, 300);
  }
}
