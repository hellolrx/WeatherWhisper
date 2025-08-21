<script setup lang="ts">
import { ref, watch, computed, defineProps, defineEmits } from 'vue'
import type { FavoriteCity } from '../../types/weather'
import { useNotificationApi, type SendWeatherPayload, type ScheduleWeatherPayload } from '../../composables/useNotificationApi'

interface Props {
  visible: boolean
  favorites: FavoriteCity[]
  defaultCityId?: string
  defaultEmail?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'sent', payload: any): void }>()

const cityId = ref(props.defaultCityId || '')
const email = ref(props.defaultEmail || '')
const mode = ref<'NOW'|'SCHEDULE'>('NOW')
const scheduleType = ref<'ONCE'|'DAILY'>('ONCE')

// 监听 defaultCityId 变化，确保弹窗打开时选中正确的城市
watch(() => props.defaultCityId, (newCityId) => {
  if (newCityId) {
    cityId.value = newCityId
  }
}, { immediate: true })

// 监听弹窗显示状态，重置表单
watch(() => props.visible, (visible) => {
  if (visible) {
    // 弹窗打开时，确保选中正确的城市
    if (props.defaultCityId) {
      cityId.value = props.defaultCityId
    } else if (props.favorites.length > 0 && !cityId.value) {
      cityId.value = props.favorites[0].id
    }
    
    // 重置发送方式为立即发送
    mode.value = 'NOW'
    
    // 触发预览
    doPreview()
  }
})

function getNowHHMM() {
  const d = new Date()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}
function getTodayYMD() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth()+1).padStart(2,'0')
  const dd = String(d.getDate()).padStart(2,'0')
  return `${y}-${m}-${dd}`
}
function toLocalStr(iso: string | undefined) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const y = d.getFullYear()
    const m = String(d.getMonth()+1).padStart(2,'0')
    const dd = String(d.getDate()).padStart(2,'0')
    const hh = String(d.getHours()).padStart(2,'0')
    const mm = String(d.getMinutes()).padStart(2,'0')
    return `${y}-${m}-${dd} ${hh}:${mm}`
  } catch { return iso || '' }
}

const timeHHMM = ref(getNowHHMM())
const dateYMD = ref<string>(getTodayYMD())

const previewText = ref('')
const loadingPreview = ref(false)
const { sending, previewWeatherEmail, sendWeatherEmail, scheduleWeatherEmail } = useNotificationApi()

// 轻量toast
const toastMsg = ref('')
const toastType = ref<'success'|'error'>('success')
let toastTimer: number | null = null
function showToast(msg: string, type: 'success'|'error' = 'success') {
  toastMsg.value = msg
  toastType.value = type
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => (toastMsg.value = ''), 2500)
}

function currentCity() {
  const c = props.favorites.find(x => x.id === cityId.value) || props.favorites[0]
  return c
}

watch([cityId, mode, scheduleType, timeHHMM, dateYMD], () => {
  if (props.visible) doPreview()
})

watch(mode, (v) => {
  if (v === 'SCHEDULE') {
    scheduleType.value = 'ONCE'
    timeHHMM.value = getNowHHMM()
    dateYMD.value = getTodayYMD()
  }
})

async function doPreview() {
  const c = currentCity()
  if (!c) return
  loadingPreview.value = true
  try {
    const payload: SendWeatherPayload = { city_name: c.name, province: c.adm1, email: email.value, dry_run: true }
    const res = await previewWeatherEmail(payload)
    previewText.value = res?.preview || ''
  } catch (e: any) {
    previewText.value = '预览失败，请稍后重试。'
  } finally {
    loadingPreview.value = false
  }
}

async function handleSubmit() {
  const c = currentCity()
  if (!c) return
  try {
    if (mode.value === 'NOW') {
      const res = await sendWeatherEmail({ city_name: c.name, province: c.adm1, email: email.value })
      showToast(res?.message || '发送成功', 'success')
      emit('sent', res)
      window.setTimeout(() => emit('close'), 1200)
    } else {
      const res = await scheduleWeatherEmail({ city_name: c.name, province: c.adm1, email: email.value, type: scheduleType.value, time: timeHHMM.value, date: dateYMD.value || undefined })
      const tip = res?.next_run_at ? `定时创建成功，将在 ${toLocalStr(res.next_run_at)} 发送` : (res?.message || '定时创建成功')
      showToast(tip, 'success')
      emit('sent', res)
      window.setTimeout(() => emit('close'), 1200)
    }
  } catch (e: any) {
    showToast(e?.response?.data?.detail || e?.message || '操作失败', 'error')
  }
}

