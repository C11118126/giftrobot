from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# === 讀取資料 ===
user_df = pd.read_csv("user_gift_data.csv", encoding="cp950")
gift_df = pd.read_csv("gift_products.csv", encoding="cp950")

user_df.columns = user_df.columns.str.strip()
gift_df.columns = gift_df.columns.str.strip()
user_df["gender"] = user_df["gender"].str.strip().str.replace("\t", "", regex=False)

gender_map = {"男": 1, "女": 0}
interest_to_preference = {
    "看書": 1, "追劇": 1, "畫畫": 1, "攝影": 1, "學語言": 1, "手作": 1, "種花": 1,
    "運動": 2, "聽音樂": 2, "跳舞": 2, "健身": 2, "跑步": 2, "唱歌": 2, "遊戲": 2,
    "露營": 2, "騎腳踏車": 2, "旅行": 2, "逛街": 2, "看電影": 2,
    "烹飪": 3, "喜歡出去玩": 3,
}

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = None
    if request.method == "POST":
        interest = request.form["interest"]
        gender = request.form["gender"]
        max_price = int(request.form["price"])

        preference_id = interest_to_preference.get(interest)
        gender_id = gender_map.get(gender)

        if preference_id is not None and gender_id is not None:
            filtered = gift_df[
                ((gift_df["gender_id"] == gender_id) | (gift_df["gender_id"] == 3)) &
                (gift_df["preference_id"] == preference_id) &
                (gift_df["price"] <= max_price)
            ][["name", "price"]]
            recommendations = filtered.to_dict(orient="records")
    return render_template("index.html", recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
