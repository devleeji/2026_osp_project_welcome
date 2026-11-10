"""
기존 상품 데이터(상품명이 키)를 Firebase 자동 키(item_id) 방식으로 옮기는 1회용 스크립트.

사용법 (레포 최상위에서, venv 켠 상태):
    python tools/migrate_items.py          # 미리보기만 (아무것도 안 바뀜)
    python tools/migrate_items.py --apply  # 실제로 옮기기

- 이미 product_name 필드가 있는 상품(새 방식)은 건드리지 않음
- 옛 방식 상품은 product_name 필드를 넣어 새 키로 push한 뒤, 옛 키를 삭제
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DBhandler  # noqa: E402


def main():
    apply = "--apply" in sys.argv
    DB = DBhandler()
    items = DB.get_items()

    old_items = {key: value for key, value in items.items() if "product_name" not in value}
    print(f"전체 상품 {len(items)}개 중 옮길 상품 {len(old_items)}개")

    for old_key, value in old_items.items():
        new_value = dict(value)
        new_value["product_name"] = value.get("name", old_key)
        new_value.pop("name", None)
        new_value.setdefault("category", "")

        if apply:
            result = DB.db.child("item").push(new_value)
            DB.db.child("item").child(old_key).remove()
            print(f"  {old_key} -> {result['name']}")
        else:
            print(f"  (미리보기) {old_key} -> 새 item_id")

    if not apply and old_items:
        print("\n실제로 옮기려면: python tools/migrate_items.py --apply")


if __name__ == "__main__":
    main()
