<template>
  <div v-if="device" class="sidebar">
    <div class="sidebar-header">
      <h3>Device Details</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>

    <!-- Tab Navigation -->
    <div class="tab-nav">
      <button 
        :class="['tab-btn', { active: activeTab === 'overview' }]"
        @click="activeTab = 'overview'"
      >
        Overview
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'interfaces' }]"
        @click="loadInterfaces(); activeTab = 'interfaces'"
      >
        Interfaces
      </button>
      <button 
        v-if="showOpticalTab"
        :class="['tab-btn', { active: activeTab === 'optical' }]"
        @click="activeTab = 'optical'"
      >
        Optical
      </button>
    </div>

    <div class="sidebar-body">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="detail-row">
          <span class="label">Name:</span>
          <span class="value">{{ device.name }}</span>
        </div>

        <div class="detail-row">
          <span class="label">Type:</span>
          <span class="value">{{ device.device_type }}</span>
        </div>

        <div class="detail-row">
          <span class="label">Status:</span>
          <span class="value" :class="`status-${device.status.toLowerCase()}`">
            {{ device.status }}
            <span v-if="device.status_override" class="override-badge">
              🔒 Override
            </span>
          </span>
        </div>

        <div v-if="device.status_override" class="detail-row">
          <span class="label">Override Reason:</span>
          <span class="value override-reason">{{ device.override_reason || 'None' }}</span>
        </div>

        <div class="detail-row">
          <span class="label">Position:</span>
          <span class="value">{{ device.x }}, {{ device.y }}</span>
        </div>

        <div class="detail-row">
          <span class="label">ID:</span>
          <span class="value">#{{ device.id }}</span>
        </div>
      </div>

      <!-- Interfaces Tab -->
      <div v-else-if="activeTab === 'interfaces'" class="tab-content">
        <div v-if="loadingInterfaces" class="loading">
          Loading interfaces...
        </div>
        <div v-else-if="interfaces.length === 0" class="empty-state">
          No interfaces found
        </div>
        <div v-else class="interfaces-list">
          <div
            v-for="iface in interfaces"
            :key="iface.id"
            class="interface-card"
          >
            <div class="interface-header">
              <span class="interface-name">{{ iface.name }}</span>
              <span :class="['interface-status', `status-${iface.effective_status?.toLowerCase()}`]">
                {{ iface.effective_status || 'UNKNOWN' }}
              </span>
            </div>
            <div class="interface-details">
              <div class="interface-row">
                <span class="interface-label">MAC:</span>
                <span class="interface-value mac">{{ iface.mac || 'N/A' }}</span>
              </div>
              <div class="interface-row">
                <span class="interface-label">Role:</span>
                <span class="interface-value">{{ iface.port_role || iface.role || 'N/A' }}</span>
              </div>
              <div v-if="iface.addresses && iface.addresses.length > 0" class="addresses-section">
                <div class="interface-label">Addresses:</div>
                <div
                  v-for="addr in iface.addresses"
                  :key="addr.ip"
                  class="address-item"
                >
                  <span class="address-ip">{{ addr.ip }}/{{ addr.prefix_len }}</span>
                  <span v-if="addr.primary" class="primary-badge">PRIMARY</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Optical Tab -->
      <div v-else-if="activeTab === 'optical'" class="tab-content">
        <div v-if="device.device_type === 'ONT' || device.device_type === 'BUSINESS_ONT'" class="optical-section">
          <h4>Signal Quality</h4>
          <div class="signal-display">
            <div class="detail-row">
              <span class="label">Signal Status:</span>
              <span class="value">Computing...</span>
            </div>
            <div class="detail-row">
              <span class="label">Sensitivity Min:</span>
              <span class="value">{{ (device as any).sensitivity_min_dbm?.toFixed(2) || '-30.0' }} dBm</span>
            </div>
            <div class="note">
              💡 Optical signal budget is calculated by the backend based on path topology.
            </div>
          </div>
        </div>
        <div v-else-if="device.device_type === 'OLT'" class="optical-section">
          <h4>Optical Transmitter</h4>
          <div class="detail-row">
            <span class="label">TX Power:</span>
            <span class="value">{{ (device as any).tx_power_dbm?.toFixed(2) || '+5.0' }} dBm</span>
          </div>
        </div>
        <div v-else-if="device.device_type === 'ODF' || device.device_type === 'NVT' || device.device_type === 'SPLITTER' || device.device_type === 'HOP'" class="optical-section">
          <h4>Passive Device</h4>
          <div class="detail-row">
            <span class="label">Insertion Loss:</span>
            <span class="value">{{ (device as any).insertion_loss_db?.toFixed(2) || 'N/A' }} dB</span>
          </div>
        </div>
        <div v-else class="empty-state">
          No optical attributes for this device type
        </div>
      </div>
    </div>

    <div class="sidebar-footer">
      <!-- Status Override Section -->
      <div v-if="!device.status_override" class="override-section">
        <label class="override-label">Manual Override:</label>
        <div class="override-buttons">
          <button class="btn-override btn-override-up" @click="setOverride('UP')">
            Force UP
          </button>
          <button class="btn-override btn-override-down" @click="setOverride('DOWN')">
            Force DOWN
          </button>
        </div>
      </div>
      
      <div v-else class="override-section override-active">
        <div class="override-info">
          🔒 Status Override Active
        </div>
        <button class="btn-clear-override" @click="clearOverride">
          Clear Override
        </button>
      </div>

      <button class="btn-delete" @click="showDeleteConfirm = true">
        🗑️ Delete Device
      </button>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :is-open="showDeleteConfirm"
      title="Delete Device"
      :message="`Are you sure you want to delete '${device.name}'? This action cannot be undone.`"
      confirm-label="Delete"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ConfirmDialog from './ConfirmDialog.vue'

