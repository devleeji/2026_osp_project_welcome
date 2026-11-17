"""
테스트용 상품 9개를 Firebase에 다시 넣는 스크립트 (DB가 지워졌을 때 복구용).

사용법 (레포 최상위에서, venv 켠 상태):
    python tools/seed_items.py

- 이미 같은 상품명이 있으면 건너뜀 (여러 번 실행해도 중복 안 생김)
- DB 맨 위가 true/숫자처럼 깨져 있으면 먼저 비운 뒤 넣음
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DBhandler  # noqa: E402

ITEMS = [
    # (상품명, 판매자 ID, 가격, 장소, 카테고리, 이미지)
    ("떡볶이",     "어서오소",     "3000", "학생문화관", "분식", "01_tteokbokki.png"),
    ("순대",       "테스트부스02", "3500", "학생문화관", "분식", "02_sundae.png"),
    ("김밥",       "테스트부스03", "3000", "생활관",     "기타", "03_gimbap.png"),
    ("어묵",       "테스트부스04", "2000", "정문",       "꼬치", "04_eomuktang.png"),
    ("라볶이",     "테스트부스05", "4000", "포스코관",   "분식", "05_rabokki.png"),
    ("쫄면",       "테스트부스06", "4000", "대강당",     "국수", "06_jjolmyeon.png"),
    ("주먹밥",     "테스트부스07", "2500", "생활관",     "기타", "07_jumeokbap.png"),
    ("로제떡볶이", "테스트부스08", "4500", "학생문화관", "분식", "08_rose_tteokbokki.png"),
    ("치즈떡볶이", "테스트부스09", "4000", "학생문화관", "분식", "01_tteokbokki.png"),
]


def main():
    DB = DBhandler()

    root = DB.db.get().val()
    if root is not None and not isinstance(root, dict):
        print(f"DB 맨 위가 {root!r} 로 깨져 있어서 비웁니다.")
        DB.db.remove()

    existing = {v.get("product_name") for v in DB.get_items().values()}
    added = 0
    for name, seller, price, place, category, img in ITEMS:
        if name in existing:
            print(f"  건너뜀 (이미 있음): {name}")
            continue
        data = {
            "seller_id": seller,
            "price": price,
            "address": place,
            "status": "당일 수령 가능",
            "email": "booth@ewha.ac.kr",
            "category": category,
            "description": f"{place} 부스의 {name}입니다. (테스트 데이터)",
            "opening_hours": "09:00~16:00",
        }
        item_id = DB.insert_item(name, data, "static/illustrations/" + img)
        print(f"  추가: {name} -> {item_id}")
        added += 1

    print(f"\n완료: {added}개 추가, 전체 상품 {len(DB.get_items())}개")


if __name__ == "__main__":
    main()
