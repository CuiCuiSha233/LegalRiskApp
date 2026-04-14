import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 分析接口
export const analyze = (content, apiKey, baseUrl, configs) => {
  return api.post('/analyze', {
    content,
    api_key: apiKey,
    base_url: baseUrl,
    configs
  })
}

// 获取分析状态
export const getAnalysisStatus = (taskId) => {
  return api.get(`/analysis/status/${taskId}`)
}

// 上传文件
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 下载 PDF 报告
export const downloadPDF = (finalReport, reports, configs) => {
  return api.post('/download/pdf', {
    final_report: finalReport,
    reports,
    configs
  }, {
    responseType: 'blob'
  })
}

// 下载专家报告 TXT
export const downloadTXT = (report, expertName) => {
  return api.post('/download/txt', {
    report,
    expert_name: expertName
  }, {
    responseType: 'blob'
  })
}

export const getConfig = () => {
  return api.get('/config')
}

export const saveConfig = (config) => {
  return api.post('/config', config)
}

export const getHistory = (limit = 20) => {
  return api.get(`/history?limit=${limit}`)
}

export const getHistoryDetail = (id) => {
  return api.get(`/history/${id}`)
}

export const saveHistory = (data) => {
  return api.post('/history/save', data)
}

export const deleteHistory = (id) => {
  return api.delete(`/history/${id}`)
}

export const updateHistoryTitle = (id, title) => {
  return api.put(`/history/${id}/title`, { title })
}

export const extractKeywords = (text, topN = 50) => {
  return api.post('/extract-keywords', { text, top_n: topN })
}

// 用户认证相关 API
export const register = (user) => {
  return api.post('/register', user)
}

export const login = (username, password) => {
  return api.post('/token', new URLSearchParams({
    username,
    password,
    grant_type: 'password'
  }), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export const getCurrentUser = () => {
  return api.get('/users/me')
}

// 用户管理相关 API
export const getUsers = () => {
  return api.get('/users')
}

export const deleteUser = (userId) => {
  return api.delete(`/users/${userId}`)
}

export const updateUser = (userId, userData) => {
  return api.put(`/users/${userId}`, userData)
}

// 用户配置相关 API
export const getUserConfig = (username) => {
  return api.get(`/users/${username}/config`)
}

export const saveUserConfig = (username, config) => {
  return api.post(`/users/${username}/config`, config)
}

// 管理员相关 API
export const getAllReports = () => {
  return api.get('/admin/reports')
}

// 登出 API
export const logout = () => {
  return api.post('/logout')
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/#/login'
    }
    return Promise.reject(error)
  }
)
