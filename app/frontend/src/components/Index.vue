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
      <h2 style="max-width: 200px;">索引</h2>
      <n-text>共计{{ data.length }}个</n-text>
    </n-flex>
    <n-flex align="center">
      <n-input @keydown.enter="search" v-model:value="search_text" autosize style="min-width: 20%"
               placeholder="模糊搜索索引"/>

      <n-button @click="search" :render-icon="renderIcon(SearchFilled)"></n-button>
      <n-button @click="CreateIndexDrawerVisible = true" :render-icon="renderIcon(AddFilled)">添加索引</n-button>
      <n-button @click="downloadAllDataCsv" :render-icon="renderIcon(DriveFileMoveTwotone)">导出为csv</n-button>
      <n-button @click="queryAlias" :render-icon="renderIcon(AnnouncementOutlined)">读取别名</n-button>
      <n-button @click="downloadIndexConfig.show = true" :render-icon="renderIcon(DriveFileMoveTwotone)"
                :loading="downloadIndexConfig.loading">
        索引备份（预览）
      </n-button>

    </n-flex>

    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          ref="tableRef"
          :columns="columns"
          :data="data"
          :pagination="pagination"
          size="small"
          :bordered="false"
          striped
          :row-key="rowKey"
          v-model:checked-row-keys="selectedRowKeys"
      />
    </n-spin>
    <n-flex align="center">
      <n-dropdown :options="bulk_options">
        <n-button>批量操作</n-button>
      </n-dropdown>
      <n-text> 你选中了 {{ selectedRowKeys.length }} 行。</n-text>
    </n-flex>

    <n-drawer v-model:show="downloadIndexConfig.show" style="width: 38.2%">
      <n-drawer-content title="索引备份（预览）" style="text-align: left;">
        <n-flex vertical>
          <n-p>【当前该功能还在测试中，使用请输入QQ群号，否则无法下载。如果遇到了bug，请反馈给群主。】</n-p>
          输入要备份的索引名称
          <n-input v-model:value="downloadIndexConfig.indexName"/>
          输入查询dsl，不写默认查询所有
          <n-input type="textarea" style="min-height: 300px; max-height: 800px;"
                   v-model:value="downloadIndexConfig.dsl"/>
          测试码，也就是QQ群号，请在github上查看
          <n-input v-model:value="downloadIndexConfig.code"/>
          <n-flex align="center">
            <n-button @click="downloadIndexConfig.show = false">取消</n-button>
            <n-button type="primary" @click="downloadIndex" :loading="downloadIndexConfig.loading">开始下载</n-button>
          </n-flex>
          {{ downloadIndexConfig.msg }}
        </n-flex>
      </n-drawer-content>
    </n-drawer>


    <n-drawer v-model:show="drawerVisible" style="width: 38.2%">
      <n-drawer-content :title="drawer_title" style="text-align: left;">
        <n-code :code="json_data" language="json" show-line-numbers/>
      </n-drawer-content>
    </n-drawer>

    <!--    添加index-->
    <n-drawer v-model:show="CreateIndexDrawerVisible" style="width: 38.2%">
      <n-drawer-content title="创建索引" style="text-align: left;">
        <n-form
            :model="indexConfig"
            label-placement="top"
            style="text-align: left;"
            ref="formRef"
            :rules="{
              name: {required: true, message: '请输入索引名称', trigger: 'blur'},
              numberOfShards: {required: true, type: 'number', message: '请输入主分片', trigger: 'blur'},
              numberOfReplicas: {required: true, type: 'number', message: '请输入副本数量', trigger: 'blur'},
            }"
        >
          <n-form-item label="索引名称" path="name">
            <n-input v-model:value="indexConfig.name"/>
          </n-form-item>
          <n-form-item label="主分片" path="numberOfShards">
            <n-input-number v-model:value="indexConfig.numberOfShards"/>
          </n-form-item>
          <n-form-item label="副本数量" path="numberOfReplicas">
            <n-input-number v-model:value="indexConfig.numberOfReplicas"/>
          </n-form-item>
          <n-p>mapping</n-p>
          <n-form-item path="mapping">
            <n-input v-model:value="indexConfig.mapping" type="textarea" style="min-height: 300px; max-height: 800px;"
                     placeholder='输入mapping的json，例如
{
  "properties": {
    "created_at": {
      "type": "date",
      "format": "yyyy-MM-dd HH:mm:ss"
    }
  }
}'/>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="CreateIndexDrawerVisible = false">取消</n-button>
            <n-button type="primary" @click="addIndex" :loading="addIndexLoading">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>

    <!--    添加doc-->
    <n-drawer v-model:show="addDocDrawerVisible" style="width: 38.2%">
      <n-drawer-content title="添加文档" style="text-align: left;">
        <n-form
            :model="docConfig"
            label-placement="top"
            style="text-align: left;"
            :rules="{
              doc: {required: true, message: '请输入文档内容', trigger: 'blur'},
            }"
        >
          <n-form-item label="文档内容" path="doc">
            <n-input v-model:value="docConfig.doc" type="textarea" style="min-height: 300px; max-height: 800px;"
                     placeholder='输入文档的json，例如
{
  "field1": "value1",
  "field2": "value2"
}'/>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="addDocDrawerVisible = false">取消</n-button>
            <n-button type="primary" @click="addDocumentFunc" :loading="addDocLoading">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </n-flex>
