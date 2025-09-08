import { ReactiveControllerHost } from "lit";
import { newsService } from "../services/news.service";
import { Article } from "../models/article.model";

export class NewsController {
  private host: ReactiveControllerHost;
  private unsubscribe?: (() => boolean)[] = [];
  value = newsService.state.getValue();
  error: Error | undefined = newsService.errorState.getValue();

  _changeNews = (stories: Article[]) => {
    this.value = stories;
    this.error = undefined;
    this.host.requestUpdate();
  };

  _newsError = (error: Error) => {
    this.value = [];
    this.error = error;
    this.host.requestUpdate();
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected() {
    this.unsubscribe = [
      newsService.state.subscribe(this._changeNews),
      newsService.errorState.subscribe(this._newsError),
    ];
  }

  hostDisconnected() {
    this.unsubscribe?.forEach((u) => u());
  }
}
