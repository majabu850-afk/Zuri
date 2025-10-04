#!/usr/bin/env python3
"""
AEGIS-X AI Agent Trainer
Advanced AI agent training with real-world bug bounty methodologies
"""

import json
import random
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class BugBountyMethodology:
    """Bug bounty methodology definition"""
    name: str
    category: str
    description: str
    steps: List[str]
    tools: List[str]
    payloads: List[str]
    indicators: List[str]
    success_criteria: List[str]
    difficulty: str  # Easy, Medium, Hard, Expert, Legendary
    cve_examples: List[str]
    real_world_examples: List[str]

@dataclass
class AgentKnowledge:
    """AI agent knowledge base"""
    methodologies: List[BugBountyMethodology]
    learned_patterns: Dict[str, Any]
    success_history: List[Dict[str, Any]]
    failure_analysis: List[Dict[str, Any]]
    adaptation_rules: List[Dict[str, Any]]

class AIAgentTrainer:
    """Advanced AI agent trainer with real-world methodologies"""
    
    def __init__(self):
        self.methodologies = self._initialize_methodologies()
        self.agent_knowledge = AgentKnowledge(
            methodologies=self.methodologies,
            learned_patterns={},
            success_history=[],
            failure_analysis=[],
            adaptation_rules=[]
        )
        self.training_scenarios = self._create_training_scenarios()
        
    def _initialize_methodologies(self) -> List[BugBountyMethodology]:
        """Initialize comprehensive bug bounty methodologies"""
        methodologies = []
        
        # SQL Injection Methodologies
        methodologies.extend([
            BugBountyMethodology(
                name="Advanced SQL Injection Discovery",
                category="Injection",
                description="Comprehensive SQL injection testing using error-based, blind, and time-based techniques",
                steps=[
                    "1. Identify all input parameters (GET, POST, Headers, Cookies)",
                    "2. Test for basic SQL injection with single quotes and double quotes",
                    "3. Analyze error messages for database type identification",
                    "4. Perform error-based injection using EXTRACTVALUE, UPDATEXML",
                    "5. Test boolean-based blind injection with conditional statements",
                    "6. Implement time-based blind injection with SLEEP, WAITFOR",
                    "7. Use UNION-based injection for data extraction",
                    "8. Test second-order SQL injection in stored data",
                    "9. Exploit advanced techniques like DNS exfiltration",
                    "10. Document findings with proof-of-concept"
                ],
                tools=["sqlmap", "burp suite", "custom scripts", "manual testing"],
                payloads=[
                    "' OR 1=1--", "' UNION SELECT NULL--", "' AND SLEEP(5)--",
                    "' AND EXTRACTVALUE(1, CONCAT(0x7e, version(), 0x7e))--",
                    "' OR (SELECT COUNT(*) FROM information_schema.tables)>0--"
                ],
                indicators=[
                    "Database error messages", "Time delays in responses",
                    "Different response lengths", "Conditional content changes"
                ],
                success_criteria=[
                    "Database error disclosure", "Data extraction successful",
                    "Time-based confirmation", "Boolean logic confirmation"
                ],
                difficulty="Expert",
                cve_examples=["CVE-2021-44228", "CVE-2020-1472", "CVE-2019-0708"],
                real_world_examples=[
                    "Equifax breach 2017", "Yahoo breach 2013-2014",
                    "Target breach 2013", "Sony Pictures hack 2014"
                ]
            ),
            BugBountyMethodology(
                name="NoSQL Injection Mastery",
                category="Injection",
                description="Advanced NoSQL injection techniques for MongoDB, CouchDB, and other NoSQL databases",
                steps=[
                    "1. Identify NoSQL database technology through fingerprinting",
                    "2. Test JSON parameter injection with $ne, $gt, $regex operators",
                    "3. Exploit MongoDB-specific operators like $where, $mapReduce",
                    "4. Test JavaScript injection in NoSQL contexts",
                    "5. Perform blind NoSQL injection using response timing",
                    "6. Extract data using $regex pattern matching",
                    "7. Test authentication bypass with NoSQL operators",
                    "8. Exploit aggregation pipeline vulnerabilities",
                    "9. Test for NoSQL injection in HTTP headers",
                    "10. Document with working proof-of-concept"
                ],
                tools=["NoSQLMap", "Burp Suite", "custom Python scripts"],
                payloads=[
                    '{"$ne": null}', '{"$regex": ".*"}', '{"$where": "1==1"}',
                    '{"$or": [{"username": {"$ne": null}}, {"password": {"$ne": null}}]}'
                ],
                indicators=[
                    "Different response structures", "Authentication bypass",
                    "Data leakage in responses", "Error messages revealing NoSQL"
                ],
                success_criteria=[
                    "Authentication bypass achieved", "Data extraction successful",
                    "NoSQL error messages obtained", "Blind injection confirmed"
                ],
                difficulty="Hard",
                cve_examples=["CVE-2021-32050", "CVE-2020-7928"],
                real_world_examples=["MongoDB Atlas vulnerabilities", "CouchDB RCE"]
            )
        ])
        
        # XSS Methodologies
        methodologies.extend([
            BugBountyMethodology(
                name="Advanced XSS Exploitation",
                category="Cross-Site Scripting",
                description="Comprehensive XSS testing including reflected, stored, DOM-based, and mutation XSS",
                steps=[
                    "1. Map all input vectors (parameters, headers, file uploads)",
                    "2. Test basic XSS payloads in different contexts",
                    "3. Analyze HTML context and identify injection points",
                    "4. Test JavaScript context injection with proper escaping",
                    "5. Exploit CSS context injection with expression() and url()",
                    "6. Test attribute context injection with event handlers",
                    "7. Perform DOM-based XSS testing with sources and sinks",
                    "8. Test stored XSS in all data storage locations",
                    "9. Exploit mutation XSS using browser parsing differences",
                    "10. Create weaponized payloads for maximum impact"
                ],
                tools=["XSS Hunter", "Burp Suite", "DOM Invader", "BeEF"],
                payloads=[
                    "<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
                    "javascript:alert(1)", "';alert(1);//", "\"><script>alert(1)</script>"
                ],
                indicators=[
                    "JavaScript execution", "Alert boxes", "DOM manipulation",
                    "Cookie theft", "Keylogger installation"
                ],
                success_criteria=[
                    "JavaScript execution confirmed", "Session hijacking possible",
                    "Data exfiltration achieved", "Persistent XSS established"
                ],
                difficulty="Medium",
                cve_examples=["CVE-2021-44228", "CVE-2020-6519"],
                real_world_examples=[
                    "Twitter XSS worm 2010", "MySpace Samy worm 2005",
                    "Facebook XSS 2018", "Google XSS bounties"
                ]
            ),
            BugBountyMethodology(
                name="DOM XSS Hunting",
                category="Cross-Site Scripting",
                description="Specialized DOM-based XSS discovery using source-sink analysis",
                steps=[
                    "1. Identify JavaScript sources (location.hash, document.URL, etc.)",
                    "2. Map dangerous sinks (innerHTML, eval, setTimeout, etc.)",
                    "3. Trace data flow from sources to sinks",
                    "4. Test URL fragment manipulation for DOM XSS",
                    "5. Exploit postMessage vulnerabilities",
                    "6. Test WebSocket message injection",
                    "7. Analyze client-side routing for XSS",
                    "8. Test JSONP callback manipulation",
                    "9. Exploit client-side template injection",
                    "10. Create automated DOM XSS scanner"
                ],
                tools=["DOM Invader", "Burp Suite", "custom JavaScript", "browser dev tools"],
                payloads=[
                    "#<script>alert(1)</script>", "#javascript:alert(1)",
                    "?callback=alert", "#<img src=x onerror=alert(1)>"
                ],
                indicators=[
                    "URL fragment execution", "PostMessage vulnerabilities",
                    "Client-side routing XSS", "JSONP callback injection"
                ],
                success_criteria=[
                    "DOM manipulation achieved", "Client-side code execution",
                    "Data exfiltration via DOM", "Persistent DOM XSS"
                ],
                difficulty="Hard",
                cve_examples=["CVE-2020-6519", "CVE-2019-8674"],
                real_world_examples=["Gmail DOM XSS", "Facebook DOM XSS", "Twitter DOM XSS"]
            )
        ])
        
        # SSRF Methodologies
        methodologies.extend([
            BugBountyMethodology(
                name="Server-Side Request Forgery Mastery",
                category="Server-Side Request Forgery",
                description="Advanced SSRF exploitation including cloud metadata, internal network scanning, and protocol smuggling",
                steps=[
                    "1. Identify URL parameters and file upload functionality",
                    "2. Test basic SSRF with localhost and 127.0.0.1",
                    "3. Bypass IP blacklists using decimal, octal, hex notation",
                    "4. Exploit cloud metadata endpoints (AWS, GCP, Azure)",
                    "5. Perform internal network reconnaissance",
                    "6. Test different protocols (file://, gopher://, dict://)",
                    "7. Chain SSRF with other vulnerabilities",
                    "8. Exploit blind SSRF using DNS exfiltration",
                    "9. Test SSRF in PDF generators and image processors",
                    "10. Document internal network architecture"
                ],
                tools=["Burp Suite", "SSRFmap", "Collaborator", "custom scripts"],
                payloads=[
                    "http://127.0.0.1:80/", "http://169.254.169.254/latest/meta-data/",
                    "file:///etc/passwd", "gopher://127.0.0.1:6379/_INFO"
                ],
                indicators=[
                    "Internal service responses", "Cloud metadata access",
                    "File system access", "Network service enumeration"
                ],
                success_criteria=[
                    "Internal network access", "Cloud metadata extraction",
                    "File system disclosure", "Service enumeration"
                ],
                difficulty="Hard",
                cve_examples=["CVE-2021-26855", "CVE-2019-19781"],
                real_world_examples=[
                    "Capital One breach 2019", "Shopify SSRF", "Slack SSRF"
                ]
            )
        ])
        
        # RCE Methodologies
        methodologies.extend([
            BugBountyMethodology(
                name="Remote Code Execution Mastery",
                category="Remote Code Execution",
                description="Advanced RCE exploitation through various vectors including deserialization, template injection, and command injection",
                steps=[
                    "1. Identify code execution vectors (file uploads, deserialization, etc.)",
                    "2. Test command injection in system calls",
                    "3. Exploit deserialization vulnerabilities",
                    "4. Test server-side template injection",
                    "5. Exploit file upload restrictions",
                    "6. Test code injection in eval() functions",
                    "7. Exploit expression language injection",
                    "8. Test remote file inclusion for RCE",
                    "9. Chain multiple vulnerabilities for RCE",
                    "10. Establish persistent access and document"
                ],
                tools=["ysoserial", "Burp Suite", "custom payloads", "reverse shells"],
                payloads=[
                    "; id", "$(id)", "`id`", "__import__('os').system('id')",
                    "{{7*7}}", "#{7*7}", "${7*7}"
                ],
                indicators=[
                    "Command output in response", "Time delays from commands",
                    "DNS lookups from target", "Reverse shell connections"
                ],
                success_criteria=[
                    "Command execution confirmed", "Reverse shell established",
                    "File system access", "Network connectivity"
                ],
                difficulty="Expert",
                cve_examples=["CVE-2021-44228", "CVE-2020-1472", "CVE-2019-0708"],
                real_world_examples=[
                    "Log4j RCE 2021", "Struts2 RCE", "Spring4Shell RCE"
                ]
            )
        ])
        
        # Authentication & Authorization
        methodologies.extend([
            BugBountyMethodology(
                name="Authentication Bypass Techniques",
                category="Authentication",
                description="Advanced authentication bypass including JWT attacks, OAuth flaws, and session management issues",
                steps=[
                    "1. Analyze authentication mechanisms (JWT, OAuth, SAML)",
                    "2. Test for default credentials and weak passwords",
                    "3. Exploit JWT vulnerabilities (algorithm confusion, key confusion)",
                    "4. Test OAuth implementation flaws",
                    "5. Exploit session management vulnerabilities",
                    "6. Test for privilege escalation",
                    "7. Exploit password reset vulnerabilities",
                    "8. Test multi-factor authentication bypasses",
                    "9. Exploit LDAP injection in authentication",
                    "10. Document complete authentication bypass"
                ],
                tools=["JWT.io", "Burp Suite", "custom scripts", "LDAP tools"],
                payloads=[
                    "admin:admin", "' OR '1'='1", "JWT algorithm none",
                    "OAuth redirect_uri manipulation"
                ],
                indicators=[
                    "Authentication bypass", "Privilege escalation",
                    "Session hijacking", "Token manipulation"
                ],
                success_criteria=[
                    "Admin access achieved", "User impersonation",
                    "Session fixation", "Token forgery"
                ],
                difficulty="Hard",
                cve_examples=["CVE-2020-1472", "CVE-2019-0708"],
                real_world_examples=[
                    "Okta authentication bypass", "Auth0 vulnerabilities",
                    "Microsoft AD vulnerabilities"
                ]
            )
        ])
        
        # Business Logic Flaws
        methodologies.extend([
            BugBountyMethodology(
                name="Business Logic Vulnerability Discovery",
                category="Business Logic",
                description="Advanced business logic flaw identification and exploitation",
                steps=[
                    "1. Map application workflow and business processes",
                    "2. Identify critical business functions (payments, transfers, etc.)",
                    "3. Test for race conditions in concurrent operations",
                    "4. Exploit price manipulation vulnerabilities",
                    "5. Test for workflow bypass opportunities",
                    "6. Exploit time-of-check vs time-of-use issues",
                    "7. Test for privilege escalation through business logic",
                    "8. Exploit rate limiting bypasses",
                    "9. Test for data validation bypasses",
                    "10. Document business impact and exploitation"
                ],
                tools=["Burp Suite", "custom scripts", "race condition tools"],
                payloads=["Concurrent requests", "Negative values", "Workflow manipulation"],
                indicators=[
                    "Unexpected application behavior", "Financial manipulation",
                    "Privilege escalation", "Data integrity issues"
                ],
                success_criteria=[
                    "Business process bypass", "Financial gain",
                    "Unauthorized access", "Data manipulation"
                ],
                difficulty="Legendary",
                cve_examples=["Business logic CVEs are rare"],
                real_world_examples=[
                    "Starbucks race condition", "Uber price manipulation",
                    "Banking transfer vulnerabilities"
                ]
            )
        ])
        
        # Zero-Day Discovery
        methodologies.extend([
            BugBountyMethodology(
                name="Zero-Day Vulnerability Research",
                category="Zero-Day",
                description="Advanced zero-day discovery through fuzzing, reverse engineering, and novel attack vectors",
                steps=[
                    "1. Perform comprehensive application fingerprinting",
                    "2. Analyze application binaries and source code",
                    "3. Implement custom fuzzing strategies",
                    "4. Research novel attack vectors and techniques",
                    "5. Analyze third-party components and dependencies",
                    "6. Test edge cases and boundary conditions",
                    "7. Exploit memory corruption vulnerabilities",
                    "8. Research protocol-level vulnerabilities",
                    "9. Develop proof-of-concept exploits",
                    "10. Responsible disclosure and documentation"
                ],
                tools=[
                    "IDA Pro", "Ghidra", "AFL fuzzer", "custom tools",
                    "Wireshark", "debuggers", "static analysis tools"
                ],
                payloads=["Custom fuzzing inputs", "Memory corruption payloads", "Protocol violations"],
                indicators=[
                    "Application crashes", "Memory corruption",
                    "Unexpected behavior", "Protocol violations"
                ],
                success_criteria=[
                    "Novel vulnerability discovered", "Exploit developed",
                    "CVE assigned", "Vendor acknowledgment"
                ],
                difficulty="Legendary",
                cve_examples=["CVE-2021-44228", "CVE-2020-1472", "CVE-2019-0708"],
                real_world_examples=[
                    "Log4Shell discovery", "BlueKeep discovery",
                    "Heartbleed discovery", "Spectre/Meltdown"
                ]
            )
        ])
        
        return methodologies
    
    def _create_training_scenarios(self) -> List[Dict[str, Any]]:
        """Create realistic training scenarios"""
        scenarios = [
            {
                "name": "E-commerce Platform Assessment",
                "description": "Comprehensive security assessment of an e-commerce platform",
                "target_types": ["web application", "API", "mobile app"],
                "expected_vulnerabilities": ["SQL injection", "XSS", "IDOR", "payment bypass"],
                "difficulty": "Medium",
                "time_limit": 120,  # minutes
                "success_criteria": {
                    "min_critical": 2,
                    "min_high": 5,
                    "min_medium": 10
                }
            },
            {
                "name": "Banking Application Penetration Test",
                "description": "High-security banking application assessment",
                "target_types": ["web application", "API", "mobile app"],
                "expected_vulnerabilities": ["authentication bypass", "business logic", "IDOR", "privilege escalation"],
                "difficulty": "Hard",
                "time_limit": 240,
                "success_criteria": {
                    "min_critical": 1,
                    "min_high": 3,
                    "min_medium": 8
                }
            },
            {
                "name": "Cloud Infrastructure Assessment",
                "description": "Cloud-native application security assessment",
                "target_types": ["cloud services", "containers", "APIs"],
                "expected_vulnerabilities": ["SSRF", "cloud metadata", "container escape", "IAM bypass"],
                "difficulty": "Expert",
                "time_limit": 180,
                "success_criteria": {
                    "min_critical": 3,
                    "min_high": 6,
                    "min_medium": 12
                }
            },
            {
                "name": "Zero-Day Research Challenge",
                "description": "Novel vulnerability discovery in complex applications",
                "target_types": ["binary analysis", "protocol research", "custom applications"],
                "expected_vulnerabilities": ["zero-day", "memory corruption", "protocol flaws"],
                "difficulty": "Legendary",
                "time_limit": 480,
                "success_criteria": {
                    "min_critical": 1,
                    "min_exceptional": 1
                }
            }
        ]
        return scenarios
    
    def train_agent(self, scenario_name: str = None) -> Dict[str, Any]:
        """Train AI agent with specific scenario"""
        if scenario_name:
            scenario = next((s for s in self.training_scenarios if s['name'] == scenario_name), None)
            if not scenario:
                logger.error(f"Training scenario not found: {scenario_name}")
                return {"success": False, "error": "Scenario not found"}
        else:
            scenario = random.choice(self.training_scenarios)
        
        logger.info(f"🎯 Starting agent training with scenario: {scenario['name']}")
        
        # Select relevant methodologies
        relevant_methodologies = self._select_methodologies_for_scenario(scenario)
        
        # Simulate training process
        training_results = self._simulate_training(scenario, relevant_methodologies)
        
        # Update agent knowledge
        self._update_agent_knowledge(training_results)
        
        return training_results
    
    def _select_methodologies_for_scenario(self, scenario: Dict[str, Any]) -> List[BugBountyMethodology]:
        """Select relevant methodologies for training scenario"""
        relevant = []
        expected_vulns = scenario.get('expected_vulnerabilities', [])
        
        for methodology in self.methodologies:
            # Check if methodology is relevant to expected vulnerabilities
            if any(vuln.lower() in methodology.name.lower() or 
                   vuln.lower() in methodology.category.lower() 
                   for vuln in expected_vulns):
                relevant.append(methodology)
        
        # Add some random methodologies for comprehensive training
        other_methodologies = [m for m in self.methodologies if m not in relevant]
        relevant.extend(random.sample(other_methodologies, min(3, len(other_methodologies))))
        
        return relevant
    
    def _simulate_training(self, scenario: Dict[str, Any], methodologies: List[BugBountyMethodology]) -> Dict[str, Any]:
        """Simulate agent training process with improved success rates"""
        results = {
            "scenario": scenario['name'],
            "start_time": datetime.now().isoformat(),
            "methodologies_used": len(methodologies),
            "vulnerabilities_found": [],
            "success_rate": 0.0,
            "learning_points": [],
            "adaptation_rules": []
        }
        
        # Enhanced vulnerability discovery simulation
        for methodology in methodologies:
            success_probability = self._calculate_enhanced_success_probability(methodology, scenario)
            
            # Multiple attempts per methodology for better coverage
            for attempt in range(3):  # 3 attempts per methodology
                if random.random() < success_probability:
                    # Successful vulnerability discovery
                    vuln = self._generate_simulated_vulnerability(methodology, scenario)
                results["vulnerabilities_found"].append(vuln)
                
                # Generate learning points
                learning_point = {
                    "methodology": methodology.name,
                    "technique": random.choice(methodology.steps),
                    "success_factor": random.choice([
                        "Proper payload encoding",
                        "Context-aware testing",
                        "Comprehensive parameter analysis",
                        "Advanced evasion techniques",
                        "Business logic understanding"
                    ]),
                    "timestamp": datetime.now().isoformat()
                }
                results["learning_points"].append(learning_point)
        
        # Calculate success rate
        expected_count = len(scenario.get('expected_vulnerabilities', []))
        found_count = len(results["vulnerabilities_found"])
        results["success_rate"] = min(found_count / max(expected_count, 1), 1.0) * 100
        
        # Generate adaptation rules
        if results["success_rate"] < 70:
            results["adaptation_rules"].append({
                "rule": "Increase payload diversity",
                "reason": "Low success rate indicates insufficient payload coverage",
                "action": "Add more evasion techniques and encoding variations"
            })
        
        if found_count > expected_count:
            results["adaptation_rules"].append({
                "rule": "Optimize methodology selection",
                "reason": "High discovery rate indicates effective techniques",
                "action": "Prioritize successful methodologies in future assessments"
            })
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    def _calculate_success_probability(self, methodology: BugBountyMethodology, scenario: Dict[str, Any]) -> float:
        """Calculate probability of successful vulnerability discovery"""
        base_probability = 0.3
        
        # Adjust based on methodology difficulty vs scenario difficulty
        difficulty_mapping = {"Easy": 1, "Medium": 2, "Hard": 3, "Expert": 4, "Legendary": 5}
        scenario_difficulty = difficulty_mapping.get(scenario.get('difficulty', 'Medium'), 2)
        method_difficulty = difficulty_mapping.get(methodology.difficulty, 2)
        
        if method_difficulty >= scenario_difficulty:
            base_probability += 0.3
        else:
            base_probability -= 0.2
        
        # Adjust based on relevance
        expected_vulns = scenario.get('expected_vulnerabilities', [])
        if any(vuln.lower() in methodology.name.lower() for vuln in expected_vulns):
            base_probability += 0.4
        
        return max(0.1, min(0.9, base_probability))
    
    def _calculate_enhanced_success_probability(self, methodology: BugBountyMethodology, scenario: Dict[str, Any]) -> float:
        """Calculate enhanced success probability with learning improvements"""
        base_probability = self._calculate_success_probability(methodology, scenario)
        
        # Learning enhancement factors
        learning_boost = 0.0
        
        # Historical success boost
        if self.agent_knowledge.success_history:
            recent_successes = [h for h in self.agent_knowledge.success_history[-10:] 
                              if h.get('success_rate', 0) > 50]
            if recent_successes:
                learning_boost += 0.2
        
        # Pattern recognition boost
        vuln_type = methodology.category.lower()
        if vuln_type in self.agent_knowledge.learned_patterns:
            pattern_data = self.agent_knowledge.learned_patterns[vuln_type]
            if pattern_data.get('success_count', 0) > 5:
                learning_boost += 0.15
        
        # Methodology expertise boost
        difficulty_multipliers = {
            "Easy": 1.2,
            "Medium": 1.0,
            "Hard": 0.8,
            "Expert": 0.6,
            "Legendary": 0.4
        }
        
        difficulty = methodology.difficulty
        base_probability *= difficulty_multipliers.get(difficulty, 1.0)
        
        # Apply learning boost
        enhanced_probability = base_probability + learning_boost
        
        return max(0.2, min(0.85, enhanced_probability))  # Better range for success
    
    def _generate_simulated_vulnerability(self, methodology: BugBountyMethodology, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simulated vulnerability discovery"""
        severity_weights = {
            "Easy": {"Low": 0.5, "Medium": 0.3, "High": 0.15, "Critical": 0.05},
            "Medium": {"Low": 0.3, "Medium": 0.4, "High": 0.25, "Critical": 0.05},
            "Hard": {"Low": 0.2, "Medium": 0.3, "High": 0.35, "Critical": 0.15},
            "Expert": {"Low": 0.1, "Medium": 0.2, "High": 0.4, "Critical": 0.3},
            "Legendary": {"Low": 0.05, "Medium": 0.15, "High": 0.3, "Critical": 0.4, "Exceptional": 0.1}
        }
        
        difficulty = scenario.get('difficulty', 'Medium')
        weights = severity_weights.get(difficulty, severity_weights['Medium'])
        
        severity = np.random.choice(list(weights.keys()), p=list(weights.values()))
        
        return {
            "id": f"vuln_{random.randint(1000, 9999)}",
            "type": methodology.category,
            "methodology": methodology.name,
            "severity": severity,
            "title": f"{methodology.category} in {scenario['name']}",
            "description": f"Discovered using {methodology.name} methodology",
            "payload": random.choice(methodology.payloads) if methodology.payloads else "N/A",
            "confidence": random.uniform(0.7, 0.95),
            "exploitability": random.uniform(0.6, 0.9),
            "discovered_at": datetime.now().isoformat()
        }
    
    def _update_agent_knowledge(self, training_results: Dict[str, Any]):
        """Update agent knowledge base with training results"""
        # Update success history
        self.agent_knowledge.success_history.append(training_results)
        
        # Update learned patterns
        for vuln in training_results["vulnerabilities_found"]:
            vuln_type = vuln["type"]
            if vuln_type not in self.agent_knowledge.learned_patterns:
                self.agent_knowledge.learned_patterns[vuln_type] = {
                    "success_count": 0,
                    "total_attempts": 0,
                    "effective_payloads": [],
                    "success_indicators": []
                }
            
            pattern = self.agent_knowledge.learned_patterns[vuln_type]
            pattern["success_count"] += 1
            pattern["total_attempts"] += 1
            
            if vuln["payload"] not in pattern["effective_payloads"]:
                pattern["effective_payloads"].append(vuln["payload"])
        
        # Update adaptation rules
        for rule in training_results["adaptation_rules"]:
            self.agent_knowledge.adaptation_rules.append(rule)
        
        # Keep only recent history (last 100 training sessions)
        if len(self.agent_knowledge.success_history) > 100:
            self.agent_knowledge.success_history = self.agent_knowledge.success_history[-100:]
    
    def get_agent_recommendations(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get AI agent recommendations for target assessment"""
        recommendations = []
        
        # Analyze target characteristics
        target_type = target_info.get('type', 'web application')
        technologies = target_info.get('technologies', [])
        complexity = target_info.get('complexity', 'medium')
        
        # Select methodologies based on learned patterns
        for methodology in self.methodologies:
            score = self._calculate_methodology_score(methodology, target_info)
            
            if score > 0.6:  # Threshold for recommendation
                recommendation = {
                    "methodology": methodology.name,
                    "category": methodology.category,
                    "score": score,
                    "priority": "High" if score > 0.8 else "Medium" if score > 0.7 else "Low",
                    "expected_success_rate": self._get_expected_success_rate(methodology),
                    "recommended_payloads": methodology.payloads[:5],  # Top 5 payloads
                    "key_indicators": methodology.indicators[:3]  # Top 3 indicators
                }
                recommendations.append(recommendation)
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _calculate_methodology_score(self, methodology: BugBountyMethodology, target_info: Dict[str, Any]) -> float:
        """Calculate methodology relevance score for target"""
        score = 0.5  # Base score
        
        # Check technology relevance
        technologies = target_info.get('technologies', [])
        for tech in technologies:
            if tech.lower() in methodology.description.lower():
                score += 0.2
        
        # Check historical success rate
        if methodology.category in self.agent_knowledge.learned_patterns:
            pattern = self.agent_knowledge.learned_patterns[methodology.category]
            if pattern["total_attempts"] > 0:
                success_rate = pattern["success_count"] / pattern["total_attempts"]
                score += success_rate * 0.3
        
        # Adjust based on target complexity
        complexity = target_info.get('complexity', 'medium')
        difficulty_mapping = {"Easy": 1, "Medium": 2, "Hard": 3, "Expert": 4, "Legendary": 5}
        complexity_score = difficulty_mapping.get(complexity.title(), 2)
        method_difficulty = difficulty_mapping.get(methodology.difficulty, 2)
        
        if abs(method_difficulty - complexity_score) <= 1:
            score += 0.2
        
        return min(1.0, score)
    
    def _get_expected_success_rate(self, methodology: BugBountyMethodology) -> float:
        """Get expected success rate for methodology"""
        if methodology.category in self.agent_knowledge.learned_patterns:
            pattern = self.agent_knowledge.learned_patterns[methodology.category]
            if pattern["total_attempts"] > 0:
                return pattern["success_count"] / pattern["total_attempts"]
        
        # Default success rates based on difficulty
        default_rates = {
            "Easy": 0.8,
            "Medium": 0.6,
            "Hard": 0.4,
            "Expert": 0.25,
            "Legendary": 0.1
        }
        
        return default_rates.get(methodology.difficulty, 0.5)
    
    def export_agent_knowledge(self, filepath: str):
        """Export agent knowledge to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(self.agent_knowledge), f, indent=2, default=str)
            logger.info(f"Agent knowledge exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export agent knowledge: {str(e)}")
    
    def import_agent_knowledge(self, filepath: str):
        """Import agent knowledge from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct AgentKnowledge object
            methodologies = [BugBountyMethodology(**m) for m in data['methodologies']]
            self.agent_knowledge = AgentKnowledge(
                methodologies=methodologies,
                learned_patterns=data['learned_patterns'],
                success_history=data['success_history'],
                failure_analysis=data['failure_analysis'],
                adaptation_rules=data['adaptation_rules']
            )
            
            logger.info(f"Agent knowledge imported from {filepath}")
        except Exception as e:
            logger.error(f"Failed to import agent knowledge: {str(e)}")
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get comprehensive training statistics"""
        total_sessions = len(self.agent_knowledge.success_history)
        total_vulns = sum(len(session["vulnerabilities_found"]) for session in self.agent_knowledge.success_history)
        
        if total_sessions == 0:
            return {"error": "No training sessions completed"}
        
        avg_success_rate = sum(session["success_rate"] for session in self.agent_knowledge.success_history) / total_sessions
        
        # Vulnerability type distribution
        vuln_types = {}
        for session in self.agent_knowledge.success_history:
            for vuln in session["vulnerabilities_found"]:
                vuln_type = vuln["type"]
                vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
        
        # Methodology effectiveness
        methodology_stats = {}
        for pattern_name, pattern_data in self.agent_knowledge.learned_patterns.items():
            if pattern_data["total_attempts"] > 0:
                methodology_stats[pattern_name] = {
                    "success_rate": pattern_data["success_count"] / pattern_data["total_attempts"],
                    "total_attempts": pattern_data["total_attempts"],
                    "effective_payloads": len(pattern_data["effective_payloads"])
                }
        
        return {
            "total_training_sessions": total_sessions,
            "total_vulnerabilities_found": total_vulns,
            "average_success_rate": avg_success_rate,
            "vulnerability_type_distribution": vuln_types,
            "methodology_effectiveness": methodology_stats,
            "total_methodologies": len(self.methodologies),
            "learned_patterns": len(self.agent_knowledge.learned_patterns),
            "adaptation_rules": len(self.agent_knowledge.adaptation_rules)
        }

# Initialize the AI agent trainer
if __name__ == "__main__":
    trainer = AIAgentTrainer()
    print(f"🤖 AI Agent Trainer initialized with {len(trainer.methodologies)} methodologies")
    
    # Run a sample training session
    results = trainer.train_agent("E-commerce Platform Assessment")
    print(f"🎯 Training completed: {results['vulnerabilities_found']} vulnerabilities found")
    print(f"📊 Success rate: {results['success_rate']:.1f}%")
    
    # Get training stats
    stats = trainer.get_training_stats()
    print(f"📈 Training Statistics: {stats}")