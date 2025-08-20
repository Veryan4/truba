import { ReactiveControllerHost } from "lit";
import { newsService } from "../services/news.service";
import { Article } from "../models/article.model";

export class NewsController {
  private host: ReactiveControllerHost;
  private unsubscribe?: () => boolean;
  value = newsService.state.getValue();

  _changeNews = (stories: Article[]) => {
    this.value = stories;
    this.host.requestUpdate();
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected() {
    this.unsubscribe = newsService.state.subscribe(this._changeNews);
  }

  hostDisconnected() {
    this.unsubscribe?.();
  }
}
