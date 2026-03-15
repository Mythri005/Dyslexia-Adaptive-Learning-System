from flask import jsonify, request
from app.modules.spelling_module.spelling_service import spelling_service  # FIXED TYPO

class SpellingController:
    def start_spelling_session(self):
        """Start a new spelling session"""
        data = request.get_json()
        user_id = data.get('user_id')
        mode = data.get('mode', 'missing_letters')  # 'missing_letters' or 'complete_words'
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        if mode not in ['missing_letters', 'complete_words']:
            return jsonify({'error': 'Invalid mode. Use "missing_letters" or "complete_words"'}), 400
        
        session_data = spelling_service.start_session(user_id, mode)
        first_question = spelling_service.get_next_question(user_id)
        
        return jsonify({
            'message': f'Spelling session started ({mode})',
            'session_data': session_data,
            'current_question': first_question
        })
    
    def get_spelling_question(self):
        """Get the next spelling question"""
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
        
        question = spelling_service.get_next_question(user_id, stress_data)
        
        if 'error' in question:
            return jsonify(question), 404
        
        return jsonify({
            'question': question,
            'session_summary': spelling_service.get_session_summary(user_id)
        })
    
    def submit_spelling_answer(self):
        """Submit an answer for spelling question"""
        data = request.get_json()
        user_id = data.get('user_id')
        answer = data.get('answer')
        response_time = data.get('response_time', 0)
        
        # 🔧 FIXED: Process camera data to get full stress metrics
        camera_data = data.get('camera_data')
        stress_data = None
        
        if camera_data:
            from app.utils.camera_utils import camera_utils
            stress_data = camera_utils.analyze_stress_and_attention(camera_data)
        
        if not all([user_id, answer is not None]):
            return jsonify({'error': 'User ID and answer are required'}), 400
        
        result = spelling_service.submit_answer(user_id, answer, response_time, stress_data)
        
        return jsonify(result)
    
    def get_spelling_progress(self):
        """Get current spelling session progress"""
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        summary = spelling_service.get_session_summary(user_id)
        
        if not summary:
            return jsonify({'error': 'No active spelling session'}), 404
        
        return jsonify(summary)
    
    def end_spelling_session(self):
        """End spelling session and get final report"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        summary = spelling_service.get_session_summary(user_id)
        
        if not summary:
            return jsonify({'error': 'No active spelling session'}), 404
        
        spelling_service.save_progress_to_db(user_id)
        
        # Generate report
        from app.utils.report_generator import report_generator
        report = report_generator.generate_spelling_report(user_id, summary)
        
        # Clear session
        if user_id in spelling_service.user_sessions:
            del spelling_service.user_sessions[user_id]
        
        return jsonify({
            'message': 'Spelling session completed',
            'final_report': report,
            'session_summary': summary
        })

# Controller instance
spelling_controller = SpellingController()
