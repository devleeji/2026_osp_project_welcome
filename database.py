import json
import pyrebase


class DBhandler:
    def __init__(self):
        # authentication/ 폴더는 .gitignore로 GitHub에 올라가지 않음 (키 파일은 단톡으로 공유)
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    # ===== 상품 등록 =====
    # key: Firebase 자동 생성 키(item_id) / fields: 상품명, 판매자 ID, 가격, 주소, 상태, 이메일, 이미지 경로, 카테고리
    # data의 키는 reg_items.html 폼의 name 값과 같아야 함
    # 반환값: 새로 만들어진 item_id
    def insert_item(self, name, data, img_path):
        item_info = {
            "product_name": name,
            "seller_id": data['seller_id'],
            "price": data['price'],
            "address": data['address'],
            "status": data['status'],
            "email": data['email'],
            "img_path": img_path,
            "category": data.get('category', ''),
            "description": data.get('description', ''),
            "opening_hours": data.get('opening_hours', '')
        }
        result = self.db.child("item").push(item_info)
        item_id = result["name"]  # Firebase가 만든 고유 키
        print(item_id, data, img_path)
        return item_id

    # ===== 회원가입 (실습 2) =====
    # data: 폼 입력값(id, nickname, email, phone), pw_hash: 해시된 비밀번호
    def insert_user(self, data, pw_hash):
        user_info = {
            "id": data['id'],
            "pw": pw_hash,
            "nickname": data['nickname'],
            "email": data['email'],
            "phone": data.get('phone', '')  # 선택 항목
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False

    # 같은 ID가 이미 있으면 False, 없으면 True
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        if users.val() is None:
            return True
        for res in users.each():
            value = res.val()
            if value['id'] == id_string:
                return False
        return True

    # ===== 로그인 (09 실습) =====
    # ID와 해시된 비밀번호가 모두 일치하면 True
    def find_user(self, id_, pw_hash):
        users = self.db.child("user").get()
        if users.val() is None:
            return False
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_hash:
                return True
        return False

    # ===== 마이페이지 =====
    # 아이디로 회원 정보 하나 조회 (없으면 None) — 비밀번호는 빼고 반환
    def get_user(self, id_):
        users = self.db.child("user").get()
        if users.val() is None:
            return None
        for res in users.each():
            value = res.val()
            if value.get('id') == id_:
                return {k: v for k, v in value.items() if k != 'pw'}
        return None

    # ===== 상품 목록 =====
    # {item_id: {product_name, seller_id, price, ...}} 딕셔너리 반환
    def get_items(self):
        items = self.db.child("item").get().val()
        return dict(items) if items else {}

    # 상품 목록 + 좋아요 수 (like 노드를 한 번만 읽어서 상품마다 like_count를 붙임)
    # user_id를 주면 그 사용자가 좋아요 했는지(liked)도 붙임
    def get_items_with_likes(self, user_id=None):
        items = self.get_items()
        likes = self.db.child("like").get().val() or {}
        for item_id, item in items.items():
            item_likes = likes.get(item_id) or {}
            if not isinstance(item_likes, dict):
                item_likes = {}
            item["like_count"] = len(item_likes)
            item["liked"] = bool(user_id) and bool(item_likes.get(user_id))
        return items

    # ===== 상품 상세 =====
    # item_id로 상품 하나 조회 (없으면 None)
    def get_item_by_id(self, item_id):
        return self.db.child("item").child(item_id).get().val()

    # 상품명으로 상품 하나 조회 (없으면 None)
    # 상세 링크가 item_id로 바뀌기 전까지 쓰는 호환용 함수
    def get_item_byname(self, name):
        for item_id, item in self.get_items().items():
            if item.get("product_name", item_id) == name:
                return item
        return None

    # ===== 리뷰 작성 (10 실습) =====
    # data: 폼 입력값 (title, content, rating) / item_id, product_name: 리뷰 대상 상품
    # img_filename: 서버에 저장한 사진 파일 이름 (사진 없으면 "")
    # 반환값: 새로 만들어진 review_id (Firebase 자동 키)
    def insert_review(self, data, item_id, product_name, img_filename, user_id):
        review_info = {
            "title": data['title'],
            "content": data['content'],
            "rating": data['rating'],
            "item_id": item_id,
            "product_name": product_name,
            "img_filename": img_filename,
            "user_id": user_id
        }
        result = self.db.child("review").push(review_info)
        review_id = result["name"]
        print(review_id, review_info)
        return review_id

    # ===== 리뷰 목록 =====
    # {review_id: {title, content, rating, item_id, product_name, img_filename, user_id}} 반환
    def get_reviews(self):
        reviews = self.db.child("review").get().val()
        return dict(reviews) if reviews else {}

    # ===== 리뷰 상세 =====
    # review_id로 리뷰 하나 조회 (없으면 None)
    def get_review_by_id(self, review_id):
        return self.db.child("review").child(review_id).get().val()

    # ===== 좋아요 (10 실습) =====
    # DB 구조: like / item_id / user_id : true
    # 이미 좋아요면 취소, 아니면 좋아요. 반환값: 바뀐 뒤 좋아요 상태 (True/False)
    # 주의: pyrebase는 get/set/remove 후 경로가 초기화되므로 매번 child()로 경로를 새로 만들어야 함
    def toggle_like(self, item_id, user_id):
        if self.db.child("like").child(item_id).child(user_id).get().val():
            self.db.child("like").child(item_id).child(user_id).remove()
            return False
        self.db.child("like").child(item_id).child(user_id).set(True)
        return True

    # 이 사용자가 이 상품에 좋아요를 눌렀는지 (True/False)
    def is_liked(self, item_id, user_id):
        if not user_id:
            return False
        return bool(self.db.child("like").child(item_id).child(user_id).get().val())

    # 이 상품의 좋아요 수
    def get_like_count(self, item_id):
        likes = self.db.child("like").child(item_id).get().val()
        return len(likes) if likes else 0
