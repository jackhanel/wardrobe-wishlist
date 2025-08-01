from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
from . import db, login_required
from .models import Brand, Item

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/brands")
@login_required
def brands():
    brands = Brand.query.filter_by(user_id=session["user"]["id"]).all()
    return render_template("brands.html", brands=brands)


@views.route("/add-brand", methods=["GET", "POST"])
@login_required
def addBrand():
    if request.method == "POST":
        name = request.form.get("name")
        homepage_url = request.form.get("homepage_url")
        image_url = request.form.get("image_url")
        description = request.form.get("description")

        new_brand = Brand(
            name=name,
            homepage_url=homepage_url,
            image_url=image_url,
            description=description,
            user_id=session["user"]["id"],
        )

        db.session.add(new_brand)
        db.session.commit()

        return redirect(url_for("views.brands"))

    return render_template("add_brand.html")


@views.route("/edit-brand/<int:brand_id>", methods=["GET", "POST"])
@login_required
def edit_brand(brand_id):
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return "Brand not found", 404

    if request.method == "POST":
        brand.name = request.form["name"]
        brand.image_url = request.form.get("image_url") or None
        brand.description = request.form.get("description") or None
        db.session.commit()
        return redirect("/brands")

    return render_template("edit_brand.html", brand=brand)


@views.route("/delete-brand/<int:brand_id>", methods=["POST"])
@login_required
def delete_brand(brand_id):
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return "Brand not found", 404

    db.session.delete(brand)
    db.session.commit()
    return redirect("/brands")


@views.route("/items")
@login_required
def items():
    items = Item.query.filter_by(user_id=session["user"]["id"]).all()
    return render_template("items.html", items=items)


@views.route("/add-item", methods=["GET", "POST"])
@login_required
def addItem():
    brands = Brand.query.filter_by(user_id=session["user"]["id"]).order_by(Brand.name).all()


    if request.method == "POST":
        name = request.form.get("name")
        product_url = request.form.get("product_url")
        image_url = request.form.get("image_url")
        tags = request.form.get("tags")
        brand_name = request.form.get("brand_name", "").strip()

        brand = Brand.query.filter_by(name=brand_name, user_id=session["user"]["id"]).first()
        if not brand:
            brand = Brand(name=brand_name, user_id=session["user"]["id"])
            db.session.add(brand)
            db.session.commit()

        new_item = Item(
            name=name,
            product_url=product_url,
            image_url=image_url,
            brand_id=brand.id,
            tags=tags,
            user_id=session["user"]["id"],
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("views.items"))

    return render_template("add_item.html", brands=brands)


@views.route("/edit-item/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=session["user"]["id"]).first_or_404()
    if not item:
        return "Item not found", 404

    if request.method == "POST":
        item.name = request.form["name"]
        item.image_url = request.form["image_url"]
        item.product_url = request.form["product_url"]
        item.tags = request.form.get("tags") or None
        db.session.commit()
        return redirect("/items")  # adjust if your items route is named differently

    return render_template("edit_item.html", item=item)


@views.route("/delete-item/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=session["user"]["id"]).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("views.items"))


@views.route("/scrape-item")
@login_required
def scrapeItem():
    from flask import request, jsonify
    import requests
    from bs4 import BeautifulSoup

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=8)

        # Detect bot block or invalid HTML response
        if any(
            blocked in response.text.lower()
            for blocked in [
                "sorry, you have been blocked",
                "access denied",
                "restricted access",
            ]
        ):
            return jsonify({"error": "Blocked by site"}), 403

        soup = BeautifulSoup(response.text, "html.parser")

        # --- Name ---
        name = ""
        if meta_title := soup.find("meta", property="og:title"):
            name = meta_title.get("content", "").strip()
        if not name:
            h1 = soup.find("h1")
            name = h1.get_text(strip=True) if h1 else ""

        # --- Description ---
        description = ""
        if meta_desc := soup.find("meta", attrs={"name": "description"}):
            description = meta_desc.get("content", "").strip()
        elif meta_og_desc := soup.find("meta", property="og:description"):
            description = meta_og_desc.get("content", "").strip()
        elif desc_div := soup.find(class_="productView-description"):
            description = desc_div.get_text(strip=True)

        # --- Tags ---
        keywords = [w.lower().strip() for w in name.split() if len(w) > 3]
        tags = ", ".join(keywords[:5])

        return jsonify({"name": name, "description": description, "tags": tags})

    except Exception as e:
        print(f"Scrape error: {e}")
        return jsonify({"error": "Failed to scrape product info"}), 500
