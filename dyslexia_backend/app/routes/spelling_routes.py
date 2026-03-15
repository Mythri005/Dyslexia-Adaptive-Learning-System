from flask import Blueprint
from app.modules.spelling_module.spelling_controller import spelling_controller

spelling_bp = Blueprint('spelling', __name__)

# Spelling module routes
spelling_bp.route('/start', methods=['POST'])(spelling_controller.start_spelling_session)
spelling_bp.route('/question', methods=['POST'])(spelling_controller.get_spelling_question)
spelling_bp.route('/submit', methods=['POST'])(spelling_controller.submit_spelling_answer)
spelling_bp.route('/progress', methods=['GET'])(spelling_controller.get_spelling_progress)
spelling_bp.route('/end', methods=['POST'])(spelling_controller.end_spelling_session)
