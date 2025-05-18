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
      <h2 style="max-width: 200px;">REST</h2>
      <n-text>一个 Restful 调试工具，支持格式化/DSL提示补全/示例/下载/历史缓存</n-text>
    </n-flex>
    <n-flex align="center">
      <n-select v-model:value="method" :options="methodOptions" style="width: 120px;"/>

      <div :id="ace_editorId" class="ace-editor" style="height:34px;min-width: 610px;text-align: left;
        line-height: 34px;box-sizing: border-box;"/>

      <n-button @click="sendRequest" :loading="send_loading" :render-icon="renderIcon(SendSharp)">Send</n-button>
      <n-button @click="showDrawer = true" :render-icon="renderIcon(MenuBookTwotone)">ES查询示例</n-button>
      <n-button @click="showHistoryDrawer = true" :render-icon="renderIcon(HistoryOutlined)">历史记录</n-button>
      <n-button @click="exportJson" :render-icon="renderIcon(ArrowDownwardOutlined)">导出结果</n-button>
    </n-flex>
    <n-grid x-gap="20" :cols="2">
      <n-grid-item>
        <div id="json_editor" style="white-space: pre-wrap; white-space-collapse: preserve; border: 0 !important;" class="editarea"
             @paste="toTree"></div>
      </n-grid-item>
      <n-grid-item>
        <div id="json_view" class="editarea"></div>
      </n-grid-item>
    </n-grid>
  </n-flex>
  <!--  示例-->
  <n-drawer v-model:show="showDrawer" style="width: 38.2%" placement="right">
    <n-drawer-content title="ES DSL查询示例" style="text-align: left;">
      <n-flex vertical>
        <n-collapse>
          <n-collapse-item title="1. Term查询" name="1">
            <n-code :code="dslExamples.term" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="2. Terms查询" name="2">
            <n-code :code="dslExamples.terms" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="3. Match查询" name="3">
            <n-code :code="dslExamples.match" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="4. Match Phrase查询" name="4">
            <n-code :code="dslExamples.matchPhrase" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="5. Range查询" name="5">
            <n-code :code="dslExamples.range" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="6. Bool复合查询" name="6">
            <n-code :code="dslExamples.bool" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="7. Terms Aggregation" name="7">
            <n-code :code="dslExamples.termsAggs" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="8. Date Histogram聚合" name="8">
            <n-code :code="dslExamples.dateHistogram" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="9. Nested查询" name="9">
            <n-code :code="dslExamples.nested" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="10. Exists查询" name="10">
            <n-code :code="dslExamples.exists" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="11. Multi-match查询" name="11">
            <n-code :code="dslExamples.multiMatch" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="12. Wildcard查询" name="12">
            <n-code :code="dslExamples.wildcard" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="13. Metrics聚合" name="13">
            <n-code :code="dslExamples.metrics" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="14. Cardinality聚合" name="14">
            <n-code :code="dslExamples.cardinality" language="json"/>
          </n-collapse-item>

          <n-collapse-item title="15. Script查询" name="15">
            <n-code :code="dslExamples.script" language="json"/>
          </n-collapse-item>
        </n-collapse>
      </n-flex>
    </n-drawer-content>
  </n-drawer>

  <!-- 历史记录抽屉 -->
  <n-drawer v-model:show="showHistoryDrawer" style="width: 38.2%">
    <n-drawer-content title="查询历史记录">
      <!-- 搜索框 -->
      <n-input
          v-model:value="searchText"
          placeholder="搜索历史记录，同时支持method、path、dsl"
          clearable
          style="margin-bottom: 12px"
      >
        <template #prefix>
          <n-icon>
            <SearchFilled/>
          </n-icon>
        </template>
      </n-input>

      <!-- 历史记录列表 -->
      <n-list>
        <n-pagination
            v-model:page="currentPage"
            :page-size="pageSize"
            :item-count="filteredHistory?.length"
        />

        <n-list-item style="cursor: pointer;" @click="handleHistoryClick(item.method, item.path, item.dsl)"
                     v-for="item in currentPageData" :key="item.timestamp">
          <n-tooltip placement="left" trigger="hover" style="max-height: 618px;overflow-y: auto">
            <template #trigger>
              <div style="display: flex;font-size: 14px; justify-content: space-between;">
                <n-tag :type="getMethodTagType(item.method)">
                  {{ item.method }}
                </n-tag>
                <n-text>{{ item.path }}</n-text>
                <n-text depth="3">
                  {{ formatTimestamp(item.timestamp) }}
                </n-text>
              </div>
            </template>
            <n-code :code="formatDSL(item.dsl)" language="json" style="text-align: left;" v-if="item.dsl !== ''"/>

          </n-tooltip>
        </n-list-item>

      </n-list>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>

