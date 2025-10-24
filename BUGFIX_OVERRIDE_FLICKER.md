# 🔧 BUGFIX: Override Flickers and Reverts

**Date:** October 15, 2025  
**Bug:** Override UI flickers for split second then reverts to old state  
**Status:** ✅ **FIXED**

---

## 🐛 **PROBLEM**

### **Symptom:**
1. User clicks "Force UP" or "Force DOWN"
2. **Sidebar flickers** - shows override for split second
3. **Reverts immediately** to old state (no badge)
4. Status stays "UP" without override indication

### **Console Logs:**
```
📡 Device updated: {status_override: "UP", ...}    ← WebSocket
✅ Status override set: UP                          ← API Response
✅ Loaded: 10 devices, 24 interfaces, 8 links       ← fetchData() ❌
```

### **Root Cause:**

**Race Condition:**
```
PATCH /api/devices/6/override
  ↓
Backend commits to DB
  ↓
Backend emits WebSocket: device:updated
  ↓
Frontend: selectedDevice = NEW DATA ✅
  ↓
handleOverrideUpdated() calls fetchData()
  ↓
fetchData() loads OLD DATA from API ❌
  ↓
selectedDevice = OLD DATA (overrides WebSocket) ❌
  ↓
Sidebar shows old state ❌
```

**Why Old Data?**
- WebSocket event is FASTER than REST API
- `fetchData()` GET request might hit cache or race with commit
- Even 50ms delay isn't reliable
- `fetchData()` is unnecessary - WebSocket already has new data!

---

## ✅ **SOLUTION**

### **Remove Redundant Fetch:**

**BEFORE (❌ Bug):**
```javascript
async function handleOverrideUpdated() {
  await fetchData()  // ❌ Loads old data, overwrites WebSocket update
  
  if (selectedDevice.value) {
    const updatedDevice = devices.value.find(...)
    selectedDevice.value = updatedDevice
  }
}
```

**AFTER (✅ Fixed):**
```javascript
function handleOverrideUpdated() {
  // Nothing to do! WebSocket event already updated selectedDevice
  // (see device:updated handler which updates both devices array and selectedDevice)
  console.log('✅ Override updated via WebSocket')
}
```

---

## 🔄 **NEW FLOW**

```
User clicks "Force UP"
  ↓
DeviceSidebar: setOverride()
  ↓
PATCH /api/devices/6/override
  ↓
Backend: Updates DB + Emits WebSocket
  ↓
Frontend WebSocket Handler:
  └─ devices[6] = NEW DATA ✅
  └─ selectedDevice = NEW DATA ✅
  ↓
Vue Reactivity: Sidebar re-renders ✅
  ↓
handleOverrideUpdated() called (does nothing) ✅
  ↓
Sidebar shows: "UP 🔒 Override" ✅
```

**No More:**
- ❌ No fetchData() race
- ❌ No old data overwrite
- ❌ No flicker

---

## 🎯 **KEY INSIGHT**

**WebSocket IS The Source of Truth:**
- Backend emits `device:updated` after commit
- WebSocket handler already updates both:
  - `devices` array (for graph)
  - `selectedDevice` (for sidebar)
- No need for additional REST call!

**Event-Driven Architecture:**
```
Backend Event → WebSocket → Frontend Update
                    ↓
              Single Source of Truth ✅
```

**Old (REST-based):**
```
Backend Update → REST Polling → Frontend Update
                      ↓
                Race Conditions ❌
```

---

## ✅ **BENEFITS**

1. **No Race Conditions:** WebSocket is single source
2. **Faster UI:** No extra REST call delay
3. **Consistent:** Same data flow for all updates
4. **Simpler:** Less code, fewer edge cases

---

## 🧪 **TESTING**

### **Test 1: Quick Toggle**
1. Click "Force UP" → "Force DOWN" → "Clear" rapidly
2. **Expected:** UI follows all changes smoothly ✅

### **Test 2: Network Delay**
1. Simulate slow network (Chrome DevTools)
2. Click "Force UP"
3. **Expected:** UI updates when WebSocket arrives ✅

### **Test 3: Multiple Devices**
1. Device A: Set override
2. Device B: Set override
3. Switch between A and B
4. **Expected:** Both show correct override state ✅

---

## 📊 **DATA FLOW DIAGRAM**

**Before (❌ Broken):**
```
PATCH → Backend
         ↓
      WebSocket → Frontend (new data)
         ↓
      selectedDevice = NEW ✅
         ↓
      fetchData() → Frontend (old data)
         ↓
      selectedDevice = OLD ❌
```

**After (✅ Fixed):**
```
PATCH → Backend
         ↓
      WebSocket → Frontend (new data)
         ↓
      selectedDevice = NEW ✅
         ↓
      Done! ✅
```

---

## ✅ **CONCLUSION**

**Bug Fixed:** ✅  
**Flicker Gone:** ✅  
**Override Stable:** ✅  
**Architecture:** ✅ Event-driven

Removed redundant REST call in favor of WebSocket-only updates, eliminating race condition.

---

**Fix Date:** October 15, 2025  
**Status:** ✅ PRODUCTION READY  
**Files Changed:** 1 (frontend/src/App.vue)  
**Lines Changed:** Simplified handleOverrideUpdated() from async fetch to no-op
