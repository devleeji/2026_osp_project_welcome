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
            "category": data.get('category', '')
        }
        result = self.db.child("item").push(item_info)
        item_id = result["name"]  # Firebase가 만든 고유 키
        print(item_id, data, img_path)
        return item_id

    # ===== 회원가입 (실습 2) =====
    # data: 폼 입력값(id, nickname), pw_hash: 해시된 비밀번호
    def insert_user(self, data, pw_hash):
        user_info = {
            "id": data['id'],
            "pw": pw_hash,
            "nickname": data['nickname']
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

    # ===== 상품 목록 =====
    # {item_id: {product_name, seller_id, price, ...}} 딕셔너리 반환
    def get_items(self):
        items = self.db.child("item").get().val()
        return dict(items) if items else {}

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
