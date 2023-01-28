import { css } from "lit";

export const styles = css`
  .card {
    font-family: var(--font-family);
    width: 275px;
    margin: 110px auto;
    background-color: var(--secondary-background-color);
    border: 1px solid var(--outline-color);
    border-radius: 1px;
    padding: 30px;
    box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2),
      0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
  }
  .centered-text {
    display: flex;
    justify-content: center;
    width: 100%;
  }
  .form-field {
    line-height: 1.5;
    border-top: unset;
    padding: 0.4375em 0;
    display: block;
    position: relative;
    flex: auto;
    min-width: 0;
    width: 180px;
    margin-right: 20px;
  }
  .card-title {
    font-size: 24px;
    font-weight: 500;
    margin-bottom: 20px;
  }
  .form-buttons {
    padding: 8px 0;
  }
  .sign-btn {
    margin: 0 8px;
  }
  .consent-box {
    font-size: 12px;
    padding-bottom: 10px;
  }
  .row {
    display: flex;
  }
  #google {
    margin: 1rem 0;
  }
  a {
    cursor: pointer;
  }
  a.navigation {
    text-decoration: unset;
    color: unset;
  }

  @media only screen and (max-width: 752px) {
    .card {
      margin: 60px auto;
    }
    .card.register {
      width: 275px;
    }
    .card.register .row {
      display: flex;
      flex-direction: column;
    }
  }
`;
