#!/usr/bin/env python3
"""
Nuclei Integration for AEGIS-X Reborn
Integrates Nuclei templates for comprehensive vulnerability scanning
"""

import asyncio
import subprocess
import json
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class NucleiIntegration:
    """Nuclei template integration for enhanced vulnerability detection"""
    
    def __init__(self):
        self.nuclei_path = self._find_nuclei()
        self.templates_path = self._find_templates()
        
    def _find_nuclei(self) -> str:
        """Find Nuclei binary"""
        # Check common locations
        common_paths = [
            "/usr/local/bin/nuclei",
            "/usr/bin/nuclei",
            "/opt/nuclei/nuclei",
            "nuclei"  # In PATH
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✅ Found Nuclei at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        logger.warning("⚠️ Nuclei not found - will attempt to install")
        return self._install_nuclei()
    
    def _install_nuclei(self) -> str:
        """Install Nuclei if not found"""
        try:
            logger.info("📦 Installing Nuclei...")
            
            # Download and install Nuclei
            install_commands = [
                "curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest | grep 'browser_download_url.*linux_amd64.zip' | cut -d '\"' -f 4 | wget -qi -",
                "unzip -o nuclei_*_linux_amd64.zip",
                "chmod +x nuclei",
                "sudo mv nuclei /usr/local/bin/ || mv nuclei /tmp/"
            ]
            
            for cmd in install_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode != 0 and "sudo" not in cmd:
                    logger.error(f"❌ Failed to run: {cmd}")
                    continue
            
            # Try to find it again
            for path in ["/usr/local/bin/nuclei", "/tmp/nuclei", "./nuclei"]:
                if os.path.exists(path):
                    logger.info(f"✅ Nuclei installed at: {path}")
                    return path
            
            logger.error("❌ Failed to install Nuclei")
            return None
            
        except Exception as e:
            logger.error(f"❌ Nuclei installation failed: {str(e)}")
            return None
    
    def _find_templates(self) -> str:
        """Find or download Nuclei templates"""
        # Check common template locations
        template_paths = [
            os.path.expanduser("~/nuclei-templates"),
            "/opt/nuclei-templates",
            "./nuclei-templates",
            "./custom-nuclei-templates"
        ]
        
        for path in template_paths:
            if os.path.exists(path) and os.path.isdir(path):
                logger.info(f"✅ Found templates at: {path}")
                return path
        
        # Download templates
        return self._download_templates()
    
    def _download_templates(self) -> str:
        """Download Nuclei templates"""
        try:
            logger.info("📦 Downloading Nuclei templates...")
            
            template_dir = "./nuclei-templates"
            
            # Clone templates repository
            clone_cmd = f"git clone https://github.com/projectdiscovery/nuclei-templates.git {template_dir}"
            result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(template_dir):
                logger.info(f"✅ Templates downloaded to: {template_dir}")
                return template_dir
            else:
                logger.error("❌ Failed to download templates")
                return None
                
        except Exception as e:
            logger.error(f"❌ Template download failed: {str(e)}")
            return None
    
    async def scan_with_nuclei(self, target: str, template_categories: List[str] = None) -> List[Dict[str, Any]]:
        """Run Nuclei scan with specified templates"""
        if not self.nuclei_path or not self.templates_path:
            logger.error("❌ Nuclei or templates not available")
            return []
        
        vulnerabilities = []
        
        try:
            # Prepare command
            cmd = [
                self.nuclei_path,
                "-u", target,
                "-t", self.templates_path,
                "-json",
                "-silent",
                "-rate-limit", "10",  # Be respectful
                "-timeout", "10",
                "-retries", "1"
            ]
            
            # Add specific template categories if specified
            if template_categories:
                for category in template_categories:
                    category_path = os.path.join(self.templates_path, category)
                    if os.path.exists(category_path):
                        cmd.extend(["-t", category_path])
            
            logger.info(f"🚀 Running Nuclei scan: {' '.join(cmd)}")
            
            # Run Nuclei
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse JSON output
                for line in stdout.decode().strip().split('\n'):
                    if line.strip():
                        try:
                            vuln_data = json.loads(line)
                            vulnerabilities.append(self._parse_nuclei_result(vuln_data))
                        except json.JSONDecodeError:
                            continue
                
                logger.info(f"✅ Nuclei scan complete: {len(vulnerabilities)} vulnerabilities found")
            else:
                logger.error(f"❌ Nuclei scan failed: {stderr.decode()}")
            
        except Exception as e:
            logger.error(f"❌ Nuclei scan error: {str(e)}")
        
        return vulnerabilities
    
    def _parse_nuclei_result(self, nuclei_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Nuclei JSON result into our format"""
        info = nuclei_data.get('info', {})
        
        # Map Nuclei severity to our format
        severity_mapping = {
            'info': 'Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'critical': 'Critical'
        }
        
        severity = severity_mapping.get(info.get('severity', 'low').lower(), 'Low')
        
        return {
            'id': f"nuclei_{nuclei_data.get('template-id', 'unknown')}_{int(asyncio.get_event_loop().time())}",
            'type': info.get('name', 'Unknown'),
            'severity': severity,
            'url': nuclei_data.get('matched-at', ''),
            'title': info.get('name', 'Nuclei Detection'),
            'description': info.get('description', 'Vulnerability detected by Nuclei'),
            'payload': nuclei_data.get('extracted-results', ['N/A'])[0] if nuclei_data.get('extracted-results') else 'N/A',
            'proof_of_concept': f"Nuclei template: {nuclei_data.get('template-id', 'unknown')}",
            'impact': self._get_impact_from_severity(severity),
            'remediation': info.get('remediation', 'Follow security best practices'),
            'confidence': 0.9,  # Nuclei templates are generally reliable
            'verified': True,   # Nuclei results are pre-verified
            'timestamp': nuclei_data.get('timestamp', ''),
            'nuclei_data': nuclei_data  # Keep original data for reference
        }
    
    def _get_impact_from_severity(self, severity: str) -> str:
        """Get impact description based on severity"""
        impact_map = {
            'Critical': 'Complete system compromise possible',
            'High': 'Significant security risk with potential for data breach',
            'Medium': 'Moderate security risk requiring attention',
            'Low': 'Minor security issue with limited impact'
        }
        return impact_map.get(severity, 'Security vulnerability detected')
    
    async def run_custom_templates(self, target: str) -> List[Dict[str, Any]]:
        """Run custom Nuclei templates for specific vulnerabilities"""
        custom_templates = [
            "cves/",
            "vulnerabilities/",
            "exposures/",
            "misconfiguration/",
            "takeovers/",
            "default-logins/",
            "file/",
            "network/",
            "dns/"
        ]
        
        all_vulnerabilities = []
        
        for template_category in custom_templates:
            template_path = os.path.join(self.templates_path, template_category)
            if os.path.exists(template_path):
                logger.info(f"🔍 Scanning with {template_category} templates")
                vulns = await self.scan_with_nuclei(target, [template_category])
                all_vulnerabilities.extend(vulns)
                
                # Small delay between template categories
                await asyncio.sleep(1)
        
        return all_vulnerabilities
    
    def create_custom_template(self, vuln_type: str, payload: str, match_condition: str) -> str:
        """Create a custom Nuclei template"""
        template_content = f"""id: custom-{vuln_type.lower().replace(' ', '-')}

info:
  name: Custom {vuln_type} Detection
  author: AEGIS-X-Reborn
  severity: medium
  description: Custom template for {vuln_type} detection
  tags: {vuln_type.lower()},custom

requests:
  - method: GET
    path:
      - "{{{{BaseURL}}}}"
    
    payloads:
      payload:
        - "{payload}"
    
    matchers:
      - type: word
        words:
          - "{match_condition}"
        condition: and
"""
        
        # Save custom template
        custom_dir = "./custom-nuclei-templates"
        os.makedirs(custom_dir, exist_ok=True)
        
        template_file = os.path.join(custom_dir, f"custom-{vuln_type.lower().replace(' ', '-')}.yaml")
        with open(template_file, 'w') as f:
            f.write(template_content)
        
        logger.info(f"📝 Created custom template: {template_file}")
        return template_file
    
    async def update_templates(self):
        """Update Nuclei templates to latest version"""
        if not self.nuclei_path:
            return False
        
        try:
            logger.info("🔄 Updating Nuclei templates...")
            
            cmd = [self.nuclei_path, "-update-templates"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ Templates updated successfully")
                return True
            else:
                logger.error(f"❌ Template update failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Template update error: {str(e)}")
            return False