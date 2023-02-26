import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { userService, newsService, webSocketService } from "./services";
import {
  RouteController,
  ToastController,
  themeService,
  translateService,
} from "@veryan/lit-spa";
import { routes } from "./app.routes";
import "./components/top-bar/top-bar";

@customElement("my-app")
class Truba extends LitElement {
  static styles = [];

  private router = new RouteController(this, routes);
  private toaster = new ToastController(this);

  constructor() {
    super();
    this.registerServiceWorker();
    this.registerThemes();
    this.initNews();
    this.googleOneTap();
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

  initNews() {
    userService.me().then(
      (user) => {
        if (user.language) {
          translateService.useLanguage(user.language);
        }
        newsService.getNews(user);
      },
      (err) => newsService.getNews(null)
    );
  }

  googleOneTap() {
    const oneTapLogin = userService.googleProvider.useGoogleOneTapLogin({
      cancel_on_tap_outside: true,
      onError: () => console.error("Failed to oneTapLogin"),
      onSuccess: (res) => {
        if (res.credential) {
          userService
            .socialLogin(res.credential)
            .then((user) => newsService.getNews(user));
        }
      },
    });
    setTimeout(() => oneTapLogin());
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
      light: {
        "--primary-color": primaryBlack,
        "--primary-background-color": primaryWhite,
        "--secondary-background-color": secondaryWhite,
        "--image-color": imageColor,
        "--input-fill": inputBackgroundColor,
        "--outline-color": outlineColor,
        "--toast-background": toastBackground,
        "--chip-background": inputBackgroundColor,
      },
      dark: {
        "--primary-color": primaryWhite,
        "--primary-background-color": primaryBlack,
        "--secondary-background-color": secondaryBlack,
        "--image-color": invertedImageColor,
        "--input-fill": invertedInputBackgroundColor,
        "--outline-color": invertedOutlineColor,
        "--toast-background": secondaryBlack,
        "--chip-background": chipBackground,
      },
    } as any);
  }

  disconnectedCallback() {
    webSocketService.closeSocket();
    super.disconnectedCallback();
  }
}
