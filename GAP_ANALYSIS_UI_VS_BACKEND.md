# 🔍 **GAP ANALYSIS: Was fehlt im UI vs. Backend-Implementierung**

**Datum:** 15. Oktober 2025  
**Analyst:** GitHub Copilot  
**Zweck:** Vergleich zwischen `/backupdocs/` Specs und aktueller UI-Implementierung

---

## 📋 **EXECUTIVE SUMMARY**

### **KERNPROBLEM:**
Das Backend implementiert eine **vollständige FTTH Glasfaser-Emulation** mit:
- ✅ Automatischer Signal Budget Berechnung
- ✅ Optical Path Resolution (Dijkstra)
- ✅ Traffic Engine v2 (tariff-based)
- ✅ IPAM mit automatischer IP-Vergabe
- ✅ MAC Address Generation
- ✅ Status Propagation (Reachability)
- ✅ Congestion Detection

### **DAS UI ZEIGT:**
- ❌ **NICHTS** davon!
- Nur: Device Nodes, Links, Manual Override
- Keine Interfaces, keine IPs, keine MACs, keine Signal Values

---

## 🎯 **WAS IST IMPLEMENTIERT (BACKEND)**

### **1. OPTICAL EMULATION** ✅ VOLLSTÄNDIG

#### **Signal Budget Calculation:**
```python
# backend/services/optical_service.py (existiert!)
def resolve_optical_path(ont_id):
    # Dijkstra vom ONT zum OLT
    # Berücksichtigt:
    # - Link fiber loss (length_km * attenuation_db_per_km)
    # - Passive device insertion loss
    # - Splitter loss
    
    received_power_dbm = olt.tx_power_dbm - total_attenuation
    margin_db = received_power_dbm - ont.sensitivity_min_dbm
    
    # Classification:
    if margin_db >= 6.0: → OK
    elif margin_db >= 3.0: → WARNING  
    elif margin_db >= 0: → CRITICAL
    else: → NO_SIGNAL
```

**Events:**
- `device.optical.updated` → {id, received_dbm, signal_status, margin_db}

**UI zeigt:** ❌ NICHTS von diesem!

---

### **2. IPAM (IP Address Management)** ✅ VOLLSTÄNDIG

#### **Automatische IP-Vergabe:**
```python
# backend/services/provisioning_service.py
# Pools:
- core_mgmt: 10.250.0.0/24
- olt_mgmt: 10.250.4.0/24
- aon_mgmt: 10.250.2.0/24
- ont_mgmt: 10.250.1.0/24
- cpe_mgmt: 10.250.3.0/24

# Bei Provisioning:
1. Device wird erstellt
2. mgmt0 Interface automatisch angelegt
3. IP aus Pool zugewiesen
4. MAC Address generiert (02:55:4E:xx:xx:xx)
```

**API Endpoints:**
- `GET /api/devices/{id}/interfaces` → Liste aller Interfaces
- `GET /api/interfaces/{id}/addresses` → IP-Adressen
- `POST /api/interfaces/{id}/addresses` → IP hinzufügen

**UI zeigt:** ❌ NICHTS davon!

---

### **3. TRAFFIC ENGINE V2** ✅ VOLLSTÄNDIG

#### **Tariff-Based Traffic Generation:**
```python
# backend/services/traffic/v2_engine.py
# Für jeden Tick:
1. Generiere Traffic basierend auf Tariff
   - Asymmetrisch (up_bps, down_bps)
   - Deterministisch (PRNG seed)
   
2. Aggregiere hierarchisch:
   - Device-level (sum interfaces)
   - Link-level (sum endpoints)
   - GPON Segment-level (ODF aggregator)

3. Detect Congestion:
   - Device/Link: ≥100% → congestion
   - GPON Segment: ≥95% → congestion
   - Hysteresis (clear at 95%/85%)
```

**Events:**
- `deviceMetricsUpdated` → {device_id, bps_in, bps_out, capacity}
- `linkMetricsUpdated` → {link_id, bps, capacity}
- `segment.congestion.detected` → {segment_id, demand, capacity}

**UI zeigt:** ❌ NICHTS davon!

---

### **4. STATUS PROPAGATION & REACHABILITY** ✅ VOLLSTÄNDIG

