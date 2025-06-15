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

<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";

onMounted(() => {
  emitter.on('selectNode', selectNode)
})

const selectNode = (node) => {
}
</script>

<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2>快照</h2>
    </n-flex>
    <n-flex align="center">
      <n-p>开发中……敬请期待</n-p>
    </n-flex>
  </n-flex>
</template>

<style scoped>

</style>