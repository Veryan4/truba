import { css } from "lit";

export const checkBoxStyles = css`
  md-checkbox {
    /* System tokens */
    --md-sys-color-primary: #296954;
    --md-sys-color-on-primary: var(--input-fill);
    --md-sys-color-on-surface-variant: var(--primary-color);

    /* Component tokens */
    --md-checkbox-container-shape: 0px;
  }

  label {
    --mdc-theme-text-primary-on-background: var(--primary-color);
  }
`;
