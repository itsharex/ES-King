<template>
  <n-flex vertical>
    <n-flex align="center">
      <h2>快照管理</h2>
    </n-flex>
    <n-tabs type="line" animated>
      <!-- ==================== Tab 1: 仓库管理 ==================== -->
      <n-tab-pane name="repo" tab="仓库管理">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getRepos">刷新</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="repoForm.show = true">创建仓库</n-button>
          </n-flex>
          <n-spin :show="repoLoading" description="加载中...">
            <n-data-table
                :bordered="false"
                :columns="repoColumns"
                :data="repoData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <!-- 创建仓库弹窗 -->
        <n-modal v-model:show="repoForm.show" preset="dialog" title="创建快照仓库" positive-text="确认" negative-text="取消"
                 @positive-click="handleCreateRepo">
          <n-form label-placement="left" label-width="auto">
            <n-form-item label="仓库名称">
              <n-input v-model:value="repoForm.name" placeholder="my_backup_repo"/>
            </n-form-item>
            <n-form-item label="仓库类型">
              <n-select v-model:value="repoForm.type" :options="repoTypeOptions"/>
            </n-form-item>
            <n-form-item label="Settings (JSON)">
              <n-input v-model:value="repoForm.settings" type="textarea" :autosize="{minRows: 3, maxRows: 8}"
                       placeholder='例如: {"location": "/mount/backups/my_backup"}' />
            </n-form-item>
          </n-form>
        </n-modal>
      </n-tab-pane>

      <!-- ==================== Tab 2: 快照管理 ==================== -->
      <n-tab-pane name="snapshot" tab="快照管理">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getSnapshots">刷新</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="snapForm.show = true">创建快照</n-button>
          </n-flex>
          <n-spin :show="snapLoading" description="加载中...">
            <n-data-table
                :bordered="false"
                :columns="snapColumns"
                :data="snapData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <!-- 创建快照弹窗 -->
        <n-modal v-model:show="snapForm.show" preset="dialog" title="创建快照" positive-text="确认" negative-text="取消"
                 @positive-click="handleCreateSnapshot">
          <n-form label-placement="left" label-width="auto">
            <n-form-item label="仓库">
              <n-select v-model:value="snapForm.repository" :options="repoSelectOptions"
                        placeholder="选择目标仓库"/>
            </n-form-item>
            <n-form-item label="快照名称">
              <n-input v-model:value="snapForm.snapshot" placeholder="snapshot_2026"/>
            </n-form-item>
            <n-form-item label="索引（逗号分隔）">
              <n-input v-model:value="snapForm.indices" placeholder="留空表示所有索引"/>
            </n-form-item>
            <n-form-item label="包含全局状态">
              <n-switch v-model:value="snapForm.includeGlobalState"/>
            </n-form-item>
          </n-form>
          <n-text depth="3">快照将在后台异步创建，可在快照列表中查看进度。</n-text>
        </n-modal>

        <!-- 快照详情弹窗 -->
        <n-modal v-model:show="snapDetail.show" preset="card" title="快照详情" style="width: 600px;">
          <n-code :code="snapDetail.content" language="json" show-line-numbers/>
        </n-modal>
      </n-tab-pane>

      <!-- ==================== Tab 3: 快照恢复 ==================== -->
      <n-tab-pane name="restore" tab="快照恢复">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getRestoreStatus">刷新恢复状态
            </n-button>
          </n-flex>

          <n-card title="恢复快照" size="small">
            <n-form label-placement="left" label-width="auto">
              <n-form-item label="仓库">
                <n-select v-model:value="restoreForm.repository" :options="repoSelectOptions"
                          placeholder="选择仓库" @update:value="onRestoreRepoChange"/>
              </n-form-item>
              <n-form-item label="快照">
                <n-select v-model:value="restoreForm.snapshot" :options="restoreSnapOptions"
                          placeholder="选择要恢复的快照"/>
              </n-form-item>
              <n-form-item label="索引（逗号分隔）">
                <n-input v-model:value="restoreForm.indices" placeholder="留空表示恢复所有索引"/>
              </n-form-item>
              <n-form-item label="重命名模式">
                <n-input v-model:value="restoreForm.renamePattern" placeholder="例如: index_(.+)"/>
              </n-form-item>
              <n-form-item label="重命名替换">
                <n-input v-model:value="restoreForm.renameReplacement" placeholder="例如: restored_index_$1"/>
              </n-form-item>
              <n-form-item label="包含全局状态">
                <n-switch v-model:value="restoreForm.includeGlobalState"/>
              </n-form-item>
            </n-form>
            <n-flex>
              <n-button type="warning" @click="handleRestore">执行恢复</n-button>
            </n-flex>
            <n-text depth="3">
              警告：恢复操作会在集群中创建索引，如果同名索引已存在且未关闭，恢复将失败。建议使用重命名功能避免冲突。
            </n-text>
          </n-card>

          <n-card title="恢复进度" size="small" style="margin-top: 12px;">
            <n-spin :show="restoreStatusLoading">
              <n-data-table
                  :bordered="false"
                  :columns="restoreColumns"
                  :data="restoreStatusData"
                  :max-height="300"
                  size="small"
                  striped
              />
            </n-spin>
          </n-card>
        </n-flex>
      </n-tab-pane>

      <!-- ==================== Tab 4: 自动策略 (SLM) ==================== -->
      <n-tab-pane name="slm" tab="自动策略 (SLM)">
        <n-flex vertical>
          <n-flex align="center">
            <n-button :render-icon="renderIcon(RefreshOutlined)" text @click="getSLMPolicies">刷新</n-button>
            <n-button :render-icon="renderIcon(AddFilled)" @click="slmForm.show = true">创建策略</n-button>
          </n-flex>
          <n-spin :show="slmLoading" description="加载中...">
            <n-data-table
                :bordered="false"
                :columns="slmColumns"
                :data="slmData"
                :max-height="550"
                size="small"
                striped
            />
          </n-spin>
        </n-flex>

        <!-- 创建SLM策略弹窗 -->
        <n-modal v-model:show="slmForm.show" preset="dialog" title="创建自动快照策略" positive-text="确认"
                 negative-text="取消" @positive-click="handleCreateSLM" style="width: 520px;">
          <n-form label-placement="left" label-width="auto">
            <n-form-item label="策略ID">
              <n-input v-model:value="slmForm.policyId" placeholder="daily-snapshots"/>
            </n-form-item>
            <n-form-item label="快照名称模板">
              <n-input v-model:value="slmForm.name" placeholder="<daily-snap-{now/d}>"/>
            </n-form-item>
            <n-form-item label="Cron 调度">
              <n-input v-model:value="slmForm.schedule" placeholder="0 30 1 * * ?（每天凌晨1:30）"/>
            </n-form-item>
            <n-form-item label="仓库">
              <n-select v-model:value="slmForm.repository" :options="repoSelectOptions"
                        placeholder="目标仓库"/>
            </n-form-item>
            <n-form-item label="索引（逗号分隔）">
              <n-input v-model:value="slmForm.indices" placeholder="留空表示所有索引"/>
            </n-form-item>
            <n-form-item label="过期时间">
              <n-input v-model:value="slmForm.expireAfter" placeholder="例如: 30d"/>
            </n-form-item>
            <n-form-item label="最少保留数">
              <n-input-number v-model:value="slmForm.minCount" :min="0" placeholder="5"/>
            </n-form-item>
            <n-form-item label="最多保留数">
              <n-input-number v-model:value="slmForm.maxCount" :min="0" placeholder="50"/>
            </n-form-item>
          </n-form>
        </n-modal>
      </n-tab-pane>
    </n-tabs>
  </n-flex>
