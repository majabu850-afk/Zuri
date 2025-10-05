#!/usr/bin/env python3
"""
AEGIS-X Allegro System Test
Test the updated system with Allegro configuration
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.scope_validator import global_scope_validator
from core.rate_limiter import global_rate_limiter
from config.allegro_config import get_allegro_config, validate_target_scope

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("AEGIS-X.AllegroTest")

async def test_scope_validation():
    """Test scope validation functionality"""
    logger.info("🧪 Testing Scope Validation...")
    
    test_targets = [
        "api.allegro.pl.allegrosandbox.pl",  # Should be in-scope and priority
        "app.allegro.cz.allegrosandbox.pl",  # Should be in-scope
        "test.allegro.sk.allegrosandbox.pl", # Should be in-scope
        "api.allegro.pl",                    # Should be out-of-scope (production)
        "example.com",                       # Should be out-of-scope
        "admin.allegrogroup.com"             # Should be out-of-scope
    ]
    
    for target in test_targets:
        validation = global_scope_validator.validate_target(target)
        logger.info(f"Target: {target}")
        logger.info(f"  In-Scope: {validation['in_scope']}")
        logger.info(f"  Out-of-Scope: {validation['out_of_scope']}")
        logger.info(f"  Priority: {validation.get('priority', False)}")
        logger.info(f"  Reason: {validation['reason']}")
        logger.info("")
    
    # Generate scope report
    report = global_scope_validator.generate_scope_report()
    logger.info("📋 Scope Validation Report:")
    logger.info(report)

async def test_rate_limiting():
    """Test rate limiting functionality"""
    logger.info("🧪 Testing Rate Limiting...")
    
    # Set Allegro program
    global_rate_limiter.set_program("allegro")
    
    # Test rate limiting
    logger.info("Making 10 rapid requests to test rate limiting...")
    for i in range(10):
        start_time = asyncio.get_event_loop().time()
        await global_rate_limiter.wait_if_needed()
        end_time = asyncio.get_event_loop().time()
        
        wait_time = end_time - start_time
        logger.info(f"Request {i+1}: waited {wait_time:.3f} seconds")
    
    # Get rate limiting stats
    stats = global_rate_limiter.get_stats()
    logger.info("📊 Rate Limiting Stats:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

def test_allegro_config():
    """Test Allegro configuration"""
    logger.info("🧪 Testing Allegro Configuration...")
    
    config = get_allegro_config()
    
    logger.info("📋 Allegro Configuration:")
    logger.info(f"  Program: {config['program_name']}")
    logger.info(f"  Platform: {config['platform']}")
    logger.info(f"  Tier: {config['tier']}")
    logger.info(f"  Max Requests/sec: {config['max_requests_per_second']}")
    logger.info(f"  In-Scope Domains: {len(config['in_scope_domains'])}")
    logger.info(f"  Out-of-Scope Domains: {len(config['out_of_scope_domains'])}")
    logger.info(f"  Priority Targets: {len(config['priority_targets'])}")
    logger.info(f"  Vulnerability Categories: {len(config['vulnerability_categories'])}")
    
    # Test CVSS mapping
    test_scores = [2.5, 5.5, 8.0, 9.2, 9.8]
    logger.info("\n🎯 CVSS Score Testing:")
    for score in test_scores:
        from config.allegro_config import get_severity_from_cvss, get_reward_estimate
        severity = get_severity_from_cvss(score)
        reward = get_reward_estimate(severity)
        logger.info(f"  CVSS {score}: {severity} (€{reward['min']}-€{reward['max']})")

async def main():
    """Main test function"""
    logger.info("🚀 Starting AEGIS-X Allegro System Tests...")
    logger.info("=" * 60)
    
    try:
        # Test configuration
        test_allegro_config()
        logger.info("")
        
        # Test scope validation
        await test_scope_validation()
        logger.info("")
        
        # Test rate limiting
        await test_rate_limiting()
        logger.info("")
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())