import {NButton, NGrid, NGridItem, NInput, NSelect, useMessage} from 'naive-ui'
import {computed, nextTick, onMounted, ref} from "vue";
import JSONEditor from 'jsoneditor';
import '../assets/css/jsoneditor.min.css'
import {Search} from "../../wailsjs/go/service/ESService";
import {ArrowDownwardOutlined, HistoryOutlined, MenuBookTwotone, SearchFilled, SendSharp} from "@vicons/material";
import {formatTimestamp, renderIcon} from "../utils/common";
import 'ace-builds/src-noconflict/theme-clouds_midnight'
import 'jsoneditor/src/js/ace/theme-jsoneditor';
import ace from 'ace-builds';
import {GetConfig, GetHistory, SaveHistory} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";
import {
  GetIndexes,
} from "../../wailsjs/go/service/ESService";

const message = useMessage()
const method = ref('GET')
const searchText = ref('')
const history = ref([])
const editor = ref();
const response = ref()
const send_loading = ref(false)
const showDrawer = ref(false)
const showHistoryDrawer = ref(false)
// 状态管理
const currentPage = ref(1)
const pageSize = ref(10)

const methodOptions = [
  {label: 'GET', value: 'GET'},
  {label: 'POST', value: 'POST'},
  {label: 'PUT', value: 'PUT'},
  {label: 'HEAD', value: 'HEAD'},
  {label: 'PATCH', value: 'PATCH'},
  {label: 'OPTIONS', value: 'OPTIONS'},
  {label: 'DELETE', value: 'DELETE'}
]
// 自定义自动补全关键词
const keywords = [
  {word: 'query', meta: 'keyword'},           // 查询入口
  {word: 'bool', meta: 'keyword'},            // 布尔查询
  {word: 'filter', meta: 'keyword'},          // 过滤条件
  {word: 'must', meta: 'keyword'},            // 必须匹配
  {word: 'should', meta: 'keyword'},          // 应该匹配
  {word: 'must_not', meta: 'keyword'},        // 必须不匹配
  {word: 'term', meta: 'keyword'},            // 精确匹配查询
  {word: 'terms', meta: 'keyword'},           // 多值精确匹配查询
  {word: 'match', meta: 'keyword'},           // 全文匹配查询
  {word: 'match_phrase', meta: 'keyword'},    // 短语匹配查询
  {word: 'multi_match', meta: 'keyword'},     // 多字段匹配查询
  {word: 'range', meta: 'keyword'},           // 范围查询
  {word: 'exists', meta: 'keyword'},          // 检查字段是否存在
  {word: 'prefix', meta: 'keyword'},          // 前缀查询
  {word: 'wildcard', meta: 'keyword'},        // 通配符查询
  {word: 'regexp', meta: 'keyword'},          // 正则表达式查询
  {word: 'aggs', meta: 'keyword'},            // 聚合入口
  {word: 'aggregations', meta: 'keyword'},    // 聚合入口（aggs 的完整形式）
  {word: 'terms', meta: 'aggregation'},       // 聚合中的 terms（按字段分组）
  {word: 'sum', meta: 'aggregation'},         // 求和聚合
  {word: 'avg', meta: 'aggregation'},         // 平均值聚合
  {word: 'min', meta: 'aggregation'},         // 最小值聚合
  {word: 'max', meta: 'aggregation'},         // 最大值聚合
  {word: 'stats', meta: 'aggregation'},       // 统计聚合
  {word: 'cardinality', meta: 'aggregation'}, // 去重计数聚合
  {word: 'histogram', meta: 'aggregation'},   // 直方图聚合
  {word: 'date_histogram', meta: 'aggregation'}, // 日期直方图聚合
  {word: 'top_hits', meta: 'aggregation'},    // 返回顶部命中文档
  {word: 'size', meta: 'keyword'},            // 返回结果数量
  {word: 'from', meta: 'keyword'},            // 分页起始位置
  {word: 'sort', meta: 'keyword'},            // 排序
  {word: 'track_total_hits', meta: 'keyword'}, // 跟踪总命中数
  {word: '_source', meta: 'keyword'},         // 控制返回的字段
  {word: 'fields', meta: 'keyword'},          // 指定返回字段
  {word: 'script', meta: 'keyword'},          // 脚本字段
  {word: 'gte', meta: 'range'},               // 大于等于（范围查询）
  {word: 'lte', meta: 'range'},               // 小于等于（范围查询）
  {word: 'gt', meta: 'range'},                // 大于（范围查询）
  {word: 'lt', meta: 'range'},                // 小于（范围查询）
  {word: 'boost', meta: 'keyword'},           // 提升权重
  {word: 'minimum_should_match', meta: 'keyword'}, // should 最小匹配数
  {word: 'nested', meta: 'keyword'},          // 嵌套对象查询
  {word: 'path', meta: 'keyword'},            // 嵌套路径
  {word: 'score_mode', meta: 'keyword'},      // 嵌套查询评分模式
  {word: 'bucket', meta: 'aggregation'},      // 聚合桶
  {word: 'order', meta: 'keyword'},           // 排序顺序
  {word: 'asc', meta: 'sort'},                // 升序
  {word: 'desc', meta: 'sort'}                // 降序
];

