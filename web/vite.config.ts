import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";
import eslintPlugin from "vite-plugin-eslint";
import html from "@web/rollup-plugin-html";
import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";
import minifyHTML from "rollup-plugin-minify-html-literals";
import viteCompression from "vite-plugin-compression2";

export default defineConfig({
  build: {
    target: "esnext",
    rollupOptions: {
      plugins: [
        html({
          input: "index.html",
        }),
        resolve(),
        // Currently destroys md-switch styles so commented out. Will need to check when fixed.
        //minifyHTML(),
        terser({
          ecma: 2024,
          module: true,
        }),
      ],
    },
  },
  plugins: [
    eslintPlugin(),
    viteCompression({
      verbose: false,
      filter: (fileName: string) =>
        /\.(js|css|html|txt|xml|json|svg|ico|ttf|otf|eot)$/.test(fileName),
      algorithm: "brotliCompress",
      ext: ".br",
    }),
    VitePWA({
      registerType: "autoUpdate",
      base: "/",
      srcDir: "src",
      filename: "sw.ts",
      injectRegister: null,
      strategies: "injectManifest",
      includeAssets: ["favicon.ico", "apple-touch-icon.png", "favicon.svg"],
      manifest: {
        name: "truba",
        short_name: "truba",
        theme_color: "#000000",
        background_color: "#fafafa",
        display: "standalone",
        scope: "/",
        start_url: "/",
        icons: [
          {
            src: "/icons/icon-72x72.png",
            sizes: "72x72",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-96x96.png",
            sizes: "96x96",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-128x128.png",
            sizes: "128x128",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-144x144.png",
            sizes: "144x144",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-152x152.png",
            sizes: "152x152",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-192x192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-384x384.png",
            sizes: "384x384",
            type: "image/png",
            purpose: "maskable any",
          },
          {
            src: "/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
    }),
  ],
});
