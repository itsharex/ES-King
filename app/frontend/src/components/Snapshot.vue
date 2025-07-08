<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2>快照</h2>
      <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getData">刷新</n-button>
    </n-flex>
    <n-spin :show="loading" description="加载中...">
      <n-data-table
          :bordered="false"
          :columns="columns"
          :data="data"
          :max-height="600"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>
</template>

<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NTag, useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {RefreshOutlined} from "@vicons/material";
import {GetSnapshots} from "../../wailsjs/go/service/ESService";

const loading = ref(false)
const data = ref([])
const message = useMessage()

const selectNode = async (node) => {
  data.value = []
  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})

const getData = async () => {
  loading.value = true
  const res = await GetSnapshots()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.Results || []
  }
  loading.value = false
}

const columns = [
  {
    title: '快照名称',
    key: 'snapshot',
    width: 150,
  },
  {
    title: '仓库',
    key: 'repository',
    width: 150,
  },
  {
    title: '状态',
    key: 'state',
    width: 100,
    render: (row) => h(NTag, {
      type: row.state === 'SUCCESS' ? "success" :
          row.state === 'FAILED' ? "error" : "warning"
    }, {default: () => row.state}),
  },
  {
    title: '开始时间',
    key: 'start_time',
    width: 150,
  },
  {
    title: '结束时间',
    key: 'end_time',
    width: 150,
  },
  {
    title: '索引数量',
    key: 'indices',
    width: 100,
    render: (row) => Array.isArray(row.indices) ? row.indices.length : 0,
  },
  {
    title: '总分片数',
    key: 'total_shards',
    width: 100,
  },
  {
    title: '成功分片数',
    key: 'successful_shards',
    width: 100,
  }
]
</script>


<style scoped>

</style>