const selectNode = (node) => {
  response.value.setText('{"tip": "响应结果，支持搜索"}')
  send_loading.value = false
}

onMounted(async () => {

  emitter.on('selectNode', selectNode)
  emitter.on('update_theme', themeChange)

  const loadedConfig = await GetConfig()
  let theme = 'ace/theme/jsoneditor'
  if (loadedConfig) {
    if (loadedConfig.theme !== 'light') {
      theme = 'ace/theme/clouds_midnight'
    }
    editor.value = new JSONEditor(document.getElementById('json_editor'), {
      mode: 'code',
      ace:ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    response.value = new JSONEditor(document.getElementById('json_view'), {
      mode: 'code',
      ace:ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
    });
    editor.value.setText(null)
    editor.value.aceEditor.setOptions({
      enableBasicAutocompletion: true,
      enableLiveAutocompletion: true
    })

    // 自定义补全器
    const customCompleter = {
      getCompletions: (editor, session, pos, prefix, callback) => {
        // 根据前缀过滤关键词
        const suggestions = keywords
            .filter(k => k.word.startsWith(prefix))
            .map(k => ({
              caption: k.word,
              value: k.word,
              meta: k.meta
            }));
        callback(null, suggestions);
      }
    };

    // 添加自定义补全器
    editor.value.aceEditor.completers = [customCompleter];

    response.value.setText('{"tip": "响应结果，支持搜索"}')
  }
  await read_history()

  await nextTick()
  initAce("输入url path，以/开头")
  await setAceIndex()

});


// =============== ace编辑器 =================
import 'ace-builds/src-noconflict/mode-text'
import 'ace-builds/src-noconflict/ext-language_tools'

const ace_editor = ref(null)
const ace_editorId = "ace-editor"

// 初始化 Ace 编辑器
const initAce = (defaultValue) => {
  ace.config.set('basePath', '/node_modules/ace-builds/src-noconflict')

  ace_editor.value = ace.edit(document.getElementById(ace_editorId), {
    mode: `ace/mode/text`,
    theme: `ace/theme/clouds_midnight`,
    placeholder: defaultValue,
    fontSize: 14,
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    showLineNumbers: false,
    maxLines: 1,
    minLines: 1,
    showGutter: false,
  })
}

const getAceValue = () => {
  return ace_editor.value?.getValue()
}

const setAceValue = (newValue) => {
  ace_editor.value?.setValue(newValue, -1)
}

// 定义提示词数据
// const completions = [
// {
//   caption: "console.log", // 用户看到的名称（可选，如果和 value 相同可以省略）
//   value: "console.log(${1:value})", // 实际插入的值
//   score: 100, // 权重（越高越靠前）
//   meta: "JavaScript" // 分类（如 "JavaScript"、"CSS"、"Custom"）
// },
// ];
const setAceCompleter = (completions) => {
  const customCompleter = {
    getCompletions: function (editor, session, pos, prefix, callback) {
      callback(null, completions); // 返回提示词
    }
  };
  // 添加到编辑器的补全器列表
  ace_editor.value.completers = [customCompleter] // 覆盖默认补全器（不推荐）
  // ace_editor.value.completers.push(customCompleter); // 追加自定义补全器（推荐）
}
// ================ ace编辑器 完结 =================

const setAceIndex = async () => {
  const keywords = [
    '_search',  '_cluster',  '_cat',  '_indices',  '_nodes',  '_doc',  '?format=json&pretty',  '_forcemerge',  'wait_for_completion',  '_tasks',  '_cache',  '_flush',  '_refresh',  '_cancel',  '_mapping',  '_settings',  '_stats',  '_bulk',  '_update',  '_msearch',  '_alias',  '_rollover',  '_reindex',  '_snapshot'
  ];
  let completions = [];
  for (let k of keywords) {
    completions.push({ value: k });
  }

  const res = await GetIndexes("")
  if (res.err !== "") {
    message.error("从ES中获取索引列表并初始化编辑器提示词失败：" + res.err)
  } else {
    if (res.results && res.results.length > 0) {
      for (let item of res.results) {
        completions.push({
          value: item.index,
        })
      }
    }
  }
  if (completions.length > 0) {
    setAceCompleter(completions)
  }
}
const read_history = async () => {
  console.log("read_history")
  try {
    history.value = await GetHistory()
  } catch (e) {
    message.error(e.message)
  }
}
const write_history = async () => {
  console.log("write_history")
  try {
    // 从左侧插入history
    history.value.unshift({
      timestamp: Date.now(),
      method: method.value,
      path: getAceValue(),
      dsl: editor.value.getText()
    })
    // 只保留100条
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
    const res = await SaveHistory(history.value)
    if (res !== "") {
      message.error("保存查询失败：" + res)
    }
  } catch (e) {
    message.error(e.message)
  }
}

// 填充历史记录
function handleHistoryClick(m, p, d) {
  method.value = m
  setAceValue(p)
  editor.value.setText(d)
  showHistoryDrawer.value = false
}

function themeChange(newTheme) {
  const new_editor_theme = newTheme.name === 'dark' ? 'ace/theme/clouds_midnight' : 'ace/theme/jsoneditor'
  editor.value.aceEditor.setTheme(new_editor_theme)
  response.value.aceEditor.setTheme(new_editor_theme)

}

const formatDSL = (dsl) => {
  try {
    return JSON.stringify(JSON.parse(dsl), null, 2)
  } catch {
    return dsl
  }
}

const sendRequest = async () => {
  send_loading.value = true
  // 清空response
  response.value.set({})
  let path = getAceValue()
  if (!path.startsWith('/')) {
    setAceValue('/' + path);
  }
  try {
    const res = await Search(method.value, path, editor.value.getText())
    // 返回不是200也写入结果框
    if (res.err !== "") {
      response.value.set(res.err)
    } else {
      response.value.set(res.result)
      // 写入历史记录
      await write_history()
    }
  } catch (e) {
    message.error(e.message)
  }
  send_loading.value = false

}

const toTree = () => {
  editor.value.format();
}


function exportJson() {
  const blob = new Blob([response.value.getText()], {type: 'application/json'})
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'response.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// 过滤和分页逻辑
const filteredHistory = computed(() => {
  if (!searchText.value) {
    return history.value
  } else {
    return history.value.filter(item => {
      return item.method.includes(searchText.value) ||
          item.path.includes(searchText.value) ||
          item.dsl.includes(searchText.value)
    })
  }

})

const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})

const getMethodTagType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'info',
    'PUT': 'warning',
    'DELETE': 'error'
  }
  return types[method] || 'default'
}