</template>

<script setup>
import {computed, h, onMounted, ref} from "vue";
import emitter from "../utils/eventBus";
import {NButton, NTag, useDialog, useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {RefreshOutlined, AddFilled, DeleteOutlined, PlayArrowFilled, VisibilityOutlined, VerifiedOutlined} from "@vicons/material";
import {
  GetSnapshots, GetSnapshotRepositories, CreateSnapshotRepository, DeleteSnapshotRepository,
  VerifySnapshotRepository, CreateSnapshot, DeleteSnapshot, GetSnapshotDetail,
  RestoreSnapshot, GetSnapshotRestoreStatus,
  GetSLMPolicies, CreateSLMPolicy, DeleteSLMPolicy, ExecuteSLMPolicy,
} from "../../wailsjs/go/service/ESService";

const message = useMessage()
const dialog = useDialog()

// ==================== 仓库管理 ====================
const repoLoading = ref(false)
const repoData = ref([])

const repoForm = ref({
  show: false,
  name: '',
  type: 'fs',
  settings: '',
})

const repoTypeOptions = [
  {label: 'fs（共享文件系统）', value: 'fs'},
  {label: 's3（AWS S3）', value: 's3'},
  {label: 'hdfs（Hadoop HDFS）', value: 'hdfs'},
  {label: 'azure（Azure Blob）', value: 'azure'},
  {label: 'gcs（Google Cloud Storage）', value: 'gcs'},
  {label: 'url（只读URL）', value: 'url'},
]

const repoSelectOptions = computed(() => {
  return repoData.value.map(r => ({label: r.name, value: r.name}))
})

const getRepos = async () => {
  repoLoading.value = true
  const res = await GetSnapshotRepositories()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    repoData.value = res.results || []
  }
  repoLoading.value = false
}

