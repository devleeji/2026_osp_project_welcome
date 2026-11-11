import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from datetime import timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp"
app.permanent_session_lifetime = timedelta(days=7)  # 로그인 상태 유지 기간

# 업로드된 사진을 static/images 폴더에 저장하도록 설정
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from database import DBhandler
DB = DBhandler()

# 메인 페이지 (루트 라우팅)
@app.route("/")
def index():
    return render_template("index.html")

# 로그인 페이지 - 담당: 이지원
@app.route("/login")
def login():
    return render_template("login.html")


# 회원가입 페이지 - 담당: 이지원
@app.route("/signup")
def signup():
    return render_template("signup.html")


# 회원가입 POST 처리 - 담당: 이지원
@app.route("/signup_post", methods=['POST'])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    
    if DB.insert_user(data, pw_hash):
        # redirect를 사용하여 주소창을 /login으로 확실히 변경
        return redirect('/login')
    else:
        return render_template("signup.html", error="User ID already exists!")


# 상품 목록 - 담당: 양설아
@app.route("/list")
def view_list():
    return render_template("list.html", items=DB.get_items())


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
        
        DB.insert_item(product_name, request.form, "static/images/" + filename)

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

# 로그인 처리 - 담당: 이지원
@app.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        session.permanent = bool(request.form.get('remember'))
        return redirect(url_for('index'))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")


# 로그아웃 - 담당: 이지원
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


# 마이페이지 - 담당: 이지원
# 로그인 안 했으면 로그인 페이지로 보냄
@app.route("/mypage")
def mypage():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))

    my_id = session['id']
    user = DB.get_user(my_id)
    # 판매자 ID를 '@아이디'로 적은 경우도 내 상품으로 인식
    my_items = {item_id: item for item_id, item in DB.get_items().items()
                if str(item.get('seller_id', '')).lstrip('@') == my_id}
    return render_template("mypage.html", user=user, my_items=my_items)

# 상품 상세 - 담당: 이다은
@app.route("/detail/<name>")
def detail(name):
    item = DB.get_item_byname(name)

    if item is None:
        return "상품을 찾을 수 없습니다.", 404

    return render_template(
        "item_detail.html",
        item=item,
        product_name=name
    )

if __name__ == "__main__":
    app.run(debug=True)
