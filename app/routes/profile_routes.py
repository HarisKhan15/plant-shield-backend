from datetime import datetime
from app import app, db
from flask import request, jsonify, send_file
from app.exceptions import *
from app.models import *
from app.static import *
from app.routes import image_routes

# Create Profile
@app.route('/profile', methods=['POST'])
def create_profile():
    data = request.form
    if 'first_name' not in data or 'username' not in data:
        return jsonify({'error': 'Fullname, and username are required fields'}), 400
    try:
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        bio = data.get('bio', '')
        gender = data.get('gender', '')
        phone = data.get('phone', '')
        location = data.get('location', '')
        username = data['username']

        user = get_user_by_username(username)
        
        if user is None:
            return jsonify({'error': 'User Not found'}), 404
        
        existed_profile = Profile.query.filter_by(user_id=user.id).first()
        if existed_profile:
            return jsonify({'error': 'Profile already exist'}), 400
    

        profile = Profile(
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            gender=gender,
            phone=phone,
            location=location,
            user_id=user.id
        )
        db.session.add(profile)
        db.session.commit()

        if 'file' in request.files:
            image_file = request.files['file']
            image_routes.save_image_by_entity_and_entity_type(image_file= image_file, entity_id= profile.id, entity_name= EntityTypes.Profile)
        return jsonify({'error': 'Profile created successfully'}), 200
    except EntityTypeException as ex:
        db.session.rollback()
        return jsonify({'error': ex.message}), 404
    except ImageException as ex:
        db.session.rollback()
        return jsonify({'error': ex.message}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()
    
#Get Profile
@app.route('/profile/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = Profile.query.get(profile_id)
    
    if profile:
        image = image_routes.get_image_by_entity_id_and_entity_type(entity_id=profile_id, entity_name=EntityTypes.Profile)
        
        image_json = image.to_dict() if image else None
        
        return jsonify({
            'id': profile.id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'bio': profile.bio,
            'gender': profile.gender,
            'phone': profile.phone,
            'location': profile.location,
            'username': profile.user.username,
            'profile_picture': image_json
        })
    else:
        return jsonify({'error': 'Profile not found'}), 404

# Update Profile
@app.route('/profile/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    data = request.form
    profile = Profile.query.get(profile_id)
    if profile:
        try:
            profile.first_name = data.get('first_name', profile.first_name)
            profile.last_name = data.get('last_name', profile.last_name)
            profile.bio = data.get('bio', profile.bio)
            profile.gender = data.get('gender', profile.gender)
            profile.phone = data.get('phone', profile.phone)
            profile.location = data.get('location', profile.location)
            
            db.session.commit()
            if request.files['profile_picture']: 
                new_image = request.files['profile_picture']
                image = image_routes.get_image_by_entity_id_and_entity_type(entity_id=profile_id, entity_name=EntityTypes.Profile)
                if image:
                    image_routes.update_image(old_image= image, new_image= new_image)
                else:
                    image_routes.save_image_by_entity_and_entity_type(new_image,profile_id,EntityTypes.Profile)
            return jsonify({'message': 'Profile updated successfully'}), 200
        except EntityTypeException as e:
            db.session.rollback()
            return jsonify({'error' : e.message}), 500
        except ImageException as e:
            db.session.rollback()
            return jsonify({'error': e.message}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Profile not found'}), 404

# Delete Profile
@app.route('/profile/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    profile = Profile.query.get(profile_id)
    
    if profile:
        try:
            db.session.delete(profile)
            db.session.commit()
            
            image = image_routes.get_image_by_entity_id_and_entity_type(entity_id=profile_id, entity_name=EntityTypes.Profile)
            if image:
                db.session.delete(image)
                db.session.commit()

            return jsonify({'message': 'Profile deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Profile not found'}), 404