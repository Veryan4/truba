import { httpService } from "@veryan/lit-spa";
import { appConfig } from "../app.config";
import { newsService } from "./news.service";
import { userService } from "./user.service";

let socket: WebSocket;

export const webSocketService = {
    closeSocket
}

async function openSocket() {
    const token = httpService.getAuthToken();
    if (!token) return;
    socket = await new WebSocket(appConfig.backendSocket, token);
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (Array.isArray(data)) {
        const user = userService.getUser();
        if (user && user.language === "en") {
            newsService.changeNewsStories(data, user);
        } else {
            newsService.getNews(user);
        }
        }
    };
}

function closeSocket() {
    socket?.close();
}

window.addEventListener(
    userService.USER_EVENT,
    () => {
        const user = userService.getUser();
        if (user && !socket) {
            openSocket();
        }
        if (!user && socket) {
            closeSocket();
        }
    }
);