interface Address {
  ip: string
  prefix_len: number
  primary?: boolean
}

interface InterfaceData {
  id: string
  name: string
  mac: string | null
  role: string | null
  port_role: string | null
  admin_status: string
  effective_status: string
  addresses: Address[]
}

interface OpticalData {
  received_dbm: number | null
  signal_status: string | null
  margin_db: number | null
}

interface Device {
  id: number
  name: string
  device_type: string
  status: string
  status_override: string | null
  override_reason: string | null
  x: number
  y: number
}

const props = defineProps<{
  device: Device | null
}>()

const emit = defineEmits<{
  close: []
  delete: [id: number]
  overrideUpdated: []
}>()

const showDeleteConfirm = ref(false)
const activeTab = ref<'overview' | 'interfaces' | 'optical'>('overview')
const interfaces = ref<InterfaceData[]>([])
const loadingInterfaces = ref(false)
const opticalData = ref<OpticalData | null>(null)

// Computed: Show optical tab for optical devices
const showOpticalTab = computed(() => {
  if (!props.device) return false
  const opticalTypes = ['OLT', 'ONT', 'BUSINESS_ONT', 'ODF', 'NVT', 'SPLITTER', 'HOP']
  return opticalTypes.includes(props.device.device_type)
})

// Watch device changes to reset tab
watch(() => props.device, () => {
  activeTab.value = 'overview'
  interfaces.value = []
  opticalData.value = null
})

async function loadInterfaces() {
  if (!props.device || loadingInterfaces.value) return
  
  loadingInterfaces.value = true
  try {
    const response = await fetch(`/api/devices/${props.device.id}/interfaces`)
    if (response.ok) {
      const data = await response.json()
      interfaces.value = data
      console.log(`✅ Loaded ${data.length} interfaces`)
    } else {
      console.error('❌ Failed to load interfaces')
      interfaces.value = []
    }
  } catch (error) {
    console.error('❌ Error loading interfaces:', error)
    interfaces.value = []
  } finally {
    loadingInterfaces.value = false
  }
}

async function setOverride(status: 'UP' | 'DOWN') {
  if (!props.device) return
  
  try {
    const response = await fetch(`/api/devices/${props.device.id}/override`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status_override: status,
        override_reason: `Manually set to ${status}`
      })
    })
    
    if (response.ok) {
      console.log(`✅ Status override set: ${status}`)
      emit('overrideUpdated')
    } else {
      console.error('❌ Failed to set override')
    }
  } catch (error) {
    console.error('❌ Error setting override:', error)
  }
}

