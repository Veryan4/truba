import { css } from "lit";

export const styles = css`
  .privacy-container {
    display: flex;
    justify-content: center;
    width: 100vw;
  }
  .privacy-wrap {
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
    max-width: 935px;
    padding: 15px 20px 60px 20px;
    margin: 0 auto 30px;
  }
  .privacy-wrap.medium {
    box-sizing: content-box;
    width: 80%;
  }
  .privacy-title {
    color: var(--primary-color);
    padding-top: 25px;
    font-size: 28px;
    font-weight: 600;
    font-family: "Source Sans Pro", sans-serif;
    margin-bottom: 20px;
  }
`;
