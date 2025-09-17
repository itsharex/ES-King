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
      <h2>节点</h2>
      <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getData">refresh</n-button>
      <n-text>共计{{ data.length }}个</n-text>
      <n-button :render-icon="renderIcon(RefreshOutlined)" @click="getData">刷新</n-button>
      <n-button :render-icon="renderIcon(DriveFileMoveTwotone)" @click="downloadAllDataCsv">导出为csv</n-button>
      <n-text>集群名：{{cluster_name}}</n-text>

    </n-flex>
    <n-spin :show="loading" description="Connecting...">
      <n-data-table
          ref="tableRef"
          :bordered="false"
          :columns="refColumns(columns)"
          :data="data"
          :pagination="pagination"
          size="small"
          striped
      />
    </n-spin>
  </n-flex>
</template>
<script setup>
import {h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NDataTable, NFlex, NProgress, NTag, NText, NTooltip, useMessage} from 'naive-ui'
import {
  createCsvContent,
  download_file,
  formatBytes,
  formatMillis, formatMillisToDays,
  formatNumber,
  refColumns,
  renderIcon
} from "../utils/common";
import {DriveFileMoveTwotone, RefreshOutlined} from "@vicons/material";
import {GetNodes} from "../../wailsjs/go/service/ESService";

const selectNode = async (node) => {
  await getData()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  getData()
})


const loading = ref(false)
const data = ref([])
const message = useMessage()
const tableRef = ref();
const cluster_name = ref("");


const getData = async () => {
  loading.value = true;
  const res = await GetNodes();
  if (res.err !== "") {
    message.error(res.err);
    loading.value = false;
    return;
  }
  cluster_name.value = res.result.cluster_name;
  const nodesData = res.result.nodes || {};

  const masterEligibleNodes = Object.keys(nodesData).filter(id => nodesData[id].roles?.includes('master'));
  const masterNodeId = masterEligibleNodes.length > 0 ? masterEligibleNodes[0] : null;

  const flattenedData = Object.values(nodesData).map(node => {
    // --- 安全地访问嵌套属性 ---
    const diskTotal = node.fs?.total?.total_in_bytes ?? 0;
    const diskFree = node.fs?.total?.available_in_bytes ?? 0;
    const diskUsedPercent = diskTotal > 0 ? Math.round(((diskTotal - diskFree) / diskTotal) * 100) : 0;

    // 为每个可能缺失的嵌套对象提供一个空对象作为默认值，简化后续访问
    const indices = node.indices ?? {};
    const search = indices.search ?? {};
    const merges = indices.merges ?? {};
    const query_cache = indices.query_cache ?? {};
    const fielddata = indices.fielddata ?? {};
    const request_cache = indices.request_cache ?? {};
    const segments = indices.segments ?? {};
    const jvm = node.jvm ?? {};
    const jvm_mem = jvm.mem ?? {};
    const os_cpu = node.os?.cpu ?? {};
    const process = node.process ?? {};
    const fs_total = node.fs?.total ?? {};
    const fs_io = node.fs?.io_stats?.total ?? {};

    return {
      // 基础信息
      name: node.name,
      ip: node.transport_address?.split(':')[0] ?? 'N/A',
      roles: node.roles || [], // 确保 roles 是一个数组
      is_master: node.name === nodesData[masterNodeId]?.name,
      uptime: jvm.uptime_in_millis ?? 0,

      // 指标
      docs_count: indices.docs?.count ?? 0,
      store_size: indices.store?.size_in_bytes ?? 0,
      disk_total: diskTotal,
      disk_percent: diskUsedPercent,
      load_5m: os_cpu.load_average?.['5m'] ?? 0,
      heap_used_in_bytes: jvm_mem.heap_used_in_bytes ?? 0,
      heap_max_in_bytes: jvm_mem.heap_max_in_bytes ?? 0,
      heap_percent: jvm_mem.heap_used_percent ?? 0,
      segments_count: segments.count ?? 0,

      // 用于 Tooltip 的原始对象
      stats_search: {
        "查询总数": formatNumber(search.query_total ?? 0),
        "查询耗时": formatMillis(search.query_time_in_millis ?? 0),
        "拉取总数": formatNumber(search.fetch_total ?? 0),
        "拉取耗时": formatMillis(search.fetch_time_in_millis ?? 0),
        "滚动总数": formatNumber(search.scroll_total ?? 0),
        "滚动耗时": formatMillis(search.scroll_time_in_millis ?? 0),
      },
      stats_merges: {
        "合并总数": formatNumber(merges.total ?? 0),
        "合并总耗时": formatMillis(merges.total_time_in_millis ?? 0),
        "合并文档总数": formatNumber(merges.total_docs ?? 0),
        "合并总大小": formatBytes(merges.total_size_in_bytes ?? 0),
        "当前合并数": merges.current ?? 0,
      },
      stats_cache: `查询缓存: ${formatBytes(query_cache.memory_size_in_bytes ?? 0)} |
      Fielddata: ${formatBytes(fielddata.memory_size_in_bytes ?? 0)} |
      请求缓存: ${formatBytes(request_cache.memory_size_in_bytes ?? 0)} |
      段内存: ${formatBytes(segments.memory_in_bytes ?? 0)}`,

      stats_cache_size: (query_cache.memory_size_in_bytes ?? 0) + (fielddata.memory_size_in_bytes ?? 0) + (request_cache.memory_size_in_bytes ?? 0)
          + (segments.memory_in_bytes ?? 0),

      stats_segments: {
        "段总数": formatNumber(segments.count ?? 0),
        "总内存占用": formatBytes(segments.memory_in_bytes ?? 0),
        "词项 (Terms)": formatBytes(segments.terms_memory_in_bytes ?? 0),
        "存储字段 (Stored Fields)": formatBytes(segments.stored_fields_memory_in_bytes ?? 0),
        "Doc Values": formatBytes(segments.doc_values_memory_in_bytes ?? 0),
        "Norms": formatBytes(segments.norms_memory_in_bytes ?? 0),
      },
      stats_process: {
        "打开文件描述符": `${formatNumber(process.open_file_descriptors ?? 0)} / ${formatNumber(process.max_file_descriptors ?? 0)}`,
        "进程CPU使用率": `${process.cpu?.percent ?? 0}%`,
        "虚拟内存占用": formatBytes(process.mem?.total_virtual_in_bytes ?? 0),
      },
      stats_fs: {
        "总空间": formatBytes(fs_total.total_in_bytes ?? 0),
        "可用空间": formatBytes(fs_total.available_in_bytes ?? 0),
        "IO读操作": formatNumber(fs_io.read_operations ?? 0),
        "IO写操作": formatNumber(fs_io.write_operations ?? 0),
        "IO读流量": formatBytes((fs_io.read_kilobytes ?? 0) * 1024),
        "IO写流量": formatBytes((fs_io.write_kilobytes ?? 0) * 1024),
      }
    };
  });

  flattenedData.sort((a, b) => (b.heap_percent ?? 0) - (a.heap_percent ?? 0));
  data.value = flattenedData;
  loading.value = false;
};

