import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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
    # main page = product list
    return render_template("list.html", items=DB.get_items_with_likes(session.get('id')))

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
        flash("회원가입이 완료됐어요. 로그인해 주세요.")  
        return redirect('/login')
    else:
        return render_template("signup.html", error="이미 사용 중인 아이디예요.")   

# 아이디 중복 확인 (AJAX) - 담당: 이지원
# 회원가입 화면의 '중복 확인' 버튼이 /check_id?id=입력값 으로 요청을 보냄
@app.route("/check_id")
def check_id():
    user_id = request.args.get('id', '').strip()
    if not user_id:
        return jsonify({"available": False, "message": "아이디를 입력해 주세요."})
    if DB.user_duplicate_check(user_id):
        return jsonify({"available": True, "message": "사용할 수 있는 아이디예요."})
    return jsonify({"available": False, "message": "이미 사용 중인 아이디예요."})


# 상품 목록 - 담당: 양설아
@app.route("/list")
def view_list():
    return render_template("list.html", items=DB.get_items_with_likes(session.get('id')))


# 리뷰 목록 - 담당: 양설아 (데이터 연동 및 페이지네이션: 이지원)
@app.route("/review")
def view_review():
    page = request.args.get('page', 1, type=int)
    per_page = 4  # 2x2 레이아웃, 한 페이지당 4개

    all_reviews_dict = DB.get_reviews() or {}
    # 최신 작성 리뷰가 1페이지에 먼저 보이도록 역순 정렬
    all_reviews = list(all_reviews_dict.items())[::-1]

    total_reviews = len(all_reviews)
    total_pages = max(1, (total_reviews + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    paginated_reviews = all_reviews[start:end]

    # 상단 요약 박스용 실제 DB 별점 통계 계산
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    rating_sum = 0
    for _, rev in all_reviews:
        try:
            r = int(float(rev.get('rating', 0)))
        except (ValueError, TypeError):
            r = 0
        if 1 <= r <= 5:
            rating_counts[r] += 1
            rating_sum += r

    avg_rating = round(rating_sum / total_reviews, 1) if total_reviews > 0 else 0.0

    return render_template(
        "review.html",
        reviews=paginated_reviews,
        page=page,
        total_pages=total_pages,
        total_reviews=total_reviews,
        per_page=per_page,
        start_idx=start + 1 if total_reviews > 0 else 0,
        end_idx=min(end, total_reviews),
        avg_rating=avg_rating,
        rating_counts=rating_counts
    )

# 상품 등록 - 담당: 이다은 (로그인 체크: 이지원)
@app.route("/reg_items")
def reg_items():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))
    return render_template("reg_items.html")


# 리뷰 등록 - 담당: 황보희 (로그인 체크: 이지원)
@app.route("/reg_reviews/<item_id>")
def reg_reviews(item_id):
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))
    item = DB.get_item_by_id(item_id)
    if item is None:
        flash("상품을 찾을 수 없습니다.")
        return redirect(url_for('view_list'))
    
    return render_template("reg_reviews.html", item_id=item_id, item=item)

# 리뷰 등록 POST (로그인 체크: 이지원)
@app.route("/reg_review_post/<item_id>", methods=['POST'])
def reg_review_post(item_id):
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))
    
    item = DB.get_item_by_id(item_id)
    product_name = item.get('product_name') if item else "알 수 없는 상품"
    
    user_id = session['id'] 
    
    data = request.form
    file = request.files.get('picture')
    filename = ''
    
    if file and file.filename != '':
        filename = file.filename
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    DB.insert_review(data, item_id, product_name, filename, user_id)
    
    return redirect(url_for('view_review'))

# 리뷰 상세 - 담당 : 황보희
@app.route('/review_detail/<review_id>')
def review_detail(review_id):
    review = DB.get_review_by_id(review_id)
    if review is None:
        flash("리뷰를 찾을 수 없습니다.")
        return redirect(url_for('view_review'))

    item_id = review.get('item_id')
    item = DB.get_item_by_id(item_id) if item_id else {}

    return render_template(
        'review_detail.html',
        review=review,
        item=item or {},
        review_id=review_id
    )

# 상품 등록 POST 처리 + result.html - 담당: 이지원
@app.route("/result", methods=['POST'])
def result():
    if 'id' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        seller_id = session['id']  # 1. 로그인한 아이디로 자동 지정
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
        
        # 2. DB에 저장할 데이터에도 로그인한 아이디를 덮어씌움
        form_data = request.form.to_dict()
        form_data['seller_id'] = seller_id
        DB.insert_item(product_name, form_data, "static/images/" + filename)

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
        user = DB.get_user(id_)
        session['nickname'] = user.get('nickname') if user else id_
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
    all_items = DB.get_items()

    # 1. 내가 등록한 상품
    my_items = {item_id: item for item_id, item in all_items.items()
                if str(item.get('seller_id', '')).lstrip('@') == my_id}

    # 2. 내가 작성한 리뷰 (리뷰 DB 함수 병합 전 에러 방지 처리)
    all_reviews = DB.get_reviews() if hasattr(DB, 'get_reviews') else {}
    my_reviews = {
        rev_id: rev for rev_id, rev in (all_reviews or {}).items()
        if str(rev.get('writer_id') or rev.get('user_id') or rev.get('id', '')).lstrip('@') == my_id
    }

    # 3. 좋아요 목록
    liked_items = {item_id: item for item_id, item in all_items.items()
                if DB.is_liked(item_id, my_id)}

    return render_template(
        "mypage.html",
        user=user,
        my_items=my_items,
        my_reviews=my_reviews,
        liked_items=liked_items
    )

# 상품 상세 - 담당: 이다은
@app.route("/detail/<item_id>")
def detail(item_id):
    item = DB.get_item_by_id(item_id)

    if item is None:
        return "상품을 찾을 수 없습니다.", 404

    return render_template(
        "item_detail.html",
        item=item,
        item_id=item_id,
        liked=DB.is_liked(item_id, session.get('id')),
        like_count=DB.get_like_count(item_id)
    )

# 좋아요 (AJAX) - 담당: 장예희
# 누를 때마다 좋아요 <-> 취소, 페이지 새로고침 없이 JSON으로 결과만 돌려줌
@app.route("/like/<item_id>", methods=['POST'])
def like(item_id):
    if not session.get('id'):
        return jsonify({"error": "login_required"}), 401
    liked = DB.toggle_like(item_id, session['id'])
    return jsonify({"liked": liked, "count": DB.get_like_count(item_id)})

if __name__ == "__main__":
    app.run(debug=True)
