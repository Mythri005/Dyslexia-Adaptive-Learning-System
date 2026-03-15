from flask import Blueprint
from app.modules.math_module.math_controller import math_controller

math_bp = Blueprint('math', __name__)

# Math module routes
math_bp.route('/start', methods=['POST'])(math_controller.start_math_session)
math_bp.route('/question', methods=['POST'])(math_controller.get_math_question)
math_bp.route('/submit', methods=['POST'])(math_controller.submit_math_answer)
math_bp.route('/continue', methods=['POST'])(math_controller.continue_math_session)
math_bp.route('/progress', methods=['GET'])(math_controller.get_math_progress)
math_bp.route('/end', methods=['POST'])(math_controller.end_math_session)
