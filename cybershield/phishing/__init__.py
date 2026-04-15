"""Phishing detection module for CyberShield."""

from .detector import PhishingDetector, extract_features, is_phishing

__all__ = ['PhishingDetector', 'extract_features', 'is_phishing']
