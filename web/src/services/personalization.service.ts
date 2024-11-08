import { userService } from "./user.service";
import type { FavoriteItem, FeedbackType, Recommendation } from "../models";
import type { User } from "../models/user.model";
import { appConfig } from "../app.config";
import { httpService } from "@veryan/lit-spa";

let personalization: Recommendation | null;

export const personalizationService = {
  personalization: () => personalization,
  getPersonalization,
  postUpdatePersonalization,
  postFeedback,
  toggleFavorite,
  removeFavorite,
  addFavorite
};

function getPersonalization(user: User): Promise<Recommendation> {
  const lang = user.language ? user.language : "en";
  return httpService
    .get<Recommendation>(appConfig.backendApi + "user/info/" + lang)
    .then((pers) => {
      personalization = pers;
      return personalization;
    });
}

function postUpdatePersonalization(
  type: string,
  favoriteItem: FavoriteItem,
): Promise<any> {
  return httpService.post<any>(
    appConfig.backendApi + "favorite/" + type,
    favoriteItem,
  );
}

function postFeedback(
  searchTerm: string,
  storyId: string,
  feedBackType: FeedbackType,
): void {
  const currentUser = userService.getUser();
  if (!currentUser) return;
  const postData = {
    user_id: currentUser.user_id,
    search_term: searchTerm,
    story_id: storyId,
    feedback_type: feedBackType,
  };
  httpService.post<any>(appConfig.backendApi + "feedback", postData);
}

function toggleFavorite(item: FavoriteItem, type: string): Promise<any> {
  if (item.relevancy_rate < 0.0) {
    item.relevancy_rate = 1.0;
  }
  item.is_favorite = !item.is_favorite;
  if (!item.is_favorite) {
    item.relevancy_rate = 0.0;
  }
  const u = userService.getUser();
  if (u) item.user_id = u.user_id;
  return postUpdatePersonalization(type, item).catch((err) => {
    item.is_favorite = !item.is_favorite;
  });
}

function removeFavorite(item: FavoriteItem, type: string): Promise<any> {
  item.is_favorite = false;
  item.is_deleted = true;
  item.relevancy_rate = 0.0;
  return postUpdatePersonalization(type, item).catch((err) => {
    item.is_favorite = !item.is_favorite;
  });
}

function addFavorite(item: FavoriteItem, type: string): Promise<any> {
  item.is_favorite = true;
  item.is_added = true;
  item.relevancy_rate = 1.0;
  return postUpdatePersonalization(type, item).catch((err) => {
    item.is_favorite = !item.is_favorite;
  });
}
