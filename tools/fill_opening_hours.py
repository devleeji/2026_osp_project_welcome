"""
운영 시간(opening_hours)이 없는 상품에 기본값을 채우는 1회용 스크립트.
목록 카드의 시계 아이콘 줄은 이 값이 있을 때만 보여요.

사용법 (레포 최상위에서, venv 켠 상태):
    python tools/fill_opening_hours.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DBhandler  # noqa: E402

DEFAULT_HOURS = "09:00~16:00"


def main():
    DB = DBhandler()
    items = DB.get_items()
    filled = 0
    for item_id, item in items.items():
        if not item.get("opening_hours"):
            # pyrebase는 호출마다 경로가 초기화되므로 매번 child()로 새로 만듦
            DB.db.child("item").child(item_id).update({"opening_hours": DEFAULT_HOURS})
            print(f"  {item.get('product_name', item_id)}: {DEFAULT_HOURS}")
            filled += 1
    print(f"\n완료: {filled}개 채움 (전체 {len(items)}개)")


if __name__ == "__main__":
    main()
