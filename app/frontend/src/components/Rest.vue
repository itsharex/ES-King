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
      <h2>{{ t('rest.title') }}</h2>
      <n-text>{{ t('rest.desc') }}</n-text>
    </n-flex>
    <n-flex align="center">
      <n-select v-model:value="method" :options="methodOptions" style="width: 120px;"/>

      <div :id="ace_editorId" class="ace-editor" style="height:34px;min-width: 46.8%;text-align: left;
        line-height: 34px;box-sizing: border-box;"/>

      <n-button :loading="send_loading" :render-icon="renderIcon(SendSharp)" @click="sendRequest">{{ t('rest.send') }}</n-button>
      <n-button :render-icon="renderIcon(HistoryOutlined)" @click="showHistoryDrawer = true">{{ t('rest.history') }}</n-button>
      <n-button :render-icon="renderIcon(MenuBookTwotone)" @click="showDrawer = true">{{ t('rest.examples') }}</n-button>
      <n-button :render-icon="renderIcon(ArrowDownwardOutlined)" @click="exportJson">{{ t('rest.exportResult') }}</n-button>
    </n-flex>
    <n-grid :cols="2" x-gap="20">
      <n-grid-item>
        <div id="json_editor" class="editarea"
             style="white-space: pre-wrap; white-space-collapse: preserve; border: 0 !important;"
             @paste="toTree"></div>
      </n-grid-item>
      <n-grid-item>
        <div id="json_view" class="editarea"></div>
      </n-grid-item>
    </n-grid>
  </n-flex>

  <n-drawer v-model:show="showDrawer" placement="right" style="width: 38.2%">
    <n-drawer-content style="text-align: left;" :title="t('rest.queryExamples')">
      <n-flex vertical>
        <n-collapse>
          <n-collapse-item name="1" title="1. Term查询">
            <n-code :code="dslExamples.term" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="2" title="2. Terms查询">
            <n-code :code="dslExamples.terms" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="3" title="3. Match查询">
            <n-code :code="dslExamples.match" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="4" title="4. Match Phrase查询">
            <n-code :code="dslExamples.matchPhrase" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="5" title="5. Range查询">
            <n-code :code="dslExamples.range" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="6" title="6. Bool复合查询">
            <n-code :code="dslExamples.bool" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="7" title="7. Terms Aggregation">
            <n-code :code="dslExamples.termsAggs" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="8" title="8. Date Histogram聚合">
            <n-code :code="dslExamples.dateHistogram" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="9" title="9. Nested查询">
            <n-code :code="dslExamples.nested" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="10" title="10. Exists查询">
            <n-code :code="dslExamples.exists" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="11" title="11. Multi-match查询">
            <n-code :code="dslExamples.multiMatch" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="12" title="12. Wildcard查询">
            <n-code :code="dslExamples.wildcard" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="13" title="13. Metrics聚合">
            <n-code :code="dslExamples.metrics" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="14" title="14. Cardinality聚合">
            <n-code :code="dslExamples.cardinality" language="json"/>
          </n-collapse-item>

          <n-collapse-item name="15" title="15. Script查询">
            <n-code :code="dslExamples.script" language="json"/>
          </n-collapse-item>
        </n-collapse>
      </n-flex>
    </n-drawer-content>
  </n-drawer>

  <!-- 历史记录抽屉 -->
  <n-drawer v-model:show="showHistoryDrawer" style="width: 38.2%">
    <n-drawer-content :title="t('rest.history')">
      <n-input
          v-model:value="searchText"
          clearable
          :placeholder="t('rest.searchHistory')"
          style="margin-bottom: 12px"
      >
        <template #prefix>
          <n-icon>
            <SearchFilled/>
          </n-icon>
        </template>
      </n-input>

      <n-list>
        <n-pagination
            v-model:page="currentPage"
            :item-count="filteredHistory?.length"
            :page-size="pageSize"
        />

        <n-list-item v-for="item in currentPageData" :key="item.timestamp"
                     style="cursor: pointer;" @click="handleHistoryClick(item.method, item.path, item.dsl)">
          <n-tooltip placement="left" style="max-height: 618px;overflow-y: auto" trigger="hover">
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
            <n-code v-if="item.dsl !== ''" :code="formatDSL(item.dsl)" language="json" style="text-align: left;"/>

          </n-tooltip>
        </n-list-item>

      </n-list>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>

