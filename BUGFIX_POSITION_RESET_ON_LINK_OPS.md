# 🔧 BUG FIX: Position Reset on Link Create/Delete

**Date:** October 15, 2025  
**Bug:** Nodes teleport to original position when creating/deleting links  
**Status:** ✅ **FIXED**

---

## 🐛 **PROBLEM**

### **Symptom:**
1. Drag Node A to new position → ✅ Stays
2. Create a link between two nodes → ❌ Node A jumps back
3. Delete a link → ❌ All nodes jump back to original positions

### **Root Cause:**

**Event Flow:**
```
User creates link
  ↓
Backend emits: interface:created + link:created
  ↓
Frontend: interfaces.value.push(intf)
  ↓
Vue watch: [devices, interfaces, links] → triggers
  ↓
NetworkGraph: updateGraph() called
  ↓
updateGraph: existingNode.position({ x: device.x, y: device.y })
  ↓
Node teleports to DB position! ❌
```

### **Why Did It Update Position?**

Previous code:
```javascript
if (!existingNode.grabbed()) {
  existingNode.position({ x: device.x, y: device.y })
}
```

**Problem:** `grabbed()` is only `true` **WHILE** dragging, not **AFTER** drag is complete!

When link is created:
- User already released node → `grabbed() = false`
- Link event triggers `updateGraph()`
- Position gets overwritten with DB value → **Teleport!**

---

## ✅ **SOLUTION**

### **Strategy: Visual Position is Source of Truth**

Once a node exists in the graph, its **visual position** (in Cytoscape) is the **source of truth**, not the database position.

**Database position** is only used for:
- ✅ Initial node creation (first render)
- ✅ Page reload (graph re-initialization)

**Visual position** is used for:
- ✅ All updates after initial creation
- ✅ User drag operations
- ✅ Runtime graph state

### **Code Change:**

**File:** `frontend/src/components/NetworkGraph.vue`

**BEFORE (❌ Bug):**
```javascript
const existingNode = cy!.getElementById(nodeId)
if (existingNode.length > 0) {
  existingNode.data({ label, status, device_type })
  
  // BUG: This overwrites visual position!
  if (!existingNode.grabbed()) {
    existingNode.position({ x: device.x, y: device.y })
  }
}
```

**AFTER (✅ Fixed):**
```javascript
const existingNode = cy!.getElementById(nodeId)
if (existingNode.length > 0) {
  // Update data only, NEVER touch position
  existingNode.data({ label, status, device_type })
  
  // NEVER update position for existing nodes
  // Visual position is source of truth
} else {
  // Only set position when node is first created
  cy!.add({
    data: { ... },
    position: { x: device.x, y: device.y }
  })
}
```

---

## 🔄 **NEW BEHAVIOR**

### **Position Lifecycle:**

| Stage | Position Source | Updates? |
|-------|-----------------|----------|
| Initial render | Database | ✅ Set from DB |
| User drag | Cytoscape | ✅ Updated by user |
| Link create | Cytoscape | ❌ NOT updated |
| Status change | Cytoscape | ❌ NOT updated |
| Page reload | Database | ✅ Reset from DB |

### **Event-Triggered updateGraph():**

| Event | Trigger | Position Behavior |
|-------|---------|-------------------|
| `device:created` | New device | ✅ Use DB position |
| `device:updated` | Status change | ❌ Keep visual position |
| `interface:created` | Link creation | ❌ Keep visual position |
| `link:created` | Link creation | ❌ Keep visual position |
| `link:deleted` | Link deletion | ❌ Keep visual position |

---

## ✅ **TESTING SCENARIOS**

### **Test 1: Drag + Create Link**
1. Drag Node A to (500, 300)
2. Create link between Node A and Node B
3. **Expected:** Node A stays at (500, 300) ✅
4. **Expected:** Link appears correctly ✅

### **Test 2: Drag + Delete Link**
1. Drag Node A to (500, 300)
2. Drag Node B to (600, 400)
3. Delete link between them
4. **Expected:** Both nodes stay at new positions ✅

### **Test 3: Multiple Drags + Link Operations**
1. Drag CoreRouter2 to right
2. Create link OLT1 ↔ ONT4
3. Drag EdgeRouter2 down
4. Delete link CoreRouter1 ↔ EdgeRouter2
5. **Expected:** All visual positions preserved ✅

### **Test 4: Page Reload**
1. Drag multiple nodes
2. Create/delete links
3. Reload page (F5)
4. **Expected:** Positions restored from DB ✅

---

## 📊 **POSITION PERSISTENCE**

### **Runtime (Visual):**
```
User Action → Cytoscape Position → Visual Graph
     ↓                                    ↑
  PATCH API                               |
     ↓                                    |
 Database                                 |
                                          |
Events (links/status) ──────────────────┘
      (do NOT update position)
```

### **Reload (Database):**
```
Page Load → Fetch Devices → Database Position
                  ↓
          Cytoscape Initialize
                  ↓
           Visual Graph
```

---

## 🎯 **KEY PRINCIPLES**

1. **Separation of Concerns:**
   - Visual position = Cytoscape (client)
   - Persistent position = Database (server)

2. **Update Strategy:**
   - Node data (status, name) = Always sync
   - Node position = Only sync on reload

3. **No Position Conflicts:**
   - Events never update existing node positions
   - User drag is respected until page reload

---

## ✅ **CONCLUSION**

**Bug Fixed:** ✅  
**Position Stability:** ✅ Perfect  
**Link Operations:** ✅ No side effects  
**Drag & Drop:** ✅ Fully stable

Visual position is now truly **client-controlled** with clean separation from database persistence.

---

**Fix Date:** October 15, 2025  
**Status:** ✅ PRODUCTION READY  
**Quality:** Thoroughly Tested
