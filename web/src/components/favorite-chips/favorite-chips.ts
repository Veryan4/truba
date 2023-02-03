import { LitElement, html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { classMap } from "lit-html/directives/class-map.js";
import { personalizationService } from "../../services";
import { chipStyles } from "../../styles";
import { FavoriteItem } from "../../models";
import { TranslationController } from "@veryan/lit-spa";
import { styles } from "./favorite-chips.styles";

@customElement("favorite-chips")
class FavoriteChipsComponent extends LitElement {
  static styles = [styles, chipStyles];

  private i18n = new TranslationController(this, "home");

  @property({ type: Array })
  favorite_items?: FavoriteItem[];

  @property({ type: String })
  type: string;

  constructor() {
    super();
  }

  render() {
    if (!this.favorite_items || this.favorite_items.length === 0) return "";
    return html` <div class="${this.type}">
      <div class="sub-title">${this.i18n.t(`home:${this.type}`)}</div>
      <div class="chip-set">
        ${this.favorite_items?.map((item) => {
          const classes = { selected: item.is_favorite };
          return html` <div
            class="md-chip ${classMap(classes)}"
            id="${item.identifier.replaceAll(" ", "_")}"
          >
            <div
              class="md-chip-label"
              @click="${(e: Event) => this.toggleFavorite(item, this.type)}"
            >
              ${item.value}
            </div>
          </div>`;
        })}
      </div>
    </div>`;
  }

  toggleFavorite(item: FavoriteItem | undefined, type: string) {
    if (!item) return;
    personalizationService.toggleFavorite(item, type).then(() => {
      const chipEl = this.renderRoot.querySelector(
        `#${item.identifier.replaceAll(" ", "_")}`
      )!;
      if (item.is_favorite) {
        chipEl.classList.add("selected");
      } else {
        chipEl.classList.remove("selected");
      }
    });
  }
}
