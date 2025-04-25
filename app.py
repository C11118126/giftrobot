from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# === 讀取 CSV 資料 ===
user_df = pd.read_csv("user_gift_data.csv", encoding="utf-8-sig")
gift_df = pd.read_csv("gift_products.csv", encoding="utf-8-sig")

user_df.columns = user_df.columns.str.strip()
gift_df.columns = gift_df.columns.str.strip()
user_df["gender"] = user_df["gender"].str.strip().str.replace("\t", "", regex=False)

# 抓取所有興趣種類供 step2 用
all_interests = sorted(user_df["interest"].dropna().unique().tolist())

@app.route("/", methods=["GET"])
def step1():
    return render_template("step1.html")

@app.route("/step2", methods=["POST"])
def step2():
    gender = request.form.get("gender")
    return render_template("step2.html", gender=gender, interest_list=all_interests)

@app.route("/result", methods=["POST"])
def result():
    gender = request.form.get("gender")
    interest = request.form.get("interest")
    price = request.form.get("price")

    try:
        price = int(price)
    except ValueError:
        price = 99999

    recommendations = []
    message = None

    matched_users = user_df[
        (user_df["gender"] == gender) &
        (user_df["interest"] == interest)
    ]

    gift_score = matched_users["gift_id"].value_counts().reset_index()
    gift_score.columns = ["gift_id", "score"]

    top_gift_ids = gift_score.merge(gift_df, on="gift_id")
    top_gift_ids = top_gift_ids[top_gift_ids["price"] <= price]
    top_gift_ids = top_gift_ids.sort_values(by="score", ascending=False).head(3)

    recommendations = top_gift_ids[["name", "price", "url"]].to_dict(orient="records")

    if not recommendations:
        message = "目前沒有符合條件的推薦結果，請嘗試其他組合。"

    return render_template("result.html", recommendations=recommendations, message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)