<template>
  <div class="app">
    <header class="header">
      <h1>🌐 UNOC - Network Operations Center</h1>
      <div class="header-actions">
        <button class="btn-add" @click="openAddDeviceModal">
          ➕ Add Device
        </button>
        <button 
          class="btn-link-mode" 
          :class="{ active: isLinkMode }"
          @click="toggleLinkMode"
        >
          {{ isLinkMode ? '✓ Link Mode' : '🔗 Link Mode' }}
        </button>
        <div class="status">
          <span>Devices: {{ devices.length }}</span>
          <span>Links: {{ links.length }}</span>
          <span :class="wsStatus">{{ wsConnected ? '🟢 Live' : '🔴 Offline' }}</span>
        </div>
      </div>
    </header>
    <main class="main">
      <NetworkGraph 
        :devices="devices" 
        :links="links" 
        :interfaces="interfaces"
        :link-mode="isLinkMode"
        @device-click="handleDeviceClick"
        @position-updated="handlePositionUpdated"
      />
    </main>

    <!-- Add Device Modal -->
    <DeviceModal
      :is-open="isAddModalOpen"
      title="Add Device"
      submit-label="Create"
      @close="isAddModalOpen = false"
      @submit="handleCreateDevice"
    />

    <!-- Create Link Modal -->
    <LinkModal
      :is-open="isLinkModalOpen"
      :device-a="linkDeviceA"
      :device-b="linkDeviceB"
      @close="closeLinkModal"
      @submit="handleCreateLink"
    />

    <!-- Device Details Sidebar -->
    <DeviceSidebar
      :device="selectedDevice"
      @close="selectedDevice = null"
      @delete="handleDeleteDevice"
      @override-updated="handleOverrideUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { io } from 'socket.io-client'
import NetworkGraph from './components/NetworkGraph.vue'
import DeviceModal from './components/DeviceModal.vue'
import DeviceSidebar from './components/DeviceSidebar.vue'
import LinkModal from './components/LinkModal.vue'

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

interface Interface {
  id: number
  name: string
  device_id: number
  interface_type: string
  status: string
}

interface Link {
  id: number
  a_interface_id: number
  b_interface_id: number
  status: string
}

const devices = ref<Device[]>([])
const interfaces = ref<Interface[]>([])
const links = ref<Link[]>([])
const wsConnected = ref(false)
const isAddModalOpen = ref(false)
const selectedDevice = ref<Device | null>(null)

// Link Mode State
const isLinkMode = ref(false)
const isLinkModalOpen = ref(false)
const linkDeviceA = ref<Device | null>(null)
const linkDeviceB = ref<Device | null>(null)

const wsStatus = computed(() => wsConnected.value ? 'ws-connected' : 'ws-disconnected')

let socket: any = null

function openAddDeviceModal() {
  isAddModalOpen.value = true
}

async function handleCreateDevice(deviceData: {
  name: string
  device_type: string
  status: string
  x: number
  y: number
  tx_power_dbm?: number | null
  sensitivity_min_dbm?: number | null
  insertion_loss_db?: number | null
}) {
  try {
    const response = await fetch('/api/devices', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deviceData),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const newDevice = await response.json()
    console.log('✅ Device created:', newDevice)
    
    // Device will be added via WebSocket event automatically
  } catch (error) {
    console.error('❌ Failed to create device:', error)
    alert('Failed to create device. Check console for details.')
  }
}

function handleDeviceClick(device: Device) {
  if (isLinkMode.value) {
    // Link mode: Select devices for linking
    if (!linkDeviceA.value) {
      linkDeviceA.value = device
      console.log('🔗 Link Device A selected:', device.name)
    } else if (linkDeviceA.value.id === device.id) {
      // Clicked same device, cancel
      linkDeviceA.value = null
      console.log('🔗 Link cancelled')
    } else {
      // Second device selected, show modal
      linkDeviceB.value = device
      isLinkModalOpen.value = true
      console.log('🔗 Link Device B selected:', device.name)
    }
  } else {
    // Normal mode: Show device details
    selectedDevice.value = device
    console.log('🖱️ Device clicked:', device)
  }
}

function toggleLinkMode() {
  isLinkMode.value = !isLinkMode.value
  
  if (!isLinkMode.value) {
    // Exit link mode, reset selection
    linkDeviceA.value = null
    linkDeviceB.value = null
  }
  
  console.log(isLinkMode.value ? '🔗 Link Mode ON' : '🔗 Link Mode OFF')
}

function handlePositionUpdated(deviceId: number, x: number, y: number) {
  // Update device in reactive array
  const device = devices.value.find(d => d.id === deviceId)
  if (device) {
    device.x = x
    device.y = y
    
    // Update selected device if it's the one being dragged
    if (selectedDevice.value?.id === deviceId) {
      selectedDevice.value = { ...selectedDevice.value, x, y }
    }
  }
}

