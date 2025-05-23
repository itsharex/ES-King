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
      <h2 style="max-width: 200px;">节点</h2>
      <n-button @click="getData" text :render-icon="renderIcon(RefreshOutlined)">refresh</n-button>
      <n-text>共计{{ data.length }}个</n-text>
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">导出为csv</n-button>

    </n-flex>
    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          ref="tableRef"
          :columns="columns"
          :data="data"
          size="small"
          :bordered="false"
          striped
          :pagination="pagination"
      />
    </n-spin>
  </n-flex>
</template>
<script setup>
import {onMounted} from "vue";
import emitter from "../utils/eventBus";
import { h, ref, computed } from 'vue'
import {NButton, NDataTable, NProgress, NTag, NText, useMessage} from 'naive-ui'
import {createCsvContent, download_file, renderIcon} from "../utils/common";
import {DriveFileMoveTwotone, RefreshOutlined} from "@vicons/material";
import {GetNodes} from "../../wailsjs/go/service/ESService";

const selectNode = async (node) => {
  await getData()
}

onMounted( () => {
  emitter.on('selectNode', selectNode)
  getData()
})


const loading = ref(false)
const data = ref([])
const message = useMessage()
const tableRef = ref();

const getData = async () => {
  loading.value = true
  const res = await GetNodes()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.results
  }
  loading.value = false

}

const getProgressType = (value) => {
  const numValue = Number(value)
  if (numValue < 60) return 'success'
  if (numValue < 80) return 'warning'
  return 'error'
}

const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns)
  download_file(csvContent, '节点列表.csv', 'text/csv;charset=utf-8;')
}

const renderProgress = (row, key) => {
  const value = Number(row[key])
  return h(NProgress, {
    type:"line",
    status: getProgressType(value),
    percentage: value,
    indicatorPlacement: 'inside',
    height: 18,
    borderRadius: 4
  })
}

const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [5, 10, 20, 30, 40],
  onChange: (page) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  },
})

const columns = [
  { title: 'IP', key: 'ip', sorter: 'default',width: 100,resizable: true },
  { title: '名称', key: 'name', sorter: 'default',width: 100,resizable: true },
  {
    title: '角色',
    key: 'node.role',
    sorter: 'default',
    render: (row) => h(NTag, { type: 'info' }, { default: () => row['node.role'] }),
    width: 100
  },
  {
    title: '主节点',
    key: 'master',
    sorter: 'default',
    render: (row) => h(NTag, { type: row.master === '*' ? 'success' : 'default' }, { default: () => row.master === '*' ? '是' : '否' }),
    width: 70
  },
  {
    title: '堆使用率',
    key: 'heap.percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'heap.percent'),
    width: 100
  },
  {
    title: '内存使用率',
    key: 'ram.percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'ram.percent'),
    width: 100
  },
  {
    title: '磁盘使用率',
    key: 'disk.used_percent',
    sorter: 'default',
    render: (row) => renderProgress(row, 'disk.used_percent'),
    width: 100
  },
  {
    title: 'CPU使用率',
    key: 'cpu',
    sorter: 'default',
    render: (row) => renderProgress(row, 'cpu'),
    width: 100
  },
  {
    title: '5m负载',
    key: 'load_5m',
    sorter: 'default',
    width: 60
  },
  {
    title: '内存使用',
    key: 'memory',
    render: (row) => h(NText, { depth: 3 }, { default: () => `字段: ${row.fielddataMemory} | 查询: ${row.queryCacheMemory} | 请求: ${row.requestCacheMemory} | 段: ${row.segmentsMemory}` }),
    width: 100,
    ellipsis: {  // 带提示的省略
      tooltip: true
    }
  },
  {
    title: '段总数',
    key: 'segments.count',
    sorter: 'default',
    width: 60,
    ellipsis: {  // 带提示的省略
      tooltip: true
    }
  }
]



</script>



<style scoped>

</style>