/**
 * 创建一个通用的 Tooltip 内容 VNode
 * @param {object} stats - 键值对对象
 * @param {boolean} formatValueAsBytes - 是否将值格式化为字节
 */
function createTooltipContent(stats, formatValueAsBytes = false) {
  return h(NFlex, { vertical: true, style: { maxWidth: '400px', textAlign: 'left'} }, () =>
      Object.entries(stats).map(([key, value]) =>
          h(NText, null, () => `${key}: ${formatValueAsBytes ? formatBytes(value) : value}`)
      )
  );
}

const getProgressType = (value) => {
  const numValue = Number(value)
  if (numValue < 60) return 'success'
  if (numValue < 80) return 'warning'
  return 'error'
}

const downloadAllDataCsv = () => {
  if (!data.value || data.value.length === 0) {
    message.warning("没有数据可以导出");
    return;
  }

  // 1. 定义基础列和需要特殊处理的列
  const exportColumns = [
    { title: '节点名', key: 'name' },
    { title: 'IP', key: 'ip' },
    { title: '角色', getCsvValue: (row) => row.roles.map(role => roleMap[role.charAt(0)] || role).join('/') },
    { title: 'CPU负载(5m)', key: 'load_5m' },
    { title: '运行时间', getCsvValue: (row) => formatMillisToDays(row.uptime) },
    { title: '总文档数', getCsvValue: (row) => formatNumber(row.docs_count) },
    { title: '段总数', getCsvValue: (row) => formatNumber(row.segments_count) },
    { title: '堆内存使用率(%)', key: 'heap_percent' },
    { title: '堆内存已用', getCsvValue: (row) => formatBytes(row.heap_used_in_bytes) },
    { title: '堆内存上限', getCsvValue: (row) => formatBytes(row.heap_max_in_bytes) },
    { title: '磁盘使用率(%)', key: 'disk_percent' },
    { title: '已用空间', getCsvValue: (row) => formatBytes(row.store_size) },
    { title: '总空间', getCsvValue: (row) => formatBytes(row.disk_total) },
    { title: '缓存总大小', getCsvValue: (row) => formatBytes(row.stats_cache_size) },
    {
      title: '缓存详情',
      key: 'stats_cache',
      // 清理字符串中的换行和多余空格，使其在CSV中保持单行
      getCsvValue: (row) => (row.stats_cache || '').replace(/\s+/g, ' ').trim()
    },
  ];

  // 2. 动态地将所有嵌套的性能/系统指标对象平铺展开，作为新的列
  const firstRow = data.value[0];
  // 定义需要平铺展开的数据对象的键名和在CSV表头中使用的前缀
  const statsToFlatten = {
    '搜索': 'stats_search',
    '合并': 'stats_merges',
    '段指标': 'stats_segments',
    '进程': 'stats_process',
    '文件系统': 'stats_fs',
  };

  for (const [prefix, dataKey] of Object.entries(statsToFlatten)) {
    // 确保数据源中存在这个对象
    if (firstRow && typeof firstRow[dataKey] === 'object' && firstRow[dataKey] !== null) {
      // 遍历对象中的每一个键（如 "查询总数", "查询耗时" 等）
      for (const statKey in firstRow[dataKey]) {
        exportColumns.push({
          // CSV 表头，例如："搜索 - 查询总数"
          title: `${prefix} - ${statKey}`,
          // 使用闭包来捕获正确的 dataKey 和 statKey，从每一行数据中提取对应的值
          getCsvValue: (row) => row[dataKey]?.[statKey] ?? '',
        });
      }
    }
  }

  // 3. 生成并下载 CSV 文件
  try {
    const csvContent = createCsvContent(data.value, exportColumns);
    const fileName = `es-nodes-${cluster_name.value || 'export'}.csv`;
    download_file(csvContent, fileName, 'text/csv;charset=utf-8;');
    message.success("CSV 文件导出成功");
  } catch (e) {
    message.error("导出失败: " + e.message);
    console.error("CSV export error:", e);
  }
};

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

