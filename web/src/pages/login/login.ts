import { LitElement, html } from "lit";
import { customElement, query, state } from "lit/decorators.js";
import {
  ThemeController,
  TranslationController,
  routerService,
} from "@veryan/lit-spa";
import { newsService, userService, formService } from "../../services";
import {
  googleButtonStyles,
} from "../../styles";
import { styles } from "./login.styles";

import "../../material-web"

@customElement("auth-login")
class Login extends LitElement {
  static styles = [styles, googleButtonStyles];

  private i18n = new TranslationController(this, {scope:"auth"});
  private theme = new ThemeController(this);

  @query("#email")
  emailInput: HTMLInputElement;

  @query("#password")
  passwordInput: HTMLInputElement;

  @query("#googleBtn")
  googleBtn: HTMLElement;

  @state()
  isFormValid = false;

  render() {
    return html`
      <div class="card">
        <div class="card-title">${this.i18n.t("auth.login.title")}</div>
        <div id="googleBtn"></div>
        <br />
        <span class="centered-text">${this.i18n.t("auth.login.or")}</span>
        <br />
        <form class="card-form">
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.login.email")}"
            id="email"
            type="email"
            name="email"
            required
            @input=${this.checkInputValidity}
          ></md-filled-text-field>
          <md-filled-text-field
            class="form-field"
            label="${this.i18n.t("auth.login.password")}"
            id="password"
            type="password"
            name="password"
            required
            @input=${this.checkInputValidity}
          ></md-filled-text-field>
        </form>
        <div class="form-buttons">
          <md-filled-button
            ?disabled=${!this.isFormValid}
            @click=${this.login}
          >${this.i18n.t("auth.login.login")}</md-filled-button>
          <md-outlined-button
            class="sign-btn"
            @click=${() => routerService.navigate("/register")}
          >${this.i18n.t("auth.login.register")}</md-outlined-button>
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

  connectedCallback(): void {
    super.connectedCallback();
    setTimeout(() => {
      const renderButton = userService.googleProvider.useRenderButton({
        itp_support: true,
        element: this.googleBtn,
        type: "standard",
        theme: "outline",
        text: "signin_with",
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

  handleGoogleSignIn(idToken: string) {
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

  checkInputValidity(e: Event) {
    formService.checkInputValidity(e);
    this.checkFormValidity();
  }
}
