import { css } from "lit";

export const styles = css`
  .news-container {
    display: flex;
    justify-content: center;
    width: 100%;
  }
  .loader-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 88dvh;
  }
  .flex-row {
    display: flex;
    flex-wrap: wrap;
    max-width: 840px;
    justify-content: flex-start;
    padding: 40px 0 0 0;
    margin: 0 auto 30px;
  }
  .flex-item {
    display: flex;
    flex-direction: column;
    width: 250px;
    height: 425px;
    margin-left: 15px;
    margin-right: 15px;
  }
  .no-stories {
    height: 80dvh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    font-size: 32px;
    width: 50dvw;
    text-align: center;
  }
  @media only screen and (max-width: 840px) {
    .flex-row {
      justify-content: center;
    }
  }
`;
