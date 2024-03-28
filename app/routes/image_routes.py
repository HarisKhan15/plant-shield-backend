from datetime import datetime
import io
from flask import jsonify, send_file, request
from app import app, db
from app.exceptions import *
from app.models import *
from app.static import *

@app.route('/get-image/<int:image_id>',methods=['GET'])
def get_image(image_id):
    image = Image.query.filter_by(id=image_id).first()
    if not image:
        return jsonify({'error':'Image not found'}), 404
    return send_file(io.BytesIO(image.data),
                             mimetype=f'image/{image.image_extension}',
                             as_attachment=True,
                             download_name=f"{image.image_name}.{image.image_extension}")

def get_image_entity_type_by_entity_name(entity_name):
    return ImageEntityType.query.filter_by(entity_name=entity_name).first()

def get_image_by_entity_id_and_entity_type(entity_id, entity_name):
    image_entity_type = get_image_entity_type_by_entity_name(entity_name)
    return Image.query.filter_by(entity_id=entity_id, entity_type_id=image_entity_type.id).first()

def get_image_extension(image_name):
    return image_name.rsplit('.', 1)[1].lower() if '.' in image_name else ''

def save_image_by_entity_and_entity_type(image_file, entity_id, entity_name):
    try:
        image_data = image_file.read()
        image_name = image_file.filename
        image_extension = get_image_extension(image_name)

        image_entity_type = ImageEntityType.query.filter_by(entity_name=entity_name).first()

        if not image_entity_type:
            raise EntityTypeException("Image Entity Type ID not found for the given entity name")
        
        image = Image(
            data=image_data,
            image_name=image_name,
            image_extension=image_extension,
            entity_id=entity_id,
            entity_type_id=image_entity_type.id,
            created_date=datetime.utcnow()
        )
        db.session.add(image)
        db.session.commit()
    except:
        raise ImageException("Error occured while uploading image")

def update_image(old_image, new_image):
    try:
        old_image.data = new_image.read()
        old_image.image_name = new_image.filename
        old_image.image_extention = get_image_extension(new_image.filename)
        db.session.commit()
    except:
        raise ImageException("Error occured while updating Image")
