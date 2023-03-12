import { css } from "lit";

export const styles = css`
  #floating{
    z-index: 999;
    border-radius: 4px;
    background-color: var(--secondary-background-color);
    box-shadow: 0px 2px 1px -1px rgba(0, 0, 0, 0.2),
      0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12);
    box-sizing: border-box;
    padding: 0.5rem;
  }
  .tutorial-buttons {
    display: flex;
  }
  .hide {
    display: none;
  }
`;
