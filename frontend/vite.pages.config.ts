/** 独立构建 GitHub Pages 展示页，复用前端插件和资源处理规则。 */
import { fileURLToPath, URL } from 'node:url'
import { defineConfig, mergeConfig } from 'vite'
import appConfig from './vite.config'

export default mergeConfig(
  appConfig,
  defineConfig({
    root: fileURLToPath(new URL('./pages', import.meta.url)),
    base: process.env.PAGES_BASE_PATH || '/Drrr-chatRoom-add-AIChat/',
    publicDir: fileURLToPath(new URL('./public', import.meta.url)),
    build: {
      outDir: fileURLToPath(new URL('../dist/pages', import.meta.url)),
      emptyOutDir: true,
    },
  }),
)
