from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/plantshield'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from app.routes import *
from app.models import *
from app.static import *
from app.detection_model import *

with app.app_context():
    # db.drop_all()
    db.create_all()

    # Add data to ImageEntityType
    dummy_entity_names = ['PROFILE', 'PLANT', 'USER_PLANT']

    for entity_name in dummy_entity_names:
        existing_entity = ImageEntityType.query.filter_by(entity_name=entity_name).first()

        if not existing_entity:
            new_entity = ImageEntityType(entity_name=entity_name)
            db.session.add(new_entity)
    db.session.commit()