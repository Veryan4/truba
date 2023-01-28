import { User } from "./user.model";

export class IdValuePair {
  id: string;
  value: string;
}

export class FavoriteItem {
  _id?: string;
  id?: string;
  user_id?: string;
  identifier: string;
  value: string;
  is_favorite = false;
  is_deleted = false;
  is_recommended = false;
  is_added = false;
  relevancy_rate = 0.0;
  language: string;

  constructor(idValuePair: IdValuePair, user: User) {
    this.user_id = user.id;
    this.identifier = idValuePair.id;
    this.value = idValuePair.value;
    this.language = user.language;
  }
}