const handleCreateRepo = async () => {
  const res = await CreateSnapshotRepository(repoForm.value.name, repoForm.value.type, repoForm.value.settings)
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success("仓库创建成功")
  repoForm.value = {show: false, name: '', type: 'fs', settings: ''}
  await getRepos()
}

const handleDeleteRepo = (name) => {
  dialog.warning({
    title: '确认删除仓库',
    content: `确定要删除快照仓库「${name}」吗？这不会删除仓库中已有的快照数据文件，但会从ES集群中移除此仓库的注册信息。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await DeleteSnapshotRepository(name)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success("仓库已删除")
        await getRepos()
      }
    }
  })
}

const handleVerifyRepo = async (name) => {
  const res = await VerifySnapshotRepository(name)
  if (res.err !== "") {
    message.error("验证失败: " + res.err)
  } else {
    message.success("仓库验证通过，所有节点可访问")
  }
}

const repoColumns = [
  {title: '仓库名称', key: 'name', width: 180},
  {title: '类型', key: 'type', width: 100},
  {
    title: 'Settings',
    key: 'settings',
    render: (row) => row.settings ? JSON.stringify(row.settings) : '-',
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {size: 'small', quaternary: true, type: 'info', onClick: () => handleVerifyRepo(row.name)},
          {default: () => '验证'}),
      h(NButton, {size: 'small', quaternary: true, type: 'error', onClick: () => handleDeleteRepo(row.name)},
          {default: () => '删除'}),
    ])
  }
]

// ==================== 快照管理 ====================
const snapLoading = ref(false)
const snapData = ref([])

const snapForm = ref({
  show: false,
  repository: null,
  snapshot: '',
  indices: '',
  includeGlobalState: false,
})

const snapDetail = ref({
  show: false,
  content: '',
})

const getSnapshots = async () => {
  snapLoading.value = true
  const res = await GetSnapshots()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    snapData.value = (res.results || []).sort((a, b) => {
      return (b.start_time || '').localeCompare(a.start_time || '')
    })
  }
  snapLoading.value = false
}

const handleCreateSnapshot = async () => {
  const res = await CreateSnapshot(
      snapForm.value.repository,
      snapForm.value.snapshot,
      snapForm.value.indices,
      snapForm.value.includeGlobalState
  )
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success("快照开始创建（异步），请稍后刷新查看状态")
  snapForm.value = {show: false, repository: null, snapshot: '', indices: '', includeGlobalState: false}
  await getSnapshots()
}

const handleDeleteSnapshot = (repository, snapshot) => {
  dialog.warning({
    title: '确认删除快照',
    content: `确定要删除仓库「${repository}」中的快照「${snapshot}」吗？此操作不可逆。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await DeleteSnapshot(repository, snapshot)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success("快照已删除")
        await getSnapshots()
      }
    }
  })
}

const handleViewDetail = async (repository, snapshot) => {
  const res = await GetSnapshotDetail(repository, snapshot)
  if (res.err !== "") {
    message.error(res.err)
  } else {
    snapDetail.value.content = JSON.stringify(res.result, null, 2)
    snapDetail.value.show = true
  }
}

