import os
from flask import Flask, render_template, request

app = Flask(__name__)

# 업로드된 사진을 static/images 폴더에 저장하도록 설정
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


# 상품 등록 POST 처리 + result.html - 담당: 이지원
@app.route("/result", methods=['POST'])
def result():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        seller_id = request.form.get('seller_id')
        price = request.form.get('price')
        address = request.form.get('address')
        status = request.form.get('status')
        email = request.form.get('email')
        
        file = request.files.get('picture')
        filename = ''
        if file and file.filename != '':
            filename = file.filename
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template(
            "result.html",
            product_name=product_name,
            seller_id=seller_id,
            price=price,
            address=address,
            status=status,
            email=email,
            image_file=filename
        )


if __name__ == "__main__":
    app.run(debug=True)