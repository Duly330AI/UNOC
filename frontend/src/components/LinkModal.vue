<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal">
      <div class="modal-header">
        <h2>Create Link</h2>
        <button class="close-btn" @click="close">×</button>
      </div>
      
      <div class="modal-body">
        <div class="device-info">
          <div class="device-box">
            <span class="label">Device A:</span>
            <span class="device-name">{{ deviceA?.name }}</span>
          </div>
          <div class="arrow">→</div>
          <div class="device-box">
            <span class="label">Device B:</span>
            <span class="device-name">{{ deviceB?.name }}</span>
          </div>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="linkType">Link Type *</label>
            <select id="linkType" v-model="form.linkType" required>
              <option value="fiber">Fiber (Green)</option>
              <option value="copper">Copper (Blue)</option>
              <option value="wireless">Wireless (Orange)</option>
            </select>
          </div>

          <div class="form-group">
            <label for="status">Link Status *</label>
            <select id="status" v-model="form.status" required>
              <option value="UP">UP</option>
              <option value="DOWN">DOWN</option>
            </select>
          </div>

          <div class="info-box">
            <strong>Note:</strong> Interfaces will be created automatically on both devices.
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              Create Link
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Device {
  id: number
  name: string
  device_type: string
  status: string
  x: number
  y: number
}

interface Props {
  isOpen: boolean
  deviceA: Device | null
  deviceB: Device | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  submit: [data: {
    deviceAId: number
    deviceBId: number
    linkType: string
    status: string
  }]
}>()

const form = ref({
  linkType: 'fiber',
  status: 'UP',
})

// Reset form when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    form.value = {
      linkType: 'fiber',
      status: 'UP',
    }
  }
})

function close() {
  emit('close')
}

function handleSubmit() {
  if (!props.deviceA || !props.deviceB) return
  
  emit('submit', {
    deviceAId: props.deviceA.id,
    deviceBId: props.deviceB.id,
    linkType: form.value.linkType,
    status: form.value.status,
  })
  close()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #2a2a2a;
  border-radius: 8px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #3a3a3a;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
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

.modal-body {
  padding: 1.5rem;
}

.device-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 8px;
}

.device-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-size: 0.85rem;
  color: #aaa;
  font-weight: 500;
}

.device-name {
  font-size: 1.1rem;
  color: #4caf50;
  font-weight: 600;
}

.arrow {
  font-size: 2rem;
  color: #4caf50;
  font-weight: bold;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ccc;
}

select {
  padding: 0.75rem;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  background: #1a1a1a;
  color: #fff;
  font-size: 1rem;
}

select:focus {
  outline: none;
  border-color: #4caf50;
}

.info-box {
  padding: 1rem;
  background: rgba(76, 175, 80, 0.1);
  border-left: 3px solid #4caf50;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #ccc;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #3a3a3a;
  color: #fff;
}

.btn-secondary:hover {
  background: #4a4a4a;
}

.btn-primary {
  background: #4caf50;
  color: #fff;
  font-weight: 600;
}

.btn-primary:hover {
  background: #45a049;
  transform: translateY(-1px);
}
</style>
