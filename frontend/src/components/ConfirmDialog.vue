<template>
  <div v-if="isOpen" class="confirm-overlay" @click="handleCancel">
    <div class="confirm-dialog" @click.stop>
      <div class="confirm-header">
        <span class="confirm-icon">⚠️</span>
        <h3>{{ title }}</h3>
      </div>
      
      <div class="confirm-body">
        <p>{{ message }}</p>
      </div>
      
      <div class="confirm-footer">
        <button class="btn-cancel" @click="handleCancel">
          Cancel
        </button>
        <button class="btn-confirm" @click="handleConfirm">
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  isOpen: boolean
  title: string
  message: string
  confirmLabel?: string
}

withDefaults(defineProps<Props>(), {
  confirmLabel: 'Confirm'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function handleConfirm() {
  emit('confirm')
}

function handleCancel() {
  emit('cancel')
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-dialog {
  background: #2a2a2a;
  border-radius: 8px;
  border: 2px solid #3a3a3a;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.confirm-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid #3a3a3a;
}

.confirm-icon {
  font-size: 24px;
}

.confirm-header h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
}

.confirm-body {
  padding: 24px;
}

.confirm-body p {
  margin: 0;
  color: #ccc;
  line-height: 1.5;
}

.confirm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #3a3a3a;
}

.btn-cancel,
.btn-confirm {
  padding: 8px 20px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #3a3a3a;
  color: #ccc;
}

.btn-cancel:hover {
  background: #4a4a4a;
  color: #fff;
}

.btn-confirm {
  background: #e74c3c;
  color: white;
}

.btn-confirm:hover {
  background: #c0392b;
}
</style>
