#!/usr/bin/env python3
"""
Automation script to apply Hysteria2 UI enhancements to modalServer.vue

This script applies the following changes:
1. Updates Hysteria2 tab template with advanced/basic fields
2. Adds new fields to data() object: upMbps, downMbps, network, hysteria2ShowAdvanced
3. Updates resolveURL() to parse new parameters
4. Updates generateURL() to export new parameters
5. Updates handleClickSubmit() to handle new fields

Usage:
    python3 scripts/apply_hysteria2_ui_changes.py
"""

import re
import sys

def apply_hysteria2_changes(file_path='gui/src/components/modalServer.vue'):
    """Apply all Hysteria2 UI changes to modalServer.vue"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        print("Please run this script from the project root directory")
        return False
    
    original_content = content
    changes_made = []
    
    # Change 1: Update Hysteria2 template
    print("⏳ Applying change 1/5: Updating Hysteria2 tab template...")
    old_template = r'<b-tab-item label="Hysteria2">.*?</b-tab-item>'
    new_template = '''<b-tab-item label="Hysteria2">
          <!-- Basic Fields -->
          <b-field label="Name" label-position="on-border">
            <b-input ref="hysteria2_name" v-model="hysteria2.name" :placeholder="$t('configureServer.servername')"
              expanded />
          </b-field>
          
          <b-field label="Host" label-position="on-border">
            <b-input ref="hysteria2_server" v-model="hysteria2.server" required placeholder="IP / HOST" expanded />
          </b-field>
          
          <b-field label="Port" label-position="on-border">
            <b-input ref="hysteria2_port" v-model="hysteria2.port" required :placeholder="$t('configureServer.port')"
              type="number" expanded />
          </b-field>
          
          <b-field label="Password" label-position="on-border">
            <b-input ref="hysteria2_password" v-model="hysteria2.password" required type="password"
              :placeholder="$t('configureServer.password')" expanded />
          </b-field>
          
          <b-field label="SNI" label-position="on-border">
            <b-input ref="hysteria2_sni" v-model="hysteria2.sni" placeholder="SNI (TLS Server Name)" expanded />
          </b-field>
          
          <b-field label-position="on-border">
            <template slot="label"> Skip TLS Verify </template>
            <b-select ref="hysteria2_allow_insecure" v-model="hysteria2.allowInsecure" expanded required>
              <option :value="false">{{ $t("operations.no") }}</option>
              <option :value="true">{{ $t("operations.yes") }}</option>
            </b-select>
          </b-field>
          
          <!-- Bandwidth (Important for Hysteria2) -->
          <b-field grouped>
            <b-field label="Upload (Mbps)" label-position="on-border" expanded>
              <b-input ref="hysteria2_up_mbps" v-model.number="hysteria2.upMbps" type="number" 
                placeholder="100" min="0" expanded />
            </b-field>
            <b-field label="Download (Mbps)" label-position="on-border" expanded>
              <b-input ref="hysteria2_down_mbps" v-model.number="hysteria2.downMbps" type="number" 
                placeholder="200" min="0" expanded />
            </b-field>
          </b-field>
          
          <!-- Advanced Options Toggle -->
          <b-field>
            <b-button 
              type="is-light" 
              size="is-small" 
              expanded
              @click="hysteria2ShowAdvanced = !hysteria2ShowAdvanced"
            >
              <b-icon :icon="hysteria2ShowAdvanced ? 'menu-up' : 'menu-down'"></b-icon>
              <span>{{ hysteria2ShowAdvanced ? 'Hide' : 'Show' }} Advanced Options</span>
            </b-button>
          </b-field>
          
          <!-- Advanced Fields (Collapsible) -->
          <div v-show="hysteria2ShowAdvanced">
            <b-field label="Obfuscation" label-position="on-border">
              <b-select v-model="hysteria2.obfs" expanded>
                <option value="none">Disabled</option>
                <option value="salamander">Salamander</option>
              </b-select>
            </b-field>
            
            <b-field v-if="hysteria2.obfs !== 'none'" label="Obfs Password" label-position="on-border">
              <b-input v-model="hysteria2.obfsPassword" type="password" placeholder="Obfuscation Password" expanded />
            </b-field>
            
            <b-field label="Network" label-position="on-border">
              <b-select v-model="hysteria2.network" expanded>
                <option value="">Auto (TCP + UDP)</option>
                <option value="tcp">TCP Only</option>
                <option value="udp">UDP Only</option>
              </b-select>
            </b-field>
          </div>
        </b-tab-item>'''
    
    content_new = re.sub(old_template, new_template, content, flags=re.DOTALL)
    if content_new != content:
        content = content_new
        changes_made.append("✅ Updated Hysteria2 tab template")
    
    # Change 2: Update hysteria2 data object
    print("⏳ Applying change 2/5: Updating data() object...")
    old_data = r'hysteria2: \{[^}]+protocol: "hysteria2",[^}]+\},'
    new_data = '''hysteria2: {
      name: "",
      server: "",
      port: "",
      password: "",
      sni: "",
      obfs: "none",
      obfsPassword: "",
      allowInsecure: false,
      upMbps: 100,
      downMbps: 200,
      network: "",
      protocol: "hysteria2",
    },
    hysteria2ShowAdvanced: false,'''
    
    content_new = re.sub(old_data, new_data, content, flags=re.DOTALL)
    if content_new != content:
        content = content_new
        changes_made.append("✅ Updated hysteria2 data object")
    
    # Change 3: Update resolveURL for hysteria2
    print("⏳ Applying change 3/5: Updating resolveURL() method...")
    old_resolve = r'(url\.toLowerCase\(\)\.startsWith\("hysteria2://"\)[\s\S]*?obfsPassword: u\.params\["obfs-password"\] \|\| "",)'
    new_resolve = '''url.toLowerCase().startsWith("hysteria2://") ||
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
          upMbps: parseInt(u.params.up) || 100,
          downMbps: parseInt(u.params.down) || 200,
          network: u.params.network || "",'''
    
    # This is complex, let's use a more targeted approach
    if 'upMbps: parseInt(u.params.up)' not in content:
        # Find and add the fields
        content = content.replace(
            'obfsPassword: u.params["obfs-password"] || "",\n          protocol: "hysteria2",',
            'obfsPassword: u.params["obfs-password"] || "",\n          upMbps: parseInt(u.params.up) || 100,\n          downMbps: parseInt(u.params.down) || 200,\n          network: u.params.network || "",\n          protocol: "hysteria2",'
        )
        changes_made.append("✅ Updated resolveURL() for Hysteria2")
    
    # Change 4: Update generateURL for hysteria2
    print("⏳ Applying change 4/5: Updating generateURL() method...")
    if 'query.up = srcObj.upMbps' not in content:
        content = content.replace(
            'if (srcObj.sni !== "") {\n            query.sni = srcObj.sni;\n          }\n          if (srcObj.obfs !== "none")',
            'if (srcObj.sni !== "") {\n            query.sni = srcObj.sni;\n          }\n          if (srcObj.upMbps > 0) {\n            query.up = srcObj.upMbps;\n          }\n          if (srcObj.downMbps > 0) {\n            query.down = srcObj.downMbps;\n          }\n          if (srcObj.network !== "") {\n            query.network = srcObj.network;\n          }\n          if (srcObj.obfs !== "none")'
        )
        changes_made.append("✅ Updated generateURL() for Hysteria2")
    
    # Change 5: Update handleClickSubmit for hysteria2
    print("⏳ Applying change 5/5: Updating handleClickSubmit() method...")
    if 'upMbps, downMbps, network } = this.hysteria2' not in content:
        content = content.replace(
            'const { password, server, port, allowInsecure, obfs, obfsPassword, sni, name } = this.hysteria2;',
            'const { password, server, port, allowInsecure, obfs, obfsPassword, sni, name, upMbps, downMbps, network } = this.hysteria2;'
        )
        content = content.replace(
            'if (allowInsecure) params.push("insecure=1");\n        if (obfs && obfs',
            'if (allowInsecure) params.push("insecure=1");\n        if (upMbps > 0) params.push(`up=${upMbps}`);\n        if (downMbps > 0) params.push(`down=${downMbps}`);\n        if (network) params.push(`network=${encodeURIComponent(network)}`);\n        if (obfs && obfs'
        )
        changes_made.append("✅ Updated handleClickSubmit() for Hysteria2")
    
    # Write changes
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n" + "="*70)
        print("✅ Successfully applied all changes!")
        print("\nChanges made:")
        for change in changes_made:
            print(f"  {change}")
        print("\n📝 File updated:", file_path)
        return True
    else:
        print("⚠️  No changes were made (possibly already applied)")
        return False

if __name__ == '__main__':
    success = apply_hysteria2_changes()
    sys.exit(0 if success else 1)
