import { ReactiveControllerHost } from "lit";
import { userService } from "../services/user.service";
import { userStore } from "../services/user.store";

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
      userStore.USER_EVENT,
      this._changeUser as EventListener
    );
  }

  hostDisconnected() {
    window.removeEventListener(
      userStore.USER_EVENT,
      this._changeUser as EventListener
    );
  }
}
