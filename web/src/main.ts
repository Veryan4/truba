import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  userService,
  newsService,
} from "./services";
import { appConfig } from "./app.config";
import { RouteController, ToastController, TranslationController, httpService, themeService, translateService } from "@veryan/lit-spa";
import "./components/top-bar/top-bar";
import { routes } from "./app.routes";

@customElement("my-app")
class Truba extends LitElement {
  static styles = [];

  private router = new RouteController(this, routes);
  private toaster = new ToastController(this);

  @state()
  private _isLoaded = false;

  @property({ type: Boolean })
  hasLoadedTranslations: boolean;

  @property({ type: Object })
  socket: WebSocket;

  constructor() {
    super();
    this.registerServiceWorker();
    this.registerThemes();
    if (!this._isLoaded) {
      userService
        .me()
        .then(
          (user) => {
            if (user.language) {
              translateService.useLanguage(user.language);
            }
            return newsService.getNews(user);
          },
          (err) => {
            return newsService.getNews(null);
          }
        )
        .then((news) => {
          this._isLoaded = true;
        });
    }
  }

  render() {
    return html`
      <top-bar>
        <div class="main">${this.router.navigation()}</div>
        ${this.toaster.wait()}
      </top-bar>
    `;
  }

  registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", function () {
        navigator.serviceWorker.register("/sw.js");
      });
    }
  }

  async connectedCallback() {
    super.connectedCallback();

    const user = userService.getUser();
    if (user) {
      if (!this.socket) await this.initWebsocket();
    } else if (this.socket) {
      this.socket.close();
    }
  }

  disconnectedCallback() {
    this.socket.close();
    super.disconnectedCallback();
  }

  public async initWebsocket() {
    const token = httpService.getAuthToken();
    if (!token) return;
    this.socket = await new WebSocket(appConfig.backendSocket, token);
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (Array.isArray(data)) {
        const user = userService.getUser();
        if (user && user.language === "en") {
          newsService.changeNewsStories(data, user);
        } else {
          newsService.getNews(user);
        }
      }
    };
  }

  registerThemes() {
    const root = document.querySelector(":root") as HTMLElement;
    const primaryWhite = "#fafafa";
    const secondaryWhite = "white";
    const primaryBlack = "#2c2c2c";
    const secondaryBlack = "black";
    const imageColor = "unset";
    const invertedImageColor = "invert(100%)";
    const inputBackgroundColor = "#E8E8E8";
    const invertedInputBackgroundColor = "#696969";
    const outlineColor = "#b0bec5";
    const invertedOutlineColor = "#2c2c2c";
    const toastBackground = "#313131";
    const chipBackground = "#696969";
    themeService.registerThemes(root, {
      'light': {
        '--primary-color': primaryBlack,
        '--primary-background-color': primaryWhite,
        '--secondary-background-color': secondaryWhite,
        '--image-color': imageColor,
        '--input-fill': inputBackgroundColor,
        '--outline-color': outlineColor,
        '--toast-background': toastBackground,
        '--chip-background': inputBackgroundColor
      },
      'dark': {
        '--primary-color': primaryWhite,
        '--primary-background-color': primaryBlack,
        '--secondary-background-color': secondaryBlack,
        '--image-color': invertedImageColor,
        '--input-fill': invertedInputBackgroundColor,
        '--outline-color': invertedOutlineColor,
        '--toast-background': secondaryBlack,
        '--chip-background': chipBackground
      }
    } as any);
  }
}
