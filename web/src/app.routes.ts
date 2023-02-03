import { html } from "lit";
import { Route } from "@veryan/lit-spa";
import { authGuard } from "./guards/auth.guard";

export const routes: Route[] = [
    {
      name: "home",
      pattern: "",
      component: () =>
        import("./pages/news-cards/news-cards").then(
          () => html`<news-cards></news-cards>`
        ),
    },
    {
      name: "login",
      pattern: "login",
      component: () =>
        import("./pages/login/login").then(
          () => html`<auth-login></auth-login>`
        ),
    },
    {
      name: "register",
      pattern: "register",
      component: () =>
        import("./pages/register/register").then(
          () => html`<auth-register></auth-register>`
        ),
    },
    {
      name: "password",
      pattern: "password/:id",
      component: () =>
        import("./pages/password/password").then(
          () => html`<auth-password></auth-password>`
        ),
    },
    {
      name: "email",
      pattern: "email",
      component: () =>
        import("./pages/email/email").then(
          () => html`<auth-email></auth-email>`
        ),
      guard: authGuard,
    },
    {
      name: "unsubscribe",
      pattern: "unsubscribe",
      component: () =>
        import("./pages/unsubscribe/unsubscribe").then(
          () => html`<auth-unsubscribe></auth-unsubscribe>`
        ),
    },
    {
      name: "about",
      pattern: "about",
      component: () =>
        import("./pages/about/about").then(
          () => html`<app-about></app-about>`
        ),
    },
    {
      name: "settings",
      pattern: "settings",
      component: () =>
        import("./pages/settings/settings").then(
          () => html`<app-settings></app-settings>`
        ),
      guard: authGuard,
    },
    {
      name: "terms",
      pattern: "terms",
      component: () =>
        import("./pages/terms/terms").then(
          () => html`<app-terms></app-terms>`
        ),
    },
    {
      name: "privacy",
      pattern: "privacy",
      component: () =>
        import("./pages/privacy/privacy").then(
          () => html`<app-privacy></app-privacy>`
        ),
    },
    {
      name: "not-found",
      pattern: "*",
      component: () =>
        import("./pages/404/404").then(() => html`<not-found></not-found>`),
    },
  ];