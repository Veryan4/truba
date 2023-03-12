import { css } from "lit";

export const switchStyles = css`
  md-switch {
    /* System tokens */
    --md-sys-color-primary: var(--theme-color);
    --md-sys-color-on-primary: #ffffff;
    --md-sys-color-outline: var(--input-fill);
    --md-sys-color-surface-container-highest: #dde4e3;

    /* Component tokens */
    --md-switch-handle-shape: 0px;
    --md-switch-track-shape: 0px;
  }
`;
