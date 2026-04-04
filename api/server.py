#!/usr/bin/env python3
"""
CyberShield REST API Server
Provides comprehensive API access to all system data
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from cybershield.core.monitor import SystemMonitor
from cybershield.ml import get_detector
from cybershield.blockchain.aptos import AptosClient
from cybershield.storage.ipfs import IPFSClient
from cybershield.core.db import get_db, get_recent_events, get_stats
from cybershield.config import LOGS_DIR

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize clients
monitor = SystemMonitor()
detector = get_detector()
aptos_client = AptosClient()
ipfs_client = IPFSClient()


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status."""
    state_file = LOGS_DIR / "node_state.json"
    
    if state_file.exists():
        import json
        state = json.loads(state_file.read_text())
        return jsonify({
            'status': 'registered',
            'node_id': state.get('node_id'),
            'ip': state.get('ip'),
            'registered_at': state.get('registered_at'),
            'reg_cid': state.get('reg_cid'),
            'reg_tx': state.get('reg_tx'),
            'threat_count': state.get('threat_count', 0),
            'node_status': state.get('status', 'online')
        })
    else:
        return jsonify({
            'status': 'not_registered',
            'message': 'Node not registered yet'
        }), 404


# ============================================================================
# Metrics & Monitoring Endpoints
# ============================================================================

