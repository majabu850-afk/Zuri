#!/usr/bin/env python3
"""
AEGIS-X Rate Limiter
Ensures compliance with bug bounty program rate limits
"""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("AEGIS-X.RateLimiter")

@dataclass
class RateLimitConfig:
    """Rate limit configuration for different programs"""
    max_requests_per_second: float
    max_requests_per_minute: int
    max_requests_per_hour: int
    burst_limit: int
    cooldown_period: float

class RateLimiter:
    """
    Advanced rate limiter for ethical bug bounty testing
    """
    
    def __init__(self):
        self.request_history = []
        self.last_request_time = 0
        
        # Program-specific rate limits
        self.program_limits = {
            "allegro": RateLimitConfig(
                max_requests_per_second=5.0,
                max_requests_per_minute=300,
                max_requests_per_hour=18000,
                burst_limit=10,
                cooldown_period=0.2
            ),
            "default": RateLimitConfig(
                max_requests_per_second=2.0,
                max_requests_per_minute=120,
                max_requests_per_hour=7200,
                burst_limit=5,
                cooldown_period=0.5
            )
        }
        
        self.current_program = "default"
    
    def set_program(self, program_name: str):
        """Set the current bug bounty program for rate limiting"""
        self.current_program = program_name.lower()
        if self.current_program not in self.program_limits:
            self.current_program = "default"
        
        logger.info(f"🚦 Rate limiter configured for program: {self.current_program}")
    
    async def wait_if_needed(self) -> None:
        """Wait if necessary to comply with rate limits"""
        current_time = time.time()
        config = self.program_limits[self.current_program]
        
        # Clean old requests from history
        self._clean_request_history(current_time)
        
        # Check if we need to wait
        if self._should_wait(current_time, config):
            wait_time = self._calculate_wait_time(current_time, config)
            if wait_time > 0:
                logger.debug(f"⏳ Rate limiting: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_history.append(current_time)
        self.last_request_time = current_time
    
    def _clean_request_history(self, current_time: float):
        """Remove old requests from history"""
        # Keep only requests from the last hour
        cutoff_time = current_time - 3600
        self.request_history = [t for t in self.request_history if t > cutoff_time]
    
    def _should_wait(self, current_time: float, config: RateLimitConfig) -> bool:
        """Check if we should wait before making a request"""
        # Check minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < (1.0 / config.max_requests_per_second):
            return True
        
        # Check requests per minute
        minute_ago = current_time - 60
        requests_last_minute = len([t for t in self.request_history if t > minute_ago])
        if requests_last_minute >= config.max_requests_per_minute:
            return True
        
        # Check requests per hour
        hour_ago = current_time - 3600
        requests_last_hour = len([t for t in self.request_history if t > hour_ago])
        if requests_last_hour >= config.max_requests_per_hour:
            return True
        
        return False
    
    def _calculate_wait_time(self, current_time: float, config: RateLimitConfig) -> float:
        """Calculate how long to wait"""
        wait_times = []
        
        # Wait for minimum time between requests
        time_since_last = current_time - self.last_request_time
        min_wait = (1.0 / config.max_requests_per_second) - time_since_last
        if min_wait > 0:
            wait_times.append(min_wait)
        
        # Wait for minute limit
        minute_ago = current_time - 60
        requests_last_minute = [t for t in self.request_history if t > minute_ago]
        if len(requests_last_minute) >= config.max_requests_per_minute:
            oldest_in_minute = min(requests_last_minute)
            wait_for_minute = 60 - (current_time - oldest_in_minute)
            if wait_for_minute > 0:
                wait_times.append(wait_for_minute)
        
        # Wait for hour limit
        hour_ago = current_time - 3600
        requests_last_hour = [t for t in self.request_history if t > hour_ago]
        if len(requests_last_hour) >= config.max_requests_per_hour:
            oldest_in_hour = min(requests_last_hour)
            wait_for_hour = 3600 - (current_time - oldest_in_hour)
            if wait_for_hour > 0:
                wait_times.append(wait_for_hour)
        
        return max(wait_times) if wait_times else 0
    
    def get_stats(self) -> Dict[str, any]:
        """Get current rate limiting statistics"""
        current_time = time.time()
        self._clean_request_history(current_time)
        
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        requests_last_minute = len([t for t in self.request_history if t > minute_ago])
        requests_last_hour = len([t for t in self.request_history if t > hour_ago])
        
        config = self.program_limits[self.current_program]
        
        return {
            "program": self.current_program,
            "requests_last_minute": requests_last_minute,
            "requests_last_hour": requests_last_hour,
            "minute_limit": config.max_requests_per_minute,
            "hour_limit": config.max_requests_per_hour,
            "requests_per_second_limit": config.max_requests_per_second,
            "time_since_last_request": current_time - self.last_request_time
        }

# Global rate limiter instance
global_rate_limiter = RateLimiter()