</template>

<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NDropdown, NIcon, NTag, NText, useDialog, useMessage} from 'naive-ui'
import {createCsvContent, download_file, formatBytes, formattedJson, isValidJson, renderIcon} from "../utils/common";
import {AddFilled, AnnouncementOutlined, DriveFileMoveTwotone, MoreVertFilled, SearchFilled} from "@vicons/material";
import {
  AddDocument,
  CacheClear,
  CreateIndex,
  DeleteIndex,
  DownloadESIndex,
  Flush,
  GetDoc10,
  GetIndexAliases,
  GetIndexes,
  GetIndexInfo,
  MergeSegments,
  OpenCloseIndex,
  Refresh,
} from "../../wailsjs/go/service/ESService";

// 抽屉的可见性
const drawerVisible = ref(false)
const CreateIndexDrawerVisible = ref(false)
const json_data = ref({})
const drawer_title = ref("")
const loading = ref(false)
const tableRef = ref();
const formRef = ref();
const indexConfig = ref({
  name: "",
  numberOfShards: 1,
  numberOfReplicas: 0,
  mapping: "",
});
const data = ref([])
const message = useMessage()
const dialog = useDialog()

const search_text = ref("")
const selectedRowKeys = ref([]);
const rowKey = (row) => row.index
let aliases = {};


const downloadIndexConfig = ref({
  indexName: "",
  dsl: "",
  loading: false,
  show: false,
  code: null,
  msg: null,
});

const downloadIndex = async () => {

  const indexName = downloadIndexConfig.value.indexName; // 或者从其他地方获取
  const dsl = downloadIndexConfig.value.dsl; // 或者从其他地方获取

  if (!indexName) {
    message.error("请填写索引名");
    return;
  }
  if (downloadIndexConfig.value.code !== "964440643") {
    message.error("群号错误，请在github上查看");
    return;
  }
  const file_path = `/${indexName}-${Math.floor(Date.now() / 1000)}.json`
  message.info("开始下载，请不要退出...数据json位置：" + file_path);
  downloadIndexConfig.value.msg = "开始下载，请不要退出...数据json位置：" + file_path;

  downloadIndexConfig.value.loading = true;
  try {
    const res = await DownloadESIndex(indexName, dsl, file_path);
    if (res.err !== "") {
      message.error(res.err);
      downloadIndexConfig.value.msg = res.err;
    } else {
      message.success("备份成功");
      downloadIndexConfig.value.msg = "备份成功";
      CreateIndexDrawerVisible.value = false;
    }
  } catch (e) {
    message.error(e.message);
    downloadIndexConfig.value.msg = e;
  } finally {
    downloadIndexConfig.value.loading = false;
  }
};

const selectNode = (node) => {
  data.value = []
  selectedRowKeys.value = []
  aliases = []
}


onMounted( () => {
  emitter.on('selectNode', selectNode)
})

