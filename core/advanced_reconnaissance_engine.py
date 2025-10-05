#!/usr/bin/env python3
"""
AEGIS-X Advanced Reconnaissance Engine v2.0
Comprehensive intelligence gathering and target analysis
"""

import asyncio
import aiohttp
import json
import logging
import time
import socket
import ssl
import dns.resolver
import subprocess
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, asdict
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReconResult:
    """Reconnaissance result data structure"""
    target: str
    subdomains: List[str]
    open_ports: List[int]
    services: Dict[str, Any]
    technologies: Dict[str, Any]
    endpoints: List[str]
    vulnerabilities: List[Dict[str, Any]]
    certificates: Dict[str, Any]
    dns_records: Dict[str, Any]
    social_engineering_vectors: List[str]
    attack_surface: Dict[str, Any]
    risk_score: float
    execution_time: float
    timestamp: float

class AdvancedReconnaissanceEngine:
    """
    Advanced Reconnaissance Engine with comprehensive intelligence gathering
    """
    
    def __init__(self):
        self.session = None
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 10
        
        # Comprehensive wordlists
        self.subdomain_wordlist = [
            "www", "api", "app", "admin", "test", "dev", "staging", "prod", "production",
            "mail", "email", "smtp", "pop", "imap", "ftp", "sftp", "ssh", "vpn",
            "blog", "shop", "store", "portal", "dashboard", "panel", "control",
            "secure", "ssl", "tls", "remote", "support", "help", "docs", "wiki",
            "cdn", "static", "assets", "media", "images", "files", "download",
            "backup", "old", "new", "beta", "alpha", "demo", "sandbox", "lab",
            "db", "database", "mysql", "postgres", "mongo", "redis", "elastic",
            "jenkins", "gitlab", "github", "bitbucket", "jira", "confluence",
            "monitoring", "metrics", "logs", "kibana", "grafana", "prometheus",
            "kubernetes", "k8s", "docker", "registry", "harbor", "nexus"
        ]
        
        self.directory_wordlist = [
            "admin", "administrator", "api", "app", "application", "backup", "backups",
            "bin", "cgi-bin", "config", "configuration", "css", "data", "database",
            "db", "debug", "dev", "development", "doc", "docs", "documentation",
            "download", "downloads", "etc", "files", "ftp", "home", "html", "http",
            "https", "images", "img", "include", "includes", "index", "info", "js",
            "javascript", "lib", "library", "log", "logs", "mail", "media", "old",
            "panel", "private", "public", "root", "scripts", "secure", "security",
            "src", "static", "stats", "system", "temp", "test", "testing", "tmp",
            "upload", "uploads", "user", "users", "var", "web", "www", "xml"
        ]
        
        self.file_extensions = [
            ".php", ".asp", ".aspx", ".jsp", ".do", ".action", ".py", ".rb", ".pl",
            ".cgi", ".sh", ".bat", ".cmd", ".exe", ".dll", ".so", ".jar", ".war",
            ".zip", ".rar", ".tar", ".gz", ".bz2", ".7z", ".sql", ".db", ".sqlite",
            ".mdb", ".bak", ".backup", ".old", ".tmp", ".log", ".txt", ".xml", ".json",
            ".yaml", ".yml", ".ini", ".conf", ".config", ".properties", ".env"
        ]
        
        # Port scanning ranges
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
            1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 8888, 9000, 9200,
            27017, 50070, 11211, 6667, 1433, 1521, 2049, 3690, 5060, 5061
        ]
        
        self.extended_ports = list(range(1, 1024)) + [
            1433, 1521, 2049, 2121, 2375, 2376, 3690, 4444, 5060, 5061, 5432,
            5900, 5984, 6379, 7001, 8000, 8080, 8443, 8888, 9000, 9200, 9300,
            11211, 27017, 50070, 50470
        ]
        
        logger.info("🔍 Advanced Reconnaissance Engine initialized")
        logger.info(f"📊 Loaded {len(self.subdomain_wordlist)} subdomain patterns")
        logger.info(f"📁 Loaded {len(self.directory_wordlist)} directory patterns")
        logger.info(f"🔌 Configured {len(self.common_ports)} common ports")

    async def initialize_session(self):
        """Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
                ssl=False
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def comprehensive_reconnaissance(self, target: str, deep_scan: bool = True) -> ReconResult:
        """
        Execute comprehensive reconnaissance against target
        """
        start_time = time.time()
        logger.info(f"🔍 Starting comprehensive reconnaissance for {target}")
        
        await self.initialize_session()
        
        try:
            # Phase 1: DNS and Domain Intelligence
            logger.info("🌐 Phase 1: DNS and Domain Intelligence")
            dns_records = await self._gather_dns_intelligence(target)
            subdomains = await self._enumerate_subdomains_advanced(target)
            
            # Phase 2: Network and Service Discovery
            logger.info("🔌 Phase 2: Network and Service Discovery")
            open_ports = await self._scan_ports_advanced(target, deep_scan)
            services = await self._detect_services(target, open_ports)
            
            # Phase 3: Web Application Analysis
            logger.info("🌐 Phase 3: Web Application Analysis")
            technologies = await self._fingerprint_technologies_advanced(target)
            endpoints = await self._discover_endpoints_advanced(target)
            
            # Phase 4: SSL/TLS Analysis
            logger.info("🔒 Phase 4: SSL/TLS Certificate Analysis")
            certificates = await self._analyze_ssl_certificates(target)
            
            # Phase 5: Vulnerability Assessment
            logger.info("🎯 Phase 5: Initial Vulnerability Assessment")
            vulnerabilities = await self._assess_initial_vulnerabilities(target, endpoints, services)
            
            # Phase 6: Social Engineering Vectors
            logger.info("👥 Phase 6: Social Engineering Vector Analysis")
            social_vectors = await self._identify_social_engineering_vectors(target, technologies)
            
            # Phase 7: Attack Surface Analysis
            logger.info("🎯 Phase 7: Attack Surface Analysis")
            attack_surface = await self._analyze_attack_surface(target, subdomains, open_ports, endpoints)
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(vulnerabilities, open_ports, services, technologies)
            
            execution_time = time.time() - start_time
            
            result = ReconResult(
                target=target,
                subdomains=subdomains,
                open_ports=open_ports,
                services=services,
                technologies=technologies,
                endpoints=endpoints,
                vulnerabilities=vulnerabilities,
                certificates=certificates,
                dns_records=dns_records,
                social_engineering_vectors=social_vectors,
                attack_surface=attack_surface,
                risk_score=risk_score,
                execution_time=execution_time,
                timestamp=start_time
            )
            
            logger.info(f"✅ Reconnaissance completed in {execution_time:.2f}s")
            logger.info(f"📊 Found: {len(subdomains)} subdomains, {len(open_ports)} open ports, {len(endpoints)} endpoints")
            logger.info(f"🎯 Risk Score: {risk_score:.2f}/10")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Reconnaissance failed: {e}")
            raise
        finally:
            await self.close_session()

    async def _gather_dns_intelligence(self, target: str) -> Dict[str, Any]:
        """Gather comprehensive DNS intelligence"""
        dns_info = {
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": [],
            "soa_record": None,
            "ptr_records": []
        }
        
        domain = urlparse(f"https://{target}").netloc or target
        
        try:
            # A records
            try:
                answers = self.dns_resolver.resolve(domain, 'A')
                dns_info["a_records"] = [str(rdata) for rdata in answers]
            except:
                pass
            
            # AAAA records
            try:
                answers = self.dns_resolver.resolve(domain, 'AAAA')
                dns_info["aaaa_records"] = [str(rdata) for rdata in answers]
            except:
                pass
            
            # MX records
            try:
                answers = self.dns_resolver.resolve(domain, 'MX')
                dns_info["mx_records"] = [f"{rdata.preference} {rdata.exchange}" for rdata in answers]
            except:
                pass
            
            # NS records
            try:
                answers = self.dns_resolver.resolve(domain, 'NS')
                dns_info["ns_records"] = [str(rdata) for rdata in answers]
            except:
                pass
            
            # TXT records
            try:
                answers = self.dns_resolver.resolve(domain, 'TXT')
                dns_info["txt_records"] = [str(rdata) for rdata in answers]
            except:
                pass
            
            # SOA record
            try:
                answers = self.dns_resolver.resolve(domain, 'SOA')
                dns_info["soa_record"] = str(answers[0]) if answers else None
            except:
                pass
            
            logger.info(f"🌐 DNS intelligence gathered: {len(dns_info['a_records'])} A records, {len(dns_info['mx_records'])} MX records")
            
        except Exception as e:
            logger.debug(f"DNS intelligence error: {e}")
        
        return dns_info

    async def _enumerate_subdomains_advanced(self, target: str) -> List[str]:
        """Advanced subdomain enumeration"""
        subdomains = set()
        domain = urlparse(f"https://{target}").netloc or target
        
        # Method 1: Dictionary-based enumeration
        logger.info("🔍 Dictionary-based subdomain enumeration")
        dict_subdomains = await self._enumerate_subdomains_dictionary(domain)
        subdomains.update(dict_subdomains)
        
        # Method 2: Certificate transparency logs
        logger.info("🔍 Certificate transparency enumeration")
        ct_subdomains = await self._enumerate_subdomains_ct_logs(domain)
        subdomains.update(ct_subdomains)
        
        # Method 3: Search engine enumeration
        logger.info("🔍 Search engine enumeration")
        search_subdomains = await self._enumerate_subdomains_search_engines(domain)
        subdomains.update(search_subdomains)
        
        # Method 4: DNS zone transfer attempt
        logger.info("🔍 DNS zone transfer attempt")
        zone_subdomains = await self._attempt_zone_transfer(domain)
        subdomains.update(zone_subdomains)
        
        # Validate discovered subdomains
        valid_subdomains = []
        for subdomain in subdomains:
            if await self._validate_subdomain(subdomain):
                valid_subdomains.append(f"https://{subdomain}")
        
        logger.info(f"🔍 Found {len(valid_subdomains)} valid subdomains")
        return valid_subdomains

    async def _enumerate_subdomains_dictionary(self, domain: str) -> List[str]:
        """Dictionary-based subdomain enumeration"""
        subdomains = []
        
        tasks = []
        for subdomain in self.subdomain_wordlist:
            full_domain = f"{subdomain}.{domain}"
            tasks.append(self._check_subdomain_exists(full_domain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                subdomains.append(f"{self.subdomain_wordlist[i]}.{domain}")
        
        return subdomains

    async def _enumerate_subdomains_ct_logs(self, domain: str) -> List[str]:
        """Certificate transparency logs enumeration"""
        subdomains = []
        
        try:
            ct_urls = [
                f"https://crt.sh/?q=%.{domain}&output=json",
                f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
            ]
            
            for url in ct_urls:
                try:
                    async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "crt.sh" in url:
                                for cert in data:
                                    name_value = cert.get('name_value', '')
                                    for name in name_value.split('\n'):
                                        name = name.strip()
                                        if name.endswith(f".{domain}") and name not in subdomains:
                                            subdomains.append(name)
                            
                            elif "certspotter" in url:
                                for cert in data:
                                    dns_names = cert.get('dns_names', [])
                                    for name in dns_names:
                                        if name.endswith(f".{domain}") and name not in subdomains:
                                            subdomains.append(name)
                                            
                except Exception as e:
                    logger.debug(f"CT logs error for {url}: {e}")
                    
        except Exception as e:
            logger.debug(f"CT logs enumeration error: {e}")
        
        return subdomains

    async def _enumerate_subdomains_search_engines(self, domain: str) -> List[str]:
        """Search engine-based subdomain enumeration"""
        subdomains = []
        
        # Google dorking for subdomains
        search_queries = [
            f"site:{domain} -www",
            f"site:*.{domain}",
            f"inurl:{domain}"
        ]
        
        # Note: In a real implementation, you would use search engine APIs
        # This is a placeholder for the concept
        logger.debug("Search engine enumeration would be implemented here")
        
        return subdomains

    async def _attempt_zone_transfer(self, domain: str) -> List[str]:
        """Attempt DNS zone transfer"""
        subdomains = []
        
        try:
            # Get NS records
            ns_records = self.dns_resolver.resolve(domain, 'NS')
            
            for ns in ns_records:
                try:
                    # Attempt zone transfer (AXFR)
                    zone = dns.zone.from_xfr(dns.query.xfr(str(ns), domain))
                    for name, node in zone.nodes.items():
                        if name != dns.name.empty:
                            subdomain = f"{name}.{domain}"
                            subdomains.append(subdomain)
                            
                except Exception as e:
                    logger.debug(f"Zone transfer failed for {ns}: {e}")
                    
        except Exception as e:
            logger.debug(f"Zone transfer attempt error: {e}")
        
        return subdomains

    async def _check_subdomain_exists(self, subdomain: str) -> bool:
        """Check if subdomain exists"""
        try:
            # DNS resolution check
            self.dns_resolver.resolve(subdomain, 'A')
            return True
        except:
            try:
                # HTTP check as fallback
                async with self.session.get(f"https://{subdomain}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status < 500
            except:
                return False

    async def _validate_subdomain(self, subdomain: str) -> bool:
        """Validate subdomain accessibility"""
        try:
            async with self.session.get(f"https://{subdomain}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status < 500
        except:
            try:
                async with self.session.get(f"http://{subdomain}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status < 500
            except:
                return False

    async def _scan_ports_advanced(self, target: str, deep_scan: bool = True) -> List[int]:
        """Advanced port scanning"""
        open_ports = []
        domain = urlparse(f"https://{target}").netloc or target
        
        # Resolve domain to IP
        try:
            ip = socket.gethostbyname(domain)
        except:
            ip = domain
        
        # Choose port range based on scan depth
        ports_to_scan = self.extended_ports if deep_scan else self.common_ports
        
        logger.info(f"🔌 Scanning {len(ports_to_scan)} ports on {ip}")
        
        # Concurrent port scanning
        semaphore = asyncio.Semaphore(100)  # Limit concurrent connections
        tasks = []
        
        for port in ports_to_scan:
            tasks.append(self._scan_port(semaphore, ip, port))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                open_ports.append(ports_to_scan[i])
        
        logger.info(f"🔌 Found {len(open_ports)} open ports")
        return sorted(open_ports)

    async def _scan_port(self, semaphore: asyncio.Semaphore, host: str, port: int) -> bool:
        """Scan individual port"""
        async with semaphore:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=3
                )
                writer.close()
                await writer.wait_closed()
                return True
            except:
                return False

    async def _detect_services(self, target: str, open_ports: List[int]) -> Dict[str, Any]:
        """Detect services running on open ports"""
        services = {
            "http_services": [],
            "https_services": [],
            "ssh_services": [],
            "ftp_services": [],
            "database_services": [],
            "other_services": []
        }
        
        domain = urlparse(f"https://{target}").netloc or target
        
        for port in open_ports:
            service_info = await self._identify_service(domain, port)
            
            if service_info["type"] == "http":
                services["http_services"].append(service_info)
            elif service_info["type"] == "https":
                services["https_services"].append(service_info)
            elif service_info["type"] == "ssh":
                services["ssh_services"].append(service_info)
            elif service_info["type"] == "ftp":
                services["ftp_services"].append(service_info)
            elif service_info["type"] == "database":
                services["database_services"].append(service_info)
            else:
                services["other_services"].append(service_info)
        
        logger.info(f"🔍 Identified services: {len(services['http_services'])} HTTP, {len(services['https_services'])} HTTPS")
        return services

    async def _identify_service(self, host: str, port: int) -> Dict[str, Any]:
        """Identify service running on specific port"""
        service_info = {
            "host": host,
            "port": port,
            "type": "unknown",
            "version": "unknown",
            "banner": ""
        }
        
        # Common service mappings
        service_mappings = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
            80: "http", 110: "pop3", 143: "imap", 443: "https", 993: "imaps",
            995: "pop3s", 1433: "mssql", 3306: "mysql", 5432: "postgresql",
            6379: "redis", 27017: "mongodb"
        }
        
        service_info["type"] = service_mappings.get(port, "unknown")
        
        # Try to grab banner
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=5
            )
            
            # Read banner
            try:
                banner = await asyncio.wait_for(reader.read(1024), timeout=3)
                service_info["banner"] = banner.decode('utf-8', errors='ignore').strip()
            except:
                pass
            
            writer.close()
            await writer.wait_closed()
            
        except:
            pass
        
        # HTTP/HTTPS specific detection
        if port in [80, 8080, 8000, 9000] or service_info["type"] == "http":
            try:
                async with self.session.get(f"http://{host}:{port}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    service_info["type"] = "http"
                    service_info["version"] = response.headers.get('Server', 'unknown')
            except:
                pass
        
        elif port in [443, 8443] or service_info["type"] == "https":
            try:
                async with self.session.get(f"https://{host}:{port}", ssl=False, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    service_info["type"] = "https"
                    service_info["version"] = response.headers.get('Server', 'unknown')
            except:
                pass
        
        return service_info

    async def _fingerprint_technologies_advanced(self, target: str) -> Dict[str, Any]:
        """Advanced technology fingerprinting"""
        technologies = {
            "web_server": "unknown",
            "framework": "unknown",
            "cms": "unknown",
            "programming_language": "unknown",
            "database": "unknown",
            "cdn": "unknown",
            "analytics": [],
            "javascript_libraries": [],
            "css_frameworks": [],
            "security_tools": []
        }
        
        try:
            async with self.session.get(f"https://{target}", ssl=False, timeout=aiohttp.ClientTimeout(total=15)) as response:
                headers = response.headers
                content = await response.text()
                
                # Server and framework detection
                technologies["web_server"] = headers.get('Server', 'unknown')
                technologies["framework"] = headers.get('X-Powered-By', 'unknown')
                
                # CDN detection
                cdn_headers = ['CF-RAY', 'X-Cache', 'X-Served-By', 'X-CDN']
                for header in cdn_headers:
                    if header in headers:
                        technologies["cdn"] = header
                        break
                
                # CMS detection
                cms_patterns = {
                    'WordPress': ['wp-content', 'wp-includes', 'wp-admin'],
                    'Drupal': ['drupal', 'sites/default', 'modules/'],
                    'Joomla': ['joomla', 'administrator/', 'components/'],
                    'Magento': ['magento', 'skin/frontend', 'js/mage/'],
                    'Shopify': ['shopify', 'cdn.shopify.com'],
                    'Wix': ['wix.com', 'wixstatic.com']
                }
                
                for cms, patterns in cms_patterns.items():
                    if any(pattern in content.lower() for pattern in patterns):
                        technologies["cms"] = cms
                        break
                
                # Programming language detection
                lang_patterns = {
                    'PHP': ['.php', 'PHPSESSID', 'php'],
                    'ASP.NET': ['.aspx', '.asp', 'ASP.NET', '__VIEWSTATE'],
                    'Java': ['.jsp', '.do', 'jsessionid', 'java'],
                    'Python': ['django', 'flask', 'python'],
                    'Ruby': ['rails', 'ruby'],
                    'Node.js': ['node', 'express']
                }
                
                for lang, patterns in lang_patterns.items():
                    if any(pattern.lower() in content.lower() or pattern.lower() in str(headers).lower() for pattern in patterns):
                        technologies["programming_language"] = lang
                        break
                
                # JavaScript libraries detection
                js_libraries = {
                    'jQuery': ['jquery'],
                    'React': ['react'],
                    'Angular': ['angular'],
                    'Vue.js': ['vue'],
                    'Bootstrap': ['bootstrap'],
                    'D3.js': ['d3.js', 'd3.min.js']
                }
                
                for lib, patterns in js_libraries.items():
                    if any(pattern in content.lower() for pattern in patterns):
                        technologies["javascript_libraries"].append(lib)
                
                # Analytics detection
                analytics_patterns = {
                    'Google Analytics': ['google-analytics', 'gtag', 'ga.js'],
                    'Adobe Analytics': ['adobe', 'omniture'],
                    'Hotjar': ['hotjar'],
                    'Mixpanel': ['mixpanel']
                }
                
                for analytics, patterns in analytics_patterns.items():
                    if any(pattern in content.lower() for pattern in patterns):
                        technologies["analytics"].append(analytics)
                
                # Security tools detection
                security_patterns = {
                    'Cloudflare': ['cloudflare', 'cf-ray'],
                    'ModSecurity': ['mod_security', 'modsecurity'],
                    'Sucuri': ['sucuri'],
                    'Incapsula': ['incapsula']
                }
                
                for security, patterns in security_patterns.items():
                    if any(pattern in content.lower() or pattern in str(headers).lower() for pattern in patterns):
                        technologies["security_tools"].append(security)
                
        except Exception as e:
            logger.debug(f"Technology fingerprinting error: {e}")
        
        logger.info(f"🔍 Technologies identified: {technologies['cms']}, {technologies['programming_language']}")
        return technologies

    async def _discover_endpoints_advanced(self, target: str) -> List[str]:
        """Advanced endpoint discovery"""
        endpoints = set()
        base_url = f"https://{target}"
        
        # Method 1: Directory bruteforcing
        logger.info("📁 Directory bruteforcing")
        dir_endpoints = await self._bruteforce_directories(base_url)
        endpoints.update(dir_endpoints)
        
        # Method 2: File extension bruteforcing
        logger.info("📄 File extension bruteforcing")
        file_endpoints = await self._bruteforce_files(base_url)
        endpoints.update(file_endpoints)
        
        # Method 3: Robots.txt and sitemap.xml parsing
        logger.info("🤖 Robots.txt and sitemap analysis")
        robot_endpoints = await self._parse_robots_sitemap(base_url)
        endpoints.update(robot_endpoints)
        
        # Method 4: JavaScript file analysis
        logger.info("📜 JavaScript file analysis")
        js_endpoints = await self._analyze_javascript_files(base_url)
        endpoints.update(js_endpoints)
        
        # Method 5: API endpoint discovery
        logger.info("🔌 API endpoint discovery")
        api_endpoints = await self._discover_api_endpoints(base_url)
        endpoints.update(api_endpoints)
        
        logger.info(f"📁 Discovered {len(endpoints)} endpoints")
        return list(endpoints)

    async def _bruteforce_directories(self, base_url: str) -> List[str]:
        """Bruteforce directories"""
        endpoints = []
        
        tasks = []
        for directory in self.directory_wordlist:
            url = f"{base_url}/{directory}"
            tasks.append(self._check_endpoint_exists(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                endpoints.append(f"{base_url}/{self.directory_wordlist[i]}")
        
        return endpoints

    async def _bruteforce_files(self, base_url: str) -> List[str]:
        """Bruteforce files with extensions"""
        endpoints = []
        
        # Common filenames
        common_files = [
            "index", "admin", "login", "config", "backup", "test", "info",
            "phpinfo", "readme", "changelog", "license", "install"
        ]
        
        tasks = []
        for filename in common_files:
            for ext in self.file_extensions[:10]:  # Limit to first 10 extensions
                url = f"{base_url}/{filename}{ext}"
                tasks.append(self._check_endpoint_exists(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                file_idx = i // 10
                ext_idx = i % 10
                endpoints.append(f"{base_url}/{common_files[file_idx]}{self.file_extensions[ext_idx]}")
        
        return endpoints

    async def _parse_robots_sitemap(self, base_url: str) -> List[str]:
        """Parse robots.txt and sitemap.xml"""
        endpoints = []
        
        # Check robots.txt
        try:
            async with self.session.get(f"{base_url}/robots.txt", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract disallowed paths
                    for line in content.split('\n'):
                        if line.strip().startswith('Disallow:'):
                            path = line.split(':', 1)[1].strip()
                            if path and path != '/':
                                endpoints.append(f"{base_url}{path}")
                        elif line.strip().startswith('Sitemap:'):
                            sitemap_url = line.split(':', 1)[1].strip()
                            endpoints.append(sitemap_url)
                            
        except Exception as e:
            logger.debug(f"Robots.txt parsing error: {e}")
        
        # Check sitemap.xml
        try:
            async with self.session.get(f"{base_url}/sitemap.xml", timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract URLs from sitemap
                    import re
                    urls = re.findall(r'<loc>(.*?)</loc>', content)
                    endpoints.extend(urls)
                    
        except Exception as e:
            logger.debug(f"Sitemap.xml parsing error: {e}")
        
        return endpoints

    async def _analyze_javascript_files(self, base_url: str) -> List[str]:
        """Analyze JavaScript files for endpoints"""
        endpoints = []
        
        try:
            # Get main page to find JS files
            async with self.session.get(base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Find JavaScript files
                    import re
                    js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', content)
                    
                    for js_file in js_files[:5]:  # Limit to first 5 JS files
                        if not js_file.startswith('http'):
                            js_url = urljoin(base_url, js_file)
                        else:
                            js_url = js_file
                        
                        try:
                            async with self.session.get(js_url, timeout=aiohttp.ClientTimeout(total=10)) as js_response:
                                if js_response.status == 200:
                                    js_content = await js_response.text()
                                    
                                    # Extract API endpoints from JS
                                    api_patterns = [
                                        r'["\'](/api/[^"\']*)["\']',
                                        r'["\']([^"\']*\.php[^"\']*)["\']',
                                        r'["\']([^"\']*\.asp[x]?[^"\']*)["\']',
                                        r'["\']([^"\']*\.jsp[^"\']*)["\']'
                                    ]
                                    
                                    for pattern in api_patterns:
                                        matches = re.findall(pattern, js_content)
                                        for match in matches:
                                            if match.startswith('/'):
                                                endpoints.append(f"{base_url}{match}")
                                            
                        except Exception as e:
                            logger.debug(f"JS file analysis error for {js_url}: {e}")
                            
        except Exception as e:
            logger.debug(f"JavaScript analysis error: {e}")
        
        return endpoints

    async def _discover_api_endpoints(self, base_url: str) -> List[str]:
        """Discover API endpoints"""
        endpoints = []
        
        # Common API paths
        api_paths = [
            "/api", "/api/v1", "/api/v2", "/api/v3",
            "/rest", "/rest/v1", "/rest/v2",
            "/graphql", "/graph",
            "/swagger", "/swagger-ui", "/swagger.json",
            "/openapi", "/openapi.json",
            "/docs", "/documentation"
        ]
        
        tasks = []
        for path in api_paths:
            url = f"{base_url}{path}"
            tasks.append(self._check_endpoint_exists(url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                endpoints.append(f"{base_url}{api_paths[i]}")
        
        return endpoints

    async def _check_endpoint_exists(self, url: str) -> bool:
        """Check if endpoint exists"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status < 400
        except:
            return False

    async def _analyze_ssl_certificates(self, target: str) -> Dict[str, Any]:
        """Analyze SSL certificates"""
        cert_info = {
            "subject": {},
            "issuer": {},
            "san": [],
            "valid_from": None,
            "valid_to": None,
            "signature_algorithm": None,
            "key_size": None,
            "vulnerabilities": []
        }
        
        try:
            domain = urlparse(f"https://{target}").netloc or target
            
            # Get certificate
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate information
                    cert_info["subject"] = dict(x[0] for x in cert.get('subject', []))
                    cert_info["issuer"] = dict(x[0] for x in cert.get('issuer', []))
                    cert_info["valid_from"] = cert.get('notBefore')
                    cert_info["valid_to"] = cert.get('notAfter')
                    
                    # Subject Alternative Names
                    for ext in cert.get('subjectAltName', []):
                        if ext[0] == 'DNS':
                            cert_info["san"].append(ext[1])
                    
                    # Check for common vulnerabilities
                    if cert.get('version', 0) < 3:
                        cert_info["vulnerabilities"].append("Old certificate version")
                    
                    # Check signature algorithm
                    # Note: This would require more detailed certificate parsing
                    
        except Exception as e:
            logger.debug(f"SSL certificate analysis error: {e}")
        
        return cert_info

    async def _assess_initial_vulnerabilities(self, target: str, endpoints: List[str], services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess initial vulnerabilities"""
        vulnerabilities = []
        
        # Check for common vulnerabilities
        vuln_checks = [
            self._check_missing_security_headers,
            self._check_default_credentials,
            self._check_information_disclosure,
            self._check_directory_traversal,
            self._check_sql_injection_basic,
            self._check_xss_basic
        ]
        
        for check in vuln_checks:
            try:
                vulns = await check(target, endpoints)
                vulnerabilities.extend(vulns)
            except Exception as e:
                logger.debug(f"Vulnerability check error: {e}")
        
        logger.info(f"🎯 Found {len(vulnerabilities)} initial vulnerabilities")
        return vulnerabilities

    async def _check_missing_security_headers(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Check for missing security headers"""
        vulnerabilities = []
        
        try:
            async with self.session.get(f"https://{target}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                headers = response.headers
                
                security_headers = {
                    'Strict-Transport-Security': 'HSTS not implemented',
                    'X-Frame-Options': 'Clickjacking protection missing',
                    'X-XSS-Protection': 'XSS protection disabled',
                    'X-Content-Type-Options': 'MIME sniffing protection missing',
                    'Content-Security-Policy': 'CSP not implemented',
                    'Referrer-Policy': 'Referrer policy not set'
                }
                
                for header, description in security_headers.items():
                    if header not in headers:
                        vulnerabilities.append({
                            "type": "missing_security_header",
                            "header": header,
                            "description": description,
                            "severity": "medium",
                            "endpoint": f"https://{target}"
                        })
                        
        except Exception as e:
            logger.debug(f"Security headers check error: {e}")
        
        return vulnerabilities

    async def _check_default_credentials(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Check for default credentials"""
        vulnerabilities = []
        
        # Common default credentials
        default_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("root", "root"),
            ("test", "test")
        ]
        
        # Look for login endpoints
        login_endpoints = [ep for ep in endpoints if any(keyword in ep.lower() for keyword in ['login', 'admin', 'signin'])]
        
        for endpoint in login_endpoints[:3]:  # Check first 3 login endpoints
            for username, password in default_creds:
                try:
                    data = {
                        'username': username,
                        'password': password,
                        'user': username,
                        'pass': password
                    }
                    
                    async with self.session.post(endpoint, data=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        
                        # Check for successful login indicators
                        success_indicators = ['dashboard', 'welcome', 'logout', 'profile']
                        if any(indicator in content.lower() for indicator in success_indicators):
                            vulnerabilities.append({
                                "type": "default_credentials",
                                "username": username,
                                "password": password,
                                "endpoint": endpoint,
                                "severity": "high"
                            })
                            
                except Exception as e:
                    logger.debug(f"Default credentials check error: {e}")
        
        return vulnerabilities

    async def _check_information_disclosure(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Check for information disclosure"""
        vulnerabilities = []
        
        # Information disclosure endpoints
        info_endpoints = [
            "/.env", "/config.php", "/phpinfo.php", "/info.php",
            "/server-status", "/server-info", "/.git/config",
            "/backup.sql", "/database.sql", "/web.config"
        ]
        
        base_url = f"https://{target}"
        
        for endpoint in info_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for sensitive information
                        sensitive_patterns = [
                            'password', 'secret', 'key', 'token', 'api_key',
                            'database', 'mysql', 'postgres', 'mongodb'
                        ]
                        
                        if any(pattern in content.lower() for pattern in sensitive_patterns):
                            vulnerabilities.append({
                                "type": "information_disclosure",
                                "endpoint": url,
                                "description": f"Sensitive information exposed at {endpoint}",
                                "severity": "medium"
                            })
                            
            except Exception as e:
                logger.debug(f"Information disclosure check error: {e}")
        
        return vulnerabilities

    async def _check_directory_traversal(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Check for directory traversal vulnerabilities"""
        vulnerabilities = []
        
        # Directory traversal payloads
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for endpoint in endpoints[:5]:  # Check first 5 endpoints
            for payload in traversal_payloads:
                try:
                    # Test as GET parameter
                    test_url = f"{endpoint}?file={payload}"
                    async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        
                        # Check for successful traversal
                        if "root:" in content or "administrator" in content.lower():
                            vulnerabilities.append({
                                "type": "directory_traversal",
                                "endpoint": endpoint,
                                "payload": payload,
                                "method": "GET",
                                "severity": "high"
                            })
                            
                except Exception as e:
                    logger.debug(f"Directory traversal check error: {e}")
        
        return vulnerabilities

    async def _check_sql_injection_basic(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Basic SQL injection check"""
        vulnerabilities = []
        
        # SQL injection payloads
        sql_payloads = [
            "'",
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--"
        ]
        
        for endpoint in endpoints[:5]:  # Check first 5 endpoints
            for payload in sql_payloads:
                try:
                    # Test as GET parameter
                    test_url = f"{endpoint}?id={payload}"
                    async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        
                        # Check for SQL error messages
                        sql_errors = [
                            "mysql", "sql syntax", "ora-", "postgresql",
                            "sqlite", "mssql", "odbc", "jdbc"
                        ]
                        
                        if any(error in content.lower() for error in sql_errors):
                            vulnerabilities.append({
                                "type": "sql_injection",
                                "endpoint": endpoint,
                                "payload": payload,
                                "method": "GET",
                                "severity": "high"
                            })
                            
                except Exception as e:
                    logger.debug(f"SQL injection check error: {e}")
        
        return vulnerabilities

    async def _check_xss_basic(self, target: str, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Basic XSS check"""
        vulnerabilities = []
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>"
        ]
        
        for endpoint in endpoints[:5]:  # Check first 5 endpoints
            for payload in xss_payloads:
                try:
                    # Test as GET parameter
                    test_url = f"{endpoint}?q={payload}"
                    async with self.session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        content = await response.text()
                        
                        # Check if payload is reflected
                        if payload in content:
                            vulnerabilities.append({
                                "type": "xss",
                                "endpoint": endpoint,
                                "payload": payload,
                                "method": "GET",
                                "severity": "medium"
                            })
                            
                except Exception as e:
                    logger.debug(f"XSS check error: {e}")
        
        return vulnerabilities

    async def _identify_social_engineering_vectors(self, target: str, technologies: Dict[str, Any]) -> List[str]:
        """Identify social engineering vectors"""
        vectors = []
        
        # Technology-based vectors
        if technologies.get("cms") == "WordPress":
            vectors.append("WordPress admin credential phishing")
            vectors.append("Fake WordPress plugin update notifications")
        
        if "email" in str(technologies).lower():
            vectors.append("Email-based phishing campaigns")
            vectors.append("Business email compromise (BEC)")
        
        # Generic vectors
        vectors.extend([
            "Fake login pages",
            "Social media impersonation",
            "Phone-based social engineering",
            "Physical security bypass",
            "USB drop attacks",
            "Watering hole attacks"
        ])
        
        return vectors

    async def _analyze_attack_surface(self, target: str, subdomains: List[str], open_ports: List[int], endpoints: List[str]) -> Dict[str, Any]:
        """Analyze attack surface"""
        attack_surface = {
            "total_subdomains": len(subdomains),
            "total_open_ports": len(open_ports),
            "total_endpoints": len(endpoints),
            "high_risk_ports": [],
            "exposed_services": [],
            "attack_vectors": []
        }
        
        # High-risk ports
        high_risk_ports = [21, 22, 23, 135, 139, 445, 1433, 3306, 3389, 5432, 6379, 27017]
        attack_surface["high_risk_ports"] = [port for port in open_ports if port in high_risk_ports]
        
        # Exposed services
        if 21 in open_ports:
            attack_surface["exposed_services"].append("FTP")
        if 22 in open_ports:
            attack_surface["exposed_services"].append("SSH")
        if 3306 in open_ports:
            attack_surface["exposed_services"].append("MySQL")
        if 5432 in open_ports:
            attack_surface["exposed_services"].append("PostgreSQL")
        
        # Attack vectors
        attack_surface["attack_vectors"] = [
            "Web application attacks",
            "Network service exploitation",
            "Social engineering",
            "Physical security bypass"
        ]
        
        if len(subdomains) > 10:
            attack_surface["attack_vectors"].append("Subdomain takeover")
        
        if len(attack_surface["high_risk_ports"]) > 0:
            attack_surface["attack_vectors"].append("Network service brute force")
        
        return attack_surface

    async def _calculate_risk_score(self, vulnerabilities: List[Dict[str, Any]], open_ports: List[int], services: Dict[str, Any], technologies: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-10)"""
        risk_score = 0.0
        
        # Vulnerability-based scoring
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            if severity == "critical":
                risk_score += 2.0
            elif severity == "high":
                risk_score += 1.5
            elif severity == "medium":
                risk_score += 1.0
            elif severity == "low":
                risk_score += 0.5
        
        # Port-based scoring
        high_risk_ports = [21, 22, 23, 135, 139, 445, 1433, 3306, 3389, 5432, 6379, 27017]
        risk_score += len([port for port in open_ports if port in high_risk_ports]) * 0.5
        
        # Service-based scoring
        total_services = sum(len(service_list) for service_list in services.values())
        risk_score += min(total_services * 0.1, 2.0)
        
        # Technology-based scoring
        if technologies.get("cms") in ["WordPress", "Drupal", "Joomla"]:
            risk_score += 0.5
        
        if technologies.get("programming_language") == "PHP":
            risk_score += 0.3
        
        # Cap at 10.0
        return min(risk_score, 10.0)

# Example usage
async def main():
    """Example usage of Advanced Reconnaissance Engine"""
    recon_engine = AdvancedReconnaissanceEngine()
    
    # Execute comprehensive reconnaissance
    result = await recon_engine.comprehensive_reconnaissance("example.com", deep_scan=True)
    
    print(json.dumps(asdict(result), indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())