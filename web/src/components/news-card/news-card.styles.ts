import { css } from "lit";

export const styles = css`
  .icon {
    width: 2rem;
    height: 2rem;
    display: inline-block;
    color: var(--primary-color);
    cursor: pointer;
  }

  .mdc-card {
    font-family: var(--font-family);
    max-height: 370px;
    height: 370px;
  }

  .mdc-card.user {
    max-height: 400px;
    height: 400px;
  }

  .demo-card__primary {
    min-height: 170px;
  }
  .mdc-card__primary-action {
    height: 375px;
  }

  .mdc-card__primary-action.flipped {
    overflow-y: scroll;
  }

  h4 {
    font-weight: 500;
  }

  .demo-card__primary,
  .demo-card__secondary {
    padding: 0 1rem;
  }

  .title {
    color: var(--primary-color);
    font-size: 18px;
    font-weight: 600;
    font-family: "Source Sans Pro", sans-serif;
  }
  .source {
    color: var(--primary-color);
    font-size: 14px;
    font-weight: 400;
    font-family: "Open Sans", sans-serif;
    padding-top: 5px;
    width: fit-content;
  }
  .title,
  .source {
    cursor: pointer;
  }
  .image {
    display: block;
    border-radius: 2px 2px 0 0;
    position: relative;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    object-fit: cover;
    cursor: pointer;
  }
  a {
    text-decoration: none;
  }
  .bottom-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0px;
  }
  .bottom-row.no-emojis {
    padding: 5px 0px 20px;
  }
  .social-row {
    display: flex;
    justify-content: flex-end;
  }
  .logo-icon {
    margin-left: 10px;
    cursor: pointer;
  }
  .flex-row.medium {
    box-sizing: content-box;
    padding: 60px 20px 0;
    width: calc(100% - 40px);
  }
  .back {
    max-height: 310px;
    height: 310px;
    overflow-y: scroll;
    overflow-x: hidden;
  }
  .menu {
    background-color: var(--secondary-background-color);
  }
  i.icon {
    cursor: pointer;
    z-index: 999;
  }
  .front-bottom {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 135px;
  }
  .front-bottom.emojis {
    height: 140px;
  }
`;
