from flask import Blueprint, request, jsonify
from app.utils.camera_utils import camera_utils
from app.utils.speech_utils import speech_utils
from datetime import datetime

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/start', methods=['POST'])
def start_monitoring():
    """Start real-time monitoring for a user"""
    data = request.get_json()
    user_id = data.get('user_id')
    module = data.get('module', 'math')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Start monitoring based on module
    camera_utils.start_real_time_monitoring(user_id)
    speech_utils.start_voice_monitoring(user_id)
    
    return jsonify({
        'message': f'Real-time monitoring started for {module} module',
        'user_id': user_id,
        'module': module
    })

@monitoring_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """Stop real-time monitoring for a user"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    camera_utils.stop_real_time_monitoring(user_id)
    speech_utils.stop_voice_monitoring(user_id)
    
    return jsonify({
        'message': 'Real-time monitoring stopped',
        'user_id': user_id
    })

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get real-time monitoring metrics for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    camera_metrics = camera_utils.get_real_time_metrics(user_id)
    voice_metrics = speech_utils.get_voice_metrics(user_id)
    
    return jsonify({
        'user_id': user_id,
        'camera': camera_metrics,
        'voice': voice_metrics,
        'timestamp': datetime.now().isoformat()
    })

@monitoring_bp.route('/update-camera', methods=['POST'])
def update_camera_data():
    """Update camera data for real-time monitoring"""
    data = request.get_json()
    user_id = data.get('user_id')
    image_data = data.get('image_data')
    current_question = data.get('current_question')
    
    if not all([user_id, image_data]):
        return jsonify({'error': 'User ID and image data are required'}), 400
    
    # Analyze camera data
    analysis = camera_utils.analyze_stress_and_attention(image_data, current_question)
    
    return jsonify({
        'analysis': analysis,
        'user_id': user_id
    })

@monitoring_bp.route('/update-voice', methods=['POST'])
def update_voice_data():
    """Update voice data for real-time monitoring"""
    data = request.get_json()
    user_id = data.get('user_id')
    audio_data = data.get('audio_data')
    
    if not all([user_id, audio_data]):
        return jsonify({'error': 'User ID and audio data are required'}), 400
    
    # Analyze voice data
    voice_metrics = speech_utils.analyze_voice_metrics(audio_data, user_id)
    
    return jsonify({
        'voice_metrics': voice_metrics,
        'user_id': user_id
    })

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts for a user"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    metrics = camera_utils.get_real_time_metrics(user_id)
    alerts = metrics.get('alerts', []) if metrics else []
    
    return jsonify({
        'user_id': user_id,
        'alerts': alerts,
        'total_alerts': len(alerts)
    })

@monitoring_bp.route('/status', methods=['GET'])
def get_monitoring_status():
    """Get monitoring status for all active users"""
    active_users = list(camera_utils.real_time_data.keys())
    
    status = {
        'active_users': active_users,
        'total_monitoring': len(active_users),
        'camera_active': camera_utils.monitoring_active,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status)
