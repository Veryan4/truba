import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { NewsController } from "../../controllers";
import { styles } from "./news-cards.styles";
import "../../components/news-card/news-card.ts";

@customElement("news-cards")
class NewsCards extends LitElement {
  static styles = [styles];

  private news = new NewsController(this);

  render() {
    return this.news.value && this.news.value.length > 0
      ? html` <div id="news-container" class="news-container">
          <div class="flex-row">
            ${this.news.value.map(
              (article) => html`
                <div class="flex-item">
                  <news-card .article=${article}></news-card>
                </div>
              `
            )}
          </div>
        </div>`
      : html``;
  }
}
