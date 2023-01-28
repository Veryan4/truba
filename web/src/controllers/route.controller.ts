import { ReactiveControllerHost, noChange, html } from "lit";
import { ChildPart, DirectiveParameters, directive } from "lit/directive.js";
import { AsyncDirective } from "lit/async-directive.js";
import { Route } from "../models/route.model";
import { routerService, userService } from "../services";
import { UserController } from "./user.controller";
import "../components/loader/loader";

class RouteDirective extends AsyncDirective {
  private currentRoute: string;

  update(part: ChildPart, [route]: DirectiveParameters<this>) {
    // target element can be accessed from part
    return this.render(route);
  }

  render(route: Route) {
    if (this.currentRoute === route.name) {
      return noChange;
    }
    this.currentRoute = route.name;
    route.component().then((resolvedValue) => {
      // Rendered asynchronously:
      this.setValue(resolvedValue);
    });
    return html`<app-loader></app-loader>`;
  }
}
const routeDirective = directive(RouteDirective);

export class RouteController {
  private host: ReactiveControllerHost;
  private user: UserController;
  canceled = false;

  activeRoute: Route;

  routes: Route[] = [
    {
      name: "home",
      pattern: "",
      component: () =>
        import("../pages/news-cards/news-cards").then(
          () => html`<news-cards></news-cards>`
        ),
    },
    {
      name: "login",
      pattern: "login",
      component: () =>
        import("../pages/login/login").then(
          () => html`<auth-login></auth-login>`
        ),
    },
    {
      name: "register",
      pattern: "register",
      component: () =>
        import("../pages/register/register").then(
          () => html`<auth-register></auth-register>`
        ),
    },
    {
      name: "password",
      pattern: "password/:id",
      component: () =>
        import("../pages/password/password").then(
          () => html`<auth-password></auth-password>`
        ),
    },
    {
      name: "email",
      pattern: "email",
      component: () =>
        import("../pages/email/email").then(
          () => html`<auth-email></auth-email>`
        ),
      isProtected: true,
    },
    {
      name: "unsubscribe",
      pattern: "unsubscribe",
      component: () =>
        import("../pages/unsubscribe/unsubscribe").then(
          () => html`<auth-unsubscribe></auth-unsubscribe>`
        ),
    },
    {
      name: "about",
      pattern: "about",
      component: () =>
        import("../pages/about/about").then(
          () => html`<app-about></app-about>`
        ),
    },
    {
      name: "settings",
      pattern: "settings",
      component: () =>
        import("../pages/settings/settings").then(
          () => html`<app-settings></app-settings>`
        ),
      isProtected: true,
    },
    {
      name: "terms",
      pattern: "terms",
      component: () =>
        import("../pages/terms/terms").then(
          () => html`<app-terms></app-terms>`
        ),
    },
    {
      name: "privacy",
      pattern: "privacy",
      component: () =>
        import("../pages/privacy/privacy").then(
          () => html`<app-privacy></app-privacy>`
        ),
    },
    {
      name: "not-found",
      pattern: "*",
      component: () =>
        import("../pages/404/404").then(() => html`<not-found></not-found>`),
    },
  ];

  navigation() {
    return routeDirective(this.activeRoute);
  }

  _changeRoute = (e: CustomEvent) => {
    this.canceled = true;
    const uri = decodeURI(window.location.pathname);
    let nextRoute = this.routes.find(
      (route) =>
        route.pattern !== "*" && routerService.testRoute(uri, route.pattern)
    );
    if (nextRoute) {
      if (nextRoute.name !== this.activeRoute.name) {
        if (nextRoute.isProtected && !this.user.value) {
          this.canceled = false;
          const loginRoute = this.routes.filter(
            (route) => route.pattern === "login"
          )[0];
          Promise.resolve(userService.me())
            .then((user) => {
              if (!this.canceled) {
                if (user) {
                  this.activeRoute = nextRoute!;
                } else {
                  this.activeRoute = loginRoute;
                  window.history.pushState({}, "", loginRoute.name);
                }
                this.host.requestUpdate();
              }
            })
            .catch((err) => {
              this.activeRoute = loginRoute;
              window.history.pushState({}, "", loginRoute.name);
              this.host.requestUpdate();
            });
        } else {
          this.activeRoute = nextRoute;
          this.host.requestUpdate();
        }
      }
    } else {
      nextRoute = this.routes.find((route) => route.pattern === "*");
      if (nextRoute) {
        this.activeRoute = nextRoute;
        this.host.requestUpdate();
      }
    }
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    this.user = new UserController(host);
    const homeRoute = this.routes.find((route) => route.pattern === "");
    if (homeRoute) {
      this.activeRoute = homeRoute;
    }
    host.addController(this);
  }

  hostConnected() {
    window.addEventListener(
      routerService.ROUTE_EVENT,
      this._changeRoute as EventListener
    );
  }

  hostDisconnected() {
    window.removeEventListener(
      routerService.ROUTE_EVENT,
      this._changeRoute as EventListener
    );
  }
}
