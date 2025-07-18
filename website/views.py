from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import requests
from bs4 import BeautifulSoup
from . import db
from .models import Brand, Item

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/brands")
def brands():
    return render_template("brands.html")


@views.route("/add-brand", methods=["GET", "POST"])
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
        )

        db.session.add(new_brand)
        db.session.commit()

        return redirect(url_for("views.brands"))

    return render_template("add_brand.html")


@views.route("/items")
def items():
    items = Item.query.all()
    return render_template("items.html", items=items)


@views.route("/add-item", methods=["GET", "POST"])
def addItem():
    # brands = Brand.query.order_by(Brand.name).all()

    if request.method == "POST":
        name = request.form.get("name")
        brand_id = request.form.get("brand_id")
        image_url = request.form.get("image_url")
        description = request.form.get("description")
        tags = request.form.get("tags")
        wishlist = bool(request.form.get("wishlist"))

        # Derive category (basic example — you can improve later)
        # category = deriveCategory(name, tags, description)
        category = "test"

        new_item = Item(
            name=name,
            image_url=image_url,
            description=description,
            tags=tags,
            category=category,
            wishlist=wishlist,
            brand_id=brand_id,
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("views.items"))

    # return render_template("add_item.html", brands=brands)
    return render_template("add_item.html")


@views.route("/scrape-item")
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
