<template>
  <div class="user-management-container">
    <div class="user-management-card">
      <div class="user-management-header">
        <h2>用户管理</h2>
        <el-button type="primary" @click="goToHome">返回首页</el-button>
      </div>
      
      <el-table :data="users" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="last_login" label="最后登录" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editUser(scope.row)">
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteUser(scope.row)"
              :disabled="scope.row.username === 'admin'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="新密码 (留空不修改)">
          <el-input v-model="editForm.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEditUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from '../api'

const loading = ref(false)
const saving = ref(false)
const users = ref([])
const editDialogVisible = ref(false)
const editForm = ref({
  id: null,
  email: '',
  role: 'user',
  password: ''
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.getUsers()
    users.value = response.data
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  editForm.value = {
    id: user.id,
    email: user.email || '',
    role: user.role || 'user',
    password: ''
  }
  editDialogVisible.value = true
}

const saveEditUser = async () => {
  if (!editForm.value.id) return
  
  saving.value = true
  try {
    const userData = {}
    if (editForm.value.email !== undefined) {
      userData.email = editForm.value.email
    }
    if (editForm.value.role) {
      userData.role = editForm.value.role
    }
    if (editForm.value.password) {
      userData.password = editForm.value.password
    }
    
    await api.updateUser(editForm.value.id, userData)
    ElMessage.success('用户信息更新成功')
    editDialogVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error('更新用户信息失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.deleteUser(user.id)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除用户失败')
      console.error(error)
    }
  }
}

const goToHome = () => {
  window.location.href = '/#/home'
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.user-management-card {
  width: 100%;
  max-width: 1200px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.user-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.user-management-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}
</style>
