<template>
  <div ref="cyContainer" class="cy-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import cytoscape from 'cytoscape'

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

const props = defineProps<{
  devices: Device[]
  interfaces: Interface[]
  links: Link[]
  linkMode?: boolean
}>()

const emit = defineEmits<{
  deviceClick: [device: Device]
  positionUpdated: [deviceId: number, x: number, y: number]
}>()

const cyContainer = ref<HTMLElement | null>(null)
let cy: cytoscape.Core | null = null

function initCytoscape() {
  if (!cyContainer.value) return

  // Create Cytoscape instance
  cy = cytoscape({
    container: cyContainer.value,
    
    style: [
      // Nodes
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'text-valign': 'bottom',
          'text-halign': 'center',
          'text-margin-y': 5,
          'font-size': '12px',
          'color': '#fff',
          'width': 40,
          'height': 40,
        }
      },
      {
        selector: 'node[status="UP"]',
        style: {
          'background-color': '#10b981'
        }
      },
      {
        selector: 'node[status="DOWN"]',
        style: {
          'background-color': '#ef4444'
        }
      },
      {
        selector: 'node[status="DEGRADED"]',
        style: {
          'background-color': '#f59e0b'
        }
      },
      // Edges
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#555',
          'curve-style': 'bezier'
        }
      },
      {
        selector: 'edge[status="UP"]',
        style: {
          'line-color': '#10b981'
        }
      },
      {
        selector: 'edge[status="DEGRADED"]',
        style: {
          'line-color': '#f59e0b'
        }
      }
    ],
    
    layout: {
      name: 'preset'  // Use x,y from backend
    },
    
    // Enable zoom/pan
    zoomingEnabled: true,
    userZoomingEnabled: true,
    panningEnabled: true,
    userPanningEnabled: true,
    
    minZoom: 0.5,
    maxZoom: 2
  })

  // Add click handler for devices
  cy.on('tap', 'node', (event) => {
    const nodeData = event.target.data()
    const deviceId = parseInt(nodeData.id.replace('device-', ''))
    const device = props.devices.find(d => d.id === deviceId)
    
    if (device) {
      emit('deviceClick', device)
    }
  })

  // Add click handler for links (edges)
  cy.on('tap', 'edge', async (event) => {
    const edgeData = event.target.data()
    const linkId = parseInt(edgeData.id.replace('link-', ''))
    
    if (confirm('Delete this link?')) {
      try {
        await fetch(`/api/links/${linkId}`, {
          method: 'DELETE'
        })
        console.log(`✅ Link deleted: ${linkId}`)
      } catch (error) {
        console.error('❌ Failed to delete link:', error)
        alert('Failed to delete link')
      }
    }
  })

  // Add drag end handler to save position
  cy.on('dragfree', 'node', async (event) => {
    const node = event.target
    const position = node.position()
    const deviceId = parseInt(node.id().replace('device-', ''))
    
    const x = Math.round(position.x)
    const y = Math.round(position.y)
    
    // Lock the node position to prevent snapping back
    node.lock()
    
    try {
      await fetch(`/api/devices/${deviceId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y })
      })
      console.log(`✅ Device position updated: ${deviceId} → (${x}, ${y})`)
      
      // Emit event to update sidebar
      emit('positionUpdated', deviceId, x, y)
      
      // Unlock after save
      node.unlock()
    } catch (error) {
      console.error('❌ Failed to update device position:', error)
      node.unlock()
    }
  })

  updateGraph()
}

function updateGraph() {
  if (!cy) return

  // Get existing node IDs
  const existingNodeIds = new Set<string>()
  cy.nodes().forEach(node => {
    existingNodeIds.add(node.id())
  })

  // Get existing edge IDs
  const existingEdgeIds = new Set<string>()
  cy.edges().forEach(edge => {
    existingEdgeIds.add(edge.id())
  })

  // Add or update devices as nodes
  const currentNodeIds = new Set<string>()
  props.devices.forEach((device: Device) => {
    const nodeId = `device-${device.id}`
    currentNodeIds.add(nodeId)
    
    const existingNode = cy!.getElementById(nodeId)
    if (existingNode.length > 0) {
      // Update existing node data (but NOT position - preserve visual position)
      existingNode.data({
        label: device.name,
        status: device.status,
        device_type: device.device_type
      })
      
      // NEVER update position for existing nodes - visual position is source of truth
      // Position only set when node is first created
    } else {
      // Add new node with DB position
      cy!.add({
        data: {
          id: nodeId,
          label: device.name,
          status: device.status,
          device_type: device.device_type
        },
        position: {
          x: device.x,
          y: device.y
        }
      })
    }
  })

  // Remove nodes that no longer exist
  existingNodeIds.forEach(nodeId => {
    if (!currentNodeIds.has(nodeId)) {
      cy!.getElementById(nodeId).remove()
    }
  })

  // Create interface-to-device mapping
  const interfaceToDevice = new Map<number, number>()
  props.interfaces.forEach((intf: Interface) => {
    interfaceToDevice.set(intf.id, intf.device_id)
  })

  // Add or update links as edges
  const currentEdgeIds = new Set<string>()
  props.links.forEach((link: Link) => {
    const sourceDeviceId = interfaceToDevice.get(link.a_interface_id)
    const targetDeviceId = interfaceToDevice.get(link.b_interface_id)

    if (!sourceDeviceId || !targetDeviceId) {
      console.warn('⚠️  Link missing device mapping:', link)
      return
    }

    const edgeId = `link-${link.id}`
    currentEdgeIds.add(edgeId)
    
    const existingEdge = cy!.getElementById(edgeId)
    if (existingEdge.length > 0) {
      // Update existing edge
      existingEdge.data({
        source: `device-${sourceDeviceId}`,
        target: `device-${targetDeviceId}`,
        status: link.status
      })
    } else {
      // Add new edge
      cy!.add({
        data: {
          id: edgeId,
          source: `device-${sourceDeviceId}`,
          target: `device-${targetDeviceId}`,
          status: link.status
        }
      })
    }
  })

  // Remove edges that no longer exist
  existingEdgeIds.forEach(edgeId => {
    if (!currentEdgeIds.has(edgeId)) {
      cy!.getElementById(edgeId).remove()
    }
  })

  console.log('📊 Graph updated:', cy!.nodes().length, 'nodes,', cy!.edges().length, 'edges')
}

onMounted(() => {
  initCytoscape()
})

watch(() => [props.devices, props.interfaces, props.links], () => {
  updateGraph()
}, { deep: true })
</script>

<style scoped>
.cy-container {
  width: 100%;
  height: 100%;
  background: #1a1a1a;
}
</style>
