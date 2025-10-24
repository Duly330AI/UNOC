# WebSocket Live Demo Script

This script demonstrates the real-time WebSocket functionality.

## Prerequisites
- Backend running on `http://localhost:5001`
- Frontend running on `http://localhost:5174`

## Test 1: Live Device Creation

1. Open browser at http://localhost:5174
2. Open DevTools Console (F12)
3. You should see: `🔌 WebSocket connected`
4. Click "➕ Add Device" button
5. Fill in:
   - Name: `test_live_device`
   - Type: `CORE_ROUTER`
   - Status: `UP`
6. Click "Create"
7. **Expected:** Device appears in graph **immediately** without page refresh
8. Console should show: `📡 Device created: {...}`

## Test 2: Live Device Deletion

1. Click any device in the graph
2. Sidebar opens on the right
3. Click "🗑️ Delete" button
4. Confirm deletion
5. **Expected:** Device disappears **immediately** from graph
6. Console should show: `📡 Device deleted: {id: ...}`

## Test 3: Live Link Creation

1. Click "🔗 Link Mode" button (top right)
2. Click Device A (e.g., CoreRouter1)
3. Click Device B (e.g., EdgeRouter1)
4. Modal opens with interface selection
5. Select interfaces and click "Create Link"
6. **Expected:** 
   - Link appears **immediately**
   - Console shows: `📡 Interface created: {...}` (2x)
   - Console shows: `📡 Link created: {...}`

## Test 4: Multi-Client Sync

1. Open http://localhost:5174 in **2 browser windows** (side by side)
2. In Window 1: Create a device
3. **Expected:** Device appears in **both windows simultaneously**
4. In Window 2: Delete a device
5. **Expected:** Device disappears in **both windows**

## Test 5: Connection Status

1. Open browser at http://localhost:5174
2. Top-right corner shows: `🟢 Live`
3. Stop Docker backend: `docker-compose stop backend`
4. **Expected:** Status changes to `🔴 Offline`
5. Start backend: `docker-compose start backend`
6. **Expected:** Status returns to `🟢 Live` (auto-reconnect)

## Test 6: Provision Device (Phase 2.4 Integration)

1. Open DevTools Console
2. Run this command:
```javascript
fetch('/api/devices/provision', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'olt_live_test',
    device_type: 'OLT',
    validate_upstream: false,
    tx_power_dbm: 5.5
  })
}).then(r => r.json()).then(console.log)
```
3. **Expected:**
   - Device appears in graph **immediately**
   - Console shows: `📡 Device created: {name: 'olt_live_test', ...}`
   - Device has 10 interfaces (mgmt0, lo0, pon0-7)

## Success Criteria

✅ **All operations happen in real-time**  
✅ **No manual page refresh needed**  
✅ **Multiple clients stay synchronized**  
✅ **Connection status indicator works**  
✅ **Auto-reconnect after server restart**

## Troubleshooting

### WebSocket not connecting?
- Check backend logs: `docker logs unoc-backend --tail 50`
- Look for: `🔌 Client connected: ...`
- Check CORS: Should include `http://localhost:5174`

### Events not received?
- Open DevTools Console
- Check for: `📡 Device created: ...` messages
- Verify WebSocket status: Should show `🟢 Live`

### Port conflicts?
- Frontend on 5173 or 5174 (Vite chooses)
- Backend on 5001 (Docker)
- Database on 5432 (Docker)
