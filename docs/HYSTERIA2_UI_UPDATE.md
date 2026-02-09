# Hysteria2 UI Enhancement Guide

## 📋 Overview

This document describes the UI enhancements for Hysteria2 protocol support in v2rayA, including:

- **Two-stage form design**: Basic + Advanced (collapsible)
- **Bandwidth configuration**: Upload/Download Mbps fields
- **Network selection**: TCP/UDP configuration
- **Complete URL parsing**: Support for all Hysteria2 parameters

---

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

Run the automation script from project root:

```bash
python3 scripts/apply_hysteria2_ui_changes.py
```

This will automatically apply all 5 changes to `gui/src/components/modalServer.vue`.

### Option 2: Manual Changes

Follow the detailed instructions below to manually apply each change.

---

## 📝 Detailed Changes

### Change 1: Update Hysteria2 Tab Template

**Location**: `gui/src/components/modalServer.vue` around line 700-750

**Replace** the entire `<b-tab-item label="Hysteria2">` section with the new template (see patch file or script).

**Key additions**:
- Grouped bandwidth fields (Upload/Download Mbps)
- Toggle button for Advanced Options
- Collapsible advanced section with Obfuscation and Network fields

---

### Change 2: Update `data()` Object

**Location**: Around line 950

**Before**:
```javascript
hysteria2: {
  name: "",
  server: "",
  port: "",
  password: "",
  sni: "",
  obfs: "none",
  obfsPassword: "",
  allowInsecure: false,
  protocol: "hysteria2",
},
```

**After**:
```javascript
hysteria2: {
  name: "",
  server: "",
  port: "",
  password: "",
  sni: "",
  obfs: "none",
  obfsPassword: "",
  allowInsecure: false,
  upMbps: 100,        // ⭐ NEW
  downMbps: 200,      // ⭐ NEW
  network: "",        // ⭐ NEW
  protocol: "hysteria2",
},
hysteria2ShowAdvanced: false,  // ⭐ NEW: Controls advanced section visibility
```

---

### Change 3: Update `resolveURL()` Method

**Location**: Around line 1050

**Add these lines** after `obfsPassword`:

```javascript
} else if (
  url.toLowerCase().startsWith("hysteria2://") ||
  url.toLowerCase().startsWith("hy2://")
) {
  let u = parseURL(url);
  return {
    name: decodeURIComponent(u.hash),
    password: decodeURIComponent(u.username),
    server: u.host,
    port: u.port,
    sni: u.params.sni || "",
    allowInsecure: u.params.insecure === "true" || u.params.insecure === "1",
    obfs: u.params.obfs || "none",
    obfsPassword: u.params["obfs-password"] || "",
    upMbps: parseInt(u.params.up) || 100,        // ⭐ NEW
    downMbps: parseInt(u.params.down) || 200,    // ⭐ NEW
    network: u.params.network || "",              // ⭐ NEW
    protocol: "hysteria2",
  };
```

---

### Change 4: Update `generateURL()` Method

**Location**: Around line 1300, in `case "hysteria2"`

**Add after** `query.sni = srcObj.sni;`:

```javascript
case "hysteria2":
  query = {
    insecure: srcObj.allowInsecure ? "1" : "0",
  };
  if (srcObj.sni !== "") {
    query.sni = srcObj.sni;
  }
  // ⭐ NEW: Add bandwidth parameters
  if (srcObj.upMbps > 0) {
    query.up = srcObj.upMbps;
  }
  if (srcObj.downMbps > 0) {
    query.down = srcObj.downMbps;
  }
  if (srcObj.network !== "") {
    query.network = srcObj.network;
  }
  // End NEW
  if (srcObj.obfs !== "none") {
    query.obfs = srcObj.obfs;
    query["obfs-password"] = srcObj.obfsPassword;
  }
```

---

### Change 5: Update `handleClickSubmit()` Method

**Location**: Around line 1650, `else if (this.tabChoice === 6)`

**Before**:
```javascript
else if (this.tabChoice === 6) {
  const { password, server, port, allowInsecure, obfs, obfsPassword, sni, name } = this.hysteria2;
  let params = [];
  if (allowInsecure) params.push("insecure=1");
  if (obfs && obfs !== "none") params.push(`obfs=${encodeURIComponent(obfs)}`);
```

**After**:
```javascript
else if (this.tabChoice === 6) {
  const { password, server, port, allowInsecure, obfs, obfsPassword, sni, name, upMbps, downMbps, network } = this.hysteria2;  // ⭐ Added new fields
  let params = [];
  if (allowInsecure) params.push("insecure=1");
  // ⭐ NEW: Add bandwidth and network params
  if (upMbps > 0) params.push(`up=${upMbps}`);
  if (downMbps > 0) params.push(`down=${downMbps}`);
  if (network) params.push(`network=${encodeURIComponent(network)}`);
  // End NEW
  if (obfs && obfs !== "none") params.push(`obfs=${encodeURIComponent(obfs)}`);
```

---

## 🎯 Features Summary

### Basic Section (Always Visible)
1. **Name**: Server display name
2. **Host**: Server address (IP/Domain)
3. **Port**: Server port number
4. **Password**: Connection password
5. **SNI**: TLS Server Name Indication
6. **Skip TLS Verify**: Allow insecure connections
7. **Upload/Download Bandwidth**: ⭐ Critical for Hysteria2 performance

### Advanced Section (Collapsible)
1. **Obfuscation**: None or Salamander
2. **Obfs Password**: Password for obfuscation (if enabled)
3. **Network**: Auto (TCP+UDP) / TCP Only / UDP Only

---

## 🧪 Testing

After applying changes:

1. **Build the frontend**:
   ```bash
   cd gui
   npm install
   npm run build
   ```

2. **Test URL parsing**:
   - Import a Hysteria2 URL with bandwidth params:
     ```
     hysteria2://password@server:port?up=100&down=200&network=tcp#MyServer
     ```
   - Verify all fields are populated correctly

3. **Test URL generation**:
   - Create a new Hysteria2 server with bandwidth settings
   - Export and verify the URL contains `up`, `down`, `network` parameters

4. **Test UI**:
   - Toggle Advanced Options button
   - Verify fields show/hide correctly
   - Check grouped bandwidth fields layout

---

## 📚 Related Files

- **Backend**: `service/core/serverObj/hysteria2.go`
- **Frontend**: `gui/src/components/modalServer.vue`
- **Patch**: `docs/hysteria2-ui-update.patch`
- **Script**: `scripts/apply_hysteria2_ui_changes.py`

---

## 🔗 References

- [Hysteria2 Documentation](https://v2.hysteria.network/)
- [Sing-box Hysteria2 Config](https://sing-box.sagernet.org/configuration/outbound/hysteria2/)
- Backend changes: [commit 1b29a55](https://github.com/mrkarami1/v2rayA/commit/1b29a5538b462681ab50b03c7d64cd49f3a47604)

---

## ✅ Checklist

- [ ] Applied all 5 changes to modalServer.vue
- [ ] Built frontend successfully
- [ ] Tested URL import/export
- [ ] Verified UI toggle functionality
- [ ] Committed changes with descriptive message
- [ ] Ready for code review

---

**Last Updated**: 2026-02-09  
**Author**: v2rayA Team  
**Status**: Ready for Review