function handleOverrideUpdated() {
  // Nothing to do! WebSocket event already updated selectedDevice
  // (see device:updated handler which updates both devices array and selectedDevice)
  console.log('✅ Override updated via WebSocket')
}

function closeLinkModal() {
  isLinkModalOpen.value = false
  linkDeviceA.value = null
  linkDeviceB.value = null
}

async function handleCreateLink(data: {
  deviceAId: number
  deviceBId: number
  linkType: string
  status: string
}) {
  try {
    console.log('🔗 Creating link:', data)
    
    const response = await fetch('/api/links/create-simple', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_a_id: data.deviceAId,
        device_b_id: data.deviceBId,
        link_type: data.linkType,
        status: data.status,
      }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('✅ Link created:', result.message)
    
    // Link, interfaces will be added via WebSocket events automatically
    closeLinkModal()
    isLinkMode.value = false
  } catch (error) {
    console.error('❌ Failed to create link:', error)
    alert(`Failed to create link: ${error}`)
  }
}

async function handleDeleteDevice(deviceId: number) {
  try {
    const response = await fetch(`/api/devices/${deviceId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    console.log('✅ Device deleted:', deviceId)
    selectedDevice.value = null
    
    // Device will be removed via WebSocket event automatically
  } catch (error) {
    console.error('❌ Failed to delete device:', error)
    alert('Failed to delete device. Check console for details.')
  }
}

async function fetchData() {
  try {
    const [devicesRes, interfacesRes, linksRes] = await Promise.all([
      fetch('/api/devices'),
      fetch('/api/interfaces'),
      fetch('/api/links')
    ])
    devices.value = await devicesRes.json()
    interfaces.value = await interfacesRes.json()
    links.value = await linksRes.json()
    console.log('✅ Loaded:', devices.value.length, 'devices,', interfaces.value.length, 'interfaces,', links.value.length, 'links')
  } catch (error) {
    console.error('❌ Failed to load data:', error)
  }
}

function setupWebSocket() {
  // Connect to WebSocket server
  socket = io('http://localhost:5001', {
    transports: ['websocket', 'polling'],
  })

  // Connection events
  socket.on('connect', () => {
    console.log('🔌 WebSocket connected')
    wsConnected.value = true
  })

  socket.on('disconnect', () => {
    console.log('🔌 WebSocket disconnected')
    wsConnected.value = false
  })

  // Device events
  socket.on('device:created', (device: Device) => {
    console.log('📡 Device created:', device)
    devices.value.push(device)
  })

  socket.on('device:deleted', (data: { id: number }) => {
    console.log('📡 Device deleted:', data.id)
    devices.value = devices.value.filter((d: Device) => d.id !== data.id)
  })

  socket.on('device:updated', (device: Device) => {
    console.log('📡 Device updated:', device)
    const index = devices.value.findIndex((d: Device) => d.id === device.id)
    if (index !== -1) {
      // Update device but PRESERVE local position (to avoid drag conflicts)
      const updatedDevice = {
        ...device,
        x: devices.value[index].x,  // Keep current x
        y: devices.value[index].y   // Keep current y
      }
      devices.value[index] = updatedDevice
      
      // Also update selectedDevice if it's the same device
      if (selectedDevice.value?.id === device.id) {
        selectedDevice.value = updatedDevice
      }
    }
  })

  // Interface events
  socket.on('interface:created', (intf: Interface) => {
    console.log('📡 Interface created:', intf)
    interfaces.value.push(intf)
  })

  // Link events
  socket.on('link:created', (link: Link) => {
    console.log('📡 Link created:', link)
    links.value.push(link)
  })

  socket.on('link:deleted', (data: { id: number }) => {
    console.log('📡 Link deleted:', data.id)
    links.value = links.value.filter((l: Link) => l.id !== data.id)
  })
}

onMounted(() => {
  fetchData()
  setupWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
})
</script>

<style scoped>
.app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  background: #2a2a2a;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #3a3a3a;
}

h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.btn-add {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #45a049;
  transform: translateY(-1px);
}

.btn-link-mode {
  padding: 0.5rem 1rem;
  background: #3a3a3a;
  color: #fff;
  border: 2px solid #3a3a3a;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-link-mode:hover {
  background: #4a4a4a;
  border-color: #4a4a4a;
}

.btn-link-mode.active {
  background: #2196f3;
  border-color: #2196f3;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(33, 150, 243, 0);
  }
}

.status {
  display: flex;
  gap: 2rem;
  font-size: 0.9rem;
  color: #aaa;
}

.ws-connected {
  color: #4caf50;
  font-weight: 600;
}

.ws-disconnected {
  color: #f44336;
  font-weight: 600;
}

.main {
  flex: 1;
  overflow: hidden;
}
</style>
