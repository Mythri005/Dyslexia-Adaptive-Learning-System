from flask import jsonify, request
from app.modules.math_module.math_service import math_service
from app.utils.camera_utils import camera_utils

class MathController:
    def start_math_session(self):
        """Start a new math learning session"""
        data = request.get_json()
        user_id = data.get('user_id')
        camera_data = data.get('camera_data')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Analyze camera data for initial stress level
        stress_data = None
        if camera_data:
            stress_data = camera_utils.analyze_stress_and_attention(camera_data)
        
        session_data = math_service.start_session(user_id)
        first_question = math_service.get_next_question(user_id, stress_data)
        
        return jsonify({
            'message': 'Math session started',
            'session_data': session_data,
            'current_question': first_question,
            'stress_analysis': stress_data
        })
    
    def get_math_question(self):
        """Get the next math question with stress analysis"""
        data = request.get_json()
        user_id = data.get('user_id')
        camera_data = data.get('camera_data')
        current_question = data.get('current_question')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Analyze camera data for stress and attention
        stress_data = None
        if camera_data:
            stress_data = camera_utils.analyze_stress_and_attention(camera_data, current_question)
        
        question = math_service.get_next_question(user_id, stress_data)
        
        return jsonify({
            'question': question,
            'session_summary': math_service.get_session_summary(user_id),
            'stress_analysis': stress_data
        })
    
    def submit_math_answer(self):
        """Submit an answer for math question"""
        data = request.get_json()
        user_id = data.get('user_id')
        answer = data.get('answer')
        response_time = data.get('response_time', 0)
        camera_data = data.get('camera_data')
        current_question = data.get('current_question')
        
        if not all([user_id, answer is not None]):
            return jsonify({'error': 'User ID and answer are required'}), 400
        
        # Analyze camera data
        stress_data = None
        if camera_data:
            stress_data = camera_utils.analyze_stress_and_attention(camera_data, current_question)
        
        result = math_service.submit_answer(user_id, answer, response_time, stress_data)
        
        return jsonify(result)
    
    def continue_math_session(self):
        """Continue math session with next set of questions"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = math_service.continue_session(user_id)
        next_question = math_service.get_next_question(user_id)
        
        return jsonify({
            **result,
            'next_question': next_question
        })
    
    def get_math_progress(self):
        """Get current math session progress"""
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        summary = math_service.get_session_summary(user_id)
        
        if not summary:
            return jsonify({'error': 'No active math session'}), 404
        
        return jsonify(summary)
    
    def end_math_session(self):
        """End math session and get final report"""
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        summary = math_service.get_session_summary(user_id)
        
        if not summary:
            return jsonify({'error': 'No active math session'}), 404

        math_service.save_progress_to_db(user_id)
        
        # Generate report
        from app.utils.report_generator import report_generator
        report = report_generator.generate_math_report(user_id, summary)
        
        # Clear session
        if user_id in math_service.user_sessions:
            del math_service.user_sessions[user_id]
        
        return jsonify({
            'message': 'Math session completed',
            'final_report': report,
            'session_summary': summary
        })

# Controller instance
math_controller = MathController()
