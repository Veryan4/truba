import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import { ThemeController, TranslationController } from "../../controllers";
import { appConfig } from "../../app.config";
import {
  newsService,
  userService,
  formService,
  routerService,
} from "../../services";
import { textFieldStyles, buttonStyles } from "../../styles";
import { styles } from "./login.styles";

import "@material/mwc-button";
import "@material/mwc-formfield";
import "@material/mwc-textfield";
import "@google-web-components/google-signin";
import "@google-web-components/google-signin/google-signin-aware";

@customElement("auth-login")
class Login extends LitElement {
  static styles = [styles, buttonStyles, textFieldStyles];

  private i18n = new TranslationController(this);
  private theme = new ThemeController(this);

  @query("#email")
  emailInput: HTMLInputElement;

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
      <div class="card">
        <div class="card-title">${this.i18n.t("auth.login.title")}</div>
        <google-signin
          id="google"
          brand="google"
          client-id="${appConfig.googleAuthClientId}"
          label-signin=${this.i18n.t("auth.login.google")}
          theme=${this.theme.value}
          width="wide"
          height="tall"
        ></google-signin>
        <br />
        <span class="centered-text">${this.i18n.t("auth.login.or")}</span>
        <br />
        <form class="card-form">
          <mwc-textfield
            class="form-field"
            label="${this.i18n.t("auth.login.email")}"
            id="email"
            type="email"
            name="email"
            required
            @input=${this.checkFormValidity}
          ></mwc-textfield>
          <mwc-textfield
            class="form-field"
            label="${this.i18n.t("auth.login.password")}"
            id="password"
            type="password"
            name="password"
            required
            @input=${this.checkFormValidity}
          ></mwc-textfield>
        </form>
        <div class="form-buttons">
          <mwc-button
            dense
            unelevated
            ?disabled=${!this.isFormValid}
            @click=${this.login}
            label=${this.i18n.t("auth.login.login")}
          ></mwc-button>
          <mwc-button
            class="sign-btn"
            dense
            label=${this.i18n.t("auth.login.register")}
            @click=${() => routerService.navigate("/register")}
          ></mwc-button>
        </div>
        <br />
        ${this.i18n.t("auth.login.about_1")}<a href="/about"
          >${this.i18n.t("auth.login.about_2")}</a
        >.
        <br />
        <a href="/password">${this.i18n.t("auth.login.forgot")}</a>
      </div>
    `;
  }

  login(): void {
    if (!this.isFormValid) {
      return;
    }

    const formData = this.collectFormData();

    userService
      .login(formData.email, formData.password)
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
}