import { useI18n } from 'vue-i18n'
import {NButton, NGrid, NGridItem, NInput, NSelect, useMessage} from 'naive-ui'
import {computed, nextTick, onMounted, ref} from "vue";
import {Search} from "../../wailsjs/go/service/ESService";
import {ArrowDownwardOutlined, HistoryOutlined, MenuBookTwotone, SearchFilled, SendSharp} from "@vicons/material";
import {formatTimestamp, renderIcon} from "../utils/common";
import {GetConfig, GetHistory, SaveHistory} from "../../wailsjs/go/config/AppConfig";
import emitter from "../utils/eventBus";

import JSONEditor from 'jsoneditor';
import '../assets/css/jsoneditor.min.css'
import 'jsoneditor/src/js/ace/theme-jsoneditor';
import 'ace-builds/src-noconflict/mode-text'
import 'ace-builds/src-noconflict/ext-language_tools'
import 'ace-builds/src-noconflict/theme-textmate'
import 'ace-builds/src-noconflict/theme-monokai'
import ace from 'ace-builds';

const { t } = useI18n()

const message = useMessage()
const method = ref('POST')
const searchText = ref('')
const history = ref([])
const editor = ref();
const response = ref()
const send_loading = ref(false)
const showDrawer = ref(false)
const showHistoryDrawer = ref(false)
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
const keywords = [
  {word: 'query', meta: 'keyword'},
  {word: 'bool', meta: 'keyword'},
  {word: 'filter', meta: 'keyword'},
  {word: 'must', meta: 'keyword'},
  {word: 'should', meta: 'keyword'},
  {word: 'must_not', meta: 'keyword'},
  {word: 'term', meta: 'keyword'},
  {word: 'terms', meta: 'keyword'},
  {word: 'match', meta: 'keyword'},
  {word: 'match_phrase', meta: 'keyword'},
  {word: 'multi_match', meta: 'keyword'},
  {word: 'range', meta: 'keyword'},
  {word: 'exists', meta: 'keyword'},
  {word: 'prefix', meta: 'keyword'},
  {word: 'wildcard', meta: 'keyword'},
  {word: 'regexp', meta: 'keyword'},
  {word: 'aggs', meta: 'keyword'},
  {word: 'aggregations', meta: 'keyword'},
  {word: 'terms', meta: 'aggregation'},
  {word: 'sum', meta: 'aggregation'},
  {word: 'avg', meta: 'aggregation'},
  {word: 'min', meta: 'aggregation'},
  {word: 'max', meta: 'aggregation'},
  {word: 'stats', meta: 'aggregation'},
  {word: 'cardinality', meta: 'aggregation'},
  {word: 'histogram', meta: 'aggregation'},
  {word: 'date_histogram', meta: 'aggregation'},
  {word: 'top_hits', meta: 'aggregation'},
  {word: 'size', meta: 'keyword'},
  {word: 'from', meta: 'keyword'},
  {word: 'sort', meta: 'keyword'},
  {word: 'track_total_hits', meta: 'keyword'},
  {word: '_source', meta: 'keyword'},
  {word: 'fields', meta: 'keyword'},
  {word: 'script', meta: 'keyword'},
  {word: 'gte', meta: 'range'},
  {word: 'lte', meta: 'range'},
  {word: 'gt', meta: 'range'},
  {word: 'lt', meta: 'range'},
  {word: 'boost', meta: 'keyword'},
  {word: 'minimum_should_match', meta: 'keyword'},
  {word: 'nested', meta: 'keyword'},
  {word: 'path', meta: 'keyword'},
  {word: 'score_mode', meta: 'keyword'},
  {word: 'bucket', meta: 'aggregation'},
  {word: 'order', meta: 'keyword'},
  {word: 'asc', meta: 'sort'},
  {word: 'desc', meta: 'sort'}
];

const selectNode = (node) => {
  response.value.setText(t('rest.responseResult'))
  send_loading.value = false
}

