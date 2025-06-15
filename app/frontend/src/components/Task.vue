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
      <h2>Task线程</h2>
      <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getData">refresh</n-button>
    </n-flex>
    <n-flex align="center">
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">导出为csv</n-button>

    </n-flex>

    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          v-model:checked-row-keys="selectedRowKeys"
          :bordered="false"
          :columns="refColumns(columns)"
          :data="data"
          :max-height="600"
          :pagination="pagination"
          :row-key="rowKey"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>

  <n-drawer v-model:show="drawerVisible" style="width: 38.2%">
    <n-drawer-content style="text-align: left;" title="结果">
      <n-code :code="json_data" language="json" show-line-numbers/>
    </n-drawer-content>
  </n-drawer>

</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NDropdown, NIcon, NTag, NText, useMessage} from 'naive-ui'
import {createCsvContent, download_file, formatDate, formattedJson, refColumns, renderIcon} from "../utils/common";
import {DriveFileMoveTwotone, DeleteOutlined, RefreshOutlined} from "@vicons/material";
import {
  GetTasks, CancelTasks
} from "../../wailsjs/go/service/ESService";

const drawerVisible = ref(false)
const json_data = ref()

const loading = ref(false)
const data = ref([])
const message = useMessage()
const selectedRowKeys = ref([]);
const rowKey = (row) => row['task_id']

const selectNode = async (node) => {
  drawerVisible.value = false
  json_data.value = null
  loading.value = false
  data.value = []
  selectedRowKeys.value = []

  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})


const getData = async () => {
  const res = await GetTasks()
  console.log(res)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    console.log(res)
    data.value = res.results
  }

}

const CancelTask = async (row) => {
  loading.value = true
  const res = await CancelTasks(row['task_id'])
  console.log(res)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawerVisible.value = true
  }

  loading.value = false
  await getData()
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
  itemCount: data.value.length
})


const columns = [
  {
    title: '任务id',
    key: 'task_id',
    width: 80,
  },
  {
    title: '父任务id',
    key: 'parent_task_id',
    width: 80,
  },
  {
    title: '任务节点',
    key: 'node_name',
    width: 60,
  },
  {title: 'IP', key: 'node_ip', width: 60,},
  {title: '类型', key: 'type', width: 60,},
  {
    title: '任务行为',
    key: 'action',
    width: 120,
    render: (row) => h(NTag, {type: "info"}, {default: () => row['action']}),
  },
  {
    title: '开始时间',
    key: 'start_time_in_millis',
    width: 60,
    render(row) {
      // 将毫秒时间戳转换为 Date 对象
      const date = new Date(row['start_time_in_millis']);
      // 格式化日期时间
      return h('span', null, formatDate(date));
    },
  },
  {
    title: '运行时间',
    key: 'running_time_in_nanos',
    width: 60,
  },
  // 在 Vue 的模板中，布尔值会被转换为空字符串！！！
  {
    title: '是否可取消',
    key: 'cancellable',
    width: 60,
    render: (row) => h(NTag,
        {type: row['cancellable'] ? "error" : "info"},
        {default: () => row['cancellable'] ? '是' : '否'}
    ),
  },
  {
    title: '操作',
    key: 'actions',
    width: 60,
    render: (row) => {
      return h(
          NButton,
          {
            strong: true,
            secondary: true,
            onClick: () => CancelTask(row),
            disabled: !row['cancellable'],
          },
          {
            default: () => '终止', icon: () => h(NIcon, null, {default: () => h(DeleteOutlined)})
          }
      )
    }
  }
]


// 下载所有数据的 CSV 文件
const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns)
  download_file(csvContent, '任务列表.csv', 'text/csv;charset=utf-8;')
}

</script>


<style scoped>

</style>