const roleMap = { m: '主', d: '数据', i: 'Ingest', l: 'ML', c: '协调', r: '远程', t: '转换', h: '热', w: '温', f: '冻', v: '投票' };

const columns = [
  { title: '节点名', key: 'name', width: 120,
    fixed: 'left' // 可以选择固定列
  },
  { title: 'IP', key: 'ip', width: 120 },
  {
    title: '角色', key: 'roles', width: 120,
    render: (row) => row.roles.map(role => roleMap[role.charAt(0)] || role).join('/')
  },
  { title: 'CPU负载', key: 'load_5m', width: 100 },
  {
    title: '堆内存使用率', key: 'heap_percent', width: 160,
    render: (row) => h(NFlex, { vertical: true }, () => [
      h(NText, null, () => `${formatBytes(row.heap_used_in_bytes)} / ${formatBytes(row.heap_max_in_bytes)}`),
      h(NProgress, { type: "line", percentage: row.heap_percent, status: getProgressType(row.heap_percent), indicatorPlacement: 'inside', borderRadius: 4, })
    ]),
    sorter: (a, b) => a.heap_percent - b.heap_percent
  },
  {
    title: '磁盘使用率', key: 'disk_percent', width: 160,
    render: (row) => h(NFlex, { vertical: true }, () => [
      h(NText, null, () => `${formatBytes(row.store_size)} / ${formatBytes(row.disk_total)}`),
      h(NProgress, { type: "line", percentage: row.disk_percent, status: getProgressType(row.disk_percent), indicatorPlacement: 'inside', borderRadius: 4, })
    ]),
    sorter: (a, b) => a.disk_percent - b.disk_percent
  },

  {
    title: '性能指标', key: 'perf', width: 160,
    render: (row) => h(NFlex, null, () => [
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => '搜索' }), default: () => createTooltipContent(row.stats_search) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => '合并' }), default: () => createTooltipContent(row.stats_merges) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'primary' }, { default: () => '段' }), default: () => createTooltipContent(row.stats_segments) }),
    ])
  },
  {
    title: '系统指标', key: 'sys', width: 120,
    render: (row) => h(NFlex, null, () => [
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'info' }, { default: () => '进程' }), default: () => createTooltipContent(row.stats_process) }),
      h(NTooltip, null, { trigger: () => h(NTag, { type: 'info' }, { default: () => 'FS' }), default: () => createTooltipContent(row.stats_fs) }),
    ])
  },
  {title: '缓存', key: 'cache', width: 100, render: (row) => row.stats_cache,
    sorter: (a, b) => a.stats_cache_size - b.stats_cache_size
  },
  {title: '总文档数', key: 'docs_count', width: 100, render: (row) => formatNumber(row.docs_count),},
  { title: '段总数', key: 'segments_count', width: 100, render: (row) => formatNumber(row.segments_count)},
  { title: '运行时间', key: 'uptime', width: 90, render: (row) => formatMillisToDays(row.uptime) },

];


</script>


<style scoped>

</style>