onMounted(async () => {

  emitter.on('selectNode', selectNode)
  emitter.on('update_theme', themeChange)

  const loadedConfig = await GetConfig()
  let theme = 'ace/theme/jsoneditor'
  if (loadedConfig) {
    if (loadedConfig.theme !== 'light') {
      theme = 'ace/theme/monokai'
    }
    editor.value = new JSONEditor(document.getElementById('json_editor'), {
      mode: 'code',
      ace: ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
      showPrintMargin: false,
      placeholder: t('rest.requestBody')
    });
    response.value = new JSONEditor(document.getElementById('json_view'), {
      mode: 'code',
      ace: ace,
      theme: theme,
      mainMenuBar: false,
      statusBar: false,
      showPrintMargin: false,
    });
    editor.value.setText(null)
    editor.value.aceEditor.setOptions({
      enableBasicAutocompletion: true,
      enableLiveAutocompletion: true
    })

    const customCompleter = {
      getCompletions: (editor, session, pos, prefix, callback) => {
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

    editor.value.aceEditor.completers = [customCompleter];

    response.value.setText(t('rest.responseResult'))
  }
  await read_history()

  await nextTick()
  initAce(t('rest.enterApi'), loadedConfig.theme)
  await setAceIndex()

});

const ace_editor = ref(null)
const ace_editorId = "ace-editor"

const initAce = (defaultValue, theme) => {
  ace.config.set('basePath', '/node_modules/ace-builds/src-noconflict')

  ace_editor.value = ace.edit(document.getElementById(ace_editorId), {
    mode: `ace/mode/text`,
    theme: theme === 'light'? 'ace/theme/textmate': 'ace/theme/monokai',
    placeholder: defaultValue,
    fontSize: 14,
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    showLineNumbers: false,
    maxLines: 1,
    minLines: 1,
    showGutter: false,
    showPrintMargin: false,
  })
}

const getAceValue = () => {
  return ace_editor.value?.getValue()
}

const setAceValue = (newValue) => {
  ace_editor.value?.setValue(newValue, -1)
}

const setAceCompleter = (completions) => {
  const customCompleter = {
    getCompletions: function (editor, session, pos, prefix, callback) {
      callback(null, completions);
    }
  };
  ace_editor.value.completers = [customCompleter]
}

const setAceIndex = async () => {
  const keywords = [
    '_search', '_cluster', '_cat', '_nodes', '_doc', '_tasks', '_flush', '_refresh',
    '_mapping', '_settings', '_stats', '_bulk', '_update', '_msearch', '_alias',
    '_rollover', '_reindex', '_snapshot', '_forcemerge', '_indices', '_count',
    '_validate', '_explain', '_field_caps', '_search_shards', '_analyze',
    'pretty', 'human', 'master_timeout', 'ignore_unavailable', 'allow_no_indices',
    'expand_wildcards', 'wait_for_active_shards', 'wait_for_completion',
    'format=json', 'size', 'from', 'q', 'scroll', 'routing', 'preference',
    'timeout', 'filter_path',
  ];
  let completions = [];
  for (let k of keywords) {
    completions.push({value: k});
  }
  const key = 'es_king_indexes';
  const stored = localStorage.getItem(key);
  if (stored) {
    const values = JSON.parse(stored)
    for (let v of values) {
      completions.push({
        value: v,
      })
    }
  }
  if (completions.length > 0) {
    setAceCompleter(completions)
  }
}

const read_history = async () => {
  try {
    history.value = await GetHistory()
  } catch (e) {
    message.error(e.message)
  }
}

const write_history = async () => {
  try {
    history.value.unshift({
      timestamp: Date.now(),
      method: method.value,
      path: getAceValue(),
      dsl: editor.value.getText()
    })
    if (history.value.length > 100) {
      history.value = history.value.slice(0, 100)
    }
    const res = await SaveHistory(history.value)
    if (res !== "") {
      message.error(t('rest.saveFailed', { msg: res }))
    }
  } catch (e) {
    message.error(e.message)
  }
}

function handleHistoryClick(m, p, d) {
  method.value = m
  setAceValue(p)
  editor.value.setText(d)
  showHistoryDrawer.value = false
}

function themeChange(newTheme) {
  const new_editor_theme = newTheme.name === 'dark' ? 'ace/theme/monokai' : 'ace/theme/textmate'
  editor.value.aceEditor.setTheme(new_editor_theme)
  response.value.aceEditor.setTheme(new_editor_theme)
  ace_editor.value?.setTheme(new_editor_theme)
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
  response.value.set({})
  let path = getAceValue()
  if (!path.startsWith('/')) {
    setAceValue('/' + path);
  }
  try {
    const res = await Search(method.value, path, editor.value.getText())
    if (res.err !== "") {
      try {
        response.value.set(JSON.parse(res.err))
      } catch {
        response.value.set(res.err)
      }
    } else {
      response.value.set(res.result)
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

.ace_editor:not(.ace_focus) .ace_cursor {
  opacity: 0 !important;
}

.ace_editor .ace_placeholder {
  position: absolute;
  z-index: 10;
}
</style>
