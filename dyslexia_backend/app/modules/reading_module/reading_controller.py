from flask import jsonify, request
from app.modules.reading_module.reading_service import reading_service

class ReadingController:
    def start_reading_session(self):
        """Start a new reading session"""
        data = request.get_json()
        user_id = data.get('user_id')
        mode = data.get('mode', 'words')  # 'words', 'sentences', 'paragraphs'
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        if mode not in ['words', 'sentences', 'paragraphs']:
            return jsonify({'error': 'Invalid mode. Use "words", "sentences", or "paragraphs"'}), 400
        
        session_data = reading_service.start_session(user_id, mode)
        first_item = reading_service.get_next_item(user_id)
        
        return jsonify({
            'message': f'Reading session started ({mode})',
            'session_data': session_data,
            'current_item': first_item
        })
    
    def get_reading_item(self):
        """Get the next reading item"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        # 🔧 FIXED: Process camera data to get full stress metrics
        camera_data = data.get('camera_data')
        stress_data = None
        
        if camera_data:
            from app.utils.camera_utils import camera_utils
            stress_data = camera_utils.analyze_stress_and_attention(camera_data)
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        item = reading_service.get_next_item(user_id, stress_data)
        
        if 'error' in item:
            return jsonify(item), 404
        
        return jsonify({
            'item': item,
            'session_summary': reading_service.get_session_summary(user_id)
        })
    
    def evaluate_pronunciation(self):
        """Evaluate user's pronunciation"""
        data = request.get_json()
        user_id = data.get('user_id')
        transcribed_text = data.get('spoken_text', '')
        
        # 🔧 FIXED: Process camera data to get full stress metrics
        camera_data = data.get('camera_data')
        stress_data = None
        
        if camera_data:
            from app.utils.camera_utils import camera_utils
            stress_data = camera_utils.analyze_stress_and_attention(camera_data)
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = reading_service.evaluate_pronunciation(
            user_id,
            stress_data,
            transcribed_text
        )
        
        return jsonify(result)
    
    def get_reading_help(self):
        """Get help for current reading item"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        help_info = reading_service.provide_help(user_id)
        
        return jsonify(help_info)
    
    def get_reading_progress(self):
        """Get cumulative reading progress for checkpoints"""
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Use the new get_progress method, not get_session_summary
        progress = reading_service.get_progress(user_id)
        
        # Even if no session, return zeros (not 404)
        return jsonify(progress), 200
    
    def continue_reading_session(self):
        """Continue reading session with next set of items"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = reading_service.continue_session(user_id)
        
        return jsonify(result), 200
    
    def end_reading_session(self):
        """End reading session and get final report"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Get final progress before ending
        final_progress = reading_service.get_progress(user_id)
        
        # 🔥 SAVE TO DATABASE BEFORE GENERATING REPORT
        reading_service.save_progress_to_db(user_id)
        
        # Generate report
        from app.utils.report_generator import report_generator
        report = report_generator.generate_reading_report(user_id, final_progress)
        
        # Clear session
        if user_id in reading_service.user_sessions:
            del reading_service.user_sessions[user_id]
        
        return jsonify({
            'message': 'Reading session completed',
            'final_report': report,
            'session_summary': final_progress
        })

# Controller instance
reading_controller = ReadingController()
