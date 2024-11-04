<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";

onMounted(async () => {
  emitter.on('selectNode', selectNode)
})

const selectNode = (node) => {}
</script>

<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2 style="max-width: 200px;">快照</h2>
    </n-flex>
    <n-flex align="center">
      <n-p>开发中……敬请期待</n-p>
    </n-flex>
  </n-flex>
</template>

<style scoped>

</style>