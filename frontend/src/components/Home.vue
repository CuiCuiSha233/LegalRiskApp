<template>
  <div class="app-container">
    <div class="top-bar">
      <div class="top-bar-left">
        <h2>LLMs分析社交行为法律风险系统</h2>
      </div>
      <div class="top-bar-right">
        <el-button type="primary" @click="goToHistory" v-if="currentPage !== 'history'">
          <el-icon><Clock /></el-icon> 历史报告
        </el-button>
        <el-button type="primary" @click="goToSettings" v-if="currentPage === 'home'">
          <el-icon><Setting /></el-icon> 设置
        </el-button>
        <el-button type="default" @click="goToHome" v-if="currentPage !== 'home'">
          <el-icon><HomeFilled /></el-icon> 返回首页
        </el-button>
        <el-button type="warning" @click="resetAnalysis" v-if="analysis.status === 'completed'">
          重置分析
        </el-button>
        <el-dropdown v-if="isLoggedIn">
          <el-button type="info">
            <el-icon><User /></el-icon> {{ user?.username }} <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>

              <el-dropdown-item @click="goToUserManagement" v-if="user?.role === 'admin'">用户管理</el-dropdown-item>
              <el-dropdown-item @click="goToAllReports" v-if="user?.role === 'admin'">所有报告</el-dropdown-item>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="content-area">
      <template v-if="currentPage === 'home'">
        <div class="home-content">
          <el-card class="upload-card">
            <template #header>
              <div class="card-header">
                <span>📂 文件上传</span>
              </div>
            </template>
            <el-upload
              class="upload-demo"
              drag
              action=""
              :auto-upload="false"
              :on-change="handleFileChange"
              accept=".txt,.docx,.json,.csv,.xlsx,.xls"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">支持上传 TXT、DOCX、JSON、CSV、Excel 文件</div>
              </template>
            </el-upload>
          </el-card>
          
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>📝 输入待分析内容</span>
              </div>
            </template>
            <el-input
              v-model="content"
              type="textarea"
              :rows="8"
              placeholder="请输入或粘贴待分析的文本内容"
            />
            <el-button 
              type="primary" 
              class="analyze-btn"
              :disabled="!content || loading"
              @click="startAnalysis"
            >
              🚀 开始多模型法律风险研判
            </el-button>
          </el-card>
          
          <el-card v-if="analysis.status !== 'idle'" class="progress-card">
            <template #header>
              <div class="card-header">
                <span>⏳ 分析进度</span>
              </div>
            </template>
            <el-progress 
              :percentage="analysis.progress" 
              :status="analysis.status === 'error' ? 'exception' : ''"
              :stroke-width="20"
            />
            <div class="progress-info">
              <div class="progress-step">
                <el-icon v-if="analysis.status === 'completed'" color="#67c23a"><CircleCheckFilled /></el-icon>
                <el-icon v-else-if="analysis.status === 'error'" color="#f56c6c"><CircleCloseFilled /></el-icon>
                <el-icon v-else class="is-loading"><Loading /></el-icon>
                <span class="step-text">{{ getStatusText() }}</span>
              </div>
              <div class="progress-detail" v-if="analysis.status !== 'idle'">
                <div class="step-item" :class="{ active: analysis.status === 'started' }">
                  <span>📤 提交分析任务...</span>
                  <el-icon v-if="analysisProgress >= 15"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
                <div class="step-item" :class="{ active: analysis.status === 'running_experts' }">
                  <span>⚖️ {{ configs.expert1?.name || '刑法专家' }} {{ getExpertStatus(1) }}</span>
                  <el-icon v-if="analysisProgress >= 50"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
                <div class="step-item" :class="{ active: analysis.status === 'running_experts' }">
                  <span>📋 {{ configs.expert2?.name || '合规审查专家' }} {{ getExpertStatus(2) }}</span>
                  <el-icon v-if="analysisProgress >= 50"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
                <div class="step-item" :class="{ active: analysis.status === 'running_experts' }">
                  <span>🔎 {{ configs.expert3?.name || '证据分析专家' }} {{ getExpertStatus(3) }}</span>
                  <el-icon v-if="analysisProgress >= 50"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
                <div class="step-item" :class="{ active: analysis.status === 'running_summary' }">
                  <span>📝 整合三位专家意见...</span>
                  <el-icon v-if="analysisProgress >= 75"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
                <div class="step-item" :class="{ active: analysis.status === 'running_summary' }">
                  <span>📖 {{ configs.summary?.name || '汇总专家' }} 生成报告...</span>
                  <el-icon v-if="analysisProgress >= 100"><CircleCheckFilled color="#67c23a" /></el-icon>
                </div>
              </div>
            </div>
          </el-card>

          <el-card v-if="analysis.status === 'running_experts' || analysis.status === 'running_summary'" class="live-card">
            <template #header>
              <div class="card-header">
                <span>🔍 专家实时分析</span>
              </div>
            </template>
            <div class="live-experts">
              <div v-for="(name, i) in liveExpertNames" :key="i" class="live-expert-col">
                <div class="live-expert-title">
                  {{ name || configs[Object.keys(configs)[i]]?.name || '专家' + (i+1) }}
                  <span v-if="liveExpertDone[i]" style="color:#67c23a;"> ✅</span>
                  <span v-else-if="liveExpertTexts[i]" class="live-cursor"> ⏳</span>
                </div>
                <div class="live-expert-text">
                  <div v-if="liveExpertTexts[i]" :class="liveExpertDone[i] ? 'markdown-content' : 'live-plain-text'" v-html="liveExpertDone[i] ? renderMarkdown(liveExpertTexts[i]) : liveExpertTexts[i].replace(/\n/g, '<br>')"></div>
                  <div v-else class="live-placeholder">等待响应...</div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card v-if="analysis.status === 'running_summary'" class="live-card">
            <template #header>
              <div class="card-header">
                <span>📝 汇总报告生成中</span>
              </div>
            </template>
            <div v-if="liveSummaryText" class="live-plain-text" v-html="liveSummaryText.replace(/\n/g, '<br>')"></div>
            <div v-else class="live-placeholder">等待响应...</div>
          </el-card>

          <el-card v-if="analysis.status === 'completed'" class="result-card">
            <template #header>
              <div class="card-header">
                <span>📜 最终汇总研判报告</span>
                <div style="display:flex;gap:8px;">
                  <el-button type="success" @click="downloadPDF" class="download-btn">📥 PDF</el-button>
                  <el-button type="primary" @click="downloadDOCX" class="download-btn">📝 Word</el-button>
                </div>
              </div>
            </template>
            <el-skeleton :loading="!analysis.finalReport" :rows="6" animated>
              <template #default>
                <div class="markdown-content" v-html="renderMarkdown(analysis.finalReport)"></div>
              </template>
            </el-skeleton>
          </el-card>
          
          <el-card v-if="analysis.status === 'completed'" class="experts-card">
            <template #header>
              <div class="card-header">
                <span>💡 专家报告</span>
              </div>
            </template>
            <div v-for="(report, index) in analysis.reports" :key="index" class="expert-report">
              <el-collapse>
                <el-collapse-item :title="Object.values(configs)[index]?.name">
                  <div class="markdown-content" v-html="renderMarkdown(report)"></div>
                  <el-button type="info" @click="downloadTXT(report, Object.values(configs)[index]?.name)" class="download-txt-btn">
                    保存 TXT
                  </el-button>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
          
          <el-card v-if="analysis.status === 'completed'" class="wordcloud-card">
            <template #header>
              <div class="card-header">
                <span>☁️ 分词词云</span>
                <el-button type="primary" @click="generateWordCloud">
                  点击生成词云
                </el-button>
              </div>
            </template>
            <div v-if="wordCloudVisible" class="wordcloud-container">
              <div id="wordCloudChart" class="wordcloud-chart"></div>
              <el-button type="default" @click="closeWordCloud" class="close-wordcloud-btn">关闭</el-button>
            </div>
            <div v-else class="wordcloud-placeholder">
              <p>点击上方"点击生成词云"按钮，从原始输入文本提取关键词生成词云</p>
            </div>
          </el-card>
        </div>
      </template>
      
      <template v-if="currentPage === 'settings'">
        <div class="settings-content">
          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <span>🔑 API 配置</span>
              </div>
            </template>
            <el-form :model="apiForm" label-width="100px">
              <el-form-item label="API Key">
                <el-input v-model="apiForm.apiKey" type="password" placeholder="输入 API Key" />
              </el-form-item>
              <el-form-item label="Base URL">
                <el-input v-model="apiForm.baseUrl" placeholder="输入 API Base URL" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveAllConfig">保存配置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card class="settings-card" v-for="(config, key) in configs" :key="key">
            <template #header>
              <div class="card-header">
                <span>{{ config.name }} - 模型配置</span>
              </div>
            </template>
            <el-form :model="config" label-width="80px">
              <el-form-item label="模型">
                <el-input v-model="config.model" placeholder="输入模型名称" />
              </el-form-item>
              <el-form-item label="提示词">
                <el-input v-model="config.prompt" type="textarea" :rows="4" placeholder="输入提示词" />
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-button type="success" @click="saveAllConfig" class="save-all-btn">
            保存所有配置
          </el-button>
          
          <div class="config-tip">
            <p>配置文件自动保存在: C:\Users\{{ username }}\AppData\Roaming\LegalRiskApp\config.json</p>
          </div>
        </div>
      </template>
      
      <template v-if="currentPage === 'history'">
        <div class="history-content">
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <span>📋 历史报告</span>
                <div style="display:flex;gap:10px;">
                  <el-input v-model="historySearch" placeholder="搜索标题..." clearable size="small" style="width:200px;" @click.stop />
                  <el-button type="primary" @click="loadHistory">刷新</el-button>
                </div>
              </div>
            </template>
            <el-table :data="filteredHistoryList" style="width: 100%" @row-click="viewHistory">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="created_at" label="时间" width="250" />
              <el-table-column label="标题" width="420">
                <template #default="scope">
                  <div class="title-cell">
                    <el-input 
                      v-model="scope.row.title" 
                      size="small" 
                      placeholder="输入标题"
                      class="title-input"
                      @click.stop
                    />
                    <el-button type="primary" size="small" class="save-btn" @click.stop="saveTitle(scope.row)">
                      保存
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button type="primary" size="small" class="action-btn" @click.stop="viewHistory(scope.row)">查看</el-button>
                  <el-button type="danger" size="small" class="action-btn" @click.stop="deleteHistory(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
          
          <el-card v-if="selectedHistory" class="history-detail-card">
            <template #header>
              <div class="card-header">
                <span>📜 报告详情 - {{ selectedHistory.created_at }}</span>
                <el-button type="success" @click="downloadHistoryPDF">保存 PDF</el-button>
              </div>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(selectedHistory.final_report)"></div>
          </el-card>
          
          <el-card v-if="selectedHistory" class="history-experts-card">
            <template #header>
              <div class="card-header">
                <span>💡 专家报告</span>
              </div>
            </template>
            <div v-for="(name, idx) in ['刑法专家', '合规审查专家', '证据分析专家']" :key="idx" class="expert-report">
              <el-collapse>
                <el-collapse-item :title="name">
                  <div class="markdown-content" v-html="renderMarkdown([selectedHistory.expert1_report, selectedHistory.expert2_report, selectedHistory.expert3_report][idx])"></div>
                  <el-button type="info" size="small" @click="downloadHistoryTXT([selectedHistory.expert1_report, selectedHistory.expert2_report, selectedHistory.expert3_report][idx], name)">
                    保存 TXT
                  </el-button>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
        </div>
      </template>
      
      <template v-if="currentPage === 'allReports'">
        <div class="history-content">
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <span>📋 所有用户报告</span>
                <el-button type="primary" @click="loadAllReports">刷新</el-button>
              </div>
            </template>
            <el-table :data="allReportsList" style="width: 100%" @row-click="viewHistory">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column prop="username" label="用户" width="120" />
              <el-table-column prop="created_at" label="时间" width="200" />
              <el-table-column label="标题" width="350">
                <template #default="scope">
                  <div class="title-cell">
                    <el-input 
                      v-model="scope.row.title" 
                      size="small" 
                      placeholder="输入标题"
                      class="title-input"
                      @click.stop
                    />
                    <el-button type="primary" size="small" class="save-btn" @click.stop="saveTitle(scope.row)">
                      保存
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button type="primary" size="small" class="action-btn" @click.stop="viewHistory(scope.row)">查看</el-button>
                  <el-button type="danger" size="small" class="action-btn" @click.stop="deleteHistory(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
          
          <el-card v-if="selectedHistory" class="history-detail-card">
            <template #header>
              <div class="card-header">
                <span>📜 报告详情 - {{ selectedHistory.created_at }} (用户: {{ selectedHistory.username }})</span>
                <el-button type="success" @click="downloadHistoryPDF">保存 PDF</el-button>
              </div>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(selectedHistory.final_report)"></div>
          </el-card>
          
          <el-card v-if="selectedHistory" class="history-experts-card">
            <template #header>
              <div class="card-header">
                <span>💡 专家报告</span>
              </div>
            </template>
            <div v-for="(name, idx) in ['刑法专家', '合规审查专家', '证据分析专家']" :key="idx" class="expert-report">
              <el-collapse>
                <el-collapse-item :title="name">
                  <div class="markdown-content" v-html="renderMarkdown([selectedHistory.expert1_report, selectedHistory.expert2_report, selectedHistory.expert3_report][idx])"></div>
                  <el-button type="info" size="small" @click="downloadHistoryTXT([selectedHistory.expert1_report, selectedHistory.expert2_report, selectedHistory.expert3_report][idx], name)">
                    保存 TXT
                  </el-button>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '../store'