#### **Dependency Resolution:**
```python
# backend/services/status_service.py
def compute_device_status(device):
    # 1. Admin Override gewinnt
    if device.admin_override == DOWN: return DOWN
    
    # 2. Always Online
    if device.role == ALWAYS_ONLINE: return UP  # Backbone
    
    # 3. Passive: Propagation Snapshot
    if device.role == PASSIVE:
        return UP if reachable else DEGRADED
    
    # 4. Active: Dependency Check
    if device.role == ACTIVE:
        if not provisioned: return DOWN
        if ONT and signal_status == NO_SIGNAL: return DOWN
        return UP if has_valid_upstream else DEGRADED
```

**Upstream Dependency Rules:**
- EDGE_ROUTER → requires CORE or BACKBONE
- OLT → requires EDGE
- ONT → requires OLT + optical path + signal

**UI zeigt:** ❌ Status ja, aber NICHT die Gründe/Dependencies!

---

### **5. INTERFACES & MAC ADDRESSES** ✅ VOLLSTÄNDIG

#### **Auto-Interface Creation:**
```python
# Bei Device Provisioning:
OLT:
  - mgmt0 (management)
  - lo0 (loopback)
  - pon0-pon7 (8 PON ports)

AON_SWITCH:
  - mgmt0
  - lo0  
  - eth0-eth23 (24 Ethernet ports)

ONT:
  - eth0 (single access port)

SPLITTER:
  - in0 (1 input)
  - out0-out31 (32 output ports)
```

**MAC Generation:**
- OUI: `02:55:4E` (locally administered)
- Counter: Monotonic, deterministic
- Format: `02:55:4E:xx:xx:xx`

**UI zeigt:** ❌ NICHTS davon!

---

## ❌ **WAS FEHLT IM UI**

### **KRITISCHE FEHLENDE FEATURES:**

| Feature | Backend Status | UI Status | Impact |
|---------|---------------|-----------|---------|
| **Interfaces List** | ✅ Vollständig | ❌ Nicht vorhanden | **KRITISCH** |
| **IP Addresses** | ✅ Auto-assigned | ❌ Nicht sichtbar | **KRITISCH** |
| **MAC Addresses** | ✅ Auto-generated | ❌ Nicht sichtbar | **KRITISCH** |
| **Signal Budget** | ✅ Berechnet | ❌ Nicht angezeigt | **KRITISCH** |
| **Optical Path** | ✅ Resolved | ❌ Nicht visualisiert | **HOCH** |
| **Traffic Metrics** | ✅ Live | ❌ Nicht angezeigt | **HOCH** |
| **Congestion** | ✅ Detected | ❌ Nicht angezeigt | **HOCH** |
| **Link Properties** | ✅ length_km | ❌ Nicht editierbar | **MITTEL** |
| **Fiber Types** | ✅ 5 Typen | ❌ Nicht auswählbar | **MITTEL** |
| **Port Occupancy** | ✅ Calculated | ❌ Nicht angezeigt | **MITTEL** |
| **Dependency Reasons** | ✅ Computed | ❌ Nicht erklärt | **NIEDRIG** |

---

## 🎯 **WAS DU WIRKLICH WILLST**

### **FTTH Glasfaser Emulator UI sollte zeigen:**

#### **1. Device Details Sidebar:**
```
┌─────────────────────────────────────┐
│ OLT1                           [×]  │
├─────────────────────────────────────┤
│ Overview                            │
│ Status: UP ✅                       │
│ Type: OLT                           │
│ Position: 200, 300                  │
│                                     │
│ Interfaces: (3 total)               │
│ ┌─────────────────────────────────┐ │
│ │ mgmt0                           │ │
│ │ MAC: 02:55:4E:00:00:01          │ │
│ │ IP: 10.250.4.1/24               │ │
│ │ Status: UP ✅                   │ │
│ ├─────────────────────────────────┤ │
│ │ pon0                            │ │
│ │ MAC: 02:55:4E:00:00:02          │ │
│ │ Status: UP ✅                   │ │
│ │ Connected ONTs: 3/32            │ │
│ │ Traffic: 450 Mbps / 2.5 Gbps    │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Optical:                            │
│ TX Power: +5.0 dBm                  │
│ Connected ONTs: 3                   │
│                                     │
│ Traffic:                            │
│ Downstream: 1.2 Gbps                │
│ Upstream: 0.8 Gbps                  │
│ Total Capacity: 2.5 Gbps            │
└─────────────────────────────────────┘
```

