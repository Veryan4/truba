import { FavoriteItem, IdValuePair } from "./favorite-item.model";

export class Article {
  story_id: string;
  image: string;
  title: string;
  shortTitle: string;
  url: string;
  published_at: string;
  author: IdValuePair;
  source: IdValuePair;
  keywords: IdValuePair[] = [];
  entities: IdValuePair[] = [];
  favorite_author?: FavoriteItem;
  favorite_source?: FavoriteItem;
  favorite_keywords?: FavoriteItem[];
  favorite_entities?: FavoriteItem[];
  is_flipped = false;

  constructor(article: any) {
    this.story_id = article.story_id;
    // upgrade to https to make to avoid Mixed Content
    if (article.image) {
      if (article.image.startsWith("http:")) {
        article.image = article.image.substring(4);
        article.image = "https" + article.image;
      }
      this.image = article.image;
    }
    this.title = article.title;
    this.shortTitle = this.truncate(article.title, 80);
    this.source = {
      id: article.source_id,
      value: article.source,
    };
    this.url = article.url;
    this.published_at = article.published_at;
    if (
      article.author &&
      article.author !== article.source &&
      article.author.trim() !== "" &&
      !article.author.includes("</")
    ) {
      this.author = {
        id: article.author_id,
        value: article.author,
      };
    }
    if (article.keywords) {
      this.keywords = article.keywords.map((keyword: string) => {
        const item: IdValuePair = {
          id: keyword,
          value: keyword,
        };
        return item;
      });
    }
    if (article.entities) {
      for (let i = 0; i < article.entities.length; i++) {
        const entity: IdValuePair = {
          id: article.entity_links[i],
          value: article.entities[i],
        };
        this.entities.push(entity);
      }
    }
  }

  private truncate(str: string, n: number) {
    if (str.length <= n) {
      return str;
    }
    const subString = str.substr(0, n - 1);
    return subString.substr(0, subString.lastIndexOf(" ")) + "...";
  }
}
