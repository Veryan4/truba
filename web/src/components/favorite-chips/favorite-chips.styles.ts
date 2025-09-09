import { css } from "lit";

export const styles = css`
  .mdc-evolution-chip.mdc-evolution-chip--selected {
    background-color: var(--primary-color);
  }

  .mdc-evolution-chip.mdc-evolution-chip--selected
    .mdc-evolution-chip__text-label {
    color: var(--secondary-background-color);
  }

  .sub-title {
    padding: 0.5rem 0;
  }
`;
