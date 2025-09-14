import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en/translation.json'
import zh from './locales/zh/translation.json'

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
      'zh-CN': { translation: zh },
      'zh-TW': { translation: zh },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    detection: {
      order: ['querystring', 'localStorage', 'navigator', 'htmlTag'],
      lookupQuerystring: 'lng',
      caches: ['localStorage'],
    },
  })

export default i18n
