import { ReactiveControllerHost } from "lit";
import { userService } from "../services/user.service";
import { User } from "../models";

export class UserController {
  private host: ReactiveControllerHost;
  private unsubscribe?: () => boolean;
  value = userService.state.getValue();

  _changeUser = (user: User | null) => {
    this.value = user;
    this.host.requestUpdate();
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected() {
    this.unsubscribe = userService.state.subscribe(this._changeUser);
  }

  hostDisconnected() {
    this.unsubscribe?.();
  }
}