const snapColumns = [
  {title: '快照名称', key: 'snapshot', width: 160},
  {title: '仓库', key: 'repository', width: 130},
  {
    title: '状态', key: 'state', width: 110,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.state === 'SUCCESS' ? "success" : row.state === 'FAILED' ? "error" :
          row.state === 'IN_PROGRESS' ? "info" : "warning"
    }, {default: () => row.state}),
  },
  {title: '开始时间', key: 'start_time', width: 170},
  {title: '结束时间', key: 'end_time', width: 170},
  {
    title: '索引数', key: 'indices', width: 80,
    render: (row) => Array.isArray(row.indices) ? row.indices.length : 0,
  },
  {title: '总分片', key: 'total_shards', width: 80},
  {title: '成功分片', key: 'successful_shards', width: 90},
  {
    title: '操作', key: 'actions', width: 200,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {
        size: 'small', quaternary: true, type: 'info',
        onClick: () => handleViewDetail(row.repository, row.snapshot)
      }, {default: () => '详情'}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'warning',
        onClick: () => {
          restoreForm.value.repository = row.repository
          restoreForm.value.snapshot = row.snapshot
          // 切换到恢复tab (让用户确认参数后手动执行)
          message.info('已填入恢复参数，请切换到「快照恢复」标签页确认并执行')
        }
      }, {default: () => '恢复'}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'error',
        onClick: () => handleDeleteSnapshot(row.repository, row.snapshot)
      }, {default: () => '删除'}),
    ])
  }
]

// ==================== 快照恢复 ====================
const restoreForm = ref({
  repository: null,
  snapshot: null,
  indices: '',
  renamePattern: '',
  renameReplacement: '',
  includeGlobalState: false,
})

const restoreSnapOptions = ref([])
const restoreStatusLoading = ref(false)
const restoreStatusData = ref([])

const onRestoreRepoChange = async (repo) => {
  restoreSnapOptions.value = []
  restoreForm.value.snapshot = null
  // 如果数据为空则先获取，再统一过滤
  if (snapData.value.length === 0) {
    await getSnapshots()
  }
  const filtered = snapData.value.filter(s => s.repository === repo && s.state === 'SUCCESS')
  restoreSnapOptions.value = filtered.map(s => ({label: s.snapshot, value: s.snapshot}))
}

const handleRestore = () => {
  if (!restoreForm.value.repository || !restoreForm.value.snapshot) {
    message.warning("请选择仓库和快照")
    return
  }
  dialog.warning({
    title: '确认恢复快照',
    content: `即将从仓库「${restoreForm.value.repository}」恢复快照「${restoreForm.value.snapshot}」。恢复操作会在集群中创建索引数据，请确认已了解影响。`,
    positiveText: '确认恢复',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await RestoreSnapshot(
          restoreForm.value.repository,
          restoreForm.value.snapshot,
          restoreForm.value.indices,
          restoreForm.value.renamePattern,
          restoreForm.value.renameReplacement,
          restoreForm.value.includeGlobalState
      )
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success("恢复任务已提交（异步执行），请查看恢复进度")
        await getRestoreStatus()
      }
    }
  })
}

const getRestoreStatus = async () => {
  restoreStatusLoading.value = true
  const res = await GetSnapshotRestoreStatus()
  if (res.err !== "") {
    message.error(res.err)
    restoreStatusData.value = []
  } else {
    // _recovery 返回 {indexName: {shards: [...]}, ...}
    const data = res.result || {}
    const list = []
    for (const [indexName, info] of Object.entries(data)) {
      const shards = info.shards || []
      for (const shard of shards) {
        list.push({
          index: indexName,
          shard: shard.id,
          type: shard.type,
          stage: shard.stage,
          source_node: shard.source?.name || '-',
          target_node: shard.target?.name || '-',
          bytes_recovered: shard.index?.size?.recovered_in_bytes || 0,
          bytes_total: shard.index?.size?.total_in_bytes || 0,
        })
      }
    }
    restoreStatusData.value = list
  }
  restoreStatusLoading.value = false
}

const restoreColumns = [
  {title: '索引', key: 'index', width: 160},
  {title: '分片', key: 'shard', width: 60},
  {title: '类型', key: 'type', width: 100},
  {
    title: '阶段', key: 'stage', width: 100,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.stage === 'DONE' ? 'success' : row.stage === 'INDEX' ? 'info' : 'warning'
    }, {default: () => row.stage})
  },
  {title: '源节点', key: 'source_node', width: 120},
  {title: '目标节点', key: 'target_node', width: 120},
  {
    title: '进度', key: 'progress', width: 120,
    render: (row) => {
      if (row.bytes_total === 0) return '-'
      const pct = Math.round(row.bytes_recovered / row.bytes_total * 100)
      return pct + '%'
    }
  },
]

