import { defineConfig } from "eslint/config";
import wcPlugin from "eslint-plugin-wc";
import litPlugin from "eslint-plugin-lit";
import tseslint from "typescript-eslint";
import eslint from "@eslint/js";

export default defineConfig([
  eslint.configs.recommended,
  tseslint.configs.recommended,
  wcPlugin.configs["flat/recommended"],
  litPlugin.configs["flat/recommended"],
  {
    ...wcPlugin.configs["flat/recommended"],
    ...litPlugin.configs["flat/recommended"],
    ignores: [
      "**/*.js",
      "node_modules",
      ".DS_Store",
      "dist",
      "dist-ssr",
      "*.local",
      ".gitignore",
    ],
    rules: {
      "@typescript-eslint/no-non-null-assertion": "off",
      "@typescript-eslint/ban-ts-comment": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "off", // "seems to be a bug with '_'"
      "no-prototype-builtins": "off",
    },
    settings: {
      wc: {
        elementBaseClasses: ["LitElement"],
      },
    },
  },
]);
