import { css } from "lit";

export const styles = css`
  mwc-textfield {
    --mdc-theme-primary: #296954;
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

  .mdc-evolution-chip.mdc-evolution-chip--selected .material-icons {
    color: var(--secondary-background-color);
  }

  .settings-container {
    display: flex;
    justify-content: center;
    width: 100vw;
    font-family: var(--font-family);
  }
  .settings-wrap {
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
    max-width: 935px;
    padding: 15px 20px 60px 20px;
    margin: 0 auto 30px;
  }
  .settings-title {
    color: var(--primary-color);
    padding-top: 25px;
    padding-bottom: 25px;
    font-size: 28px;
    font-weight: 600;
    font-family: "Source Sans Pro", sans-serif;
  }
  .settings-item {
    padding: 25px 0px;
  }
  .submit-wrap {
    display: flex;
    justify-content: flex-end;
    padding: 20px 30px 0px 0px;
  }
  button.mat-raised-button {
    width: 30px;
  }
  strong {
    display: inline;
  }
  .mat-slide-toggle.mat-disabled {
    opacity: 1;
  }
  h5 {
    margin: 15px 0px;
  }
  .mat-form-field {
    min-width: 535px;
  }
  .settings-sub-title {
    padding-top: 20px;
    font-size: 28px;
  }
  @media only screen and (max-width: 752px) {
    .mat-form-field {
      min-width: 250px;
    }
  }
`;
