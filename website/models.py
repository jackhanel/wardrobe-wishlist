from . import db
from sqlalchemy.sql import func


class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    homepage_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)

    items = db.relationship("Item", backref="brand", lazy=True)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    tags = db.Column(db.String(255))  # stored as comma-separated string (e.g., "linen, boxy, summer")
    category = db.Column(db.String(50))
    wishlist = db.Column(db.Boolean, default=False)

    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
