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
  <n-flex vertical>
    <n-flex align="center">
      <h2>关于</h2>
    </n-flex>
  </n-flex>
  <n-flex align="center">

    <n-form label-placement="top" style="text-align: left;">
      <n-form-item label="项目主页">
        <n-button @click="BrowserOpenURL(home_url)" :render-icon="renderIcon(HouseTwotone)">ES-King</n-button>
      </n-form-item>
      <n-form-item label="推荐同款 Kafka 客户端">
        <n-button @click="BrowserOpenURL(kafka_home_url)" :render-icon="renderIcon(HouseTwotone)">KafKa-King</n-button>
      </n-form-item>
      <n-form-item label="技术交流群">
        <n-button :focusable="false" @click="openUrl(qq_url)">点我加群✨</n-button>
      </n-form-item>

    </n-form>
  </n-flex>
</template>

<script setup>
import {onMounted} from 'vue'
import {NButton, NForm, NFormItem, useMessage,} from 'naive-ui'
import {BrowserOpenURL} from "../../wailsjs/runtime";
import {openUrl, renderIcon} from "../utils/common";
import {HouseTwotone} from '@vicons/material'

const kafka_home_url = "https://github.com/Bronya0/kafka-King"
const qq_url = "https://qm.qq.com/cgi-bin/qm/qr?k=pDqlVFyLMYEEw8DPJlRSBN27lF8qHV2v&jump_from=webapi&authKey=Wle/K0ARM1YQWlpn6vvfiZuMedy2tT9BI73mUvXVvCuktvi0fNfmNR19Jhyrf2Nz"
const home_url = "https://github.com/Bronya0/ES-King"


const message = useMessage()

onMounted(async () => {

})


</script>