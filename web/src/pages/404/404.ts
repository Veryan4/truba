import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";
import { TranslationController } from "@veryan/lit-spa";

@customElement("not-found")
class NotFound extends LitElement {
  static styles = [
    css`
      html,
      body {
        font-family: var(--font-family);
        font-weight: 100;
        height: 100vh;
        margin: 0;
      }
      .full-height {
        height: 100vh;
      }
      .flex-center {
        align-items: center;
        display: flex;
        justify-content: center;
      }
      .position-ref {
        position: relative;
      }
      .code {
        border-right: 2px solid;
        font-size: 26px;
        padding: 0 10px 0 15px;
        text-align: center;
      }
      .message {
        font-size: 18px;
        text-align: center;
        padding: 10px;
      }
    `,
  ];

  private i18n = new TranslationController(this);

  render() {
    return html`
      <div class="flex-center position-ref full-height">
        <div class="code">404</div>
        <div class="message">Not Found</div>
      </div>
    `;
  }
}
