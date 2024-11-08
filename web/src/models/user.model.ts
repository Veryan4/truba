export class User {
  _id: string;
  user_id: string;
  email: string;
  username: string;
  language: string;
  is_admin: boolean;
  is_personalized: boolean;
  has_personalization: boolean;
  rated_count: number;
  subscription: PushSubscription;

  constructor(user: any) {
    this._id = user._id;
    this.user_id = user.user_id;
    this.email = user.email;
    this.username = user.username;
    this.language = user.language;
    this.is_admin = user.is_admin;
    this.is_personalized = user.is_personalized;
    this.has_personalization = user.has_personalization;
    this.rated_count = user.rated_count;
    this.subscription = user.subscription;
  }
}
