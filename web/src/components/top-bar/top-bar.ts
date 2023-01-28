import { LitElement, html } from "lit";
import { customElement, query } from "lit/decorators.js";
import {
  TranslationController,
  DeviceController,
  UserController,
} from "../../controllers";
import { User } from "../../models";
import {
  userService,
  translateService,
  newsService,
  routerService,
  themeService,
} from "../../services";
import {
  buttonStyles,
  iconButtonStyles,
  topAppBarStyles,
  switchStyles,
  menuStyles,
} from "../../styles";
import { styles } from "./top-bar.styles";

import "../tooltip/tooltip";
import "@material/mwc-menu";
import "@material/mwc-list/mwc-list-item";
import "@material/mwc-switch";
import "@material/mwc-formfield";
import "@material/mwc-button";

@customElement("top-bar")
class TopBar extends LitElement {
  static styles = [
    topAppBarStyles,
    iconButtonStyles,
    buttonStyles,
    switchStyles,
    menuStyles,
    styles,
  ];

  private i18n = new TranslationController(this);
  private user = new UserController(this);
  private device = new DeviceController(this);

  @query("#anchor")
  anchor: HTMLElement;

  @query("#lang-anchor")
  langAnchor: HTMLElement;

  @query("#menu")
  menu: any;

  render() {
    return html` <header class="mdc-top-app-bar top-bar">
        <div class="mdc-top-app-bar__row">
          <section
            class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start"
          >
            <a href="/" class="logo"></a>
          </section>
          <section
            class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end"
            role="toolbar"
          >
            ${this.renderButtons()}
            <div style="position: relative;">
              <button
                @click=${(e: Event) => (this.menu.open = true)}
                id="anchor"
                aria-label="Options"
                class="material-icons mdc-top-app-bar__action-item mdc-icon-button hamburger toolbar mdc-menu-surface--anchor"
              >
                view_headline
              </button>
              ${this.renderMenu()}
            </div>
          </section>
        </div>
      </header>
      <main class="mdc-top-app-bar--fixed-adjust">
        <slot></slot>
      </main>`;
  }

  renderButtons() {
    return this.user.value
      ? html` <tool-tip text=${this.i18n.t("header.switch")} position="bottom"
          ><mwc-switch
            .selected=${this.user.value.is_personalized}
            @click=${this.onTabSwitch}
          ></mwc-switch
        ></tool-tip>`
      : html`
          <mwc-button
            dense
            unelevated
            label=${this.i18n.t("header.login")}
            @click=${() => routerService.navigate("/login")}
          ></mwc-button>
          <mwc-button
            dense
            label=${this.i18n.t("header.register")}
            @click=${() => routerService.navigate("/register")}
          ></mwc-button>
        `;
  }

  renderMenu() {
    return html`
      <mwc-menu
        id="menu"
        .anchor=${this.anchor}
        .corner=${this.device.isMobile ? "TOP_RIGHT" : "TOP_LEFT"}
        .menuCorner=${this.device.isMobile ? "END" : "START"}
      >
        <mwc-list-item @click=${() => routerService.navigate("/about")}>
          <i class="material-icons mdc-icon-button__icon">info</i>
          ${this.i18n.t("header.about")}
        </mwc-list-item>
        <mwc-list-item @click=${themeService.changeTheme}>
          <i class="material-icons mdc-icon-button__icon">invert_colors</i>
          ${this.i18n.t("header.dark_mode")}
        </mwc-list-item>
        ${this.user.value
          ? html` <mwc-list-item
                @click=${() => routerService.navigate("/settings")}
              >
                <i class="material-icons mdc-icon-button__icon">settings</i>
                ${this.i18n.t("header.settings")}
              </mwc-list-item>
              <mwc-list-item @click=${this.logout}
                ><i class="material-icons mdc-icon-button__icon">clear</i
                >${this.i18n.t("header.logout")}</mwc-list-item
              >`
          : ""}
        <hr />
        <mwc-list-item @click=${(e: Event) => this.language("en")}>
          <i class="material-icons mdc-icon-button__icon flag uk-flag"></i>
          English
        </mwc-list-item>
        <mwc-list-item @click=${(e: Event) => this.language("fr")}>
          <i class="material-icons mdc-icon-button__icon flag fr-flag"></i>
          Francais
        </mwc-list-item>
      </mwc-menu>
    `;
  }

  async logout(): Promise<void> {
    this.menu.open = false;
    await userService.signOut();
    await newsService.getNews(null);
  }

  async language(lang: string): Promise<void> {
    await translateService.useLanguage(lang);
    const user = userService.getUser();
    if (user) {
      user.language = lang;
      userService.updateUser(user).then((u) => newsService.getNews(u));
    } else {
      newsService.getNews(null);
    }
  }

  onTabSwitch(): void {
    const user = userService.getUser() as User;
    user.is_personalized = !user.is_personalized;
    userService.updateUser(user).then((updatedUser) => {
      newsService.getNews(updatedUser);
    });
  }
}
