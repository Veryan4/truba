import { ReactiveControllerHost } from "lit";
import { newsService } from "../services/news.service";
import { Article } from "../models/article.model";

export class NewsController {
  private host: ReactiveControllerHost;
  value = newsService.newsStories();

  _changeUser = (e: CustomEvent) => {
    if (this.value !== newsService.newsStories()) {
      this.value = newsService.newsStories();
      this.host.requestUpdate();
    }
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected() {
    window.addEventListener(
      newsService.NEWS_EVENT,
      this._changeUser as EventListener
    );
  }

  hostDisconnected() {
    window.removeEventListener(
      newsService.NEWS_EVENT,
      this._changeUser as EventListener
    );
  }
}