async function clearOverride() {
  if (!props.device) return
  
  try {
    const response = await fetch(`/api/devices/${props.device.id}/override`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      console.log('✅ Override cleared')
      emit('overrideUpdated')
    } else {
      console.error('❌ Failed to clear override')
    }
  } catch (error) {
    console.error('❌ Error clearing override:', error)
  }
}

function handleDelete() {
  if (props.device) {
    emit('delete', props.device.id)
    showDeleteConfirm.value = false
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  height: 100%;
  background: #2a2a2a;
  border-left: 2px solid #3a3a3a;
  display: flex;
  flex-direction: column;
  z-index: 100;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #3a3a3a;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #fff;
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  border-bottom: 1px solid #3a3a3a;
  background: #1a1a1a;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  color: #aaa;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 3px solid transparent;
}

.tab-btn:hover {
  color: #fff;
  background: #2a2a2a;
}

.tab-btn.active {
  color: #4caf50;
  border-bottom-color: #4caf50;
  background: #2a2a2a;
}

.sidebar-body {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #1a1a1a;
  border-radius: 4px;
}

.label {
  font-size: 0.9rem;
  color: #aaa;
  font-weight: 500;
}

.value {
  font-size: 0.95rem;
  color: #fff;
  font-weight: 600;
}

.status-up {
  color: #4caf50;
}

.status-down {
  color: #f44336;
}

.status-degraded {
  color: #ff9800;
}

/* Interfaces List */
.loading, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #aaa;
  font-style: italic;
}

.interfaces-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.interface-card {
  background: #1a1a1a;
  border: 1px solid #3a3a3a;
  border-radius: 8px;
  padding: 1rem;
}

.interface-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #3a3a3a;
}

.interface-name {
  font-size: 1rem;
  font-weight: 700;
  color: #4caf50;
}

.interface-status {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
}

.interface-status.status-up {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.interface-status.status-down {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.interface-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.interface-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.interface-label {
  color: #aaa;
  font-weight: 500;
}

.interface-value {
  color: #fff;
  font-weight: 600;
}

.interface-value.mac {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.addresses-section {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #3a3a3a;
}

.address-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.5rem;
  background: #0a0a0a;
  border-radius: 3px;
  margin-top: 0.4rem;
}

.address-ip {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #4caf50;
}

.primary-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.4rem;
  background: #2196f3;
  color: white;
  border-radius: 3px;
  font-weight: 600;
}

/* Optical Section */
.optical-section h4 {
  margin: 0 0 1rem 0;
  color: #ff9800;
  font-size: 1rem;
}

.signal-display {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.note {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(33, 150, 243, 0.1);
  border-left: 3px solid #2196f3;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #aaa;
  line-height: 1.4;
}

.signal-status {
  text-align: center;
  padding: 0.75rem;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.signal-status.signal-ok {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 2px solid #4caf50;
}

.signal-status.signal-warning {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 2px solid #ff9800;
}

.signal-status.signal-critical {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 2px solid #f44336;
}

.signal-status.signal-no_signal {
  background: rgba(128, 128, 128, 0.2);
  color: #888;
  border: 2px solid #888;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid #3a3a3a;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Override Section */
.override-section {
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 8px;
  border: 2px solid #3a3a3a;
}

.override-section.override-active {
  border-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.override-label {
  display: block;
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.override-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-override {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-override-up {
  background: #4caf50;
  color: white;
}

.btn-override-up:hover {
  background: #45a049;
  transform: translateY(-1px);
}

.btn-override-down {
  background: #f44336;
  color: white;
}

.btn-override-down:hover {
  background: #d32f2f;
  transform: translateY(-1px);
}

.override-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #ff9800;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.btn-clear-override {
  width: 100%;
  padding: 0.5rem;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear-override:hover {
  background: #f57c00;
  transform: translateY(-1px);
}

.override-badge {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.2rem 0.5rem;
  background: #ff9800;
  color: white;
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 600;
}

.override-reason {
  font-style: italic;
  color: #ff9800;
}

.btn-delete {
  width: 100%;
  padding: 0.75rem;
  background: #f44336;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #d32f2f;
  transform: translateY(-1px);
}
</style>
