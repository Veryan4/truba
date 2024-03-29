import { ReactiveControllerHost } from "lit";
import { userService } from "../services/user.service";

export class UserController {
  private host: ReactiveControllerHost;
  value = userService.getUser();

  _changeUser = (e: CustomEvent) => {
    if (this.value !== userService.getUser()) {
      this.value = userService.getUser();
      this.host.requestUpdate();
    }
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected() {
    window.addEventListener(
      userService.USER_EVENT,
      this._changeUser as EventListener
    );
  }

  hostDisconnected() {
    window.removeEventListener(
      userService.USER_EVENT,
      this._changeUser as EventListener
    );
  }
}
