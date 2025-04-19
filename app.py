from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# === 讀取資料 ===
user_df = pd.read_csv("user_gift_data.csv", encoding="utf-8-sig")
gift_df = pd.read_csv("gift_products.csv", encoding="utf-8-sig")

user_df.columns = user_df.columns.str.strip()
gift_df.columns = gift_df.columns.str.strip()
user_df["gender"] = user_df["gender"].str.strip().str.replace("\t", "", regex=False)

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    message = None

    if request.method == "POST":
        gender = request.form.get("gender")
        interest = request.form.get("interest")
        price = request.form.get("price")

        try:
            price = int(price)
        except ValueError:
            price = 99999

        # 找出符合條件的使用者紀錄，計算推薦分數
        matched_users = user_df[
            (user_df["gender"] == gender) &
            (user_df["interest"] == interest)
        ]

        gift_score = matched_users["gift_id"].value_counts().reset_index()
        gift_score.columns = ["gift_id", "score"]

        # 找出 top 推薦商品
        top_gift_ids = gift_score.merge(gift_df, on="gift_id")
        top_gift_ids = top_gift_ids[top_gift_ids["price"] <= price]
        top_gift_ids = top_gift_ids.sort_values(by="score", ascending=False).head(3)

        recommendations = top_gift_ids[["name", "price"]].to_dict(orient="records")

        if not recommendations:
            message = "目前沒有符合條件的推薦結果，請嘗試其他組合。"

    return render_template("index.html", recommendations=recommendations, message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
