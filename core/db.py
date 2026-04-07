# core/db.py
"""
Thin adapter — redirects to cybershield.core.db so CLI imports work.
The real Supabase logic lives in cybershield/core/db.py.
"""
from cybershield.core.db import log_event, upsert_node, get_recent_events, get_stats, get_db

__all__ = ['log_event', 'upsert_node', 'get_recent_events', 'get_stats', 'get_db']