#### **2. ONT Details mit Signal Budget:**
```
┌─────────────────────────────────────┐
│ ONT3                           [×]  │
├─────────────────────────────────────┤
│ Status: UP ✅                       │
│ Type: ONT                           │
│                                     │
│ Signal Quality: OK ✅               │
│ ┌─────────────────────────────────┐ │
│ │ Received Power: -17.5 dBm       │ │
│ │ Sensitivity: -30.0 dBm          │ │
│ │ Margin: 12.5 dB ✅              │ │
│ │                                 │ │
│ │ Path to OLT1:                   │ │
│ │ OLT1 → [5km, -1.75dB]           │ │
│ │ → Splitter1 [-3.5dB]            │ │
│ │ → [1km, -0.35dB]                │ │
│ │ → ONT3                          │ │
│ │                                 │ │
│ │ Total Loss: -5.6 dB             │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Interface eth0:                     │
│ MAC: 02:55:4E:00:00:15              │
│ IP: 10.250.1.15/24                  │
│                                     │
│ Traffic:                            │
│ Down: 50 Mbps / 100 Mbps (50%)      │
│ Up: 10 Mbps / 50 Mbps (20%)         │
└─────────────────────────────────────┘
```

#### **3. Link Properties Modal:**
```
┌─────────────────────────────────────┐
│ Link Properties                [×]  │
├─────────────────────────────────────┤
│ From: OLT1 (pon0)                   │
│ To: Splitter1 (in0)                 │
│                                     │
│ Length (km): [___5.0___]            │
│                                     │
│ Fiber Type:                         │
│ ○ SMF G.652D (0.35 dB/km)           │
│ ● SMF G.657A1 (0.35 dB/km)          │
│ ○ MMF OM3 (3.50 dB/km)              │
│                                     │
│ Calculated Loss: -1.75 dB           │
│                                     │
│ Status: UP ✅                       │
│                                     │
│ Traffic:                            │
│ Current: 450 Mbps                   │
│ Capacity: 2.5 Gbps                  │
│ Utilization: 18%                    │
│                                     │
│ [ Save ]  [ Cancel ]                │
└─────────────────────────────────────┘
```

---

## 🚨 **MISSVERSTÄNDNISSE KLARGESTELLT**

### **WAS ICH FALSCH VERSTANDEN HABE:**

#### **❌ FALSCH:**
"TX Power ist ein manuell eingegebener Wert vom User"

#### **✅ RICHTIG:**
"TX Power ist ein **Geräteparameter** (OLT hat immer +5.0 dBm), aber der **empfangene Power** beim ONT wird **automatisch berechnet** basierend auf:
- OLT TX Power: +5.0 dBm
- Link Loss (Fiber): length_km * attenuation
- Passive Device Loss: insertion_loss_db
- **= Received Power am ONT**"

---

#### **❌ FALSCH:**
"User erstellt Devices mit allen Properties manuell"

#### **✅ RICHTIG:**
"User klickt 'Add OLT', System:
1. Erstellt Device (OLT)
2. Auto-creates: mgmt0 + pon0-7 Interfaces
3. Auto-assigns: IP 10.250.4.x/24
4. Auto-generates: MAC 02:55:4E:xx:xx:xx
5. Sets Status: DOWN (kein Upstream)
6. **User sieht alles automatisch!**"

---

#### **❌ FALSCH:**
"Backbone Gateway ist normal DOWN"

#### **✅ RICHTIG:**
"Backbone Gateway ist **ALWAYS ONLINE** (Always UP) - das ist die **Single Source of Truth**:
- Backbone = ✅ UP (immer!)
- Core Router = ✅ UP (wenn Backbone erreichbar)
- Edge Router = ✅ UP (wenn Core erreichbar)
- OLT = ✅ UP (wenn Edge erreichbar)
- ONT = ✅ UP (wenn OLT erreichbar + Signal OK)"

---

## 📊 **IMPLEMENTIERUNGS-PRIORITÄTEN**

### **PHASE 1: KRITISCHE UI-FIXES** (2-3h)

