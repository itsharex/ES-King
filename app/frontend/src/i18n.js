import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import en from './locales/en.json'
import ja from './locales/ja.json'

/**
 * 根据 navigator.language 检测系统语言，匹配支持的语言
 */
function detectLocale() {
  const lang = navigator.language || navigator.userLanguage || 'zh-CN'
  if (lang.startsWith('zh')) return 'zh-CN'
  if (lang.startsWith('ja')) return 'ja'
  return 'en' // fallback to English
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: detectLocale(),
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en': en,
    'ja': ja,
  },
})

export default i18n
