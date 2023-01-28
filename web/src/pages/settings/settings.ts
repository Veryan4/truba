import { LitElement, html } from "lit";
import { customElement, state, query } from "lit/decorators.js";
import { classMap } from "lit-html/directives/class-map.js";
import { TranslationController } from "../../controllers";
import { userService, personalizationService } from "../../services";
import { Recommendation, FavoriteItem, IdValuePair } from "../../models";
import { textFieldStyles, iconButtonStyles, chipStyles } from "../../styles";
import { styles } from "./settings.styles";

import "@material/mwc-formfield";
import "@material/mwc-textfield";

@customElement("app-settings")
class Settings extends LitElement {
  static styles = [styles, textFieldStyles, chipStyles, iconButtonStyles];

  private i18n = new TranslationController(this);

  @state()
  availableKeywords: FavoriteItem[];

  @state()
  availableEntities: FavoriteItem[];

  @state()
  availableSources: FavoriteItem[];

  @state()
  availableAuthors: FavoriteItem[];

  @query("#keywords")
  keywordInput: HTMLInputElement;

  constructor() {
    super();
    const user = userService.getUser();
    if (user) {
      personalizationService
        .getPersonalization(user)
        .then((personalization) => {
          this.initAvailableItems(personalization);
        });
    } else {
      userService
        .me()
        .then((user) => {
          return personalizationService.getPersonalization(user);
        })
        .then((personalization) => {
          this.initAvailableItems(personalization);
        });
    }
  }

  render() {
    return html`
      <div class="settings-container">
        <div class="settings-wrap">
          ${this.createKeywordChips()} ${this.createEntityChips()}
          ${this.createSourcesChips()} ${this.createAuthorsChips()}
        </div>
      </div>
    `;
  }

