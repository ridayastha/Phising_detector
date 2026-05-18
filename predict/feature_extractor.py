import re
import ssl
import socket
import whois
from datetime import datetime, timezone
from urllib.parse import urlparse
import tldextract
from django.core.cache import cache

def extract_features(url):
    """Main function: returns dict of all features"""
    features = {}
    
    # 1. URL pattern analysis
    features.update(extract_url_patterns(url))
    
    # 2. Domain age (WHOIS)
    features.update(extract_domain_age(url))
    
    # 3. SSL check
    features.update(extract_ssl_info(url))
    
    return features

def extract_url_patterns(url):
    parsed = urlparse(url)
    hostname = parsed.netloc or parsed.path.split('/')[0]
    
    # URL length
    url_len = len(url)
    
    # Count special characters
    special_chars = sum(1 for c in url if c in '@-_.?=')
    
    # Contains IP address?
    has_ip = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname))
    
    # Number of subdomains
    extracted = tldextract.extract(hostname)
    subdomain = extracted.subdomain
    num_subdomains = len(subdomain.split('.')) if subdomain else 0
    
    # Contains suspicious keywords
    suspicious_keywords = ['login', 'verify', 'account', 'secure', 'signin', 'bank', 'paypal', 'confirm']
    contains_keyword = any(keyword in url.lower() for keyword in suspicious_keywords)
    
    # Using URL shortener (common domains)
    shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly']
    using_shortener = any(shortener in hostname for shortener in shorteners)
    
    # TLD rank (simplified – we'll map common TLDs to numeric rank)
    tld = extracted.suffix
    tld_rank = tld_rank_map(tld)
    
    return {
        'url_length': url_len,
        'num_special_chars': special_chars,
        'has_ip': has_ip,
        'num_subdomains': num_subdomains,
        'contains_keyword': contains_keyword,
        'using_shortener': using_shortener,
        'tld_rank': tld_rank,
    }

def tld_rank_map(tld):
    # Higher rank = more trustworthy (simplified)
    common_tlds = {'com': 5, 'org': 5, 'net': 4, 'edu': 5, 'gov': 5, 'co': 3, 'io': 2, 'info': 1}
    return common_tlds.get(tld, 0)

def extract_domain_age(url):
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        domain = domain.split(':')[0]
        
        # Try cache first
        cache_key = f"whois_age_{domain}"
        cached_age = cache.get(cache_key)
        if cached_age is not None:
            return {'domain_age_days': cached_age}
        # If not cached, perform WHOIS
        try:
            w = whois.whois(domain)
            if w.creation_date:
                creation = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                if isinstance(creation, datetime):
                    age_days = (datetime.now(timezone.utc) - creation).days
                else:
                    age_days =  (datetime.now(timezone.utc) - datetime.combine(creation, datetime.min.time())).days
            else:
                age_days = -1
        except Exception:
            age_days = -1
        
        # Store in cache for 24 hours (86400 seconds)
        cache.set(cache_key, age_days, 86400)
        return {'domain_age_days': age_days}


def extract_ssl_info(url):
    parsed = urlparse(url)
    hostname = parsed.netloc or parsed.path.split('/')[0]
    hostname = hostname.split(':')[0]
    
    ssl_valid = False
    days_remaining = 0
    
    if parsed.scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        ssl_valid = True
                        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_remaining = (expiry - datetime.now()).days
        except Exception:
            ssl_valid = False
            days_remaining = 0
    else:
        # Non-HTTPS URL: no SSL
        ssl_valid = False
        days_remaining = 0
    
    return {
        'ssl_valid': ssl_valid,
        'ssl_days_remaining': days_remaining,
    }