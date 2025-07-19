from . import db
from sqlalchemy.sql import func


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # prevent duplicates
    homepage_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # One-to-many relationship
    items = db.relationship("Item", backref="brand", lazy=True)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_url = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    tags = db.Column(db.String(255))

    # Foreign key to brand
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