const search = async () => {
  loading.value = true
  try {
    await getData(search_text.value)
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false

}


const cacheData = (results) => {
  // 缓存一下
  const key = 'es_king_indexes';
  let values = []
  const stored = localStorage.getItem(key);
  if (stored){
    values = JSON.parse(stored)
    for (let v of results) {
      if (!values.includes(v)) {
        values.push(v);
      }
    }
  }
  if (values){
    localStorage.setItem(key, JSON.stringify(values.slice(-1000)))
  }
}

const getData = async (value) => {
  const res = await GetIndexes(value)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    data.value = res.results
    cacheData(res.results)
  }
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


const getType = (value) => {
  const type = {
    "green": "success",
    "yellow": "warning",
    "open": "success",
    "close": "error",
  }
  return type[value] || 'error'
}

const columns = [
  {
    type: "selection",
  },
  {
    title: '索引名',
    key: 'index',
    sorter: 'default',
    width: 120,
    resizable: true,
    ellipsis: {tooltip: {style: {maxWidth: '800px'},}},
    render: (row) => h(NText, {
          type: 'info',
          style: {cursor: 'pointer'},
          onClick: () => viewIndexDocs(row)
        },
        {default: () => row['index']}
    )
  },
  {title: '别名', key: 'alias', sorter: 'default', width: 60, ellipsis: {tooltip: {style: {maxWidth: '800px'},}}},
  {
    title: '健康',
    key: 'health',
    sorter: 'default',
    render: (row) => h(NTag, {type: getType(row['health'])}, {default: () => row['health']}),
    width: 60
  },
  {
    title: '状态',
    key: 'status',
    sorter: 'default',
    render: (row) => h(NTag, {type: getType(row['status'])}, {default: () => row['status']}),
    width: 40
  },
  {
    title: '主分片',
    key: 'pri',
    sorter: 'default',
    width: 40
  },
  {
    title: '副本',
    key: 'rep',
    sorter: 'default',
    width: 40
  },
  {
    title: '文档总数',
    key: 'docs.count',
    sorter: 'default',
    width: 100
  },
  {
    title: '未清除的已删文档',
    key: 'docs.deleted',
    sorter: 'default',
    width: 100
  },
  {
    title: '占用存储',
    key: 'store.size',
    width: 60,
    sorter: (a, b) => a['store.size'] - b['store.size'],
    render(row) {  // 这里要显示的是label，所以得转换一下
      return h('span', formatBytes(row['store.size']))
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 60,
    render: (row) => {
      const options = [
        {label: '添加文档', key: 'addDocument'},
        {label: '查看索引构成', key: 'viewDetails'},
        {label: '别名', key: 'viewAlias'},
        {label: '查看10条文档', key: 'viewDocs'},
        {label: '段合并', key: 'mergeSegments'},
        {label: '删除索引', key: 'deleteIndex'},
        {label: row.status === 'close' ? '打开索引' : '关闭索引', key: 'openCloseIndex'},
        {label: 'Refresh', key: 'refresh'},
        {label: 'Flush', key: 'flush'},
        {label: '清理缓存', key: 'clearCache'},
      ]
      return h(
          NDropdown,
          {
            trigger: 'click',
            options,
            onSelect: (key) => handleMenuSelect(key, row)
          },
          {
            default: () => h(
                NButton,
                {
                  strong: true,
                  secondary: true,
                },
                {default: () => '操作', icon: () => h(NIcon, null, {default: () => h(MoreVertFilled)})}
            )
          }
      )
    }
  }
]

const handleMenuSelect = async (key, row) => {
  const func = {
    "addDocument": addDocument,
    "viewDetails": viewIndexDetails,
    "viewAlias": viewIndexAlias,
    "viewDocs": viewIndexDocs,
    "mergeSegments": mergeSegments,
    "deleteIndex": deleteIndex,
    "refresh": refreshIndex,
    "openCloseIndex": openCloseIndex,
    "flush": flushIndex,
    "clearCache": clearCache,
  }
  loading.value = true
  try {
    await func[key](row)
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

// 定义各种操作函数
const addDocDrawerVisible = ref(false);
const addDocLoading = ref(false);
const docConfig = ref({
  index: "",
  doc: "",
});

const addDocument = async (row) => {
  addDocDrawerVisible.value = true;
  docConfig.value.index = row.index;
}
const addDocumentFunc = async () => {
  if (!docConfig.value.doc) {
    message.error("请输入文档内容")
    return
  }
  if (!isValidJson(docConfig.value.doc)) {
    message.error("文档内容不是合法的json")
    return
  }
  addDocLoading.value = true;
  try {
    const res = await AddDocument(docConfig.value.index, docConfig.value.doc);
    console.log(res);
    if (res.err !== "") {
      message.error(res.err);
    } else {
      message.success(`文档添加成功，id：` + res.result['_id']);
      await search();
    }
  } catch (e) {
    message.error(e.message);
  } finally {
    addDocLoading.value = false;
    addDocDrawerVisible.value = false;
    docConfig.value.index = "";
    docConfig.value.doc = "";
  }
}


const viewIndexDetails = async (row) => {
  const res = await GetIndexInfo(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const viewIndexAlias = async (row) => {
  const res = await GetIndexAliases([row.index])
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const viewIndexDocs = async (row) => {
  loading.value = true
  try {
    const res = await GetDoc10(row.index)
    if (res.err !== "") {
      message.error(res.err)
    } else {
      json_data.value = formattedJson(res.result)
      drawer_title.value = row.index
      drawerVisible.value = true
    }
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}
const mergeSegments = async (row) => {
  dialog.info({
    title: '警告',
    content: `确定要对索引 ${row.index} 执行 段合并 吗？段合并非常耗资源，将提交给ES后台执行`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await mergeSegmentsFunc(row)
    }
  })
}
const mergeSegmentsFunc = async (row) => {
  const res = await MergeSegments(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    message.success("已提交段合并请求，段合并是重IO任务，请注意集群负载")
    await search()
  }
}
const deleteIndex = async (row) => {
  dialog.info({
    title: '警告',
    content: `确定要删除索引 ${row.index} 吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      await deleteIndexFunc(row)
    }
  })
}
const deleteIndexFunc = async (row) => {
  const res = await DeleteIndex(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()

  }
}
const openCloseIndex = async (row) => {
  const res = await OpenCloseIndex(row.index, row.status)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()

  }
}
const refreshIndex = async (row) => {
  const res = await Refresh(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const flushIndex = async (row) => {
  const res = await Flush(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
  }
}
const clearCache = async (row) => {
  const res = await CacheClear(row.index)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    json_data.value = formattedJson(res.result)
    drawer_title.value = row.index
    drawerVisible.value = true
    await search()

  }
}
const addIndexLoading = ref(false)
const addIndex = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      // 测试mapping有的话，能不能json格式化
      if (indexConfig.value.mapping) {
        const err = isValidJson(indexConfig.value.mapping)
        if (!err) {
          message.error("mapping不是合法的json格式")
          return
        }
      }

      addIndexLoading.value = true
      try {
        const res = await CreateIndex(indexConfig.value.name, indexConfig.value.numberOfShards, indexConfig.value.numberOfReplicas, indexConfig.value.mapping)
        if (res.err !== "") {
          message.error(res.err)
        } else {
          message.success(`索引【${indexConfig.value.name}】创建成功`)
          await search()
        }
      } catch (e) {
        message.error(e.message)
      } finally {
        addIndexLoading.value = false
        CreateIndexDrawerVisible.value = false
      }
    } else {
      message.error('请填写所有必填字段')
    }
  })
}

// 下载所有数据的 CSV 文件
const downloadAllDataCsv = async () => {
  const csvContent = createCsvContent(data.value, columns)
  download_file(csvContent, '索引列表.csv', 'text/csv;charset=utf-8;')
}
const queryAlias = async () => {
  loading.value = true
  let name_lst = []
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  let pagedData = data.value.slice(start, end);
  for (const k in pagedData.value) {
    name_lst.push(pagedData.value[k].index)
  }
  try {
    const res = await GetIndexAliases(name_lst)
    if (res.err !== "") {
      loading.value = false
      message.error(res.err)
      return
    }
    // 合并别名缓存
    // {
    //   "23": "xcx",
    // }
    aliases = {...aliases, ...res.result}
    console.log(aliases)
    for (const k in data.value) {
      const alias = aliases[data.value[k].index]
      if (alias) {
        data.value[k].alias = alias
      }
    }
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

const bulk_delete = async () => {
  loading.value = true
  let success_count = 0
  for (const Key in selectedRowKeys.value) {
    const res = await DeleteIndex(selectedRowKeys.value[Key])
    if (res.err !== "") {
      message.error(res.err)
      break
    } else {
      success_count += 1
    }
  }
  // 重置
  selectedRowKeys.value = []
  // 提示删除了几个，失败了几个
  message.success(`成功删除 ${success_count} 个索引`)
  loading.value = false
  await search()
}
const bulk_options = [
  {
    label: '批量删除',
    key: 'bulk_delete',
    props: {
      onClick: async () => {
        dialog.info({
          title: '警告',
          content: `确定要删除索引 ${selectedRowKeys.value} 吗？`,
          positiveText: '确定',
          negativeText: '取消',
          onPositiveClick: async () => {
            await bulk_delete()
          }
        })
      }
    }
  },
]
</script>


<style scoped>

</style>