import { ReactiveControllerHost } from "lit";

export class DeviceController {
  private host: ReactiveControllerHost;
  width = window.innerWidth;
  isMobile = window.innerWidth < 760;

  _checkWidth = (e: Event) => {
    const throttle = 100;
    if (
      this.width < window.innerWidth - throttle ||
      this.width > window.innerWidth + throttle
    ) {
      this.width = window.innerWidth;
      this.isMobile = window.innerWidth < 760;
      this.host.requestUpdate();
    }
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);

    // re-renders the child web components
    setTimeout(() => host.requestUpdate(), 300);
  }

  hostConnected() {
    window.addEventListener("resize", this._checkWidth as EventListener);
  }

  hostDisconnected() {
    window.removeEventListener("resize", this._checkWidth as EventListener);
  }
}
