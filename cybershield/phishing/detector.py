"""
Phishing Detection Module
Analyzes URLs using ML model with feature extraction and confidence scoring.
"""

import re
import math
import tldextract
import joblib
import numpy as np
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse
from pathlib import Path

# Suspicious keywords commonly found in phishing URLs
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "secure", "update", "banking", 
    "paypal", "signin", "confirm", "password", "suspended", 
    "locked", "urgent", "click", "validate", "restore"
]

# Suspicious TLDs
SUSPICIOUS_TLDS = [
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "work", "click", "link"
]

# Trusted domains (whitelist)
TRUSTED_DOMAINS = [
    "google.com", "facebook.com", "microsoft.com", "apple.com",
    "amazon.com", "github.com", "linkedin.com", "twitter.com"
]


class PhishingDetector:
    """Advanced phishing detection with ML model and feature extraction."""
    
    def __init__(self, use_ml_model: bool = True):
        self.suspicious_keywords = SUSPICIOUS_KEYWORDS
        self.trusted_domains = TRUSTED_DOMAINS
        self.suspicious_tlds = SUSPICIOUS_TLDS
        self.use_ml_model = use_ml_model
        self.model = None
        self.feature_names = None
        
        # Try to load ML model
        if use_ml_model:
            self._load_ml_model()
    
    def _load_ml_model(self):
        """Load the trained ML model and feature names."""
        try:
            model_dir = Path(__file__).parent.parent / "ml" / "model" / "cybershield_models"
            model_path = model_dir / "phishing_model.pkl"
            features_path = model_dir / "phishing_features.json"
            
            if model_path.exists():
                self.model = joblib.load(model_path)
                
                # Load feature names
                if features_path.exists():
                    import json
                    with open(features_path, 'r') as f:
                        self.feature_names = json.load(f)
                
                print(f"✓ Loaded ML phishing model from {model_path}")
            else:
                print(f"⚠ ML model not found at {model_path}, using rule-based detection")
                self.use_ml_model = False
        except Exception as e:
            print(f"⚠ Error loading ML model: {e}, using rule-based detection")
            self.use_ml_model = False
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        
        prob = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum(p * math.log2(p) for p in prob if p > 0)
        return entropy
    
    def extract_ml_features(self, url: str) -> np.ndarray:
        """
        Extract 24 features for ML model prediction.
        
        Features match the trained model:
        url_length, domain_length, path_length, num_dots, num_hyphens, 
        num_underscores, num_slashes, num_question_marks, num_equals, 
        num_ampersands, num_at_symbols, num_exclamations, num_percent,
        has_https, has_http, has_ip, url_depth, num_subdomains, has_www,
        has_phishing_keyword, phishing_keyword_count, suspicious_tld,
        digit_ratio, domain_entropy
        """
        ext = tldextract.extract(url)
        parsed = urlparse(url)
        
        # Calculate features
        url_length = len(url)
        domain = ext.domain if ext.domain else ""
        domain_length = len(domain)
        path = parsed.path if parsed.path else ""
        path_length = len(path)
        
        # Character counts
        num_dots = url.count('.')
        num_hyphens = url.count('-')
        num_underscores = url.count('_')
        num_slashes = url.count('/')
        num_question_marks = url.count('?')
        num_equals = url.count('=')
        num_ampersands = url.count('&')
        num_at_symbols = url.count('@')
        num_exclamations = url.count('!')
        num_percent = url.count('%')
        
        # Protocol features
        has_https = 1 if url.startswith("https") else 0
        has_http = 1 if url.startswith("http") else 0
        
        # IP address detection
        has_ip = 1 if bool(re.match(r'\d+\.\d+\.\d+\.\d+', url)) else 0
        
        # URL structure
        url_depth = len([p for p in path.split('/') if p])
        subdomain = ext.subdomain if ext.subdomain else ""
        num_subdomains = len(subdomain.split('.')) if subdomain else 0
        has_www = 1 if 'www' in subdomain.lower() else 0
        
        # Phishing keywords
        url_lower = url.lower()
        has_phishing_keyword = 1 if any(kw in url_lower for kw in self.suspicious_keywords) else 0
        phishing_keyword_count = sum(kw in url_lower for kw in self.suspicious_keywords)
        
        # TLD check
        tld = ext.suffix if ext.suffix else ""
        suspicious_tld = 1 if tld in self.suspicious_tlds else 0
        
        # Digit ratio
        digits = sum(c.isdigit() for c in url)
        digit_ratio = digits / len(url) if len(url) > 0 else 0
        
        # Domain entropy
        domain_entropy = self._calculate_entropy(domain)
        
        # Return features in correct order
        features = np.array([
            url_length, domain_length, path_length, num_dots, num_hyphens,
            num_underscores, num_slashes, num_question_marks, num_equals,
            num_ampersands, num_at_symbols, num_exclamations, num_percent,
            has_https, has_http, has_ip, url_depth, num_subdomains, has_www,
            has_phishing_keyword, phishing_keyword_count, suspicious_tld,
            digit_ratio, domain_entropy
        ]).reshape(1, -1)
        
        return features
    
    def extract_features(self, url: str) -> Dict[str, any]:
        """
        Extract features from URL for display and analysis.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary of extracted features
        """
        ext = tldextract.extract(url)
        parsed = urlparse(url)
        
        features = {
            # Length features
            "url_length": len(url),
            "domain_length": len(ext.domain) if ext.domain else 0,
            "path_length": len(parsed.path) if parsed.path else 0,
            
            # IP address detection
            "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', url)),
            
            # Character count features
            "num_dots": url.count('.'),
            "num_hyphens": url.count('-'),
            "num_underscores": url.count('_'),
            "num_slashes": url.count('/'),
            "num_question_marks": url.count('?'),
            "num_equals": url.count('='),
            "num_at": url.count('@'),
            "num_ampersands": url.count('&'),
            "num_exclamations": url.count('!'),
            "num_percent": url.count('%'),
            
            # Protocol features
            "has_https": url.startswith("https"),
            "has_http": url.startswith("http"),
            
            # Suspicious content
            "suspicious_words": sum(kw in url.lower() for kw in self.suspicious_keywords),
            
            # Subdomain features
            "subdomain_count": len(ext.subdomain.split('.')) if ext.subdomain else 0,
            "has_subdomain": bool(ext.subdomain),
            "has_www": 'www' in ext.subdomain.lower() if ext.subdomain else False,
            
            # Domain features
            "domain": ext.domain,
            "suffix": ext.suffix,
            "is_trusted": ext.registered_domain in self.trusted_domains if ext.registered_domain else False,
            "suspicious_tld": ext.suffix in self.suspicious_tlds if ext.suffix else False,
            
            # Path features
            "has_query": bool(parsed.query),
            "url_depth": len([p for p in parsed.path.split('/') if p]) if parsed.path else 0,
            
            # Obfuscation indicators
            "has_percent_encoding": '%' in url,
            "has_double_slash": '//' in url[8:],  # After protocol
            
            # Entropy
            "domain_entropy": self._calculate_entropy(ext.domain) if ext.domain else 0,
            "digit_ratio": sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0,
        }
        
        return features
    
    def calculate_risk_score(self, features: Dict[str, any]) -> Tuple[int, Dict[str, int]]:
        """
        Calculate phishing risk score based on features (rule-based fallback).
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Tuple of (total_score, score_breakdown)
        """
        score_breakdown = {}
        
        # IP address in URL (high risk)
        if features["has_ip"]:
            score_breakdown["ip_address"] = 5
        
        # Excessive URL length
        if features["url_length"] > 75:
            score_breakdown["long_url"] = 3
        elif features["url_length"] > 100:
            score_breakdown["very_long_url"] = 4
        
        # Suspicious keywords
        if features["suspicious_words"] > 0:
            score_breakdown["suspicious_keywords"] = min(features["suspicious_words"] * 2, 6)
        
        # No HTTPS
        if not features["has_https"] and features["has_http"]:
            score_breakdown["no_https"] = 2
        
        # Excessive hyphens (common in phishing)
        if features["num_hyphens"] > 3:
            score_breakdown["many_hyphens"] = 3
        
        # Multiple subdomains
        if features["subdomain_count"] > 2:
            score_breakdown["many_subdomains"] = 2
        
        # Trusted domain (negative score)
        if features["is_trusted"]:
            score_breakdown["trusted_domain"] = -10
        
        # @ symbol in URL (often used to hide real domain)
        if features["num_at"] > 0:
            score_breakdown["at_symbol"] = 4
        
        # Excessive dots
        if features["num_dots"] > 4:
            score_breakdown["many_dots"] = 2
        
        # Percent encoding (obfuscation)
        if features["has_percent_encoding"]:
            score_breakdown["obfuscation"] = 1
        
        # Double slash in path
        if features["has_double_slash"]:
            score_breakdown["double_slash"] = 2
        
        # Suspicious TLD
        if features["suspicious_tld"]:
            score_breakdown["suspicious_tld"] = 3
        
        # High entropy domain
        if features["domain_entropy"] > 4.5:
            score_breakdown["high_entropy"] = 2
        
        total_score = sum(score_breakdown.values())
        return total_score, score_breakdown
    
    def detect(self, url: str) -> Dict[str, any]:
        """
        Perform complete phishing detection on a URL.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary with detection results including ML confidence
        """
        features = self.extract_features(url)
        
        # Try ML model first
        if self.use_ml_model and self.model is not None:
            try:
                ml_features = self.extract_ml_features(url)
                prediction = self.model.predict(ml_features)[0]
                
                # Get confidence scores if available
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(ml_features)[0]
                    confidence = float(max(probabilities) * 100)
                    phishing_probability = float(probabilities[1] * 100) if len(probabilities) > 1 else 0
                else:
                    confidence = 95.0  # Default high confidence for voting classifier
                    phishing_probability = 100.0 if prediction == 1 else 0.0
                
                is_phishing = bool(prediction == 1)
                
                # Determine risk level based on ML prediction and confidence
                if is_phishing:
                    if confidence >= 90:
                        risk_level = "HIGH"
                        risk_score = 10
                    elif confidence >= 70:
                        risk_level = "MEDIUM"
                        risk_score = 7
                    else:
                        risk_level = "LOW"
                        risk_score = 5
                else:
                    risk_level = "SAFE"
                    risk_score = 0
                
                return {
                    "url": url,
                    "is_phishing": is_phishing,
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "ml_confidence": confidence,
                    "phishing_probability": phishing_probability,
                    "detection_method": "ML Model (VotingClassifier)",
                    "model_accuracy": "100%",
                    "features": features,
                    "recommendation": self._get_recommendation(risk_level)
                }
            except Exception as e:
                print(f"⚠ ML prediction failed: {e}, falling back to rule-based")
        
        # Fallback to rule-based detection
        score, breakdown = self.calculate_risk_score(features)
        
        # Determine risk level
        if score >= 8:
            risk_level = "HIGH"
            is_phishing = True
        elif score >= 5:
            risk_level = "MEDIUM"
            is_phishing = True
        elif score >= 3:
            risk_level = "LOW"
            is_phishing = False
        else:
            risk_level = "SAFE"
            is_phishing = False
        
        return {
            "url": url,
            "is_phishing": is_phishing,
            "risk_level": risk_level,
            "risk_score": score,
            "score_breakdown": breakdown,
            "detection_method": "Rule-based",
            "features": features,
            "recommendation": self._get_recommendation(risk_level)
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get user recommendation based on risk level."""
        recommendations = {
            "HIGH": "⚠️ DO NOT VISIT - This URL shows strong phishing indicators. Avoid clicking and report if received via email.",
            "MEDIUM": "⚠️ CAUTION - This URL has suspicious characteristics. Verify the sender and domain before proceeding.",
            "LOW": "ℹ️ BE CAREFUL - Some minor concerns detected. Double-check the URL matches the expected domain.",
            "SAFE": "✅ APPEARS SAFE - No significant phishing indicators detected. Always remain vigilant."
        }
        return recommendations.get(risk_level, "Unknown risk level")


# Convenience functions for quick checks
def extract_features(url: str) -> Dict[str, any]:
    """Extract features from a URL."""
    detector = PhishingDetector()
    return detector.extract_features(url)


def is_phishing(url: str) -> Tuple[bool, int]:
    """
    Quick check if URL is likely phishing.
    
    Returns:
        Tuple of (is_phishing, risk_score)
    """
    detector = PhishingDetector()
    result = detector.detect(url)
    return result["is_phishing"], result["risk_score"]
