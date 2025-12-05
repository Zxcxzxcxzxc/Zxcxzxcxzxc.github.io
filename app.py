from flask import Flask, render_template, request, jsonify
from LaptopFinder import get_game_and_laptops

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("client/index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json or {}

    game_name = data.get("game_name", "").strip()
    settings = data.get("settings", "Medium")
    resolution = data.get("resolution", "1920x1080")
    budget = data.get("budget")

    if not game_name:
        return jsonify({"error": "Не вказано назву гри"}), 400

    if isinstance(budget, str) and budget.strip() != "":
        try:
            budget = int(budget)
        except ValueError:
            budget = None

    result = get_game_and_laptops(
        game_name=game_name,
        settings=settings,
        resolution=resolution,
        budget=budget
    )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
