import { css } from "lit";

export const styles = css`
  .about-container {
    display: flex;
    justify-content: center;
    width: 100vw;
    line-height: 1.8;
    font-family: var(--font-family);
  }
  .about-wrap {
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
    max-width: 935px;
    padding: 15px 20px 60px 20px;
    margin: 0 auto 30px;
  }
  .about-wrap.medium {
    box-sizing: content-box;
    width: 80%;
  }
  .about-title {
    color: var(--primary-color);
    padding-top: 25px;
    font-size: 28px;
    font-weight: 600;
    font-family: "Source Sans Pro", sans-serif;
  }
  .about-sub-title {
    font-size: 21px;
    font-weight: 600;
  }
  .about-item {
  }
  .about-text.link {
    color: #1a0dab;
  }
  strong {
    display: inline;
  }
  .example-row {
    display: flex;
  }
  .example-col {
    display: flex;
    flex-direction: column;
    margin: 0px 40px 20px 40px;
  }
  .example-wrap {
    display: flex;
    justify-content: center;
  }
  .mat-slide-toggle.mat-disabled {
    opacity: 1;
  }
  h5 {
    margin: 15px 0px;
  }
  .mat-chip {
    cursor: pointer;
    display: inline-flex;
    padding: 7px 12px;
    border-radius: 16px;
    align-items: center;
    min-height: 32px;
    height: 1px;
    box-sizing: border-box;
    font-size: 14px;
    font-weight: 500;
    margin: 4px;
    background-color: #e0e0e0;
    color: rgba(0, 0, 0, 0.87);
  }
  .mat-chip.selected {
    background-color: #153333;
    color: #fff;
  }

  /*
* Credit to https://codepen.io/aaroniker/details/mdyYBPP
*/
  .feedback {
    --normal: #f8da69;
    --normal-shadow: #f4b555;
    --normal-mouth: #f05136;
    --normal-eye: #313036;
    --active: #f8da69;
    --active-shadow: #f4b555;
    --active-mouth: #f05136;
    --active-eye: #313036;
    --active-tear: #76b5e7;
    --active-shadow-angry: #e94f1d;
    margin: 0;
    padding: 20px 0;
    list-style: none;
    display: -webkit-box;
    display: flex;
  }
  .feedback li {
    position: relative;
    border-radius: 50%;
    background: var(--sb, var(--normal));
    box-shadow: inset 6px -6px 8px var(--sh, var(--normal-shadow));
    -webkit-transition: background 0.4s, box-shadow 0.4s, -webkit-transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, -webkit-transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, transform 0.3s,
      -webkit-transform 0.3s;
    -webkit-tap-highlight-color: transparent;
    cursor: pointer;
  }
  .feedback li:not(:last-child) {
    margin-right: 20px;
  }
  .feedback li div {
    width: 40px;
    height: 40px;
    position: relative;
    -webkit-transform: perspective(240px) translateZ(8px);
    transform: perspective(240px) translateZ(8px);
  }
  .feedback li div svg,
  .feedback li div:before,
  .feedback li div:after {
    display: block;
    position: absolute;
    left: var(--l, 10px);
    top: var(--t, 14px);
    width: var(--w, 8px);
    height: var(--h, 2px);
    -webkit-transform: rotate(var(--r, 0deg)) scale(var(--sc, 1)) translateZ(0);
    transform: rotate(var(--r, 0deg)) scale(var(--sc, 1)) translateZ(0);
  }
  .feedback li div svg {
    fill: none;
    stroke: var(--s);
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
    -webkit-transition: stroke 0.4s;
    transition: stroke 0.4s;
  }
  .feedback li div svg.eye {
    --s: var(--e, var(--normal-eye));
    --t: 18px;
    --w: 8px;
    --h: 4px;
  }
  .feedback li div svg.eye.right {
    --l: 24px;
  }
  .feedback li div svg.mouth {
    --s: var(--m, var(--normal-mouth));
    --l: 12px;
    --t: 24px;
    --w: 18px;
    --h: 8px;
  }
  .feedback li div:before,
  .feedback li div:after {
    content: "";
    z-index: var(--zi, 1);
    border-radius: var(--br, 2px);
    background: var(--b, var(--e, var(--normal-eye)));
    -webkit-transition: background 0.4s;
    transition: background 0.4s;
  }
  .feedback li.angry {
    --step-1-rx: -24deg;
    --step-1-ry: 20deg;
    --step-2-rx: -24deg;
    --step-2-ry: -20deg;
  }
  .feedback li.angry div:before {
    --r: 20deg;
  }
  .feedback li.angry div:after {
    --l: 24px;
    --r: -20deg;
  }
  .feedback li.angry div svg.eye {
    stroke-dasharray: 4.55;
    stroke-dashoffset: 8.15;
  }
  .feedback li.angry.active {
    -webkit-animation: angry 1s linear;
    animation: angry 1s linear;
  }
  .feedback li.angry.active div:before {
    --middle-y: -2px;
    --middle-r: 22deg;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li.angry.active div:after {
    --middle-y: 2px;
    --middle-r: -18deg;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li.sad {
    --step-1-rx: 20deg;
    --step-1-ry: -12deg;
    --step-2-rx: -18deg;
    --step-2-ry: 14deg;
  }
  .feedback li.sad div:before,
  .feedback li.sad div:after {
    --b: var(--active-tear);
    --sc: 0;
    --w: 6px;
    --h: 6px;
    --t: 16px;
    --br: 50%;
  }
  .feedback li.sad div:after {
    --l: 26px;
  }
  .feedback li.sad div svg.eye {
    --t: 16px;
  }
  .feedback li.sad div svg.mouth {
    --t: 24px;
    stroke-dasharray: 9.5;
    stroke-dashoffset: 33.25;
  }
  .feedback li.sad.active div:before,
  .feedback li.sad.active div:after {
    -webkit-animation: tear 0.6s linear forwards;
    animation: tear 0.6s linear forwards;
  }
  .feedback li.ok {
    --step-1-rx: 4deg;
    --step-1-ry: -22deg;
    --step-1-rz: 6deg;
    --step-2-rx: 4deg;
    --step-2-ry: 22deg;
    --step-2-rz: -6deg;
  }
  .feedback li.ok div:before {
    --l: 12px;
    --t: 18px;
    --h: 4px;
    --w: 4px;
    --br: 50%;
    box-shadow: 12px 0 0 var(--e, var(--normal-eye));
  }
  .feedback li.ok div:after {
    --l: 14px;
    --t: 26px;
    --w: 14px;
    --h: 2px;
    --br: 2px;
    --b: var(--m, var(--normal-mouth));
  }
  .feedback li.ok.active div:before {
    --middle-s-y: 0.35;
    -webkit-animation: toggle 0.2s linear forwards;
    animation: toggle 0.2s linear forwards;
  }
  .feedback li.ok.active div:after {
    --middle-s-x: 0.5;
    -webkit-animation: toggle 0.7s linear forwards;
    animation: toggle 0.7s linear forwards;
  }
  .feedback li.good {
    --step-1-rx: -14deg;
    --step-1-rz: 10deg;
    --step-2-rx: 10deg;
    --step-2-rz: -8deg;
  }
  .feedback li.good div:before {
    --b: var(--m, var(--normal-mouth));
    --w: 6px;
    --h: 6px;
    --br: 50%;
    --t: 22px;
    --zi: 0;
    opacity: 0.5;
    box-shadow: 8px 0 0 var(--b);
    -webkit-filter: blur(1px);
    filter: blur(2px);
  }
  .feedback li.good div:after {
    --sc: 0;
  }
  .feedback li.good div svg.eye {
    --t: 16px;
    --sc: -1;
    stroke-dasharray: 4.55;
    stroke-dashoffset: 8.15;
  }
  .feedback li.good div svg.mouth {
    --t: 22px;
    --sc: -1;
    stroke-dasharray: 13.3;
    stroke-dashoffset: 23.75;
  }
  .feedback li.good.active div svg.mouth {
    --middle-y: 2px;
    --middle-s: -1;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li.happy div {
    --step-1-rx: 18deg;
    --step-1-ry: 24deg;
    --step-2-rx: 18deg;
    --step-2-ry: -24deg;
  }
  .feedback li.happy div:before {
    --sc: 0;
  }
  .feedback li.happy div:after {
    --b: var(--m, var(--normal-mouth));
    --l: 12px;
    --t: 24px;
    --w: 18px;
    --h: 8px;
    --br: 0 0 8px 8px;
  }
  .feedback li.happy div svg.eye {
    --t: 14px;
    --sc: -1;
  }
  .feedback li.happy.active div:after {
    --middle-s-x: 0.95;
    --middle-s-y: 0.75;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li:not(.active):active {
    -webkit-transform: scale(0.925);
    transform: scale(0.925);
  }
  .feedback li.active {
    --sb: var(--active);
    --sh: var(--active-shadow);
    --m: var(--active-mouth);
    --e: var(--active-eye);
  }
  .feedback li.active div {
    -webkit-animation: shake 0.8s linear forwards;
    animation: shake 0.8s linear forwards;
  }

  @-webkit-keyframes shake {
    30% {
      -webkit-transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(5px);
      transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(10px);
    }
    60% {
      -webkit-transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(5px);
      transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(10px);
    }
    100% {
      -webkit-transform: perspective(240px) translateZ(4px);
      transform: perspective(240px) translateZ(4px);
    }
  }

  @keyframes shake {
    30% {
      -webkit-transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(10px);
      transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(10px);
    }
    60% {
      -webkit-transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(10px);
      transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(10px);
    }
    100% {
      -webkit-transform: perspective(240px) translateZ(4px);
      transform: perspective(240px) translateZ(4px);
    }
  }
  @-webkit-keyframes tear {
    0% {
      opacity: 0;
      -webkit-transform: translateY(-2px) scale(0) translateZ(0);
      transform: translateY(-2px) scale(0) translateZ(0);
    }
    50% {
      -webkit-transform: translateY(12px) scale(0.6, 1.2) translateZ(0);
      transform: translateY(12px) scale(0.6, 1.2) translateZ(0);
    }
    20%,
    80% {
      opacity: 1;
    }
    100% {
      opacity: 0;
      -webkit-transform: translateY(24px) translateX(4px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
      transform: translateY(48px) translateX(4px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
    }
  }
  @keyframes tear {
    0% {
      opacity: 0;
      -webkit-transform: translateY(-4px) scale(0) translateZ(0);
      transform: translateY(-4px) scale(0) translateZ(0);
    }
    50% {
      -webkit-transform: translateY(12px) scale(0.6, 1.2) translateZ(0);
      transform: translateY(12px) scale(0.6, 1.2) translateZ(0);
    }
    20%,
    80% {
      opacity: 1;
    }
    100% {
      opacity: 0;
      -webkit-transform: translateY(24px) translateX(4px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
      transform: translateY(24px) translateX(4px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
    }
  }
  @-webkit-keyframes toggle {
    50% {
      -webkit-transform: translateY(var(--middle-y, 0))
        scale(
          var(--middle-s-x, var(--middle-s, 1)),
          var(--middle-s-y, var(--middle-s, 1))
        )
        rotate(var(--middle-r, 0deg));
      transform: translateY(var(--middle-y, 0))
        scale(
          var(--middle-s-x, var(--middle-s, 1)),
          var(--middle-s-y, var(--middle-s, 1))
        )
        rotate(var(--middle-r, 0deg));
    }
  }
  @keyframes toggle {
    50% {
      -webkit-transform: translateY(var(--middle-y, 0))
        scale(
          var(--middle-s-x, var(--middle-s, 1)),
          var(--middle-s-y, var(--middle-s, 1))
        )
        rotate(var(--middle-r, 0deg));
      transform: translateY(var(--middle-y, 0))
        scale(
          var(--middle-s-x, var(--middle-s, 1)),
          var(--middle-s-y, var(--middle-s, 1))
        )
        rotate(var(--middle-r, 0deg));
    }
  }
  @-webkit-keyframes angry {
    40% {
      background: var(--active);
    }
    45% {
      box-shadow: inset 4px -4px 4px var(--active-shadow),
        inset 0 8px 10px var(--active-shadow-angry);
    }
  }
  @keyframes angry {
    40% {
      background: var(--active);
    }
    45% {
      box-shadow: inset 4px -4px 4px var(--active-shadow),
        inset 0 8px 10px var(--active-shadow-angry);
    }
  }
  html {
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
  }

  * {
    box-sizing: inherit;
  }
  *:before,
  *:after {
    box-sizing: inherit;
  }
`;
