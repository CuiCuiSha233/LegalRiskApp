import { defineStore } from 'pinia'

const DEFAULT_CONFIGS = {
  expert1: {
    name: '刑法专家',
    model: 'Pro/deepseek-ai/DeepSeek-V3',
    prompt: '你是一位刑法专家，请分析以下行为是否触犯刑法，并列出可能涉及的罪名及法条依据。'
  },
  expert2: {
    name: '合规审查专家',
    model: 'Pro/deepseek-ai/DeepSeek-V3',
    prompt: '你是一位合规审查专家，请从行政合规和行业监管的角度分析以下行为的合规风险，给出预防措施。'
  },
  expert3: {
    name: '证据分析专家',
    model: 'Pro/deepseek-ai/DeepSeek-V3',
    prompt: '你是一位证据分析专家，请指出以下描述中可能存在的证据瑕疵或需要进一步调查的疑点。'
  },
  summary: {
    name: '汇总专家',
    model: 'Pro/deepseek-ai/DeepSeek-V3',
    prompt: '你是一位资深律师和首席法官，请汇总以上三位专家的意见，进行交叉验证和冲突解决，最终为客户提供一份简洁、全面、专业的法律风险评估报告。严格注意：报告内容须直接输出，**不得包含报告出具人、日期、免责声明等任何尾部签名或脚注信息。**'
  }
}

export const useAppStore = defineStore('app', {
  state: () => ({
    apiKey: localStorage.getItem('apiKey') || '',
    baseUrl: localStorage.getItem('baseUrl') || 'https://api.siliconflow.cn',
    configs: JSON.parse(JSON.stringify(DEFAULT_CONFIGS)),
    content: '',
    analysis: {
      taskId: null,
      status: 'idle',
      progress: 0,
      currentStep: '',
      reports: [],
      finalReport: null,
      error: null
    },
    loading: false,
    currentPage: 'home',
    // 用户认证相关
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    isLoggedIn: !!localStorage.getItem('token'),

  }),
  
  actions: {
    saveApiConfig(apiKey, baseUrl) {
      this.apiKey = apiKey
      this.baseUrl = baseUrl
      localStorage.setItem('apiKey', apiKey)
      localStorage.setItem('baseUrl', baseUrl)
    },
    
    saveConfigs(configs) {
      this.configs = configs
      localStorage.setItem('configs', JSON.stringify(configs))
    },
    
    loadConfigs() {
      const savedConfigs = localStorage.getItem('configs')
      if (savedConfigs) {
        const parsed = JSON.parse(savedConfigs)
        this.configs = { ...DEFAULT_CONFIGS, ...parsed }
      }
    },
    
    startAnalysis(taskId) {
      this.analysis.taskId = taskId
      this.analysis.status = 'started'
      this.analysis.progress = 10
      this.analysis.currentStep = '正在初始化分析任务...'
      this.analysis.reports = []
      this.analysis.finalReport = null
      this.analysis.error = null
    },
    
    updateAnalysisStatus(status) {
      this.analysis = { ...this.analysis, ...status }
    },
    
    resetAnalysis() {
      this.analysis = {
        taskId: null,
        status: 'idle',
        progress: 0,
        currentStep: '',
        reports: [],
        finalReport: null,
        error: null
      }
      this.content = ''
    },

    setCurrentPage(page) {
      this.currentPage = page
    },

    // 用户认证相关方法
    async login(username, password) {
      try {
        const response = await import('../api').then(m => m.login(username, password))
        this.token = response.data.access_token
        this.isLoggedIn = true
        localStorage.setItem('token', this.token)
        
        // 获取用户信息
        const userResponse = await import('../api').then(m => m.getCurrentUser())
        this.user = userResponse.data
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },

    async register(username, password, email) {
      try {
        const response = await import('../api').then(m => m.register({ username, password, email }))
        return true
      } catch (error) {
        console.error('Registration failed:', error)
        return false
      }
    },

    async logout() {
      try {
        // 调用后端登出API清除数据库中的token
        await import('../api').then(m => m.logout())
      } catch (error) {
        console.error('Logout API call failed:', error)
      }
      // 清除本地状态
      this.token = null
      this.user = null
      this.isLoggedIn = false
      this.content = ''
      this.resetAnalysis()
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('apiKey')
      localStorage.removeItem('baseUrl')
      localStorage.removeItem('configs')
    },


  }
})
