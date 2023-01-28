import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  translateService,
  routerService,
  tokenService,
  userService,
  newsService,
} from "./services";
import { RouteController, ToastController } from "./controllers";
import { appConfig } from "./app.config";
import "./components/top-bar/top-bar";

@customElement("my-app")
class Truba extends LitElement {
  static styles = [];

  private router = new RouteController(this);
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

  shouldUpdate(
    changedProperties: Map<string | number | symbol, unknown>
  ): boolean {
    return this.hasLoadedTranslations && super.shouldUpdate(changedProperties);
  }

  async connectedCallback() {
    super.connectedCallback();

    window.dispatchEvent(new CustomEvent(routerService.ROUTE_EVENT));
    window.onpopstate = () => {
      window.dispatchEvent(new CustomEvent(routerService.ROUTE_EVENT));
    };

    const user = userService.getUser();
    if (user) {
      if (!this.socket) await this.initWebsocket();
    } else if (this.socket) {
      this.socket.close();
    }

    !this.hasLoadedTranslations &&
      (await translateService.initTranslateLanguage());
    this.hasLoadedTranslations = true;
  }

  disconnectedCallback() {
    this.socket.close();
    super.disconnectedCallback();
  }

  public async initWebsocket() {
    const token = tokenService.getToken();
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
}
