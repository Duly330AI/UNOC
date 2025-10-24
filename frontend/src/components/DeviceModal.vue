<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="close">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="close-btn" @click="close">×</button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="name">Device Name *</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              placeholder="e.g., Router3"
            />
          </div>

          <div class="form-group">
            <label for="type">Device Type *</label>
            <select id="type" v-model="form.device_type" required>
              <option value="">-- Select Type --</option>
              
              <optgroup label="🔌 Active Devices">
                <option value="BACKBONE_GATEWAY">Backbone Gateway</option>
                <option value="CORE_ROUTER">Core Router</option>
                <option value="EDGE_ROUTER">Edge Router</option>
                <option value="OLT">OLT (Optical Line Terminal)</option>
                <option value="AON_SWITCH">AON Switch</option>
                <option value="ONT">ONT (Residential)</option>
                <option value="BUSINESS_ONT">Business ONT</option>
                <option value="AON_CPE">AON CPE</option>
              </optgroup>
              
              <optgroup label="📦 Container Devices">
                <option value="POP">POP (Point of Presence)</option>
                <option value="CORE_SITE">Core Site</option>
              </optgroup>
              
              <optgroup label="⚡ Passive Devices">
                <option value="ODF">ODF (Optical Distribution Frame)</option>
                <option value="NVT">NVT (Network Termination Vault)</option>
                <option value="SPLITTER">Splitter (1:N Optical)</option>
                <option value="HOP">HOP (Handhole Optical Point)</option>
              </optgroup>
            </select>
          </div>

          <!-- Optical Attributes (for optical devices) -->
          <div v-if="showOpticalFields" class="optical-section">
            <h3 class="section-title">⚡ Optical Attributes</h3>
            
            <div v-if="form.device_type === 'OLT'" class="form-group">
              <label for="tx_power">TX Power (dBm)</label>
              <input
                id="tx_power"
                v-model.number="form.tx_power_dbm"
                type="number"
                step="0.1"
                placeholder="Default: +5.0 dBm"
              />
              <small>Transmit power for OLT (default: +5.0 dBm)</small>
            </div>

            <div v-if="form.device_type === 'ONT' || form.device_type === 'BUSINESS_ONT'" class="form-group">
              <label for="sensitivity">Sensitivity Min (dBm)</label>
              <input
                id="sensitivity"
                v-model.number="form.sensitivity_min_dbm"
                type="number"
                step="0.1"
                placeholder="Default: -30.0 dBm"
              />
              <small>Minimum receiver sensitivity for ONT (default: -30.0 dBm)</small>
            </div>

            <div v-if="isPassiveDevice" class="form-group">
              <label for="insertion_loss">Insertion Loss (dB)</label>
              <input
                id="insertion_loss"
                v-model.number="form.insertion_loss_db"
                type="number"
                step="0.1"
                placeholder="Default: varies by type"
              />
              <small>
                Defaults: ODF/HOP: 0.5 dB, NVT: 0.1 dB, Splitter: 3.5 dB
              </small>
            </div>
          </div>

          <div class="form-group">
            <label for="status">Status *</label>
            <select id="status" v-model="form.status" required>
              <option value="UP">UP (Green)</option>
              <option value="DOWN">DOWN (Red)</option>
              <option value="DEGRADED">DEGRADED (Orange)</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="x">Position X</label>
              <input
                id="x"
                v-model.number="form.x"
                type="number"
                step="10"
              />
            </div>
            <div class="form-group">
              <label for="y">Position Y</label>
              <input
                id="y"
                v-model.number="form.y"
                type="number"
                step="10"
              />
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ submitLabel }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface Props {
  isOpen: boolean
  title?: string
  submitLabel?: string
  initialData?: {
    name: string
    device_type: string
    status: string
    x: number
    y: number
    tx_power_dbm?: number | null
    sensitivity_min_dbm?: number | null
    insertion_loss_db?: number | null
  }
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Add Device',
  submitLabel: 'Create',
  initialData: () => ({
    name: '',
    device_type: '',
    status: 'UP',
    x: 400,
    y: 300,
    tx_power_dbm: null,
    sensitivity_min_dbm: null,
    insertion_loss_db: null,
  }),
})

const emit = defineEmits<{
  close: []
  submit: [data: {
    name: string
    device_type: string
    status: string
    x: number
    y: number
    tx_power_dbm?: number | null
    sensitivity_min_dbm?: number | null
    insertion_loss_db?: number | null
  }]
}>()

const form = ref({ ...props.initialData })

// Computed: Show optical fields for optical devices
const showOpticalFields = computed(() => {
  const opticalTypes = ['OLT', 'ONT', 'BUSINESS_ONT', 'ODF', 'NVT', 'SPLITTER', 'HOP']
  return opticalTypes.includes(form.value.device_type)
})

// Computed: Check if device is passive
const isPassiveDevice = computed(() => {
  const passiveTypes = ['ODF', 'NVT', 'SPLITTER', 'HOP']
  return passiveTypes.includes(form.value.device_type)
})

// Reset form when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    form.value = { ...props.initialData }
  }
})

function close() {
  emit('close')
}

function handleSubmit() {
  emit('submit', { ...form.value })
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
  max-width: 500px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ccc;
}

input,
select {
  padding: 0.75rem;
  border: 1px solid #3a3a3a;
  border-radius: 4px;
  background: #1a1a1a;
  color: #fff;
  font-size: 1rem;
}

input:focus,
select:focus {
  outline: none;
  border-color: #4caf50;
}

small {
  display: block;
  margin-top: 0.5rem;
  color: #888;
  font-size: 0.85rem;
}

/* Optical Section */
.optical-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 152, 0, 0.05);
  border: 1px solid rgba(255, 152, 0, 0.3);
  border-radius: 8px;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #ff9800;
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
