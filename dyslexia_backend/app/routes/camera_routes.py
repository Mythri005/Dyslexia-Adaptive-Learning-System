from flask import Blueprint, request, jsonify
from app.utils.camera_utils import camera_utils

camera_bp = Blueprint('camera', __name__)

@camera_bp.route('/analyze', methods=['POST'])
def analyze_camera():
    """Analyze camera feed for stress and attention"""
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        current_question = data.get('current_question')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Analyze the camera feed
        analysis = camera_utils.analyze_stress_and_attention(image_data, current_question)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@camera_bp.route('/test', methods=['GET'])
def test_camera():
    """Test camera endpoint"""
    return jsonify({
        'message': 'Camera API is working!',
        'status': 'active'
    })
