import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { appConfig } from "../../app.config";
import {
  newsService,
  userService,
  formService,
  routerService,
} from "../../services";
import { ThemeController, TranslationController } from "../../controllers";
import { checkBoxStyles, textFieldStyles, buttonStyles } from "../../styles";
import { styles } from "./register.styles";

import "@material/mwc-button";
import "@material/mwc-checkbox";
import "@material/mwc-formfield";
import "@material/mwc-textfield";
import "@google-web-components/google-signin";
import "@google-web-components/google-signin/google-signin-aware";

@customElement("auth-register")
class Register extends LitElement {
  static styles = [styles, buttonStyles, textFieldStyles, checkBoxStyles];

  private i18n = new TranslationController(this);
  private theme = new ThemeController(this);

  @query("#password")
  passwordInput: HTMLInputElement;

  @state()
  isFormValid = false;

  constructor() {
    super();
    window.addEventListener("google-signin-aware-success", (e: Event) => {
      const idToken = (window as any).gapi.auth2
        .getAuthInstance()
        .currentUser.get()
        .getAuthResponse().id_token;
      userService
        .socialLogin(idToken)
        .then((user) => {
          return newsService.getNews(user);
        })
        .then(() => routerService.navigate("/"));
    });
  }

  render() {
    return html`
    <div class="card register">
      <div class="card-title">${this.i18n.t("auth.register.title")}</div>
      <google-signin
        id="google"
        brand="google"
        client-id="${appConfig.googleAuthClientId}"
        label-signin="${this.i18n.t("auth.register.google")}"
        theme=${this.theme.value}
        width="wide"
        height="tall"
      ></google-signin>
      <br />
      <span class="centered-text">${this.i18n.t("auth.register.or")}</span>
      <br />
      <form class="card-form">
        <div class="row">
          <mwc-textfield
              class="form-field"
              label="${this.i18n.t("auth.register.username")}"
              id="username"
              type="text"
              name="username"
              @input=${this.checkFormValidity}
              required></mwc-textfield>
          <mwc-textfield
              class="form-field"
              label="${this.i18n.t("auth.register.email")}"
              id="email"
              type="email"
              name="email"
              @input=${this.checkFormValidity}
              required></mwc-textfield>
        </div>
        <div class="row">
          <mwc-textfield
              class="form-field"
              label="${this.i18n.t("auth.register.password")}"
              id="password"
              type="password"
              name="password"
              @input=${this.checkFormValidity}
              required></mwc-textfield>
            <mwc-textfield
              class="form-field"
              label="${this.i18n.t("auth.register.repeat")}"
              id="repeatPassword"
              type="password"
              name="repeatPassword"
              .autoValidate=${true}
              .validationMessage=${"Password missmatch"}
              .validityTransform=${(
                value: string,
                nativeValidity: ValidityState
              ) =>
                this.passwordsMatchValidator(
                  value,
                  nativeValidity,
                  this.passwordInput
                )}
              required></mwc-textfield>
        </div>
        <div class="consent-box">
          <mwc-formfield nowrap>
            <mwc-checkbox id="privacy" name="privacy" @change=${
              this.checkFormValidity
            }></mwc-checkbox>
            I have read truba's <a href="/privacy" target="_blank">Privacy Policy</a>
          </mwc-formfield>
        </div>
        <div class="consent-box">
          <mwc-formfield nowrap>
            <mwc-checkbox id="terms" name="terms" @change=${
              this.checkFormValidity
            }></mwc-checkbox>
            I have read and agree to the <a href="/terms" target="_blank">Terms of Service</a>
          </mwc-formfield>
          </mat-checkbox>
        </div>
      </form>
      <div class="form-buttons">
      <mwc-button 
        dense
        unelevated
        ?disabled=${!this.isFormValid}
        @click=${this.register}
        label=${this.i18n.t("auth.register.register")}
      >
      </mwc-button>
      <mwc-button 
        class="sign-btn" 
        dense
        label=${this.i18n.t("auth.register.login")}
        @click=${() => routerService.navigate("/login")}
      >
      </mwc-button>
      </div>
      <br />
      ${this.i18n.t("auth.register.about_1")}<a href="/about">${this.i18n.t(
      "auth.register.about_2"
    )}</a>.
    </div>`;
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
    passwordInput: HTMLInputElement
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
