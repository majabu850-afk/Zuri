#!/usr/bin/env python3
"""
AEGIS-X Allegro Bug Bounty Program Configuration
Specific configuration for Intigriti Allegro program compliance
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AllegroConfig:
    """Configuration for Allegro bug bounty program"""
    
    # Program Information
    program_name = "Allegro"
    platform = "Intigriti"
    tier = "Tier 2"
    
    # Scope Configuration
    in_scope_domains = [
        "*.allegro.pl.allegrosandbox.pl",
        "*.allegro.cz.allegrosandbox.pl", 
        "*.allegro.sk.allegrosandbox.pl"
    ]
    
    out_of_scope_domains = [
        "*.allegro.pl",
        "*.allegro.sk", 
        "*.allegro.cz",
        "*.allegrogroup.com"
    ]
    
    # High-Priority Targets
    priority_targets = [
        "api.allegro.pl.allegrosandbox.pl",
        "app.allegro.pl.allegrosandbox.pl",
        "admin.allegro.pl.allegrosandbox.pl",
        "mobile.allegro.pl.allegrosandbox.pl",
        "developer.allegro.pl.allegrosandbox.pl",
        "api.allegro.cz.allegrosandbox.pl",
        "app.allegro.cz.allegrosandbox.pl",
        "api.allegro.sk.allegrosandbox.pl",
        "app.allegro.sk.allegrosandbox.pl"
    ]
    
    # Rate Limiting Rules
    max_requests_per_second = 5
    user_agent_required = "@intigriti.me"
    automated_tooling_allowed = True
    sandbox_only = True
    
    # Reward Structure (EUR)
    reward_tiers = {
        "Low": {"min": 100, "max": 300},
        "Medium": {"min": 300, "max": 700},
        "High": {"min": 700, "max": 1500},
        "Critical": {"min": 1500, "max": 2500},
        "Exceptional": {"min": 2500, "max": 3500}
    }
    
    # CVSS Score Mapping
    cvss_mapping = {
        "Low": {"min": 0.1, "max": 3.9},
        "Medium": {"min": 4.0, "max": 6.9},
        "High": {"min": 7.0, "max": 8.9},
        "Critical": {"min": 9.0, "max": 9.4},
        "Exceptional": {"min": 9.5, "max": 10.0}
    }
    
    # Testing Guidelines
    testing_rules = {
        "respect_rate_limits": True,
        "use_required_user_agent": True,
        "test_sandbox_only": True,
        "avoid_destructive_tests": True,
        "anonymize_data": True,
        "delete_gathered_data": True,
        "one_vulnerability_per_report": True,
        "detailed_reproduction_steps": True
    }
    
    # Vulnerability Categories
    vulnerability_categories = [
        "Cross-Site Scripting (XSS)",
        "SQL Injection",
        "Remote Code Execution (RCE)",
        "Server-Side Request Forgery (SSRF)",
        "Local File Inclusion (LFI)",
        "Authentication Bypass",
        "Authorization Flaws",
        "Business Logic Flaws",
        "Information Disclosure",
        "File Upload Vulnerabilities",
        "CORS Misconfigurations",
        "Security Header Issues",
        "API Security Issues",
        "Session Management Flaws",
        "Cryptographic Issues"
    ]
    
    # Excluded Vulnerability Types
    excluded_vulnerabilities = [
        "Self-XSS",
        "Clickjacking on pages without sensitive actions",
        "Missing security headers without demonstrated impact",
        "Logout CSRF",
        "Username enumeration",
        "Password policy issues",
        "Missing CAPTCHA",
        "Social engineering attacks",
        "Physical attacks",
        "Denial of Service (DoS)",
        "Brute force attacks"
    ]
    
    # Report Template Requirements
    report_requirements = {
        "title": "Clear, concise vulnerability title",
        "severity": "CVSS v3.1 score with justification",
        "description": "Detailed technical description",
        "impact": "Business impact assessment",
        "reproduction_steps": "Step-by-step reproduction guide",
        "proof_of_concept": "Working PoC code/screenshots",
        "remediation": "Specific remediation recommendations",
        "references": "Relevant security references"
    }
    
    # Compliance Checks
    compliance_checks = [
        "verify_in_scope",
        "check_rate_limits",
        "validate_user_agent",
        "confirm_sandbox_environment",
        "ensure_non_destructive",
        "verify_vulnerability_uniqueness",
        "validate_cvss_score",
        "check_report_completeness"
    ]

def get_allegro_config() -> Dict[str, Any]:
    """Get Allegro configuration as dictionary"""
    config = AllegroConfig()
    return {
        "program_name": config.program_name,
        "platform": config.platform,
        "tier": config.tier,
        "in_scope_domains": config.in_scope_domains,
        "out_of_scope_domains": config.out_of_scope_domains,
        "priority_targets": config.priority_targets,
        "max_requests_per_second": config.max_requests_per_second,
        "user_agent_required": config.user_agent_required,
        "automated_tooling_allowed": config.automated_tooling_allowed,
        "sandbox_only": config.sandbox_only,
        "reward_tiers": config.reward_tiers,
        "cvss_mapping": config.cvss_mapping,
        "testing_rules": config.testing_rules,
        "vulnerability_categories": config.vulnerability_categories,
        "excluded_vulnerabilities": config.excluded_vulnerabilities,
        "report_requirements": config.report_requirements,
        "compliance_checks": config.compliance_checks
    }

def validate_target_scope(target: str) -> Dict[str, Any]:
    """Validate if target is in scope for Allegro program"""
    config = AllegroConfig()
    
    result = {
        "in_scope": False,
        "out_of_scope": False,
        "priority": False,
        "reason": ""
    }
    
    # First check if target is in scope (sandbox domains)
    for in_domain in config.in_scope_domains:
        domain_pattern = in_domain.replace("*.", "")
        if domain_pattern in target:
            result["in_scope"] = True
            result["reason"] = f"Target matches in-scope domain: {in_domain}"
            
            # Check if it's a priority target
            if target in config.priority_targets:
                result["priority"] = True
                result["reason"] += " (Priority target)"
            
            return result
    
    # If not in scope, check if it's explicitly out of scope (production domains)
    for out_domain in config.out_of_scope_domains:
        domain_pattern = out_domain.replace("*.", "")
        if domain_pattern in target and "allegrosandbox.pl" not in target:
            result["out_of_scope"] = True
            result["reason"] = f"Target matches out-of-scope domain: {out_domain}"
            return result
    
    result["reason"] = "Target does not match any scope patterns"
    return result

def get_severity_from_cvss(cvss_score: float) -> str:
    """Get severity level from CVSS score"""
    config = AllegroConfig()
    
    for severity, score_range in config.cvss_mapping.items():
        if score_range["min"] <= cvss_score <= score_range["max"]:
            return severity
    
    return "Unknown"

def get_reward_estimate(severity: str) -> Dict[str, int]:
    """Get reward estimate for severity level"""
    config = AllegroConfig()
    
    if severity in config.reward_tiers:
        return config.reward_tiers[severity]
    
    return {"min": 0, "max": 0}