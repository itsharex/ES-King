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
  <!--  https://www.naiveui.com/zh-CN/os-theme/components/form  -->
  <n-flex vertical justify="start">
    <h2>设置</h2>
    <n-form :model="config" label-placement="top" style="text-align: left;">

      <n-form-item label="窗口宽度">
        <n-input-number v-model:value="config.width" :min="800" :max="1920" :style="{ maxWidth: '120px' }"/>
      </n-form-item>
      <n-form-item label="窗口高度">
        <n-input-number v-model:value="config.height" :min="600" :max="1080" :style="{ maxWidth: '120px' }"/>
      </n-form-item>
      <n-form-item label="语言">
        <n-select v-model:value="config.language" :options="languageOptions" :style="{ maxWidth: '120px' }"/>
      </n-form-item>

      <n-form-item label="主题">
        <n-switch
            :checked-value="darkTheme.name"
            :unchecked-value="lightTheme.name"
            v-model:value="theme"
            @update-value="changeTheme"
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
          <n-button @click="saveConfig" strong type="primary">保存设置</n-button>
          <n-tooltip>
            <template #trigger>
              <n-button @click="getSysInfo()" style="width: 100px">ProcessInfo</n-button>
            </template>
            <n-p style="white-space: pre-wrap; max-height: 400px; overflow: auto; text-align: left">{{ sys_info }}</n-p>
          </n-tooltip>
        </n-flex>
      </n-form-item>

    </n-form>
  </n-flex>
</template>

<script setup>
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
  {label: '中文', value: 'zh-CN'},
  {label: 'English', value: 'en-US'}
]

const getSysInfo = async () => {
  sys_info.value = await GetProcessInfo()
}

onMounted(async () => {
  console.info("初始化settings……")

  // 从后端加载配置
  const loadedConfig = await GetConfig()
  console.log(loadedConfig)
  if (loadedConfig) {
    config.value = loadedConfig
    theme = loadedConfig.theme
  }
  await getSysInfo()

})


const saveConfig = async () => {
  config.value.theme = theme
  const err = await SaveConfig(config.value)
  if (err !== "") {
    message.error("保存失败：" + err)
    return
  }

  WindowSetSize(config.value.width, config.value.height)

  emitter.emit('update_theme', theme)
  // 可以添加保存成功的提示
  message.success("保存成功")
  config.value = await GetConfig()

}

const changeTheme = () => {
  emitter.emit('update_theme', theme)
}


</script>