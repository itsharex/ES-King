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
  <n-page-header style="padding: 4px;--wails-draggable:drag">
    <template #avatar>
      <n-avatar :src="icon"/>
    </template>
    <template #subtitle>
      <n-tooltip>
        <template #trigger>
          <n-tag :type=title_tag v-if="subtitle">{{subtitle}}</n-tag>
          <n-p v-else>{{desc}}</n-p>
        </template>
        健康：{{title_tag}}
      </n-tooltip>
    </template>
    <template #title>
      <div style="font-weight: 800">{{ app_name }}</div>
    </template>
    <template #extra>
      <n-flex justify="flex-end" style="--wails-draggable:no-drag" class="right-section">
        <n-button quaternary :focusable="false" @click="openUrl(qq_url)">交流群✨</n-button>
<!--        <n-button quaternary :focusable="false" @click="changeTheme" :render-icon="renderIcon(MoonOrSunnyOutline)"/>-->

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
        <n-button quaternary @click="openUrl(update_url)"
                  :render-icon="renderIcon(HouseTwotone)"/>
          </template>
          <span>主页</span>
        </n-tooltip>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button quaternary :focusable="false" :loading="update_loading" @click="checkForUpdates"
                      :render-icon="renderIcon(SystemUpdateAltSharp)"/>
          </template>
          <span> 检查版本：{{ version.tag_name }} {{ check_msg }}</span>
        </n-tooltip>

        <n-button quaternary :focusable="false" @click="minimizeWindow" :render-icon="renderIcon(RemoveOutlined)"/>
        <n-button quaternary :focusable="false" @click="resizeWindow" :render-icon="renderIcon(MaxMinIcon)"/>
        <n-button quaternary style="font-size: 22px" :focusable="false" @click="closeWindow">
          <n-icon>
            <CloseFilled/>
          </n-icon>
        </n-button>
      </n-flex>
    </template>
  </n-page-header>
</template>

<script setup>
import {NAvatar, NButton, NFlex, useMessage} from 'naive-ui'
import {
  SystemUpdateAltSharp,
  RemoveOutlined,
  CloseFilled,
  CropSquareFilled,
  ContentCopyFilled, HouseTwotone
} from '@vicons/material'
import icon from '../assets/images/appicon.png'
import {h, onMounted, ref, shallowRef} from "vue";
import {BrowserOpenURL, Quit, WindowMaximise, WindowMinimise, WindowUnmaximise} from "../../wailsjs/runtime";
import {CheckUpdate} from '../../wailsjs/go/system/Update'
import {useNotification} from 'naive-ui'
import {openUrl, renderIcon} from "../utils/common";
import {GetVersion, GetAppName} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

// defineProps(['options', 'value']);

// const MoonOrSunnyOutline = shallowRef(WbSunnyOutlined)
const isMaximized = ref(false);
const title_tag = ref("success");
const check_msg = ref("");
const app_name = ref("");
const MaxMinIcon = shallowRef(CropSquareFilled)
const update_url = "https://github.com/Bronya0/ES-King/releases"
const qq_url = "https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz"

const update_loading = ref(false)
// let theme = lightTheme

let version = ref({
  tag_name: "",
  body: "",
})

const desc = "更人性化的ES GUI "
const subtitle = ref("")

const notification = useNotification()
const message = useMessage()

const checkForUpdates = async () => {
  update_loading.value = true
  try {
    const v = await GetVersion()
    const resp = await CheckUpdate()
    if (!resp) {
      message.error("无法连接github，检查更新失败")
    } else if (resp.tag_name !== v) {
      check_msg.value = '发现新版本 ' + resp.tag_name
      version.value.body = resp.body
      const n = notification.success({
        title: '发现新版本: ' + resp.name,
        // description: resp.body,
        action: () =>
            h(NFlex, {justify: "flex-end"}, () => [
              h(
                  NButton,
                  {
                    type: 'primary',
                    secondary: true,
                    onClick: () => BrowserOpenURL(update_url),
                  },
                  () => "立即下载",
              ),
              h(
                  NButton,
                  {
                    secondary: true,
                    onClick: () => {
                      n.destroy()
                    },
                  },
                  () => "取消",
              ),
            ]),
        onPositiveClick: () => BrowserOpenURL(update_url),
      })
    }
  } finally {
    update_loading.value = false
  }
}

onMounted(async () => {
  emitter.on('selectNode', selectNode)
  emitter.on('changeTitleType', changeTitleType)

  app_name.value = await GetAppName()

  // const config = await GetConfig()
  // MoonOrSunnyOutline.value = config.theme === lightTheme.name ? WbSunnyOutlined : NightlightRoundFilled
  const v = await GetVersion()
  version.value.tag_name = v
  subtitle.value = desc + " " + v
  await checkForUpdates()

})

const selectNode = (node) => {
  subtitle.value = "当前集群：【" + node.name + "】"
}

// 动态修改title的类型
const changeTitleType = (type) => {
  console.log(type)
  title_tag.value = type
}

const minimizeWindow = () => {
  WindowMinimise()
}

const resizeWindow = () => {
  isMaximized.value = !isMaximized.value;
  if (isMaximized.value) {
    WindowMaximise();
    MaxMinIcon.value = ContentCopyFilled;
  } else {
    WindowUnmaximise();
    MaxMinIcon.value = CropSquareFilled;
  }
  console.log(isMaximized.value)

}

const closeWindow = () => {
  Quit()
}
// const changeTheme = () => {
//   MoonOrSunnyOutline.value = MoonOrSunnyOutline.value === NightlightRoundFilled ? WbSunnyOutlined : NightlightRoundFilled;
//   theme = MoonOrSunnyOutline.value === NightlightRoundFilled ? darkTheme : lightTheme
//   emitter.emit('update_theme', theme)
// }
</script>

<style scoped>


.right-section .n-button {
  padding: 0 8px;
}
</style>