// ==================== SLM 策略管理 ====================
const slmLoading = ref(false)
const slmData = ref([])

const slmForm = ref({
  show: false,
  policyId: '',
  name: '<daily-snap-{now/d}>',
  schedule: '0 30 1 * * ?',
  repository: null,
  indices: '',
  expireAfter: '30d',
  minCount: 5,
  maxCount: 50,
})

const getSLMPolicies = async () => {
  slmLoading.value = true
  const res = await GetSLMPolicies()
  if (res.err !== "") {
    message.error(res.err)
  } else {
    slmData.value = res.results || []
  }
  slmLoading.value = false
}

const handleCreateSLM = async () => {
  const f = slmForm.value
  const res = await CreateSLMPolicy(
      f.policyId, f.name, f.schedule, f.repository, f.indices,
      f.expireAfter, f.minCount || 0, f.maxCount || 0
  )
  if (res.err !== "") {
    message.error(res.err)
    return false
  }
  message.success("SLM 策略创建成功")
  slmForm.value = {
    show: false, policyId: '', name: '<daily-snap-{now/d}>', schedule: '0 30 1 * * ?',
    repository: null, indices: '', expireAfter: '30d', minCount: 5, maxCount: 50
  }
  await getSLMPolicies()
}

const handleDeleteSLM = (policyId) => {
  dialog.warning({
    title: '确认删除策略',
    content: `确定要删除自动快照策略「${policyId}」吗？已创建的快照不会被删除。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await DeleteSLMPolicy(policyId)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success("策略已删除")
        await getSLMPolicies()
      }
    }
  })
}

const handleExecuteSLM = (policyId) => {
  dialog.info({
    title: '手动执行策略',
    content: `确定要立即执行策略「${policyId}」创建一个快照吗？`,
    positiveText: '执行',
    negativeText: '取消',
    onPositiveClick: async () => {
      const res = await ExecuteSLMPolicy(policyId)
      if (res.err !== "") {
        message.error(res.err)
      } else {
        message.success("策略已触发执行，快照正在创建")
      }
    }
  })
}

const slmColumns = [
  {title: '策略ID', key: 'name', width: 160},
  {
    title: '仓库', key: 'repository', width: 130,
    render: (row) => (row.policy && row.policy.repository) || '-'
  },
  {
    title: '调度计划', key: 'schedule', width: 160,
    render: (row) => (row.policy && row.policy.schedule) || '-'
  },
  {
    title: '快照名称模板', key: 'snapshot_name', width: 200,
    render: (row) => (row.policy && row.policy.name) || '-'
  },
  {
    title: '下次执行', key: 'next_execution_millis', width: 170,
    render: (row) => row.next_execution ? row.next_execution : '-'
  },
  {
    title: '最近成功', key: 'last_success', width: 170,
    render: (row) => {
      if (row.last_success && row.last_success.time) return row.last_success.time
      return '-'
    }
  },
  {
    title: '最近失败', key: 'last_failure', width: 170,
    render: (row) => {
      if (row.last_failure && row.last_failure.time) {
        return h(NTag, {size: 'small', type: 'error'}, {default: () => row.last_failure.time})
      }
      return '-'
    }
  },
  {
    title: '操作', key: 'actions', width: 180,
    render: (row) => h('div', {style: 'display: flex; gap: 8px;'}, [
      h(NButton, {
        size: 'small', quaternary: true, type: 'info',
        onClick: () => handleExecuteSLM(row.name)
      }, {default: () => '执行'}),
      h(NButton, {
        size: 'small', quaternary: true, type: 'error',
        onClick: () => handleDeleteSLM(row.name)
      }, {default: () => '删除'}),
    ])
  }
]

// ==================== 生命周期 ====================
const selectNode = async () => {
  repoData.value = []
  snapData.value = []
  slmData.value = []
  await loadAllData()
}

const loadAllData = async () => {
  await getRepos()
  await getSnapshots()
  await getSLMPolicies()
}

onMounted(() => {
  emitter.on('selectNode', selectNode)
  loadAllData()
})
</script>

<style scoped>
</style>