function handleClose() { emit('close') }
</script>

<template>
  <div v-if="visible" class="modal-mask">
    <div class="modal">
      <div class="modal-header">
        <h3>发送今日天气到邮箱</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>
      <div v-if="toastMsg" class="global-toast" :class="toastType">{{ toastMsg }}</div>
      <div class="modal-body">
        <div class="form-row">
          <label>城市</label>
          <select v-model="cityId">
            <option v-for="c in favorites" :key="c.id" :value="c.id">{{ c.adm1 }} · {{ c.name }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="默认使用当前登录邮箱" />
        </div>
        <div class="form-row">
          <label>发送方式</label>
          <div class="radio-group">
            <label><input type="radio" value="NOW" v-model="mode" /> 立即发送</label>
            <label><input type="radio" value="SCHEDULE" v-model="mode" /> 定时发送</label>
          </div>
        </div>
        <div v-if="mode==='SCHEDULE'" class="schedule-box">
          <div class="form-row">
            <label>频率</label>
            <div class="radio-group">
              <label><input type="radio" value="ONCE" v-model="scheduleType" /> 一次</label>
              <label><input type="radio" value="DAILY" v-model="scheduleType" /> 每天</label>
            </div>
          </div>
          <div class="form-row">
            <label>时间</label>
            <input v-model="timeHHMM" type="time" />
          </div>
          <div v-if="scheduleType==='ONCE'" class="form-row">
            <label>日期</label>
            <input v-model="dateYMD" type="date" />
          </div>
        </div>
        <div class="preview">
          <div class="preview-title">将发送如下内容：</div>
          <pre class="preview-text">{{ loadingPreview ? '生成预览中…' : (previewText || '示例：现在是 09:00，广州 多云。当前 28°C，体感 30°C，东北风2级，湿度 62%；今日最高 32°C、最低 26°C。') }}</pre>
        </div>
      </div>
      <div class="modal-footer">
        <button class="secondary" @click="handleClose">取消</button>
        <button class="primary" :disabled="sending" @click="handleSubmit">{{ mode==='NOW' ? (sending ? '发送中…' : '发送') : (sending ? '创建中…' : '创建定时') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 3000; }
.modal { width: min(520px, 94vw); background: #fff; border-radius: 12px; box-shadow: 0 20px 50px rgba(0,0,0,0.2); overflow: hidden; position: relative; }
.modal-header { display:flex; align-items:center; justify-content:space-between; padding: 16px 20px; border-bottom: 1px solid #eee; }
.global-toast { position: absolute; right: 16px; top: 8px; padding: 6px 10px; border-radius: 6px; font-size: 12px; color: #fff; z-index: 10; }
.global-toast.success { background: #16a34a; }
.global-toast.error { background: #ef4444; }
.modal-body { padding: 16px 20px; display:flex; flex-direction: column; gap: 12px; }
.modal-footer { padding: 12px 20px 16px; display:flex; justify-content:flex-end; gap: 8px; border-top: 1px solid #eee; }
.form-row { display:flex; align-items:center; gap: 12px; }
.form-row label { width: 72px; color: #555; }
.form-row input, .form-row select { flex: 1; padding: 8px 10px; border: 1px solid #e5e7eb; border-radius: 8px; }
.radio-group { display:flex; gap: 16px; }
.preview { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }
.preview-title { font-size: 0.9rem; color: #475569; margin-bottom: 6px; }
.preview-text { margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 0.95rem; color: #334155; }
button.primary { background: #0984e3; color: #fff; border: none; padding: 8px 14px; border-radius: 8px; }
button.secondary { background: #e5e7eb; color: #1f2937; border: none; padding: 8px 14px; border-radius: 8px; }
.close-btn { background: transparent; border: none; font-size: 20px; cursor: pointer; }
.schedule-box { padding: 8px 12px; border: 1px dashed #e5e7eb; border-radius: 8px; }
</style> 