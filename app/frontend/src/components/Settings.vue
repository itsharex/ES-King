<template>
  <!--  https://www.naiveui.com/zh-CN/os-theme/components/form  -->
  <n-flex vertical justify="start">
    <n-flex align="center">
      <h2 style="max-width: 200px;">设置</h2>
    </n-flex>

    <n-form :model="config" label-placement="top" style="text-align: left;">
      <n-form-item label="项目主页">
        <n-button @click="BrowserOpenURL(home_url)" :render-icon="renderIcon(HouseTwotone)">ES-King 项目主页</n-button>
      </n-form-item>
      <n-form-item label="同款 Kafka 客户端">
        <n-button @click="BrowserOpenURL(kafka_home_url)" :render-icon="renderIcon(HouseTwotone)">推荐同款 KafKa</n-button>
      </n-form-item>
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
        <n-flex>
          <n-button @click="theme=lightTheme" :render-icon="renderIcon(WbSunnyOutlined)"/>
          <n-button @click="theme=darkTheme" :render-icon="renderIcon(NightlightRoundFilled)"/>
        </n-flex>
      </n-form-item>
      <n-form-item>
        <n-button @click="saveConfig" strong type="primary">保存设置</n-button>
      </n-form-item>

    </n-form>
  </n-flex>
</template>

<script setup>
import {onMounted, ref} from 'vue'
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
import {WbSunnyOutlined, NightlightRoundFilled, RemoveOutlined, CloseFilled, HouseTwotone} from '@vicons/material'

import {GetConfig, SaveConfig} from '../../wailsjs/go/config/AppConfig'
import {BrowserOpenURL, WindowSetSize} from "../../wailsjs/runtime";
import {renderIcon} from "../utils/common";
import emitter from "../utils/eventBus";

const message = useMessage()
let theme = lightTheme
const home_url = "https://github.com/Bronya0/ES-King"
const kafka_home_url = "https://github.com/Bronya0/kafka-King"


const config = ref({
  width: 1248,
  height: 768,
  language: 'zh-CN',
  theme: theme.name,
})
const languageOptions = [
  {label: '中文', value: 'zh-CN'},
  {label: 'English', value: 'en-US'}
]

onMounted(async () => {
  console.info("初始化settings……")

  // 从后端加载配置
  const loadedConfig = await GetConfig()
  console.log(loadedConfig)
  if (loadedConfig) {
    config.value = loadedConfig
  }
})


const saveConfig = async () => {
  config.value.theme = theme.name
  const err = await SaveConfig(config.value)
  if (err !== "") {
    message.error("保存失败：" + err)
    return
  }

  await WindowSetSize(config.value.width, config.value.height)

  emitter.emit('update_theme', theme)
  // 可以添加保存成功的提示
  message.success("保存成功")
  config.value = await GetConfig()

}

</script>