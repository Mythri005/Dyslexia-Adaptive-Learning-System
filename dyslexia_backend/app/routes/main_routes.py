from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.models.progress import Progress
from datetime import datetime
from flask import send_file


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({
        'message': 'Dyslexia Adaptive Learning System Backend',
        'version': '1.0.0',
        'endpoints': {
            'math': '/api/math/*',
            'spelling': '/api/spelling/*', 
            'reading': '/api/reading/*',
            'users': '/api/users/*',
            'camera': '/api/camera/*',
            'monitoring': '/api/monitoring/*'
        }
    })

@main_bp.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('age') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Name, age, email and password are required'}), 400
    
    try:
        # Check if user already exists with same name and age
        existing_user = User.query.filter_by(
            email=data['email']
        ).first()
        
        if existing_user:
            return jsonify({
                "error": "User already exists. Please login."
        }), 400
        
        # Create new user
        # Optional: Hash the password
        # hashed_password = generate_password_hash(data['password'])
        user = User(
            name=data['name'],
            age=int(data['age']),
            email=data['email'],
            password=data['password']  # Consider using hashed_password instead
        )
        
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create initial progress records for all modules
        modules = ['math', 'spelling', 'reading']
        for module in modules:
            progress = Progress(
                user_id=user.id,
                module=module,
                current_level='easy',
                total_points=0,
                questions_attempted=0,
                questions_correct=0
            )
            db.session.add(progress)
        
        db.session.commit()
        
        # Fetch the newly created progress records
        progress_records = Progress.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'progress': [p.to_dict() for p in progress_records],
            'existing': False
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/users/find', methods=['GET'])
def find_user():
    """Find user by name and age"""
    name = request.args.get('name')
    age = request.args.get('age')
    
    if not name or not age:
        return jsonify({'error': 'Name and age are required'}), 400
    
    try:
        user = User.query.filter_by(name=name, age=int(age)).first()
        
        if user:
            progress_records = Progress.query.filter_by(user_id=user.id).all()
            return jsonify({
                'user': user.to_dict(),
                'progress': [p.to_dict() for p in progress_records],
                'found': True
            }), 200
        else:
            return jsonify({'found': False}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details and progress"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    progress_records = Progress.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': user.to_dict(),
        'progress': [p.to_dict() for p in progress_records]
    })

@main_bp.route('/api/users/<int:user_id>/progress', methods=['PUT'])
def update_user_progress(user_id):
    """Update user progress across modules"""
    data = request.get_json()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        for module_data in data.get('progress', []):
            module = module_data.get('module')
            points = module_data.get('points_earned', 0)
            correct = module_data.get('correct_answers', 0)
            attempted = module_data.get('questions_attempted', 0)
            
            progress = Progress.query.filter_by(user_id=user_id, module=module).first()
            if progress:
                progress.total_points += points
                progress.questions_attempted += attempted
                progress.questions_correct += correct
                
                # Update level based on performance
                accuracy = progress.questions_correct / progress.questions_attempted if progress.questions_attempted > 0 else 0
                if accuracy >= 0.8 and progress.current_level != 'hard':
                    progress.current_level = 'hard'
                elif accuracy >= 0.6 and progress.current_level == 'easy':
                    progress.current_level = 'medium'
        
        db.session.commit()
        
        return jsonify({'message': 'Progress updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })

@main_bp.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()

    # Optional: Use password hashing check
    # if not user or not check_password_hash(user.password, password):
    if not user or user.password != password:
        return jsonify({'error': 'Invalid email or password'}), 401

    progress_records = Progress.query.filter_by(user_id=user.id).all()

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'progress': [p.to_dict() for p in progress_records]
    })

@main_bp.route('/api/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    """Get aggregated progress data for a user across all modules"""
    progress_records = Progress.query.filter_by(user_id=user_id).all()

    modules = {
        "math": {"total_points": 0, "questions_attempted": 0, "questions_correct": 0},
        "spelling": {"total_points": 0, "questions_attempted": 0, "questions_correct": 0},
        "reading": {"total_points": 0, "questions_attempted": 0, "questions_correct": 0}
    }

    for record in progress_records:
        module_name = record.module.lower()
        if module_name in modules:
            m = modules[module_name]
            m["total_points"] += record.total_points
            m["questions_attempted"] += record.questions_attempted
            m["questions_correct"] += record.questions_correct

    return jsonify(modules)
