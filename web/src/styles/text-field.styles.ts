import { css } from "lit";

export const textFieldStyles = css`
  md-filled-text-field {
    background-color: var(--input-fill);
    color: var(--primary-color);
    border-radius: 4px;
    --_caret-color: var(--primary-color);
    --md-sys-color-primary: var(--theme-color);
    --md-filled-text-field-container-shape: 4px;
    --md-filled-text-field-container-color: var(--input-fill);	
    --md-filled-text-field-focus-active-indicator-color: var(--theme-color);
    --md-filled-text-field-input-text-font: var(--font-family);
    --md-filled-text-field-label-text-font: var(--font-family);
  }
`;
