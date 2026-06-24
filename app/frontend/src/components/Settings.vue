<!--
  - Copyright 2025 Bronya0 <tangssst@163.com>.
  - Author Github: https://github.com/Bronya0
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     https://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <n-flex justify="start" vertical>
    <h2>{{ t('settings.title') }}</h2>
    <n-form :model="config" label-placement="top" style="text-align: left;">

      <n-form-item :label="t('settings.windowWidth')">
        <n-input-number v-model:value="config.width" :max="1920" :min="800" :style="{ maxWidth: '120px' }"/>
      </n-form-item>
      <n-form-item :label="t('settings.windowHeight')">
        <n-input-number v-model:value="config.height" :max="1080" :min="600" :style="{ maxWidth: '120px' }"/>
      </n-form-item>
      <n-form-item :label="t('settings.language')">
        <n-select v-model:value="config.language" :options="languageOptions" :style="{ maxWidth: '120px' }" @update:value="onLanguageChange"/>
      </n-form-item>

      <n-form-item :label="t('settings.theme')">
        <n-switch
            v-model:value="theme"
            :checked-value="darkTheme.name"
            :unchecked-value="lightTheme.name"
            @update:value="changeTheme"
        >
          <template #checked-icon>
            <n-icon :component="NightlightRoundFilled"/>
          </template>
          <template #unchecked-icon>
            <n-icon :component="WbSunnyOutlined"/>
          </template>
        </n-switch>
      </n-form-item>
      <n-form-item>
        <n-flex>
          <n-button strong type="primary" @click="saveConfig">{{ t('settings.saveSettings') }}</n-button>
          <n-tooltip>
            <template #trigger>
              <n-button style="width: 100px" @click="getSysInfo()">{{ t('settings.processInfo') }}</n-button>
            </template>
            <n-p style="white-space: pre-wrap; max-height: 400px; overflow: auto; text-align: left">{{ sys_info }}</n-p>
          </n-tooltip>
        </n-flex>
      </n-form-item>

    </n-form>
  </n-flex>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import {onMounted, ref, shallowRef} from 'vue'
import {
  darkTheme,
  lightTheme,
  NButton,
  NForm,
  NFormItem,
  NInputNumber,
  NSelect,
  useMessage,
} from 'naive-ui'
import {WbSunnyOutlined, NightlightRoundFilled} from '@vicons/material'

import {GetConfig, SaveConfig} from '../../wailsjs/go/config/AppConfig'
import {GetProcessInfo} from '../../wailsjs/go/system/Update'

import {WindowSetSize} from "../../wailsjs/runtime";
import emitter from "../utils/eventBus";

const { t, locale } = useI18n()

const message = useMessage()
let theme = lightTheme.name
const sys_info = ref("")

const config = ref({
  width: 1248,
  height: 768,
  language: 'zh-CN',
  theme: theme,
})

const languageOptions = [
  {label: t('settings.langOptions.zh'), value: 'zh-CN'},
  {label: t('settings.langOptions.en'), value: 'en'},
  {label: t('settings.langOptions.ja'), value: 'ja'},
]

const onLanguageChange = (value) => {
  locale.value = value
  emitter.emit('change_language', value)
}

const getSysInfo = async () => {
  sys_info.value = await GetProcessInfo()
}

onMounted(async () => {
  const loadedConfig = await GetConfig()
  if (loadedConfig) {
    config.value = loadedConfig
    theme = loadedConfig.theme
    if (['zh-CN', 'en', 'ja'].includes(loadedConfig.language)) {
      locale.value = loadedConfig.language
    }
  }
  await getSysInfo()
})

const saveConfig = async () => {
  config.value.theme = theme
  const err = await SaveConfig(config.value)
  if (err !== "") {
    message.error(t('common.saveFailed', { msg: err }))
    return
  }

  WindowSetSize(config.value.width, config.value.height)

  emitter.emit('update_theme', theme)
  message.success(t('common.saveSuccess'))
  config.value = await GetConfig()
}

const changeTheme = () => {
  emitter.emit('update_theme', theme)
}
</script>
