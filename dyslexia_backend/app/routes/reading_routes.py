from flask import Blueprint
from app.modules.reading_module.reading_controller import reading_controller

reading_bp = Blueprint('reading', __name__)

# Reading module routes
reading_bp.route('/start', methods=['POST'])(reading_controller.start_reading_session)
reading_bp.route('/item', methods=['POST'])(reading_controller.get_reading_item)
reading_bp.route('/evaluate', methods=['POST'])(reading_controller.evaluate_pronunciation)
reading_bp.route('/help', methods=['POST'])(reading_controller.get_reading_help)
reading_bp.route('/progress', methods=['GET'])(reading_controller.get_reading_progress)
reading_bp.route('/end', methods=['POST'])(reading_controller.end_reading_session)
reading_bp.route('/continue', methods=['POST'])(reading_controller.continue_reading_session)  # ✅ ADD THIS
