import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { appConfig } from "../../app.config";
import {
  newsService,
  userService,
  formService,
} from "../../services";
import { ThemeController, TranslationController, routerService } from "@veryan/lit-spa";
import { checkBoxStyles, textFieldStyles, buttonStyles, googleButtonStyles } from "../../styles";
import { styles } from "./register.styles";

import "@material/mwc-button";
import "@material/mwc-checkbox";
import "@material/mwc-formfield";
import "@material/mwc-textfield";

@customElement("auth-register")
class Register extends LitElement {
  static styles = [styles, buttonStyles, textFieldStyles, checkBoxStyles, googleButtonStyles];

  private i18n = new TranslationController(this, "auth");
  private theme = new ThemeController(this);

  @query("#password")
  passwordInput: HTMLInputElement;

  @query("#googleBtn")
  googleBtn: HTMLElement;

  @state()
  isFormValid = false;

  render() {
    return html`
    <div class="card register">
      <div class="card-title">${this.i18n.t("auth.register.title")}</div>
      <div id="googleBtn"></div>
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

  connectedCallback(): void {
    super.connectedCallback();
    setTimeout(() => {
      const renderButton = userService.googleProvider.useRenderButton({
        itp_support: true,
        element: this.googleBtn,
        type: 'standard',
        theme: 'outline',
        text: 'signup_with',
        size: 'large',
        shape: 'rectangular',
        logo_alignment: 'left',
        ux_mode: 'popup',
        locale: navigator.language,
        onError: () => console.error('Failed to render button'),
        onSuccess: (res) => {
          if (res.credential) {
            userService
              .socialLogin(res.credential)
              .then((user) => newsService.getNews(user))
              .then(() => routerService.navigate("/"));
          }
        }
      })
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
