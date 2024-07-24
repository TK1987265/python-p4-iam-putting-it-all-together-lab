from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ("-recipes.user", "-password_hash", )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String)
    bio = db.Column(db.Text)
    recipes = db.relationship('Recipe', backref='user' )

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'username': self.username,
    #         'image_url': self.image_url,
    #         'bio': self.bio,
    #     }

    # @validates('username')
    # def validate_username(self, key, username):
    #     if not username:
    #         raise ValueError("Username must not be empty")
    #     return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__= (db.CheckConstraint("length(instructions) >= 50"),)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # @validates('title', 'instructions')
    # def validate_fields(self, key, value):
    #     if not value:
    #         raise ValueError(f"{key.capitalize()} must not be empty")
    #     if key == 'instructions' and len(value) < 50:
    #         raise ValueError("Instructions must be at least 50 characters long")
    #     return value
