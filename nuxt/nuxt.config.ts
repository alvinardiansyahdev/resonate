export default defineNuxtConfig({
  modules: ["@pinia/nuxt", "@nuxtjs/google-fonts"],
  css: ["~/assets/css/reset.css", "~/assets/css/tokens.css", "~/assets/css/motion.css"],
  googleFonts: {
    families: {
      "Instrument+Serif": [400, 400],
      Inter: [400, 500, 600],
      "JetBrains+Mono": [400],
    },
    display: "swap",
    download: true,
  },
  ssr: false,
  devtools: { enabled: true },
  nitro: {
    devProxy: {
      "/api": {
        target: "http://localhost:8000/api",
        changeOrigin: true,
      },
    },
    routeRules: {
      "/discover": { redirect: "/" },
    },
  },
  app: {
    head: {
      title: "Resonate",
      meta: [
        { name: "description", content: "Music that meets you where you are" },
        { name: "theme-color", content: "#0d0612" },
      ],
    },
  },
})
