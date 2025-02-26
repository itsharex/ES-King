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
  <n-config-provider
      :theme="Theme"
      :hljs="hljs"
      :locale="zhCN" :date-locale="dateZhCN"
  >
    <!--https://www.naiveui.com/zh-CN/os-theme/components/layout-->
    <n-message-provider container-style=" word-break: break-all;">
      <n-notification-provider placement="bottom-right" container-style="text-align: left;">
        <n-dialog-provider>
          <n-loading-bar-provider>

            <n-layout has-sider position="absolute" style="height: 100vh;" :class="headerClass">
              <!--header-->
              <n-layout-header bordered style="height: 42px; bottom: 0; padding: 0; ">
                <Header />
              </n-layout-header>
              <!--side + content-->
              <n-layout has-sider position="absolute" style="top: 42px; bottom: 0;">
                <n-layout-sider
                    bordered
                    collapse-mode="width"
                    :collapsed-width="60"
                    :collapsed="true"
                    style="--wails-draggable:drag"
                >
                  <Aside
                      :collapsed-width="60"
                      :value="activeItem.key"
                      :options="sideMenuOptions"
                  />

                </n-layout-sider>
                <n-layout-content style="padding: 0 16px;">
                  <keep-alive>
                    <component :is="activeItem.component"></component>
                  </keep-alive>

                </n-layout-content>
              </n-layout>
            </n-layout>
          </n-loading-bar-provider>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {onMounted, ref, shallowRef} from 'vue'
import {
  darkTheme,
  lightTheme,
  NConfigProvider,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NMessageProvider,
} from 'naive-ui'
import Header from './components/Header.vue'
import Settings from './components/Settings.vue'
import Health from './components/Health.vue'
import Core from './components/Core.vue'
import Nodes from './components/Nodes.vue'
import Index from './components/Index.vue'
import Rest from './components/Rest.vue'
import Conn from './components/Conn.vue'
import Task from './components/Task.vue'
import Snapshot from './components/Snapshot.vue'
import About from './components/About.vue'
import {GetConfig, SaveTheme} from "../wailsjs/go/config/AppConfig";
import {WindowSetSize} from "../wailsjs/runtime";
import {renderIcon} from "./utils/common";
import Aside from "./components/Aside.vue";
import emitter from "./utils/eventBus";
import {
  FavoriteTwotone,
  HiveOutlined,
  SettingsSuggestOutlined, TaskAltFilled,
  ApiOutlined, LibraryBooksOutlined, AllOutOutlined, BarChartOutlined, AddAPhotoTwotone, InfoOutlined
} from '@vicons/material'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'
import { zhCN, dateZhCN } from 'naive-ui'

let headerClass = shallowRef('lightTheme')
let Theme = shallowRef(lightTheme)


hljs.registerLanguage('json', json)

onMounted(async () => {
  // 从后端加载配置
  const loadedConfig = await GetConfig()
  // 设置主题
  themeChange(loadedConfig.theme === darkTheme.name ? darkTheme:lightTheme)
  // 语言切换
  // handleLanguageChange(loadedConfig.language)

  // =====================注册事件监听=====================
  // 主题切换
  emitter.on('update_theme', themeChange)
  // 菜单切换
  emitter.on('menu_select', handleMenuSelect)
})


// 左侧菜单
const sideMenuOptions = [
  {
    label: '集群',
    key: '集群',
    icon: renderIcon(HiveOutlined),
    component: Conn,
  },
  {
    label: '节点',
    key: '节点',
    icon: renderIcon(AllOutOutlined),
    component: Nodes,
  },
  {
    label: '索引',
    key: '索引',
    icon: renderIcon(LibraryBooksOutlined),
    component: Index,
  },
  {
    label: 'REST',
    key: 'REST',
    icon: renderIcon(ApiOutlined),
    component: Rest,
  },
  {
    label: 'Task',
    key: 'Task',
    icon: renderIcon(TaskAltFilled),
    component: Task,
  },
  {
    label: '健康',
    key: '健康',
    icon: renderIcon(FavoriteTwotone),
    component: Health,
  },
  {
    label: '指标',
    key: '指标',
    icon: renderIcon(BarChartOutlined),
    component: Core,
  },
  {
    label: '快照',
    key: '快照',
    icon: renderIcon(AddAPhotoTwotone),
    component: Snapshot,
  },
  {
    label: '设置',
    key: '设置',
    icon: renderIcon(SettingsSuggestOutlined),
    component: Settings
  },
  {
    label: "关于",
    key: "about",
    icon: renderIcon(InfoOutlined),
    component: About
  },
]
const activeItem = shallowRef(sideMenuOptions[0])

// 切换菜单
function handleMenuSelect(key) {
  // 根据key寻找item
  activeItem.value = sideMenuOptions.find(item => item.key === key)
}

// 主题切换
function themeChange(newTheme) {
  Theme.value = newTheme
  headerClass = newTheme === lightTheme ? "lightTheme" : "darkTheme"
}


</script>

<style>
body {
  margin: 0;
  font-family: sans-serif;

}

.lightTheme .n-layout-header {
  background-color: #f7f7fa;
}

.lightTheme .n-layout-sider {
  background-color: #f7f7fa !important;
}
</style>