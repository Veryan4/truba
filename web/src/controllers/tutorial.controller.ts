import { ReactiveControllerHost} from "lit";
import "../components/tutorial/tutorial";
import { tutorialService } from "../services/tutorial.service";

export class TutorialController {
  private host: ReactiveControllerHost;

  tutorialFrames: string[];
  currentFrameIndex: number
  currentFrame: string;

  _newTutorial = (e: CustomEvent) => {
    const tutorialFrames: string[] = e.detail.frames;
    const currentFrameIndex: number = e.detail.currentFrameIndex;
    if (this.tutorialFrames !== tutorialFrames || this.currentFrameIndex !== currentFrameIndex) {
      this.tutorialFrames = tutorialFrames;
      this.currentFrameIndex = currentFrameIndex;
      this.currentFrame = tutorialFrames[currentFrameIndex];
      this.host.requestUpdate();
    }
  };

  constructor(host: ReactiveControllerHost) {
    this.host = host;
    host.addController(this);
  }

  hostConnected(): void {
    window.addEventListener(
      tutorialService.TUTORIAL_EVENT,
      this._newTutorial as EventListener
    );
  }

  hostDisconnected(): void {
    window.removeEventListener(
      tutorialService.TUTORIAL_EVENT,
      this._newTutorial as EventListener
    );
  }
}
