from flask import Flask, render_template

app = Flask(__name__)


# 메인 페이지 (루트 라우팅)
@app.route("/")
def index():
    return render_template("index.html")


# 상품 목록 - 담당: 양설아
@app.route("/list")
def view_list():
    return render_template("list.html")


# 리뷰 목록 - 담당: 양설아
@app.route("/review")
def view_review():
    return render_template("review.html")


# 상품 등록 - 담당: 이다은
@app.route("/reg_items")
def reg_items():
    return render_template("reg_items.html")


# 리뷰 등록 - 담당: 황보희
@app.route("/reg_reviews")
def reg_reviews():
    return render_template("reg_reviews.html")


# 상품 등록 POST 처리 + result.html - 담당: 이지원 (추가 예정)


if __name__ == "__main__":
    app.run(debug=True)
