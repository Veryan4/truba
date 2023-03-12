import { LitElement, html } from "lit";
import { classMap } from "lit/directives/class-map";
import { customElement, property, query, queryAsync } from "lit/decorators.js";
import { TutorialController } from "../../controllers/tutorial.controller";
import { tutorialService } from "../../services/tutorial.service";
import { styles } from "./tutorial.styles";


// stripped this for parts: https://github.com/floating-ui/floating-ui
@customElement("lit-spa-tutorial")
class TutorialComponent extends LitElement {
  static styles = [styles];

  @property({ type: String })
  frame: string;

  @query("#reference")
  referenceElement: HTMLElement;

  @queryAsync("#floating")
  floatingElement: Promise<HTMLElement>;

  
  private tutorial = new TutorialController(this);

  private tutorialInitialized = false;
   

  render() {
    return html`
      <div id="reference">
        <slot name="reference"></slot>
      </div>
      <div id="floating" class="${classMap({hide: this.tutorial.currentFrame !== this.frame})}">
        <slot name="floating"></slot>
        <div class="tutorial-buttons">
          <button
            class="${classMap({hide: this.tutorial.currentFrameIndex === 0})}"
            dense
            label=${"Previous"}
            @click="${() => tutorialService.nextTutorialFrame(this.tutorial.currentFrameIndex - 1)}"
          ></button>
          <button
            class="${classMap({hide: this.tutorial.currentFrameIndex === (this.tutorial.tutorialFrames.length -1)})}"
            dense
            label=${"Next"}
            @click="${() => tutorialService.nextTutorialFrame(this.tutorial.currentFrameIndex + 1)}"
          ></button>
        </div>
      </div>
    `
  }

  async connectedCallback() {
    super.connectedCallback();

    if (!this.tutorialInitialized) {
      await this.initTutorial();
      this.tutorialInitialized = true;
    }
  }

  async initTutorial(strategy = 'absolute'){
    const floating = await this.floatingElement;
    const position = this.computePosition(this.referenceElement, floating, 'right');
    Object.assign(floating.style, {
      position: strategy,
      left: `${position.x}px`,
      top: `${position.y}px`,
    });
  }

  computePosition(reference:HTMLElement, floating:HTMLElement, placement =' bottom', strategy = 'absolute') {
    const isRTL = getComputedStyle(floating).direction === 'rtl'
    const rects = this.getElementRects(reference, floating, strategy);
    const {x, y} = this.computeCoordsFromPlacement(rects, placement, isRTL);

    return {
      x,
      y,
      placement,
    };
  }

  computeCoordsFromPlacement(
    rects: {[key: string]:{width: number, height: number, x: number, y: number}},
    placement: string,
    rtl?: boolean
  ): {x: number, y:number} {
    const {reference, floating} = rects;
    const commonX = reference.x + reference.width / 2 - floating.width / 2;
    const commonY = reference.y + reference.height / 2 - floating.height / 2;
    const side = placement.split('-')[0];
    const alignment = placement.split('-')[1];
    const mainAxis = ['top', 'bottom'].includes(side) ? 'x' : 'y';
    const length = mainAxis === 'y' ? 'height' : 'width';
    const commonAlign = reference[length] / 2 - floating[length] / 2;
    const isVertical = mainAxis === 'x';
  
    let coords;
    switch (side) {
      case 'top':
        coords = {x: commonX, y: reference.y - floating.height};
        break;
      case 'bottom':
        coords = {x: commonX, y: reference.y + reference.height};
        break;
      case 'right':
        coords = {x: reference.x + reference.width, y: commonY};
        break;
      case 'left':
        coords = {x: reference.x - floating.width, y: commonY};
        break;
      default:
        coords = {x: reference.x, y: reference.y};
    }
  
    switch (alignment) {
      case 'start':
        coords[mainAxis] -= commonAlign * (rtl && isVertical ? -1 : 1);
        break;
      case 'end':
        coords[mainAxis] += commonAlign * (rtl && isVertical ? -1 : 1);
        break;
      default:
    }
  
    return coords;
  }

  getElementRects(reference: HTMLElement, floating: HTMLElement, strategy: string){
    return {
      reference: this.getRectRelativeToOffsetParent(
        reference,
        floating.offsetParent as HTMLElement,
        strategy
      ),
      floating: {width: floating.offsetWidth, height: floating.offsetHeight, x: 0, y: 0},
    }
  }

  getRectRelativeToOffsetParent(
    element: HTMLElement,
    offsetParent: HTMLElement,
    strategy: string
  ) {
    const rect = this.getElementsBoundingClientRect(
      element,
      this.isScaled(offsetParent),
      strategy === 'fixed'
    );
  
    const offsets = {x: 0, y: 0};
    const offsetRect = this.getElementsBoundingClientRect(offsetParent, true);
    offsets.x = offsetRect.x + offsetParent.clientLeft;
    offsets.y = offsetRect.y + offsetParent.clientTop;

    return {
      x: rect.left + offsetParent.scrollLeft - offsets.x,
      y: rect.top + offsetParent.scrollTop - offsets.y,
      width: rect.width,
      height: rect.height,
    };
  }

  getElementsBoundingClientRect(
    element: HTMLElement,
    includeScale = false,
    isFixedStrategy = false
  ) {
    const clientRect = element.getBoundingClientRect();
  
    let scaleX = 1;
    let scaleY = 1;
  
    if (includeScale) {
      scaleX =
        element.offsetWidth > 0
          ? Math.round(clientRect.width) / element.offsetWidth || 1
          : 1;
      scaleY =
        element.offsetHeight > 0
          ? Math.round(clientRect.height) / element.offsetHeight || 1
          : 1;
    }
  
    const addVisualOffsets = !this.isLayoutViewport() && isFixedStrategy;
    const x =
      (clientRect.left +
        (addVisualOffsets ? window.visualViewport?.offsetLeft ?? 0 : 0)) /
      scaleX;
    const y =
      (clientRect.top +
        (addVisualOffsets ? window.visualViewport?.offsetTop ?? 0 : 0)) /
      scaleY;
    const width = clientRect.width / scaleX;
    const height = clientRect.height / scaleY;
  
    return {
      width,
      height,
      top: y,
      right: x + width,
      bottom: y + height,
      left: x,
      x,
      y,
    };
  }

  isScaled(element: HTMLElement): boolean {
    const rect = this.getElementsBoundingClientRect(element);
    return (
      Math.round(rect.width) !== element.offsetWidth ||
      Math.round(rect.height) !== element.offsetHeight
    );
  }

  isLayoutViewport(): boolean {
    // Not Safari
    return !/^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  }

  isOverflowElement(element: HTMLElement): boolean {
    // Firefox wants us to check `-x` and `-y` variations as well
    const {overflow, overflowX, overflowY, display} = getComputedStyle(element);
    return (
      /auto|scroll|overlay|hidden/.test(overflow + overflowY + overflowX) &&
      !['inline', 'contents'].includes(display)
    );
  }
  
}


declare global {
  interface HTMLElementTagNameMap {
    "lit-spa-tutorial": TutorialComponent;
  }
}