import * as api from '../api'
import { marked } from 'marked'
import { UploadFilled, Setting, HomeFilled, CircleCheckFilled, CircleCloseFilled, Loading, Clock, User, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

const store = useAppStore()

const apiForm = ref({ apiKey: '', baseUrl: '' })
const content = ref('')
const loading = ref(false)
const username = ref('')
const historyList = ref([])
const historySearch = ref('')
const filteredHistoryList = computed(() => {
  if (!historySearch.value) return historyList.value
  const q = historySearch.value.toLowerCase()
  return historyList.value.filter(h => (h.title || '').toLowerCase().includes(q))
})
const allReportsList = ref([])
const selectedHistory = ref(null)

const configs = computed(() => store.configs)
const analysis = computed(() => store.analysis)
const currentPage = computed(() => store.currentPage)
const analysisProgress = computed(() => analysis.value.progress || 0)
const user = computed(() => store.user)
const isLoggedIn = computed(() => store.isLoggedIn)

const wordCloudVisible = ref(false)
const wordCloudChart = ref(null)

const liveExpertTexts = ref(['', '', ''])
const liveSummaryText = ref('')
const liveExpertNames = ref(['', '', ''])
const liveExpertDone = ref([false, false, false])

const getTimestamp = () => new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')

const saveBlob = async (blob, filename, successMsg = '保存成功') => {
  if (window.pywebview?.api) {
    const b64 = await new Promise(r => { const rd = new FileReader(); rd.onload = () => r(rd.result.split(',')[1]); rd.readAsDataURL(blob) })
    const res = await window.pywebview.api.save_file({ filename, content: b64 })
    res.success ? ElMessage.success(successMsg) : ElMessage.error(successMsg.replace('成功', '失败'))
  } else {
    const u = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = u; a.download = filename; a.click()
    setTimeout(() => URL.revokeObjectURL(u), 5000)
    ElMessage.success(successMsg)
  }
}

username.value = 'Administrator'

const goToSettings = () => store.setCurrentPage('settings')
const goToHome = () => store.setCurrentPage('home')
const goToHistory = async () => {
  store.setCurrentPage('history')
  selectedHistory.value = null
  await loadHistory()
}

const goToUserManagement = () => {
  window.location.href = '/#/users'
}
const goToAllReports = () => {
  store.setCurrentPage('allReports')
  selectedHistory.value = null
  loadAllReports()
}
const logout = () => {
  store.logout()
  window.location.href = '/#/login'
}

const loadHistory = async () => {
  try {
    const res = await api.getHistory(50)
    historyList.value = res.data
  } catch (e) {
    ElMessage.error('加载历史失败')
  }
}

const loadAllReports = async () => {
  try {
    const res = await api.getAllReports()
    allReportsList.value = res.data
  } catch (e) {
    ElMessage.error('加载所有报告失败')
  }
}

const deleteHistory = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条历史记录吗？此操作不可撤销。', '确认删除', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await api.deleteHistory(id)
    ElMessage.success('删除成功')
    await loadHistory()
    if (selectedHistory.value && selectedHistory.value.id === id) {
      selectedHistory.value = null
    }
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const saveTitle = async (row) => {
  try {
    await api.updateHistoryTitle(row.id, row.title)
    ElMessage.success('标题保存成功')
    await loadHistory()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const viewHistory = async (row) => {
  try {
    const res = await api.getHistoryDetail(row.id)
    selectedHistory.value = res.data
  } catch (e) {
    ElMessage.error('加载报告详情失败')
  }
}

let downloadHistoryPDF = async () => {
  if (!selectedHistory.value) return
  const reports = [selectedHistory.value.expert1_report, selectedHistory.value.expert2_report, selectedHistory.value.expert3_report]
  try {
    const res = await api.downloadPDF(selectedHistory.value.final_report, reports, { expert1:{name:'刑法专家'}, expert2:{name:'合规审查专家'}, expert3:{name:'证据分析专家'} })
    if (res.status !== 200) throw new Error('保存失败')
    await saveBlob(res.data, `历史报告_${selectedHistory.value.id}_${getTimestamp()}.pdf`)
  } catch (e) { ElMessage.error('保存失败') }
}

let downloadHistoryTXT = async (report, expertName) => {
  try {
    const res = await api.downloadTXT(report, expertName)
    if (res.status !== 200) throw new Error('保存失败')
    await saveBlob(res.data, `${expertName}报告_${getTimestamp()}.txt`)
  } catch (e) { ElMessage.error('保存失败') }
}

const saveAllConfig = async () => {
  const config = {
    api_key: apiForm.value.apiKey,
    base_url: apiForm.value.baseUrl,
    model: configs.value.expert1?.model || 'mimo-v2.5-pro',
    prompt_configs: configs.value
  }
  store.saveConfigs(configs.value)
  store.saveApiConfig(apiForm.value.apiKey, apiForm.value.baseUrl)
  try {
    if (store.isLoggedIn && store.user) {
      await api.saveUserConfig(store.user.username, config)
      ElMessage.success('配置已保存到服务器')
    } else {
      await api.saveConfig(config)
      ElMessage.success('配置已保存')
    }
  } catch (e) {
    ElMessage.warning('本地保存成功，服务器保存失败')
  }
}

const handleFileChange = async (file) => {
  loading.value = true
  try {
    const response = await api.uploadFile(file.raw)
    content.value = response.data.content
    ElMessage.success('文件内容提取成功')
  } catch (error) {
    ElMessage.error('文件处理失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const startAnalysis = async () => {
  if (!content.value) { ElMessage.warning('请输入或上传待分析内容'); return }
  if (!apiForm.value.apiKey) { ElMessage.warning('请先配置 API Key'); goToSettings(); return }

  loading.value = true
  thinkingIndex.value = 0
  expertStatusIdx.value = { 1: 0, 2: 0, 3: 0 }
  liveExpertTexts.value = ['', '', '']
  liveSummaryText.value = ''
  liveExpertNames.value = ['', '', '']
  liveExpertDone.value = [false, false, false]
  store.startAnalysis('stream')

  const expertBuf = ['', '', '']
  let summaryBuf = ''
  let dirty = false
  let rafId = null

  const flush = () => {
    if (!dirty) { rafId = null; return }
    dirty = false
    for (let i = 0; i < 3; i++) {
      if (expertBuf[i]) { liveExpertTexts.value[i] = expertBuf[i]; expertBuf[i] = '' }
    }
    if (summaryBuf) { liveSummaryText.value = summaryBuf; summaryBuf = '' }
    rafId = requestAnimationFrame(flush)
  }

  const scheduleFlush = () => {
    if (!rafId) rafId = requestAnimationFrame(flush)
  }

  thinkingTimer = setInterval(() => {
    if (analysis.value.status === 'running_experts' || analysis.value.status === 'running_summary') {
      thinkingIndex.value++
    }
    for (let i = 1; i <= 3; i++) expertStatusIdx.value[i]++
  }, 1500)

  await api.analyzeStream(
    content.value,
    apiForm.value.apiKey,
    apiForm.value.baseUrl,
    configs.value,
    (evt) => {
      if (evt.type === 'start') {
        store.updateAnalysisStatus({ status: 'running_experts', progress: 20, currentStep: evt.message })
      } else if (evt.type === 'expert_stream') {
        expertBuf[evt.expert] = (expertBuf[evt.expert] || liveExpertTexts.value[evt.expert] || '') + evt.chunk
        liveExpertNames.value[evt.expert] = evt.name
        dirty = true; scheduleFlush()
      } else if (evt.type === 'expert_done') {
        expertBuf[evt.expert] = ''
        liveExpertTexts.value[evt.expert] = evt.text
        liveExpertDone.value[evt.expert] = true
      } else if (evt.type === 'experts_done') {
        store.updateAnalysisStatus({ reports: evt.reports, progress: 50 })
      } else if (evt.type === 'summary_start') {
        store.updateAnalysisStatus({ status: 'running_summary', progress: 60, currentStep: evt.message })
      } else if (evt.type === 'summary_stream') {
        summaryBuf = (summaryBuf || liveSummaryText.value || '') + evt.chunk
        dirty = true; scheduleFlush()
      } else if (evt.type === 'summary_done') {
        summaryBuf = ''
        liveSummaryText.value = evt.report
        store.updateAnalysisStatus({ finalReport: evt.report, progress: 90 })
      } else if (evt.type === 'error') {
        store.updateAnalysisStatus({ status: 'error', error: evt.message })
        clearInterval(thinkingTimer); if (rafId) cancelAnimationFrame(rafId)
        loading.value = false
      }
    },
    async (data) => {
      clearInterval(thinkingTimer); if (rafId) cancelAnimationFrame(rafId)
      store.updateAnalysisStatus({ status: 'completed', finalReport: data.report, reports: data.reports, progress: 100, currentStep: '✅ 分析完成' })
      loading.value = false
      const ts = getTimestamp()
      try {
        await api.saveHistory({
          title: `法律风险评估报告-${ts}`,
          input_content: content.value,
          final_report: data.report,
          expert1_report: data.reports[0],
          expert2_report: data.reports[1],
          expert3_report: data.reports[2]
        })
        ElMessage.success('报告已自动保存到历史记录')
      } catch (e) { console.error('保存历史失败', e) }
    },
    (err) => {
      clearInterval(thinkingTimer); if (rafId) cancelAnimationFrame(rafId)
      store.updateAnalysisStatus({ status: 'error', error: err })
      loading.value = false
      ElMessage.error('分析失败: ' + err)
    }
  )
}

const expertStatusTexts = {
  1: ['分析中...', '正在理解案件...', '查找相关法规...', '评估风险...', '生成报告...'],
  2: ['分析中...', '正在检查合规性...', '查找监管要求...', '评估风险...', '生成报告...'],
  3: ['分析中...', '正在审查证据...', '分析疑点...', '评估效力...', '生成报告...'],
}
const expertStatusIdx = ref({ 1: 0, 2: 0, 3: 0 })

const thinkingTexts = ['思考中...', '深度分析中...', '理解案件细节...', '查找相关法规...', '评估法律风险...', '生成专业意见...']
const thinkingIndex = ref(0)
let thinkingTimer = null

const getThinkingText = () => thinkingTexts[thinkingIndex.value % thinkingTexts.length]

const getExpertStatus = (expertNum) => {
  if (analysis.value.status !== 'running_experts' || analysisProgress.value >= 50) {
    return '✅ 已完成'
  }
  return expertStatusTexts[expertNum][expertStatusIdx.value[expertNum] % expertStatusTexts[expertNum].length]
}

const getStatusText = () => {
  if (analysis.value.status === 'running_experts') {
    return '🔍 ' + getThinkingText()
  }
  if (analysis.value.status === 'running_summary') {
    return '📝 正在整合三位专家意见...'
  }
  const m = { started: '分析已启动', completed: '分析完成', error: '分析失败' }
  return m[analysis.value.status] || analysis.value.status
}

const renderMarkdown = (t) => marked(t || '')

const downloadPDF = async () => {
  try {
    ElMessage.info('正在生成 PDF...')
    const response = await api.downloadPDF(analysis.value.finalReport, analysis.value.reports, configs.value)
    if (response.status !== 200) throw new Error('下载失败')
    await saveBlob(response.data, `法律风险研判报告_${getTimestamp()}.pdf`, 'PDF保存成功')
  } catch (e) { ElMessage.error('PDF保存失败') }
}

const downloadDOCX = async () => {
  try {
    ElMessage.info('正在生成 Word...')
    const response = await api.downloadDOCX(analysis.value.finalReport, analysis.value.reports, configs.value)
    if (response.status !== 200) throw new Error('下载失败')
    await saveBlob(response.data, `法律风险研判报告_${getTimestamp()}.docx`, 'Word保存成功')
  } catch (e) { ElMessage.error('Word保存失败') }
}

const downloadTXT = async (report, expertName) => {
  try {
    const response = await api.downloadTXT(report, expertName)
    if (response.status !== 200) throw new Error('保存失败')
    await saveBlob(response.data, `${expertName}初步报告_${getTimestamp()}.txt`, 'TXT保存成功')
  } catch (e) { ElMessage.error('TXT保存失败') }
}

const generateWordCloud = async () => {
  if (!content.value) {
    ElMessage.warning('请先输入待分析内容')
    return
  }
  wordCloudVisible.value = true
  try {
    const res = await api.extractKeywords(content.value, 80)
    const keywords = res.data.keywords || []
    if (keywords.length === 0) {
      ElMessage.warning('未提取到关键词')
      return
    }
    setTimeout(() => {
      const chartDom = document.getElementById('wordCloudChart')
      if (!chartDom) return
      if (wordCloudChart.value) {
        wordCloudChart.value.dispose()
      }
      wordCloudChart.value = echarts.init(chartDom)
      const option = {
        tooltip: {
          show: true
        },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '90%',
          height: '90%',
          right: null,
          bottom: null,
          sizeRange: [12, 60],
          rotationRange: [-45, 90],
          rotationStep: 45,
          gridSize: 8,
          drawOutOfBound: false,
          layoutAnimation: true,
          textStyle: {
            fontFamily: 'Microsoft YaHei',
            fontWeight: 'bold',
            color: () => {
              const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          data: keywords.map(k => ({ name: k.word, value: k.count }))
        }]
      }
      wordCloudChart.value.setOption(option)
    }, 100)
  } catch (e) {
    ElMessage.error('词云生成失败')
  }
}

const closeWordCloud = () => {
  wordCloudVisible.value = false
  if (wordCloudChart.value) {
    wordCloudChart.value.dispose()
    wordCloudChart.value = null
  }
}

const resetAnalysis = () => { store.resetAnalysis(); content.value = ''; ElMessage.success('分析已重置') }

onMounted(async () => {
  try {
    // 如果未登录，跳转到登录页
    if (!store.isLoggedIn) {
      window.location.href = '/#/login'
      return
    }
    
    // 加载用户特定配置
    if (store.user) {
      try {
        const userConfig = await api.getUserConfig(store.user.username)
        if (userConfig.data.api_key) {
          apiForm.value.apiKey = userConfig.data.api_key
          store.saveApiConfig(userConfig.data.api_key, userConfig.data.base_url || store.baseUrl)
        }
        if (userConfig.data.base_url) {
          apiForm.value.baseUrl = userConfig.data.base_url
        }
        if (userConfig.data.prompt_configs) {
          store.configs = { ...store.configs, ...userConfig.data.prompt_configs }
        }
      } catch (e) {
        // 如果用户配置加载失败，加载全局配置
        const res = await api.getConfig()
        const data = res.data
        if (data.apiKey) { apiForm.value.apiKey = data.apiKey; store.saveApiConfig(data.apiKey, data.baseUrl) }
        if (data.baseUrl) apiForm.value.baseUrl = data.baseUrl
        if (data.configs) { store.configs = { ...store.configs, ...data.configs } }
      }
    } else {
      // 加载全局配置
      const res = await api.getConfig()
      const data = res.data
      if (data.apiKey) { apiForm.value.apiKey = data.apiKey; store.saveApiConfig(data.apiKey, data.baseUrl) }
      if (data.baseUrl) apiForm.value.baseUrl = data.baseUrl
      if (data.configs) { store.configs = { ...store.configs, ...data.configs } }
    }
  } catch {}
})

onUnmounted(() => {
  if (thinkingTimer) clearInterval(thinkingTimer)
})
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; overflow: hidden; }

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.top-bar h2 { font-size: 18px; font-weight: bold; margin: 0; }

.top-bar-right { display: flex; gap: 10px; align-items: center; }

.content-area {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.home-content, .settings-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 900px;
  margin: 0 auto;
}

.settings-content .settings-card { width: 100%; }

.history-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 1000px;
  margin: 0 auto;
}

.history-card, .history-detail-card, .history-experts-card { width: 100%; }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 分析按钮样式 */
.analyze-btn {
  width: 100%;
  margin-top: 15px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: bold;
}

.progress-info { margin-top: 15px; }

.progress-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.step-text { font-weight: bold; color: #409eff; }

.progress-detail { display: flex; flex-direction: column; gap: 8px; }

.step-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
}

.step-item.active { background: #ecf5ff; color: #409eff; }

.is-loading { animation: rot 2s linear infinite; }
@keyframes rot { from { transform: rotate(0); } to { transform: rotate(360deg); } }

.markdown-content { 
  line-height: 1.8; 
  font-size: 14px;
  color: #303133;
}
.markdown-content p { margin-bottom: 12px; text-align: justify; }
.markdown-content h1 { font-size: 18px; color: #409eff; border-bottom: 1px solid #dcdfe6; padding-bottom: 8px; }
.markdown-content h2 { font-size: 16px; color: #303133; margin-top: 20px; }
.markdown-content h3 { font-size: 15px; color: #606266; }
.markdown-content ul, .markdown-content ol { padding-left: 20px; margin-bottom: 12px; }
.markdown-content li { margin-bottom: 6px; }
.markdown-content strong { color: #e6a23c; }
.markdown-content code { background: #f5f7fa; padding: 2px 4px; border-radius: 3px; }
.markdown-content pre { background: #f5f7fa; padding: 10px; border-radius: 5px; overflow-x: auto; margin-bottom: 10px; }
.markdown-content table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
.markdown-content th, .markdown-content td { border: 1px solid #e4e7ed; padding: 8px; text-align: left; }
.markdown-content th { background: #f5f7fa; font-weight: bold; }

.expert-report { margin-top: 10px; }
.download-txt-btn { margin-top: 10px; padding: 6px 12px; font-size: 12px; }
.save-all-btn { width: 100%; margin-top: 15px; padding: 10px 20px; font-size: 14px; }
.config-tip { text-align: center; color: #909399; font-size: 12px; margin-top: 15px; }
.title-cell { display: flex; align-items: center; gap: 8px; }
.title-input { width: 250px; }
.save-btn { padding: 4px 12px; border-radius: 4px; font-size: 12px; min-width: 60px; }
.action-btn { padding: 4px 12px; border-radius: 4px; font-size: 12px; min-width: 60px; margin-right: 5px; }
.wordcloud-card { width: 100%; }
.wordcloud-container { position: relative; }
.wordcloud-chart { width: 100%; height: 400px; }
.wordcloud-placeholder { text-align: center; padding: 60px 20px; color: #909399; }
.close-wordcloud-btn { position: absolute; top: 10px; right: 10px; padding: 4px 12px; font-size: 12px; }

/* 上传按钮样式优化 */
:deep(.el-upload__text) {
  font-size: 14px;
  color: #606266;
}

/* 卡片样式优化 */
:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

/* 输入框样式优化 */
:deep(.el-input__inner) {
  border-radius: 6px;
  height: 36px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
  min-height: 120px;
}

/* 下拉菜单样式优化 */
:deep(.el-dropdown-menu) {
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.15);
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: bold;
}

:deep(.el-table tr:hover) {
  background-color: #ecf5ff;
}

.live-card { margin-top: 15px; }
.live-experts { display: flex; gap: 12px; }
.live-expert-col { flex: 1; min-width: 0; border: 1px solid #e4e7ed; border-radius: 8px; padding: 12px; background: #fafafa; }
.live-expert-title { font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.live-expert-text { max-height: 300px; overflow-y: auto; font-size: 13px; line-height: 1.6; }
.live-placeholder { color: #c0c4cc; font-style: italic; padding: 20px 0; text-align: center; }
.live-plain-text { white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.8; color: #303133; max-height: 300px; overflow-y: auto; }
.live-cursor { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0.3; } }
</style>