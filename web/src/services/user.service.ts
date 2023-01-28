import { User } from "../models/user.model";
import { userStore } from "./user.store";
import { appConfig } from "../app.config";
import { httpService } from "./http.service";
import { tokenService } from "./token.service";
import { translateService } from "./translate.service";

export const userService = {
  getUser: () => userStore.getUser(),
  login,
  register,
  forgotPassword,
  resetPassword,
  updateUser,
  me,
  socialLogin,
  signOut,
  unsubscribeEmail,
  confirmEmail
};

function setUser(newUser: User | null): User | null {
  if (!newUser) {
    userStore.setUser(null);
    return null;
  }
  const user = new User(newUser);
  userStore.setUser(user);
  return user;
}

function login(email: string, password: string): Promise<User | null> {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);
  return httpService
    .post(appConfig.backendApi + "token", formData)
    .then((data: any) => {
      tokenService.setToken(data.token);
      subscribeUser(data.user);
      return setUser(data.user);
    });
}

function register(
  username: string,
  email: string,
  password: string
): Promise<User | null> {
  return httpService
    .post(appConfig.backendApi + "users", {
      username,
      email,
      password,
      terms_consent: new Date().toISOString(),
    })
    .then((data: any) => {
      tokenService.setToken(data.token);
      return setUser(data.user);
    });
}

function forgotPassword(email: string): Promise<any> {
  return httpService.post(appConfig.backendApi + "forgot_password", {
    email,
  });
}

function resetPassword(
  token: string,
  newPassword: string
): Promise<User | null> {
  return httpService
    .post(appConfig.backendApi + "reset_password", {
      token,
      new_password: newPassword,
    })
    .then((data: any) => {
      tokenService.setToken(data.token);
      return setUser(data.user);
    });
}

function updateUser(user: any): Promise<User | null> {
  const lang = user.language
    ? user.language
    : translateService.getStoredLanguage();
  return httpService
    .put(appConfig.backendApi + "users", {
      id: user.id,
      user_id: user.user_id,
      username: user.username,
      email: user.email,
      is_personalized: user.is_personalized,
      language: lang,
      has_personalization: user.has_personalization,
      rated_count: user.rated_count,
      subscription: user.subscription,
    })
    .then((data: any) => {
      return setUser(data.user);
    });
}

function me(): Promise<any> {
  const tokenVal = tokenService.getToken();
  if (!tokenVal) {
    setUser(null);
    return Promise.reject(Error("No token found."));
  }
  return httpService
    .get(appConfig.backendApi + "users/me")
    .then((data: any) => {
      return setUser(data.user);
    })
    .catch((_) => {
      setUser(null);
      return Error("Failed to get user with token");
    });
}

function confirmEmail(): Promise<any> {
  const tokenVal = tokenService.getToken();
  if (!tokenVal) {
    setUser(null);
    return Promise.reject(Error("No token found."));
  }
  return httpService
    .get(appConfig.backendApi + "users/email")
    .then((data: any) => {
      return setUser(data.user);
    })
    .catch((_) => {
      setUser(null);
      return Error("Failed to confirm Email");
    });
}

function socialLogin(idToken: string): Promise<User | null> {
  return httpService
    .get(appConfig.backendApi + "google/" + idToken)
    .then((data: any) => {
      tokenService.setToken(data.token);
      subscribeUser(data.user);
      return setUser(data.user);
    });
}

async function signOut(): Promise<void> {
  tokenService.removeToken();
  await setUser(null);
  if ((window as any).gapi) {
    const auth2 = (window as any).gapi.auth2.getAuthInstance();
    const currentUser = auth2.currentUser.get();
    if (currentUser) {
      await currentUser.disconnect();
    }
    await auth2.signOut();
    await auth2.disconnect();
  }
}

function unsubscribeEmail(userEmail: string): Promise<boolean> {
  return httpService
    .get(appConfig.backendApi + `unsubscribe/${encodeURI(userEmail)}`)
    .then((data: any) => {
      return data.result;
    });
}

function subscribeUser(user: User) {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.ready.then((reg) => {
      reg.pushManager
        .subscribe({
          userVisibleOnly: true,
        })
        .then((sub) => {
          user.subscription = sub;
          updateUser(user);
        })
        .catch((e) => {
          if (Notification.permission === "denied") {
            console.warn("Permission for notifications was denied");
          } else {
            console.error("Unable to subscribe to push", e);
          }
        });
    });
  }
}
