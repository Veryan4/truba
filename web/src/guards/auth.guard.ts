import { userService } from "../services";

export function authGuard() {
  const user = userService.state.getValue();
  if (user) {
    return Promise.resolve(true);
  }
  return userService
    .me()
    .then((user) => {
      if (user) {
        return Promise.resolve(true);
      }
      return Promise.reject("login");
    })
    .catch(() => Promise.reject("login"));
}
