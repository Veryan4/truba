import { css } from "lit";

export const styles = css`
  .mdc-evolution-chip.mdc-evolution-chip--selected {
    background-color: var(--primary-color);
  }

  .mdc-evolution-chip.mdc-evolution-chip--selected
    .mdc-evolution-chip__text-label {
    color: var(--secondary-background-color);
  }

  .material-icons {
    font-family: "Material Icons";
    font-weight: normal;
    font-style: normal;
    font-size: 24px;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: "liga";
    -webkit-font-smoothing: antialiased;
  }

  .sub-title {
    padding: 0.5rem 0;
  }
`;
