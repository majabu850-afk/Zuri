#!/usr/bin/env python3
"""
AEGIS-X Scope Validator
Ensures all testing stays within authorized bug bounty program scope
"""

import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from config.allegro_config import get_allegro_config, validate_target_scope

logger = logging.getLogger("AEGIS-X.ScopeValidator")

class ScopeValidator:
    """
    Validates targets against bug bounty program scope
    Prevents testing of out-of-scope targets
    """
    
    def __init__(self):
        self.allegro_config = get_allegro_config()
        self.validated_targets = {}
        self.blocked_targets = set()
        
        logger.info("🛡️ Scope Validator initialized")
    
    def validate_target(self, target: str) -> Dict[str, Any]:
        """
        Validate if target is within authorized scope
        """
        # Normalize target URL
        normalized_target = self._normalize_target(target)
        
        # Check cache first
        if normalized_target in self.validated_targets:
            return self.validated_targets[normalized_target]
        
        # Validate against Allegro scope
        validation_result = validate_target_scope(normalized_target)
        
        # Add additional validation logic
        validation_result.update({
            "normalized_target": normalized_target,
            "original_target": target,
            "validation_timestamp": self._get_timestamp(),
            "program": "Allegro",
            "platform": "Intigriti"
        })
        
        # Cache result
        self.validated_targets[normalized_target] = validation_result
        
        # Block if out of scope
        if validation_result["out_of_scope"]:
            self.blocked_targets.add(normalized_target)
            logger.warning(f"🚫 Target blocked - OUT OF SCOPE: {target}")
            logger.warning(f"   Reason: {validation_result['reason']}")
        elif validation_result["in_scope"]:
            logger.info(f"✅ Target validated - IN SCOPE: {target}")
            if validation_result["priority"]:
                logger.info(f"⭐ Priority target identified: {target}")
        else:
            logger.warning(f"❓ Target scope unclear: {target}")
        
        return validation_result
    
    def is_target_allowed(self, target: str) -> bool:
        """
        Quick check if target is allowed for testing
        """
        validation = self.validate_target(target)
        return validation["in_scope"] and not validation["out_of_scope"]
    
    def get_priority_targets(self) -> List[str]:
        """
        Get list of high-priority targets
        """
        return self.allegro_config["priority_targets"]
    
    def filter_targets(self, targets: List[str]) -> Dict[str, List[str]]:
        """
        Filter targets into allowed and blocked lists
        """
        allowed = []
        blocked = []
        priority = []
        
        for target in targets:
            validation = self.validate_target(target)
            
            if validation["out_of_scope"]:
                blocked.append(target)
            elif validation["in_scope"]:
                allowed.append(target)
                if validation["priority"]:
                    priority.append(target)
            else:
                blocked.append(target)  # Block unclear targets for safety
        
        return {
            "allowed": allowed,
            "blocked": blocked,
            "priority": priority
        }
    
    def _normalize_target(self, target: str) -> str:
        """
        Normalize target URL for consistent validation
        """
        # Add protocol if missing
        if not target.startswith(('http://', 'https://')):
            target = f"https://{target}"
        
        # Parse URL
        parsed = urlparse(target)
        
        # Return normalized domain
        return parsed.netloc.lower()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_scope_summary(self) -> Dict[str, Any]:
        """
        Get summary of scope validation results
        """
        total_validated = len(self.validated_targets)
        in_scope_count = sum(1 for v in self.validated_targets.values() if v["in_scope"])
        out_of_scope_count = sum(1 for v in self.validated_targets.values() if v["out_of_scope"])
        priority_count = sum(1 for v in self.validated_targets.values() if v.get("priority", False))
        
        return {
            "total_targets_validated": total_validated,
            "in_scope_targets": in_scope_count,
            "out_of_scope_targets": out_of_scope_count,
            "priority_targets": priority_count,
            "blocked_targets": len(self.blocked_targets),
            "program": "Allegro",
            "platform": "Intigriti"
        }
    
    def generate_scope_report(self) -> str:
        """
        Generate a detailed scope validation report
        """
        summary = self.get_scope_summary()
        
        report = f"""
🛡️ AEGIS-X Scope Validation Report
=====================================

Program: {summary['program']} ({summary['platform']})
Validation Timestamp: {self._get_timestamp()}

📊 Validation Summary:
  Total Targets Validated: {summary['total_targets_validated']}
  ✅ In-Scope Targets: {summary['in_scope_targets']}
  🚫 Out-of-Scope Targets: {summary['out_of_scope_targets']}
  ⭐ Priority Targets: {summary['priority_targets']}
  🛑 Blocked Targets: {summary['blocked_targets']}

🎯 Scope Configuration:
  In-Scope Domains: {', '.join(self.allegro_config['in_scope_domains'])}
  Out-of-Scope Domains: {', '.join(self.allegro_config['out_of_scope_domains'])}
  Priority Targets: {len(self.allegro_config['priority_targets'])} configured

⚠️ Compliance Status: {'✅ COMPLIANT' if summary['out_of_scope_targets'] == 0 else '❌ NON-COMPLIANT'}

🔍 Detailed Validation Results:
"""
        
        for target, validation in self.validated_targets.items():
            status = "✅ IN-SCOPE" if validation["in_scope"] else "🚫 OUT-OF-SCOPE"
            priority = " ⭐ PRIORITY" if validation.get("priority", False) else ""
            report += f"  {status}{priority}: {target}\n"
            report += f"    Reason: {validation['reason']}\n"
        
        return report

# Global scope validator instance
global_scope_validator = ScopeValidator()