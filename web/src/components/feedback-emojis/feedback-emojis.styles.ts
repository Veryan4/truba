import { css } from "lit";

export const styles = css`
  .feedback-container {
    display: flex;
    justify-content: flex-end;
    padding: 5px 0px;
  }
  fieldset {
    margin: 0;
    padding: 0;
    border: none;
  }
  lit-spa-tooltip:not(:last-child) {
    margin-right: 10px;
  }
  /*
* Credit to https://codepen.io/aaroniker/details/mdyYBPP for emoji animations
*/
  .feedback {
    --normal: #eceaf3;
    --normal-shadow: #d9d8e3;
    --normal-mouth: #9795a4;
    --normal-eye: #595861;
    --active: #f8da69;
    --active-shadow: #f4b555;
    --active-mouth: #f05136;
    --active-eye: #313036;
    --active-tear: #76b5e7;
    --active-shadow-angry: #e94f1d;
    margin: 0;
    padding: 0;
    list-style: none;
    display: -webkit-box;
    display: flex;
  }
  .feedback li {
    position: relative;
    border-radius: 50%;
    background: var(--sb, var(--normal));
    box-shadow: inset 3px -3px 4px var(--sh, var(--normal-shadow));
    -webkit-transition: background 0.4s, box-shadow 0.4s, -webkit-transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, -webkit-transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, transform 0.3s;
    transition: background 0.4s, box-shadow 0.4s, transform 0.3s,
      -webkit-transform 0.3s;
    -webkit-tap-highlight-color: transparent;
  }

  .feedback li div {
    width: 20px;
    height: 20px;
    position: relative;
    -webkit-transform: perspective(240px) translateZ(4px);
    transform: perspective(240px) translateZ(4px);
  }
  .feedback li div svg,
  .feedback li div:before,
  .feedback li div:after {
    display: block;
    position: absolute;
    left: var(--l, 5px);
    top: var(--t, 7px);
    width: var(--w, 4px);
    height: var(--h, 1px);
    -webkit-transform: rotate(var(--r, 0deg)) scale(var(--sc, 1)) translateZ(0);
    transform: rotate(var(--r, 0deg)) scale(var(--sc, 1)) translateZ(0);
  }
  .feedback li div svg {
    fill: none;
    stroke: var(--s);
    stroke-width: 1px;
    stroke-linecap: round;
    stroke-linejoin: round;
    -webkit-transition: stroke 0.4s;
    transition: stroke 0.4s;
  }
  .feedback li div svg.eye {
    --s: var(--e, var(--normal-eye));
    --t: 9px;
    --w: 4px;
    --h: 2px;
  }
  .feedback li div svg.eye.right {
    --l: 12px;
  }
  .feedback li div svg.mouth {
    --s: var(--m, var(--normal-mouth));
    --l: 6px;
    --t: 12px;
    --w: 9px;
    --h: 4px;
  }
  .feedback li div:before,
  .feedback li div:after {
    content: "";
    z-index: var(--zi, 1);
    border-radius: var(--br, 1px);
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
    --l: 12px;
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
    --middle-y: -1px;
    --middle-r: 22deg;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li.angry.active div:after {
    --middle-y: 1px;
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
    --w: 3px;
    --h: 3px;
    --t: 8px;
    --br: 50%;
  }
  .feedback li.sad div:after {
    --l: 13px;
  }
  .feedback li.sad div svg.eye {
    --t: 8px;
  }
  .feedback li.sad div svg.mouth {
    --t: 12px;
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
    --l: 6px;
    --t: 9px;
    --h: 2px;
    --w: 2px;
    --br: 50%;
    box-shadow: 6px 0 0 var(--e, var(--normal-eye));
  }
  .feedback li.ok div:after {
    --l: 7px;
    --t: 13px;
    --w: 7px;
    --h: 1px;
    --br: 1px;
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
    --w: 3px;
    --h: 3px;
    --br: 50%;
    --t: 11px;
    --zi: 0;
    opacity: 0.5;
    box-shadow: 8px 0 0 var(--b);
    -webkit-filter: blur(1px);
    filter: blur(1px);
  }
  .feedback li.good div:after {
    --sc: 0;
  }
  .feedback li.good div svg.eye {
    --t: 8px;
    --sc: -1;
    stroke-dasharray: 4.55;
    stroke-dashoffset: 8.15;
  }
  .feedback li.good div svg.mouth {
    --t: 11px;
    --sc: -1;
    stroke-dasharray: 13.3;
    stroke-dashoffset: 23.75;
  }
  .feedback li.good.active div svg.mouth {
    --middle-y: 1px;
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
    --l: 6px;
    --t: 12px;
    --w: 9px;
    --h: 4px;
    --br: 0 0 4px 4px;
  }
  .feedback li.happy div svg.eye {
    --t: 7px;
    --sc: -1;
  }
  .feedback li.happy.active div:after {
    --middle-s-x: 0.95;
    --middle-s-y: 0.75;
    -webkit-animation: toggle 0.8s linear forwards;
    animation: toggle 0.8s linear forwards;
  }
  .feedback li:not(.active) {
    cursor: pointer;
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
        translateZ(5px);
    }
    60% {
      -webkit-transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(5px);
      transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(5px);
    }
    100% {
      -webkit-transform: perspective(240px) translateZ(2px);
      transform: perspective(240px) translateZ(2px);
    }
  }

  @keyframes shake {
    30% {
      -webkit-transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(5px);
      transform: perspective(240px) rotateX(var(--step-1-rx, 0deg))
        rotateY(var(--step-1-ry, 0deg)) rotateZ(var(--step-1-rz, 0deg))
        translateZ(5px);
    }
    60% {
      -webkit-transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(5px);
      transform: perspective(240px) rotateX(var(--step-2-rx, 0deg))
        rotateY(var(--step-2-ry, 0deg)) rotateZ(var(--step-2-rz, 0deg))
        translateZ(5px);
    }
    100% {
      -webkit-transform: perspective(240px) translateZ(2px);
      transform: perspective(240px) translateZ(2px);
    }
  }
  @-webkit-keyframes tear {
    0% {
      opacity: 0;
      -webkit-transform: translateY(-1px) scale(0) translateZ(0);
      transform: translateY(-1px) scale(0) translateZ(0);
    }
    50% {
      -webkit-transform: translateY(6px) scale(0.6, 1.2) translateZ(0);
      transform: translateY(6px) scale(0.6, 1.2) translateZ(0);
    }
    20%,
    80% {
      opacity: 1;
    }
    100% {
      opacity: 0;
      -webkit-transform: translateY(12px) translateX(2px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
      transform: translateY(24px) translateX(2px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
    }
  }
  @keyframes tear {
    0% {
      opacity: 0;
      -webkit-transform: translateY(-2px) scale(0) translateZ(0);
      transform: translateY(-2px) scale(0) translateZ(0);
    }
    50% {
      -webkit-transform: translateY(6px) scale(0.6, 1.2) translateZ(0);
      transform: translateY(6px) scale(0.6, 1.2) translateZ(0);
    }
    20%,
    80% {
      opacity: 1;
    }
    100% {
      opacity: 0;
      -webkit-transform: translateY(12px) translateX(2px) rotateZ(-30deg)
        scale(0.7, 1.1) translateZ(0);
      transform: translateY(12px) translateX(2px) rotateZ(-30deg)
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
      box-shadow: inset 2px -2px 2px var(--active-shadow),
        inset 0 4px 5px var(--active-shadow-angry);
    }
  }
  @keyframes angry {
    40% {
      background: var(--active);
    }
    45% {
      box-shadow: inset 2px -2px 2px var(--active-shadow),
        inset 0 4px 5px var(--active-shadow-angry);
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
  .feedback li:hover {
    background-color: #f8da69;
    box-shadow: inset 3px -3px 4px #f4b555;
  }
  .feedback li.happy:hover div:before,
  .feedback li.happy:hover div:after {
    background-color: #f05136;
  }
`;
