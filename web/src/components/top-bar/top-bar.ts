import { LitElement, html } from "lit";
import { customElement, query } from "lit/decorators.js";
import { UserController } from "../../controllers";
import { User } from "../../models";
import { userService, newsService } from "../../services";
import {
  DeviceController,
  TranslationController,
  translateService,
  routerService,
  themeService,
  ThemeController,
} from "@veryan/lit-spa";
import {
  closeIcon,
  infoIcon,
  invertColorsIcon,
  menuIcon,
  settingsIcon,
} from "../../styles";
import { styles, mdcTopAppBarStyles } from "./top-bar.styles";

import "@veryan/lit-spa";
import "../../material-web";

@customElement("top-bar")
class TopBar extends LitElement {
  static styles = [mdcTopAppBarStyles, styles];

  private i18n = new TranslationController(this, { scope: "header" });
  private user = new UserController(this);
  private device = new DeviceController(this);
  private theme = new ThemeController(this);

  @query("#menu")
  menu: any;

  render() {
    return html`<header class="mdc-top-app-bar top-bar">
        <div class="mdc-top-app-bar__row">
          <section
            class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start"
          >
            <a @click=${() => routerService.navigate("/")} class="logo"></a>
          </section>
          <section
            class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end"
            role="toolbar"
          >
            ${this.renderButtons()}
            <div style="position: relative;">
              <div
                class="icon hamburger toolbar mdc-top-app-bar__action-item mdc-menu-surface--anchor"
                id="anchor"
                aria-label="Options"
                @click=${(e: Event) => (this.menu.open = true)}
              >
                ${menuIcon()}
              </div>
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
      ? html` <lit-spa-tooltip
          text=${this.i18n.t("header.switch")}
          position="bottom"
          ><md-switch
            .selected=${this.user.value.is_personalized}
            show-only-selected-icon
            @click=${this.onTabSwitch}
          ></md-switch
        ></lit-spa-tooltip>`
      : html` <div class="button-wrap">
          <md-filled-button @click=${() => routerService.navigate("/login")}
            >${this.i18n.t("header.login")}</md-filled-button
          >
          <md-outlined-button
            @click=${() => routerService.navigate("/register")}
            >${this.i18n.t("header.register")}</md-outlined-button
          >
        </div>`;
  }

  renderMenu() {
    return html`
      <md-menu
        id="menu"
        anchor="anchor"
        .anchor-corner=${this.device.isMobile ? "TOP_RIGHT" : "TOP_LEFT"}
        .menu-corner=${this.device.isMobile ? "END" : "START"}
      >
        <md-menu-item @click=${() => routerService.navigate("/about")}>
          <div class="menu-item" slot="headline">
            <i class="icon mdc-icon-button__icon">${infoIcon()}</i>
            ${this.i18n.t("header.about")}
          </div>
        </md-menu-item>
        <md-menu-item @click=${this.changeTheme}>
          <div class="menu-item" slot="headline">
            <i class="icon mdc-icon-button__icon">${invertColorsIcon()}</i>
            ${this.i18n.t("header.dark_mode")}
          </div>
        </md-menu-item>
        ${this.user.value
          ? html` <md-menu-item
                @click=${() => routerService.navigate("/settings")}
              >
                <div class="menu-item" slot="headline">
                  <i class="icon mdc-icon-button__icon">${settingsIcon()}</i>
                  ${this.i18n.t("header.settings")}
                </div>
              </md-menu-item>
              <md-menu-item @click=${this.logout}>
                <div class="menu-item" slot="headline">
                  <i class="icon mdc-icon-button__icon">${closeIcon()}</i
                  >${this.i18n.t("header.logout")}
                </div>
              </md-menu-item>`
          : ""}
        <hr />
        <md-menu-item @click=${(e: Event) => this.language("en")}>
          <div class="menu-item" slot="headline">
            <i class="icon mdc-icon-button__icon flag uk-flag"></i>
            English
          </div>
        </md-menu-item>
        <md-menu-item @click=${(e: Event) => this.language("fr")}>
          <div class="menu-item" slot="headline">
            <i class="icon mdc-icon-button__icon flag fr-flag"></i>
            Francais
          </div>
        </md-menu-item>
      </md-menu>
    `;
  }

  async logout(): Promise<void> {
    this.menu.open = false;
    await userService.signOut();
    await newsService.getNews(null);
    routerService.navigate("/");
  }

  async language(lang: string): Promise<void> {
    await translateService.useLanguage(lang);
    const user = userService.state.getValue();
    if (user) {
      user.language = lang;
      userService.updateUser(user).then((u) => newsService.getNews(u));
    } else {
      newsService.getNews(null);
    }
  }

  onTabSwitch(): void {
    const user = userService.state.getValue() as User;
    user.is_personalized = !user.is_personalized;
    userService.updateUser(user).then((updatedUser) => {
      newsService.getNews(updatedUser);
    });
  }

  changeTheme() {
    if (this.theme.value == "light") {
      themeService.changeTheme("dark");
    } else {
      themeService.changeTheme("light");
    }
  }
}
