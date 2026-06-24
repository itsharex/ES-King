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
          <n-tag v-if="subtitle" :type=title_tag>{{ subtitle }}</n-tag>
          <n-p v-else>{{ desc }}</n-p>
        </template>
        {{ t('header.health', { status: title_tag }) }}
      </n-tooltip>
    </template>
    <template #title>
      <div style="font-weight: 800">{{ app_name }}</div>
    </template>
    <template #extra>
      <n-flex justify="flex-end" style="--wails-draggable:no-drag" class="right-section">
        <n-button quaternary :focusable="false" @click="openUrl(qq_url)">{{ t('header.techGroup') }}</n-button>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button :render-icon="renderIcon(HouseTwotone)" quaternary
                      @click="openUrl(update_url)"/>
          </template>
          <span>{{ t('header.homePage') }}</span>
        </n-tooltip>

        <n-tooltip placement="bottom" trigger="hover">
          <template #trigger>
            <n-button quaternary :focusable="false" :loading="update_loading" @click="checkForUpdates"
                      :render-icon="renderIcon(SystemUpdateAltSharp)"/>
          </template>
          <span>{{ t('header.checkVersion', { version: version.tag_name, msg: check_msg }) }}</span>
        </n-tooltip>

        <n-button quaternary :focusable="false" @click="minimizeWindow" :render-icon="renderIcon(RemoveOutlined)"/>
        <n-button quaternary :focusable="false" @click="resizeWindow" :render-icon="renderIcon(MaxMinIcon)"/>
        <n-button quaternary class="close-btn" style="font-size: 22px" :focusable="false" @click="closeWindow">
          <n-icon>
            <CloseFilled/>
          </n-icon>
        </n-button>
      </n-flex>
    </template>
  </n-page-header>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()

const isMaximized = ref(false);
const title_tag = ref("success");
const check_msg = ref("");
const app_name = ref("");
const MaxMinIcon = shallowRef(CropSquareFilled)
const update_url = "https://github.com/Bronya0/ES-King/releases"
const qq_url = "https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz"

const update_loading = ref(false)

let version = ref({
  tag_name: "",
  body: "",
})

const desc = t('header.desc')
const subtitle = ref("")

const notification = useNotification()
const message = useMessage()

const checkForUpdates = async () => {
  update_loading.value = true
  try {
    const v = await GetVersion()
    const resp = await CheckUpdate()
    if (!resp) {
      message.error(t('header.checkFailed'))
    } else if (resp.tag_name !== v) {
      check_msg.value = t('header.newVersionFound', { tag: resp.tag_name })
      version.value.body = resp.body
      const n = notification.success({
        title: t('header.newVersionFound', { tag: resp.name }),
        description: resp.body,
        action: () =>
            h(NFlex, {justify: "flex-end"}, () => [
              h(
                  NButton,
                  {
                    type: 'primary',
                    secondary: true,
                    onClick: () => BrowserOpenURL(update_url),
                  },
                  () => t('header.downloadNow'),
              ),
              h(
                  NButton,
                  {
                    secondary: true,
                    onClick: () => {
                      n.destroy()
                    },
                  },
                  () => t('header.cancel'),
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

  const v = await GetVersion()
  version.value.tag_name = v
  subtitle.value = desc + " " + v
  await checkForUpdates()
})

const selectNode = (node) => {
  subtitle.value = t('header.currentCluster', { name: node.name })
}

const changeTitleType = (type) => {
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
}

const closeWindow = () => {
  Quit()
}
</script>

<style scoped>
.close-btn:hover {
  background-color: red;
}

.right-section .n-button {
  padding: 0 8px;
}
</style>
