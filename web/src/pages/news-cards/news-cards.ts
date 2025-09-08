import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { NewsController } from "../../controllers";
import { styles } from "./news-cards.styles";
import { TranslationController } from "@veryan/lit-spa";
import "../../components/news-card/news-card.ts";
import "@veryan/lit-spa";

@customElement("news-cards")
class NewsCards extends LitElement {
  static styles = [styles];

  private news = new NewsController(this);
  private i18n = new TranslationController(this, { scope: "home" });

  render() {
    if (this.news.error) {
      return html` <div id="news-container" class="news-container">
        <div class="no-stories">${this.i18n.t("home.newsError")}</div>
      </div>`;
    }
    if (!this.news.value) {
      return html` <div class="loader-wrap">
        <lit-spa-loader .styleInfo=${{ width: "10rem" }}></lit-spa-loader>
      </div>`;
    }
    return this.news.value.length > 0
      ? html` <div id="news-container" class="news-container">
          <div class="flex-row">
            ${this.news.value.map(
              (article) => html`
                <div class="flex-item">
                  <news-card .article=${article}></news-card>
                </div>
              `,
            )}
          </div>
        </div>`
      : html` <div id="news-container" class="news-container">
          <div class="no-stories">${this.i18n.t("home.noNews")}</div>
        </div>`;
  }
}