@app.route('/api/metrics/current', methods=['GET'])
def current_metrics():
    """Get current system metrics."""
    metrics = monitor.get_metrics()
    verdict, confidence, model_scores = detector.detect(metrics)
    
    return jsonify({
        'metrics': metrics,
        'detection': {
            'verdict': verdict,
            'confidence': confidence,
            'model_scores': model_scores
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/metrics/history', methods=['GET'])
def metrics_history():
    """Get metrics history from Supabase."""
    limit = request.args.get('limit', 100, type=int)
    events = get_recent_events(limit=limit)
    
    return jsonify({
        'events': events,
        'count': len(events)
    })


# ============================================================================
# ML Model Endpoints
# ============================================================================

@app.route('/api/ml/models', methods=['GET'])
def ml_models():
    """Get ML model information."""
    return jsonify({
        'models': list(detector.models.keys()),
        'model_count': len(detector.models),
        'features': detector.feature_names,
        'feature_count': len(detector.feature_names),
        'zk_proof_hash': detector.model_hash if detector.model_hash else None
    })


@app.route('/api/ml/detect', methods=['POST'])
def ml_detect():
    """Run ML detection on provided metrics."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    verdict, confidence, model_scores = detector.detect(data)
    
    return jsonify({
        'verdict': verdict,
        'confidence': confidence,
        'model_scores': model_scores,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/ml/test', methods=['GET'])
def ml_test():
    """Test ML models with current system metrics."""
    metrics = monitor.get_metrics()
    verdict, confidence, model_scores = detector.detect(metrics)
    
    return jsonify({
        'metrics': metrics,
        'verdict': verdict,
        'confidence': confidence,
        'model_scores': model_scores,
        'timestamp': datetime.utcnow().isoformat()
    })


# ============================================================================
# Blockchain Endpoints
# ============================================================================

@app.route('/api/blockchain/info', methods=['GET'])
def blockchain_info():
    """Get blockchain connection info."""
    return jsonify({
        'network': aptos_client.network,
        'node_url': aptos_client.node_url,
        'address': aptos_client.address,
        'explorer_base': f"https://explorer.aptoslabs.com"
    })


@app.route('/api/blockchain/count', methods=['GET'])
def blockchain_count():
    """Get threat count from blockchain."""
    try:
        count = aptos_client.get_log_count()
        return jsonify({
            'count': count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/blockchain/tx/<tx_hash>', methods=['GET'])
def blockchain_tx(tx_hash):
    """Get blockchain transaction URL."""
    return jsonify({
        'tx_hash': tx_hash,
        'explorer_url': aptos_client.explorer_url(tx_hash),
        'network': aptos_client.network
    })


# ============================================================================
# IPFS Endpoints
# ============================================================================

@app.route('/api/ipfs/info', methods=['GET'])
def ipfs_info():
    """Get IPFS connection info."""
    return jsonify({
        'provider': 'Pinata',
        'gateway': 'https://gateway.pinata.cloud/ipfs/',
        'status': 'connected'
    })


@app.route('/api/ipfs/cid/<cid>', methods=['GET'])
def ipfs_cid(cid):
    """Get IPFS content URL."""
    return jsonify({
        'cid': cid,
        'gateway_url': ipfs_client.gateway_url(cid),
        'ipfs_url': f"ipfs://{cid}"
    })


@app.route('/api/ipfs/content/<cid>', methods=['GET'])
def ipfs_content(cid):
    """Fetch IPFS content (proxy)."""
    import requests
    try:
        url = ipfs_client.gateway_url(cid)
        response = requests.get(url, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ipfs/pin', methods=['POST'])
def ipfs_pin():
    """Pin data to IPFS."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        name = data.get('name', 'api-pin')
        content = data.get('content', {})
        
        cid = ipfs_client.pin_json(content, name)
        
        return jsonify({
            'cid': cid,
            'gateway_url': ipfs_client.gateway_url(cid),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Database Endpoints (Supabase)
# ============================================================================

@app.route('/api/db/events', methods=['GET'])
def db_events():
    """Get events from database."""
    limit = request.args.get('limit', 100, type=int)
    verdict = request.args.get('verdict', None)
    
    events = get_recent_events(limit=limit)
    
    # Filter by verdict if specified
    if verdict:
        events = [e for e in events if e.get('verdict') == verdict]
    
    return jsonify({
        'events': events,
        'count': len(events)
    })


@app.route('/api/db/stats', methods=['GET'])
def db_stats():
    """Get database statistics."""
    stats = get_stats()
    return jsonify(stats)


@app.route('/api/db/threats', methods=['GET'])
def db_threats():
    """Get only threat events."""
    limit = request.args.get('limit', 50, type=int)
    events = get_recent_events(limit=limit)
    threats = [e for e in events if e.get('verdict') == 'anomaly']
    
    return jsonify({
        'threats': threats,
        'count': len(threats)
    })


# ============================================================================
# Evidence Endpoints (Combined Data)
# ============================================================================

@app.route('/api/evidence/<event_id>', methods=['GET'])
def evidence(event_id):
    """Get complete evidence for an event."""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        # Get event from database
        result = db.table("events").select("*").eq("id", event_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Event not found'}), 404
        
        event = result.data[0]
        
        # Build complete evidence
        evidence_data = {
            'event': event,
            'ipfs': {
                'cid': event.get('ipfs_cid'),
                'gateway_url': ipfs_client.gateway_url(event.get('ipfs_cid')) if event.get('ipfs_cid') else None
            },
            'blockchain': {
                'tx_hash': event.get('aptos_tx'),
                'explorer_url': aptos_client.explorer_url(event.get('aptos_tx')) if event.get('aptos_tx') else None
            },
            'timestamp': event.get('created_at')
        }
        
        return jsonify(evidence_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evidence/latest', methods=['GET'])
def latest_evidence():
    """Get latest threat evidence."""
    events = get_recent_events(limit=10)
    threats = [e for e in events if e.get('verdict') == 'anomaly']
    
    if not threats:
        return jsonify({'message': 'No threats detected yet'}), 404
    
    latest = threats[0]
    
    return jsonify({
        'event': latest,
        'ipfs': {
            'cid': latest.get('ipfs_cid'),
            'gateway_url': ipfs_client.gateway_url(latest.get('ipfs_cid')) if latest.get('ipfs_cid') else None
        },
        'blockchain': {
            'tx_hash': latest.get('aptos_tx'),
            'explorer_url': aptos_client.explorer_url(latest.get('aptos_tx')) if latest.get('aptos_tx') else None
        }
    })


# ============================================================================
# Node & Network Endpoints
# ============================================================================

@app.route('/api/nodes', methods=['GET'])
def nodes():
    """Get all registered nodes."""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        result = db.table("nodes").select("*").execute()
        return jsonify({
            'nodes': result.data,
            'count': len(result.data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>', methods=['GET'])
def node_info(node_id):
    """Get specific node information."""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        result = db.table("nodes").select("*").eq("node_id", node_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Node not found'}), 404
        
        return jsonify(result.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Analytics Endpoints
# ============================================================================

@app.route('/api/analytics/summary', methods=['GET'])
def analytics_summary():
    """Get analytics summary."""
    stats = get_stats()
    events = get_recent_events(limit=1000)
    
    # Calculate additional metrics
    total_events = len(events)
    threats = [e for e in events if e.get('verdict') == 'anomaly']
    threat_count = len(threats)
    
    # Average ML scores
    if events:
        avg_ml_score = sum(e.get('ml_score', 0) for e in events) / len(events)
    else:
        avg_ml_score = 0
    
    # Threat rate over time
    from collections import defaultdict
    threats_by_hour = defaultdict(int)
    for threat in threats:
        if threat.get('created_at'):
            hour = threat['created_at'][:13]  # YYYY-MM-DDTHH
            threats_by_hour[hour] += 1
    
    return jsonify({
        'summary': {
            'total_events': total_events,
            'total_threats': threat_count,
            'safe_events': total_events - threat_count,
            'threat_rate': (threat_count / total_events * 100) if total_events > 0 else 0,
            'avg_ml_score': avg_ml_score
        },
        'threats_by_hour': dict(threats_by_hour),
        'nodes': stats.get('nodes', []),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/analytics/timeline', methods=['GET'])
def analytics_timeline():
    """Get event timeline."""
    limit = request.args.get('limit', 100, type=int)
    events = get_recent_events(limit=limit)
    
    timeline = []
    for event in events:
        timeline.append({
            'timestamp': event.get('created_at'),
            'verdict': event.get('verdict'),
            'ml_score': event.get('ml_score'),
            'cpu': event.get('cpu'),
            'memory': event.get('memory'),
            'node_id': event.get('node_id')
        })
    
    return jsonify({
        'timeline': timeline,
        'count': len(timeline)
    })


# ============================================================================
# Search & Query Endpoints
# ============================================================================

@app.route('/api/search/events', methods=['GET'])
def search_events():
    """Search events with filters."""
    node_id = request.args.get('node_id')
    verdict = request.args.get('verdict')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)
    limit = request.args.get('limit', 100, type=int)
    
    events = get_recent_events(limit=limit)
    
    # Apply filters
    filtered = events
    
    if node_id:
        filtered = [e for e in filtered if e.get('node_id') == node_id]
    
    if verdict:
        filtered = [e for e in filtered if e.get('verdict') == verdict]
    
    if min_score is not None:
        filtered = [e for e in filtered if e.get('ml_score', 0) >= min_score]
    
    if max_score is not None:
        filtered = [e for e in filtered if e.get('ml_score', 0) <= max_score]
    
    return jsonify({
        'events': filtered,
        'count': len(filtered),
        'filters': {
            'node_id': node_id,
            'verdict': verdict,
            'min_score': min_score,
            'max_score': max_score
        }
    })


# ============================================================================
# Export Endpoints
# ============================================================================

@app.route('/api/export/events', methods=['GET'])
def export_events():
    """Export events as JSON."""
    limit = request.args.get('limit', 1000, type=int)
    events = get_recent_events(limit=limit)
    
    return jsonify({
        'export_date': datetime.utcnow().isoformat(),
        'event_count': len(events),
        'events': events
    })


@app.route('/api/export/threats', methods=['GET'])
def export_threats():
    """Export only threats as JSON."""
    limit = request.args.get('limit', 1000, type=int)
    events = get_recent_events(limit=limit)
    threats = [e for e in events if e.get('verdict') == 'anomaly']
    
    return jsonify({
        'export_date': datetime.utcnow().isoformat(),
        'threat_count': len(threats),
        'threats': threats
    })


# ============================================================================
# Documentation Endpoint
# ============================================================================

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation."""
    return jsonify({
        'name': 'CyberShield API',
        'version': '1.0.0',
        'description': 'REST API for CyberShield IDS',
        'endpoints': {
            'health': {
                'GET /api/health': 'Health check'
            },
            'status': {
                'GET /api/status': 'Get node status'
            },
            'metrics': {
                'GET /api/metrics/current': 'Get current metrics',
                'GET /api/metrics/history': 'Get metrics history'
            },
            'ml': {
                'GET /api/ml/models': 'Get ML model info',
                'POST /api/ml/detect': 'Run ML detection',
                'GET /api/ml/test': 'Test ML models'
            },
            'blockchain': {
                'GET /api/blockchain/info': 'Get blockchain info',
                'GET /api/blockchain/count': 'Get threat count',
                'GET /api/blockchain/tx/<tx_hash>': 'Get TX URL'
            },
            'ipfs': {
                'GET /api/ipfs/info': 'Get IPFS info',
                'GET /api/ipfs/cid/<cid>': 'Get CID URL',
                'GET /api/ipfs/content/<cid>': 'Fetch IPFS content',
                'POST /api/ipfs/pin': 'Pin data to IPFS'
            },
            'database': {
                'GET /api/db/events': 'Get events',
                'GET /api/db/stats': 'Get statistics',
                'GET /api/db/threats': 'Get threats only'
            },
            'evidence': {
                'GET /api/evidence/<event_id>': 'Get complete evidence',
                'GET /api/evidence/latest': 'Get latest threat'
            },
            'nodes': {
                'GET /api/nodes': 'Get all nodes',
                'GET /api/nodes/<node_id>': 'Get node info'
            },
            'analytics': {
                'GET /api/analytics/summary': 'Get analytics summary',
                'GET /api/analytics/timeline': 'Get event timeline'
            },
            'search': {
                'GET /api/search/events': 'Search events with filters'
            },
            'export': {
                'GET /api/export/events': 'Export all events',
                'GET /api/export/threats': 'Export threats only'
            }
        }
    })


# ============================================================================
# Main
# ============================================================================

def start(host='0.0.0.0', port=5000, debug=False):
    """Start the API server."""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel(
        f"[bold cyan]CyberShield REST API[/bold cyan]\n\n"
        f"  URL: [cyan]http://{host}:{port}[/cyan]\n"
        f"  Docs: [cyan]http://{host}:{port}/api/docs[/cyan]\n\n"
        f"  [dim]CORS enabled - accessible from any origin[/dim]",
        border_style="cyan",
        expand=False
    ))
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start(debug=True)
