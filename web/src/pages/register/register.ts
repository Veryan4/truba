import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { newsService, userService, formService } from "../../services";
import {
  ThemeController,
  TranslationController,
  routerService,
} from "@veryan/lit-spa";
import {
  checkBoxStyles,
  textFieldStyles,
  buttonStyles,
  googleButtonStyles,
} from "../../styles";
import { styles } from "./register.styles";

import "../../material-web";

@customElement("auth-register")
class Register extends LitElement {
  static styles = [
    styles,
    buttonStyles,
    textFieldStyles,
    checkBoxStyles,
    googleButtonStyles,
  ];

  private i18n = new TranslationController(this, "auth");
  private theme = new ThemeController(this);

  @query("#password")
  passwordInput: HTMLInputElement;

  @query("#googleBtn")
  googleBtn: HTMLElement;

  @state()
  isFormValid = false;

  render() {
    return html` <div class="card register">
      <div class="card-title">${this.i18n.t("auth.register.title")}</div>
      <div id="googleBtn"></div>
      <br />
      <span class="centered-text">${this.i18n.t("auth.register.or")}</span>
      <br />
      <form class="card-form">
        <div class="row">
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.register.username")}"
            id="username"
            type="text"
            name="username"
            @input=${this.checkFormValidity}
            required
          ></md-filled-text-field>
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.register.email")}"
            id="email"
            type="email"
            name="email"
            @input=${this.checkFormValidity}
            required
          ></md-filled-text-field>
        </div>
        <div class="row">
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.register.password")}"
            id="password"
            type="password"
            name="password"
            @input=${this.checkFormValidity}
            required
          ></md-filled-text-field>
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.register.repeat")}"
            id="repeatPassword"
            type="password"
            name="repeatPassword"
            .autoValidate=${true}
            .validationMessage=${"Password missmatch"}
            .validityTransform=${(
              value: string,
              nativeValidity: ValidityState,
            ) =>
              this.passwordsMatchValidator(
                value,
                nativeValidity,
                this.passwordInput,
              )}
            required
          ></md-filled-text-field>
        </div>
        <div class="consent-box">
          <label>
            <md-checkbox
              id="privacy"
              name="privacy"
              @change=${this.checkFormValidity}
              touch-target="wrapper"
            ></md-checkbox>
            I have read truba's
            <a href="/privacy" target="_blank">Privacy Policy</a>
          </label>
        </div>
        <div class="consent-box">
          <label>
            <md-checkbox
              id="terms"
              name="terms"
              @change=${this.checkFormValidity}
              touch-target="wrapper"
            ></md-checkbox>
            I have read and agree to the
            <a href="/terms" target="_blank">Terms of Service</a>
          </label>
        </div>
      </form>
      <div class="form-buttons">
        <md-filled-button
          unelevated
          ?disabled=${!this.isFormValid}
          @click=${this.register}
          >${this.i18n.t("auth.register.register")}
        </md-filled-button>
        <md-filled-button
          class="sign-btn"
          @click=${() => routerService.navigate("/login")}
          >${this.i18n.t("auth.register.login")}
        </md-filled-button>
      </div>
      <br />
      ${this.i18n.t("auth.register.about_1")}<a href="/about"
        >${this.i18n.t("auth.register.about_2")}</a
      >.
    </div>`;
  }

  connectedCallback(): void {
    super.connectedCallback();
    setTimeout(() => {
      const renderButton = userService.googleProvider.useRenderButton({
        itp_support: true,
        element: this.googleBtn,
        type: "standard",
        theme: "outline",
        text: "signup_with",
        size: "large",
        shape: "rectangular",
        logo_alignment: "left",
        ux_mode: "popup",
        locale: navigator.language,
        onError: () => console.error("Failed to render button"),
        onSuccess: (res) => {
          if (res.credential) {
            userService
              .socialLogin(res.credential)
              .then((user) => newsService.getNews(user))
              .then(() => routerService.navigate("/"));
          }
        },
      });
      renderButton();
    });
  }

  register(): void {
    if (!this.isFormValid) {
      return;
    }

    const formData = this.collectFormData();

    userService
      .register(formData.username, formData.email, formData.password)
      .then((user) => {
        return newsService.getNews(user);
      })
      .then(() => routerService.navigate("/"));
  }

  handleGoogleRegister(idToken: string) {
    userService
      .socialLogin(idToken)
      .then((user) => {
        return newsService.getNews(user);
      })
      .then(() => routerService.navigate("/"));
  }

  checkFormValidity() {
    this.isFormValid = formService.checkFormValidity(this.shadowRoot!);
  }

  collectFormData(): Record<string, any> {
    if (this.isFormValid) {
      return formService.collectFormData(this.shadowRoot!);
    }
    return {};
  }

  passwordsMatchValidator(
    value: string,
    nativeValidity: ValidityState,
    passwordInput: HTMLInputElement,
  ): Partial<ValidityState> | null {
    if (nativeValidity.valid) {
      const isValid = passwordInput.value === value;
      return {
        valid: isValid,
        customError: !isValid,
      };
    } else {
      return {};
    }
  }
}
