from datetime import datetime
from app import app, db
from flask import request, jsonify, send_file
from app.models import *
from app.static import *

# Create a new plant
@app.route('/plant', methods=['POST'])
def create_plant():
    data = request.form
    try:
        plant_name = data.get('plant_name', '')
        description = data.get('description', '')
        species = data.get('species', '')
        watering_schedule = data.get('watering_schedule', '')
        sunlight_requirements = data.get('sunlight_requirements', '')
        temperature_requirements = data.get('temperature_requirements', '')
        care_instructions = data.get('care_instructions', '')
        notes = data.get('notes', '')
        is_favorite = bool(data.get('is_favorite', False))
        is_blooming = bool(data.get('is_blooming', False))
        tags = data.get('tags', '')

        new_plant = Plant(
            plant_name=plant_name,
            description=description,
            species=species,
            watering_schedule=watering_schedule,
            sunlight_requirements=sunlight_requirements,
            temperature_requirements=temperature_requirements,
            care_instructions=care_instructions,
            notes=notes,
            is_favorite=is_favorite,
            is_blooming=is_blooming,
            tags=tags,
            created_date=datetime.utcnow()
        )
        db.session.add(new_plant)
        db.session.commit()

        if 'plant_image' in request.files:
            image_file = request.files['plant_image']
            image_data = image_file.read()
            image_name = image_file.filename
            image_extension = image_name.rsplit('.', 1)[1].lower() if '.' in image_name else ''

            image_entity_type = ImageEntityType.query.filter_by(entity_name=EntityTypes.Plant).first()  

            if not image_entity_type:
                return jsonify({'error': 'Image Entity Type ID not found for the given entity name'}), 404
            
            image = Image(
                data=image_data,
                image_name=image_name,
                image_extension=image_extension,
                entity_id=new_plant.id,
                entity_type_id=image_entity_type.id,
                created_date=datetime.utcnow()
            )
            db.session.add(image)
            db.session.commit()
        return jsonify({'message': 'Plant created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Read all plants
@app.route('/plants', methods=['GET'])
def get_all_plants():
    plants = Plant.query.all()
    image_entity_type = ImageEntityType.query.filter_by(entity_name=EntityTypes.Plant).first()
    plant_list = [
            {
                'id': plant.id,
                'plant_name': plant.plant_name,
                'created_date': plant.created_date.isoformat(),
                'plant_image': Image.query.filter_by(entity_id=plant.id, entity_type_id=image_entity_type.id).first().to_dict() if Image.query.filter_by(entity_id=plant.id, entity_type_id=image_entity_type.id).first() else None
            }
            for plant in plants
        ]
    return jsonify({'plants': plant_list})

# Read a specific plant
@app.route('/plant/<int:plant_id>', methods=['GET'])
def get_plant(plant_id):
    plant = Plant.query.get(plant_id)

    image_entity_type = ImageEntityType.query.filter_by(entity_name=EntityTypes.Plant).first()
    image = Image.query.filter_by(entity_id=plant.id, entity_type_id=image_entity_type.id).first()
    image_json = image.to_dict() if image else None
    plant_data = {
        'id': plant.id,
        'plant_name': plant.plant_name,
        'description': plant.description,
        'species': plant.species,
        'watering_schedule': plant.watering_schedule,
        'sunlight_requirements': plant.sunlight_requirements,
        'temperature_requirements': plant.temperature_requirements,
        'care_instructions': plant.care_instructions,
        'notes': plant.notes,
        'is_favorite': plant.is_favorite,
        'is_blooming': plant.is_blooming,
        'tags': plant.tags,
        'created_date': plant.created_date.isoformat(),
        'plant_image': image_json
    }
    return jsonify({'plant': plant_data})

# Update a plant
@app.route('/plant/<int:plant_id>', methods=['PUT'])
def update_plant(plant_id):
    data = request.form
    plant = Plant.query.get(plant_id)
    if plant:
        try:
            plant.plant_name = data.get('plant_name', plant.plant_name)
            plant.description = data.get('description', plant.description)
            plant.species = data.get('species', plant.species)
            plant.watering_schedule = data.get('watering_schedule', plant.watering_schedule)
            plant.sunlight_requirements = data.get('sunlight_requirements', plant.sunlight_requirements)
            plant.temperature_requirements = data.get('temperature_requirements', plant.temperature_requirements)
            plant.care_instructions = data.get('care_instructions', plant.care_instructions)
            plant.notes = data.get('notes', plant.notes)
            plant.is_favorite = bool(data.get('is_favorite', plant.is_favorite))
            plant.is_blooming = bool(data.get('is_blooming', plant.is_blooming))
            plant.tags = data.get('tags', plant.tags)
            db.session.commit()
            if request.files['plant_image']:
                        new_image = request.files['plant_image']
                        image_entity_type = ImageEntityType.query.filter_by(entity_name=EntityTypes.Plant).first()
                        image = Image.query.filter_by(entity_id=plant.id, entity_type_id=image_entity_type.id).first()
                        if image:
                            image.data = new_image.read()
                            image.image_name = new_image.filename
                            image.image_extention = new_image.filename.rsplit('.', 1)[1].lower() if '.' in image.image_name else ''
                            db.session.commit()
                        else:
                            image_data = new_image.read()
                            image_name = new_image.filename
                            image_extension = image_name.rsplit('.', 1)[1].lower() if '.' in image_name else ''
                            image = Image(
                                data=image_data,
                                image_name=image_name,
                                image_extension=image_extension,
                                entity_id=plant.id,
                                entity_type_id=image_entity_type.id,
                                created_date=datetime.utcnow()
                            )
                            db.session.add(image)
                            db.session.commit()
            return jsonify({'message': 'Plant updated successfully'})
        except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500    
    else:
         return jsonify({'error': 'Plant not found'}), 404
    

# Delete a plant
@app.route('/plant/<int:plant_id>', methods=['DELETE'])
def delete_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if plant:
        try:
            db.session.delete(plant)
            db.session.commit()
            
            image_entity_type = ImageEntityType.query.filter_by(entity_name=EntityTypes.Plant).first()
            image = Image.query.filter_by(entity_id=plant.id, entity_type_id=image_entity_type.id).first()
            if image:
                db.session.delete(image)
                db.session.commit()

            return jsonify({'message': 'Plant deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Plant not found'}), 404
