const TUTORIAL_EVENT = "tutorial";
let tutorialFrames = ['initial'];

export const tutorialService = { newTutorial, nextTutorialFrame, TUTORIAL_EVENT };

function newTutorial(frames: string[]): void {
  tutorialFrames = frames;
  window.dispatchEvent(
    new CustomEvent(TUTORIAL_EVENT, {
      detail: {
        currentFrameIndex: 0,
        frames: tutorialFrames
      },
    })
  );
}

function nextTutorialFrame(frameIndex?: number): void {
  window.dispatchEvent(
    new CustomEvent(TUTORIAL_EVENT, {
      detail: {
        currentFrameIndex: frameIndex,
        frames:tutorialFrames
      },
    })
  );
}