  private createKeywordChips() {
    if (!this.availableKeywords || this.availableKeywords.length === 0)
      return "";
    return html` <div class="settings-sub-title">
        ${this.i18n.t("home.keyword")}
      </div>
      <div class="settings-item">
        <div class="chip-set">
          ${this.availableKeywords?.map((keyword, i) => {
            const classes = { selected: keyword.is_favorite };
            return html` <div
              class="md-chip ${classMap(classes)}"
              id="keyword-${keyword.identifier.replaceAll(" ", "_")}"
            >
              <div
                class="md-chip-label"
                @click="${(e: Event) => this.toggle(keyword, "keyword")}"
              >
                ${keyword.value}
              </div>
              <i
                class="material-icons mdc-icon-button__icon"
                @click="${(e: Event) =>
                  this.removeFavorite(keyword, "keyword")}"
                >close</i
              >
            </div>`;
          })}
        </div>
        <mwc-textfield
          id="keywords"
          type="text"
          name="keywords"
          @submit=${this.addKeyword}
        ></mwc-textfield>
      </div>`;
  }

  private createEntityChips() {
    if (!this.availableEntities || this.availableEntities.length === 0)
      return "";
    return html` <div class="settings-sub-title">
        ${this.i18n.t("home.entity")}
      </div>
      <div class="settings-item">
        <div class="chip-set">
          ${this.availableEntities?.map((entity) => {
            const classes = { selected: entity.is_favorite };
            return html` <div
              class="md-chip ${classMap(classes)}"
              id="entity-${entity.identifier.replaceAll(" ", "_")}"
            >
              <div
                class="md-chip-label"
                @click="${(e: Event) => this.toggle(entity, "entity")}"
              >
                ${entity.value}
              </div>
              <i
                class="material-icons mdc-icon-button__icon"
                @click="${(e: Event) => this.removeFavorite(entity, "entity")}"
                >close</i
              >
            </div>`;
          })}
        </div>
      </div>`;
  }

  private createSourcesChips() {
    if (!this.availableSources || this.availableSources.length === 0) return "";
    return html` <div class="settings-sub-title">
        ${this.i18n.t("home.source")}s
      </div>
      <div class="settings-item">
        <div class="chip-set">
          ${this.availableSources?.map((source) => {
            const classes = { selected: source.is_favorite };
            return html` <div
              class="md-chip ${classMap(classes)}"
              id="source-${source.identifier.replaceAll(" ", "_")}"
            >
              <div
                class="md-chip-label"
                @click="${(e: Event) => this.toggle(source, "source")}"
              >
                ${source.value}
              </div>
              <i
                class="material-icons mdc-icon-button__icon"
                @click="${(e: Event) => this.removeFavorite(source, "source")}"
                >close</i
              >
            </div>`;
          })}
        </div>
      </div>`;
  }

  private createAuthorsChips() {
    if (!this.availableAuthors || this.availableAuthors.length === 0) return "";
    return html` <div class="settings-sub-title">
        ${this.i18n.t("home.author")}s
      </div>
      <div class="settings-item">
        <div class="chip-set">
          ${this.availableAuthors?.map((author) => {
            const classes = { selected: author.is_favorite };
            return html` <div
              class="md-chip ${classMap(classes)}"
              id="author-${author.identifier.replaceAll(" ", "_")}"
            >
              <div
                class="md-chip-label"
                @click="${(e: Event) => this.toggle(author, "author")}"
              >
                ${author.value}
              </div>
              <i
                class="material-icons mdc-icon-button__icon"
                @click="${(e: Event) => this.removeFavorite(author, "author")}"
                >close</i
              >
            </div>`;
          })}
        </div>
      </div>`;
  }

  initAvailableItems(personalization: Recommendation) {
    this.availableKeywords = this.setAvailableItems(
      personalization.favorite_items.favorite_keywords,
      personalization.recommended_items.favorite_keywords
    );

    this.availableEntities = this.setAvailableItems(
      personalization.favorite_items.favorite_entities,
      personalization.recommended_items.favorite_entities
    );

    this.availableSources = this.setAvailableItems(
      personalization.favorite_items.favorite_sources,
      personalization.recommended_items.favorite_sources
    );

    this.availableAuthors = this.setAvailableItems(
      personalization.favorite_items.favorite_authors,
      personalization.recommended_items.favorite_authors
    );
  }

  setAvailableItems(
    favorite_items: FavoriteItem[],
    recommended_items: FavoriteItem[]
  ): FavoriteItem[] {
    const recommended = recommended_items.filter(
      (rec) => !favorite_items.some((fav) => fav.identifier === rec.identifier)
    );
    return favorite_items.concat(recommended);
  }

  toggle(item: FavoriteItem, type: string): void {
    personalizationService.toggleFavorite(item, type).then(() => {
      const chipEl = this.renderRoot.querySelector(
        `#${type + "-" + item.identifier.replaceAll(" ", "_")}`
      )!;
      if (item.is_favorite) {
        chipEl.classList.add("selected");
      } else {
        chipEl.classList.remove("selected");
      }
    });
  }

  removeFavorite(item: FavoriteItem, type: string): void {
    personalizationService.removeFavorite(item, type).then(() => {
      switch (type) {
        case "keyword":
          this.availableKeywords = this.availableKeywords.filter(
            (x) => x.identifier !== item.identifier
          );
          break;
        case "entity":
          this.availableEntities = this.availableEntities.filter(
            (x) => x.identifier !== item.identifier
          );
          break;
        case "source":
          this.availableSources = this.availableSources.filter(
            (x) => x.identifier !== item.identifier
          );
          break;
        case "author":
          this.availableAuthors = this.availableAuthors.filter(
            (x) => x.identifier !== item.identifier
          );
          break;
      }
      const chipEl = this.renderRoot.querySelector(
        `#${type + "-" + item.identifier.replaceAll(" ", "_")}`
      )!;
      chipEl.remove();
    });
  }

  addKeyword(event: InputEvent): void {
    const value = event.data;

    if (value) {
      const pair: IdValuePair = {
        id: value!.trim(),
        value: value!.trim(),
      };
      const item = new FavoriteItem(pair, userService.getUser()!);
      item.is_favorite = true;
      item.is_added = true;
      this.availableKeywords.push(item);
    }

    this.keywordInput.value = "";
  }
}