#### **1.1 Device Sidebar - Interfaces Tab**
```typescript
// Neues Tab: "Interfaces"
- Liste aller Interfaces
- Pro Interface: Name, MAC, IP, Status
- Click → Interface Details
```

#### **1.2 Link Properties Modal**
```typescript
// Statt "Delete" → "Properties"
- length_km editieren
- fiber_type auswählen
- Calculated loss anzeigen
- Traffic stats anzeigen
```

#### **1.3 Signal Budget Display (ONT only)**
```typescript
// Im ONT Sidebar:
- Received Power
- Margin
- Signal Status (OK/WARNING/CRITICAL)
- Path visualization
```

---

### **PHASE 2: TRAFFIC VISUALIZATION** (3-4h)

#### **2.1 Live Traffic Bars**
```typescript
// Auf jedem Device:
- Grüner Bar: Current Traffic
- Graue Bar: Capacity
- Text: "450 Mbps / 2.5 Gbps (18%)"
```

#### **2.2 Congestion Indicators**
```typescript
// Wenn ≥100% utilization:
- Device/Link wird ROT
- Badge: "CONGESTED ⚠️"
- Tooltip: "Demand exceeds capacity"
```

---

### **PHASE 3: ENHANCED TOPOLOGY** (2-3h)

#### **3.1 Optical Path Highlighting**
```typescript
// Click auf ONT:
- Highlighted Path zum OLT
- Zeige Loss pro Segment
- Color-coded by signal quality
```

#### **3.2 Port Occupancy (OLT)**
```typescript
// OLT Sidebar:
- "PON Ports: 3/8 used"
- Liste: pon0 → 3 ONTs, pon1 → empty, etc.
```

---

## ❓ **NÄCHSTE SCHRITTE - DEINE ENTSCHEIDUNG**

### **OPTION A: UI FOUNDATION FIX** 🏗️ (EMPFOHLEN)
**Dauer:** 2-3 Stunden  
**Ziel:** UI zeigt EXISTIERENDE Backend-Daten

**Was:**
1. Interfaces Tab im Device Sidebar
2. Link Properties Modal (statt nur Delete)
3. Signal Budget für ONTs

**Resultat:**
- User sieht IPs, MACs
- User kann Link length_km editieren
- ONTs zeigen Signal Quality

---

### **OPTION B: KOMPLETTES RETHINK** 📋
**Dauer:** 4-6 Stunden  
**Ziel:** Komplette FTTH Emulator UI

**Was:**
- Alles aus Option A
- + Traffic Visualization
- + Congestion Detection
- + Optical Path Highlighting
- + Port Occupancy

**Resultat:**
- Vollständiger FTTH Emulator
- Alle Backend-Features sichtbar

---

### **OPTION C: DOKUMENTATION FIRST** 📚
**Dauer:** 1-2 Stunden  
**Ziel:** Plan erstellen

**Was:**
- Feature-by-Feature Mapping
- UI Mockups
- Implementation Plan
- Priorität setzen

**Resultat:**
- Klarer Roadmap
- Keine Überraschungen mehr

---

## 💡 **MEINE EMPFEHLUNG:**

**START WITH OPTION A** (UI Foundation Fix)

**Warum:**
1. **Quick Win** - 2-3 Stunden
2. **Zeigt sofort Wert** - User sieht IPs, MACs, Signal
3. **Validiert Backend** - Stellt sicher dass alles funktioniert
4. **Momentum** - Motiviert für weitere Features

**Dann:**
- Phase 2: Traffic Viz (wenn Basics OK)
- Phase 3: Advanced Features (wenn Traffic OK)

---

## ❓ **FRAGEN AN DICH:**

1. **Stimmt meine Analyse?** Habe ich das Backend richtig verstanden?

2. **Priorität?** Was ist am wichtigsten zu sehen?
   - Interfaces/IPs?
   - Signal Budget?
   - Traffic?

3. **Scope?** Wie viel Zeit hast du heute noch?
   - 2-3h → Option A
   - 4-6h → Option B
   - 1-2h → Option C

4. **Bestätigung:** Backbone Gateway sollte **IMMER UP** sein, richtig?

---

**Ich warte auf deine Entscheidung!** 🎯