const dslExamples = {
  term: JSON.stringify({
    "query": {
      "term": {
        "status": "active"
      }
    },
    "size": 10,
    "track_total_hits": true
  }, null, 2),

  terms: JSON.stringify({
    "query": {
      "terms": {
        "user_id": [1, 2, 3, 4]
      }
    },
    "size": 10
  }, null, 2),

  match: JSON.stringify({
    "query": {
      "match": {
        "description": "quick brown fox"
      }
    },
    "size": 20
  }, null, 2),

  matchPhrase: JSON.stringify({
    "query": {
      "match_phrase": {
        "description": {
          "query": "quick brown fox",
          "slop": 1
        }
      }
    }
  }, null, 2),

  range: JSON.stringify({
    "query": {
      "range": {
        "age": {
          "gte": 20,
          "lte": 30
        }
      }
    }
  }, null, 2),

  bool: JSON.stringify({
    "query": {
      "bool": {
        "must": [
          {"term": {"status": "active"}}
        ],
        "must_not": [
          {"term": {"type": "deleted"}}
        ],
        "should": [
          {"term": {"category": "electronics"}},
          {"term": {"category": "computers"}}
        ],
        "minimum_should_match": 1
      }
    }
  }, null, 2),

  termsAggs: JSON.stringify({
    "aggs": {
      "status_counts": {
        "terms": {
          "field": "status",
          "missing": "N/A",
          "size": 10
        }
      }
    },
    "size": 0
  }, null, 2),

  dateHistogram: JSON.stringify({
    "aggs": {
      "sales_over_time": {
        "date_histogram": {
          "field": "created_at",
          "calendar_interval": "1d",
          "format": "yyyy-MM-dd"
        }
      }
    },
    "size": 0
  }, null, 2),

  nested: JSON.stringify({
    "query": {
      "nested": {
        "path": "comments",
        "query": {
          "bool": {
            "must": [
              {"match": {"comments.text": "great"}},
              {"term": {"comments.rating": 5}}
            ]
          }
        }
      }
    }
  }, null, 2),

  exists: JSON.stringify({
    "query": {
      "exists": {
        "field": "email"
      }
    }
  }, null, 2),

  multiMatch: JSON.stringify({
    "query": {
      "multi_match": {
        "query": "quick brown fox",
        "fields": ["title", "description^2"],
        "type": "best_fields"
      }
    }
  }, null, 2),

  wildcard: JSON.stringify({
    "query": {
      "wildcard": {
        "email": "*@gmail.com"
      }
    }
  }, null, 2),

  metrics: JSON.stringify({
    "aggs": {
      "avg_price": {"avg": {"field": "price"}},
      "max_price": {"max": {"field": "price"}},
      "min_price": {"min": {"field": "price"}},
      "sum_quantity": {"sum": {"field": "quantity"}}
    },
    "size": 0
  }, null, 2),

  cardinality: JSON.stringify({
    "aggs": {
      "unique_users": {
        "cardinality": {
          "field": "user_id",
          "precision_threshold": 100
        }
      }
    },
    "size": 0
  }, null, 2),

  script: JSON.stringify({
    "query": {
      "script_score": {
        "query": {"match_all": {}},
        "script": {
          "source": "doc['price'].value * doc['rating'].value",
          "lang": "painless"
        }
      }
    }
  }, null, 2)
}

</script>

<style>
.editarea, .json_view {
  height: 72dvh;
}

/* 隐藏ace编辑器的脱离聚焦时携带的光标 */
.ace_editor:not(.ace_focus) .ace_cursor {
  opacity: 0 !important;
}
</style>