import { precacheAndRoute, cleanupOutdatedCaches } from "workbox-precaching";
import { clientsClaim } from "workbox-core";

declare let self: ServiceWorkerGlobalScope;
declare let clients: Clients;

// self.__WB_MANIFEST is default injection point
self.skipWaiting();
clientsClaim();
cleanupOutdatedCaches();
precacheAndRoute(self.__WB_MANIFEST);

self.addEventListener("notificationclick", function (e) {
  const notification = e.notification;
  const action = e.action;

  if (action === "close") {
    notification.close();
  } else {
    clients.openWindow("https://truba.news");
    notification.close();
  }
});
