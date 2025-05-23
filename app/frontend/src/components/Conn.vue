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
  <div>
    <n-flex vertical>
      <n-flex align="center">
        <h2 style="max-width: 200px;">集群</h2>
        <n-text>共有 {{ esNodes.length }} 个</n-text>
        <n-button @click="addNewNode" :render-icon="renderIcon(AddFilled)">添加集群</n-button>
      </n-flex>
      <n-spin :show="spin_loading" description="Connecting...">

        <n-grid :x-gap="12" :y-gap="12" :cols="4">
          <n-gi v-for="node in esNodes" :key="node.id">
            <n-card :title="node.name" @click="selectNode(node)" hoverable class="conn_card">

              <template #header-extra>
                <n-space>
                  <n-button @click.stop="editNode(node)" size="small">
                    编辑
                  </n-button>
                  <n-popconfirm @positive-click="deleteNode(node.id)" negative-text="取消" positive-text="确定">
                    <template #trigger>
                      <n-button @click.stop size="small">
                        删除
                      </n-button>
                    </template>
                    确定删除吗？
                  </n-popconfirm>
                </n-space>
              </template>
              <n-descriptions :column="1" label-placement="left">
                <n-descriptions-item label="主机">
                  {{ node.host }}
                </n-descriptions-item>
              </n-descriptions>
            </n-card>
          </n-gi>
        </n-grid>
      </n-spin>
    </n-flex>

    <n-drawer v-model:show="showEditDrawer" style="width: 38.2%" placement="right">
      <n-drawer-content :title="drawerTitle">
        <n-form
            ref="formRef"
            :model="currentNode"
            :rules="{
              name: {required: true, message: '请输入昵称', trigger: 'blur'},
              host: {required: true, message: '请输入主机地址', trigger: 'blur'},
              port: {required: true, type: 'number', message: '请输入有效的端口号', trigger: 'blur'},
            }"
            label-placement="top"
            style="text-align: left;"
        >
          <n-form-item label="昵称" path="name">
            <n-input v-model:value="currentNode.name" placeholder="输入节点名称"/>
          </n-form-item>
          <n-form-item label="协议://主机:端口" path="host">
            <n-input v-model:value="currentNode.host" placeholder="输入协议://主机:端口"/>
          </n-form-item>
          <n-form-item label="用户名" path="username">
            <n-input v-model:value="currentNode.username" placeholder="输入用户名"/>
          </n-form-item>
          <n-form-item label="密码" path="password">
            <n-input
                v-model:value="currentNode.password"
                type="password"
                placeholder="输入密码"
            />
          </n-form-item>

          <n-form-item label="使用 SSL" path="useSSL">
            <n-switch :round="false" v-model:value="currentNode.useSSL"/>
          </n-form-item>

          <n-form-item  label="跳过 SSL 验证" path="skipSSLVerify">
            <n-switch :round="false" v-model:value="currentNode.skipSSLVerify"/>
          </n-form-item>

          <n-form-item label="CA 证书" path="caCert">
            <n-input v-model:value="currentNode.caCert" type="textarea" placeholder="输入 CA 证书内容"/>
          </n-form-item>

        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="test_connect" :loading="test_connect_loading">连接测试</n-button>
            <n-button @click="showEditDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveNode">保存</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {useMessage} from 'naive-ui'
import {renderIcon} from "../utils/common";
import {AddFilled} from "@vicons/material";
import emitter from "../utils/eventBus";
import {SetConnect, TestClient} from "../../wailsjs/go/service/ESService";
import {GetConfig, SaveConfig} from "../../wailsjs/go/config/AppConfig";


const message = useMessage()

const esNodes = ref([])

const showEditDrawer = ref(false)
const currentNode = ref({
  name: '',
  host: '',
  port: 9200,
  username: '',
  password: '',
  useSSL: false,
  skipSSLVerify: false,
  caCert: ''
})
const isEditing = ref(false)
const spin_loading = ref(false)
const test_connect_loading = ref(false)

const drawerTitle = computed(() => isEditing.value ? '编辑连接' : '添加连接')

const formRef = ref(null)

onMounted( () => {
  refreshNodeList()
})

const refreshNodeList = async () => {
  spin_loading.value = true
  const config = await GetConfig()
  esNodes.value = config.connects
  spin_loading.value = false
}

function editNode(node) {
  currentNode.value = {...node}
  isEditing.value = true
  showEditDrawer.value = true
}

const addNewNode = async () => {
  currentNode.value = {}
  isEditing.value = false
  showEditDrawer.value = true
}

const saveNode = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      const config = await GetConfig()
      // edit
      if (isEditing.value) {
        const index = esNodes.value.findIndex(node => node.id === currentNode.value.id)
        if (index !== -1) {
          esNodes.value[index] = {...currentNode.value}
        }
      } else {
        // add
        const newId = Math.max(...esNodes.value.map(node => node.id), 0) + 1
        esNodes.value.push({...currentNode.value, id: newId})
      }

      // 保存
      config.connects = esNodes.value
      await SaveConfig(config)
      showEditDrawer.value = false

      await refreshNodeList()
      message.success('保存成功')
    } else {
      message.error('请填写所有必填字段')
    }
  })
}

const deleteNode = async (id) => {
  console.log(esNodes.value)
  console.log(id)
  esNodes.value = esNodes.value.filter(node => node.id !== id)
  console.log(esNodes.value)
  const config = await GetConfig()
  config.connects = esNodes.value
  await SaveConfig(config)
  await refreshNodeList()
  message.success('删除成功')
}

const test_connect = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {

      test_connect_loading.value = true
      try {
        const node = currentNode.value
        const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
        if (res !== "") {
          message.error("连接失败：" + res)
        } else {
          message.success('连接成功')
        }
      } catch (e) {
        message.error(e.message)
      }
      test_connect_loading.value = false

    } else {
      message.error('请填写所有必填字段')
    }
  })
}
const selectNode = async (node) => {
  // 这里实现切换菜单的逻辑
  console.log('选中节点:', node)
  spin_loading.value = true

  try {
    const res = await TestClient(node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
    if (res !== "") {
      message.error("连接失败：" + res)
    } else {
      await SetConnect(node.name, node.host, node.username, node.password, node.caCert, node.useSSL, node.skipSSLVerify)
      message.success('连接成功')
      emitter.emit('menu_select', "节点")
      emitter.emit('selectNode', node)
    }
  } catch (e) {
    message.error(e.message)
  }
  spin_loading.value = false

}
</script>

<style>

.lightTheme .conn_card {
  background-color: #fafafc
}
</style>