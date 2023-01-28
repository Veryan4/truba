import { AppConfig } from "./models/app-config.model";

export const appConfig: AppConfig = {
  backendApi: import.meta.env.VITE_BACKEND_API as string,
  backendSocket: import.meta.env.VITE_BACKEND_SOCKET as string,
  googleAuthClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID as string,
  publicVapid: import.meta.env.VITE_PUBLIC_VAPID as string,
};
