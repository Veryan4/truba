import { User } from "../models/user.model";

const USER_EVENT = "user-update";

let user: User | null;

function setUser(nextUser: User | null) {
  user = nextUser;
  window.dispatchEvent(new CustomEvent(USER_EVENT));
}

function getUser(): User | null {
  return user;
}

export const userStore = { setUser, getUser, USER_EVENT };
