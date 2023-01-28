import { personalizationService } from "./personalization.service";
import { Article } from "../models/article.model";
import type { User } from "../models/user.model";
import type { Recommendation } from "../models/personalization.model";
import { FavoriteItem, IdValuePair } from "../models/favorite-item.model";

import { appConfig } from "../app.config";
import { httpService } from "./http.service";
import { translateService } from "./translate.service";

let newsStories: Article[] = [];
const seenStoryIds = new Set<string>();
const NEWS_EVENT = "news-update";

export const newsService = {
  newsStories: () => newsStories,
  seenStoryIds,
  getNews,
  getSingleArticle,
  getRandomNewsImage,
  changeNewsStories,
  NEWS_EVENT,
};

function changeNewsStories(
  news: Article[],
  user: User | null,
  recommendations: Recommendation | null = null,
  isSingleArticle = false
): void {
  news = news.map((article) => {
    article = new Article(article);
    if (article && !article.image) {
      article.image = getRandomNewsImage();
    }
    if (!user) {
      return article;
    }
    const favKeywords =
      recommendations && recommendations.favorite_items
        ? recommendations.favorite_items.favorite_keywords
        : null;
    article.favorite_keywords = article.keywords.map((keywordPair) => {
      return getFavoriteItem(keywordPair, user, favKeywords);
    });
    const favEntities =
      recommendations && recommendations.favorite_items
        ? recommendations.favorite_items.favorite_entities
        : null;
    article.favorite_entities = article.entities.map((entityPair) => {
      return getFavoriteItem(entityPair, user, favEntities);
    });
    const favSources =
      recommendations && recommendations.favorite_items
        ? recommendations.favorite_items.favorite_sources
        : null;
    article.favorite_source = getFavoriteItem(article.source, user, favSources);
    if (!article.author) return article;
    const favAuthors =
      recommendations && recommendations.favorite_items
        ? recommendations.favorite_items.favorite_authors
        : null;
    article.favorite_author = getFavoriteItem(article.author, user, favAuthors);
    return article;
  });
  if (isSingleArticle) {
    news = newsStories.concat(news);
  }
  newsStories = news;
  newsStories.forEach((x) => seenStoryIds.add(x.story_id));
  window.dispatchEvent(new CustomEvent(NEWS_EVENT));
}

async function getNews(user: User | null): Promise<void> {
  if (user && user.is_personalized) {
    return Promise.all([
      getRecommendedArticles(user),
      personalizationService.getPersonalization(user),
    ]).then(([articles, recommendations]) => {
      return changeNewsStories(articles, user, recommendations);
    });
  } else if (user && !user.is_personalized) {
    return Promise.all([
      getPublicArticles(),
      personalizationService.getPersonalization(user),
    ]).then(([articles, recommendations]) => {
      return changeNewsStories(articles, user, recommendations);
    });
  } else {
    return getPublicArticles().then((articles) => {
      return changeNewsStories(articles, null);
    });
  }
}

function getRecommendedArticles(user: User): Promise<Article[]> {
  return httpService.get<Article[]>(
    appConfig.backendApi + "recommended-news/" + user.language
  );
}

function getPublicArticles(): Promise<Article[]> {
  const language = translateService.getStoredLanguage();
  return httpService.get<Article[]>(appConfig.backendApi + "news/" + language);
}

async function getSingleArticle(
  user: User | null,
  ratedId: string
): Promise<Article[]> {
  const postData = [...seenStoryIds];
  let lang = "en";
  if (user) lang = user.language;
  await httpService
    .post<Article>(appConfig.backendApi + "single-article/" + lang, postData)
    .then(delay(700))
    .then((article: Article) => {
      newsStories = newsStories.filter((x) => x.story_id !== ratedId);
      return changeNewsStories(
        [article],
        user,
        personalizationService.personalization(),
        true
      );
    });
  return newsStories;
}

function getFavoriteItem(
  idValuePair: IdValuePair,
  user: User,
  favoriteItems: FavoriteItem[] | null = null
): FavoriteItem {
  if (!favoriteItems) {
    return new FavoriteItem(idValuePair, user);
  }
  const found = favoriteItems.find((fav) => fav.identifier === idValuePair.id);
  return found ? found : new FavoriteItem(idValuePair, user);
}

export function getRandomNewsImage(): string {
  const imgArr = [
    "1.jpg",
    "2.jpg",
    "3.jpg",
    "4.jpg",
    "5.jpg",
    "6.jpg",
    "7.jpg",
    "8.jpg",
    "9.jpg",
    "10.jpg",
    "11.jpg",
    "12.jpg",
  ];
  const path = "./newspapers/";
  const num = Math.floor(Math.random() * imgArr.length);
  const img = imgArr[num];
  return path + img;
}

function delay<T>(ms: number): (x: T) => Promise<T> {
  return function (x: T) {
    return new Promise<T>((resolve) => setTimeout(() => resolve(x), ms));
  };
}
