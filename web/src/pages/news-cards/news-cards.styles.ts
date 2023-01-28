import { css } from "lit";

export const styles = css`
  .news-container {
    display: flex;
    justify-content: center;
    width: 100%;
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

  @media only screen and (max-width: 840px) {
    .flex-row {
      justify-content: center;
    }
  }
`;
