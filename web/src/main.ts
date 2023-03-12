import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { userService, newsService, webSocketService } from "./services";
import {
  httpService,
  RouteController,
  routerService,
  themeService,
  translateService,
} from "@veryan/lit-spa";
import { routes } from "./app.routes";

import "@veryan/lit-spa";
import "./components/top-bar/top-bar";

@customElement("my-app")
class Truba extends LitElement {
  static styles = [];

  private router = new RouteController(this, routes);

  constructor() {
    super();
    this.registerServiceWorker();
    this.registerThemes();
    httpService.baseHttp = this.customBaseHttp;
    this.initNews();
  }

  render() {
    return html`
      <top-bar>
        <div class="main">${this.router.navigation()}</div>
        <lit-spa-toast></lit-spa-toast>
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
        if (!user) {
          this.googleOneTap();
        }
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
    themeService.registerThemes({
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

  customBaseHttp<T>(url: string, options?: RequestInit, bustCache = false): Promise<T>{
    return httpService.cachedHttp(url, options, bustCache).then((response) => {
      if (response.status == 401 || response.status == 403) {
        httpService.removeAuthToken();
        routerService.navigate("/login");
        throw new Error("Unauthorized");
      }
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      return response.json();
    });
  }

  disconnectedCallback() {
    webSocketService.closeSocket();
    super.disconnectedCallback();
  }
}
