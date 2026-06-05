from __future__ import annotations


BUSINESS_INTENTS = {
    "launch_offer": ["런칭", "특가", "이벤트", "할인", "혜택", "쿠폰", "오픈"],
    "feature_highlight": ["기능", "강조", "흡수력", "효과", "성능", "포인트", "보송함"],
    "review_trust": ["후기", "리뷰", "만족", "검증", "믿고", "재구매"],
    "social_proof": ["인기", "베스트", "추천", "판매량", "1위", "소셜 증거"],
    "urgency": ["오늘만", "마감", "임박", "한정", "지금", "놓치지", "cta"],
    "product_demo": ["사용법", "전후", "비교", "보여줘", "보여주는", "시연", "순서", "단계", "여러 장", "카드 넘김"],
    "reaction_pack": ["리액션팩", "감정", "카톡", "친구한테"],
}

TARGET_HINTS = {
    "detail-page": ["상세페이지", "상세", "제품페이지", "상품페이지"],
    "ad-banner": ["광고", "배너", "브랜드 배너", "소셜", "인스타", "정사각"],
    "sticker": ["스티커", "말풍선"],
    "chat": ["카톡", "채팅", "친구", "짤"],
    "lightweight-web": ["용량", "최적화", "가볍게", "삽입", "웹"],
}

TONE_HINTS = {
    "subtle": ["고급", "고급스러운", "깔끔", "프리미엄", "차분", "너무 정신없지", "과하지 않게"],
    "energetic": ["딸깍", "통통", "튀", "튀는", "빠르게", "눈에 띄게", "강하게"],
}

REFERENCE_HINTS = ["레퍼런스", "참고", "이런", "처럼", "따라", "비슷하게"]

SPRITE_HINTS = ["스프라이트", "스프라이트시트", "4x4", "16프레임", "16 프레임", "캐릭터처럼", "캐릭터화"]

OPTIMIZE_HINTS = ["용량", "줄여", "최적화", "가볍게", "삽입하기 좋게", "웹에"]

PACK_HINTS = ["리액션팩", "팩", "4개", "네 개", "네개", "세트", "감정 스티커"]

MARKETING_HINTS = [
    "상세페이지",
    "상세",
    "제품페이지",
    "상품페이지",
    "광고",
    "배너",
    "브랜드",
    "제품",
    "상품",
    "혜택",
    "런칭",
    "특가",
    "이벤트",
    "쿠폰",
    "후기",
    "리뷰",
    "재구매",
    "판매량",
    "1위",
    "cta",
    "사용법",
    "전후",
    "비교",
    "시연",
]

DEFAULT_CAPTIONS = {
    "launch_offer": "런칭 특가",
    "feature_highlight": "포인트 체크",
    "review_trust": "만족 후기",
    "social_proof": "완전 추천",
    "urgency": "오늘만",
    "product_demo": "한눈에 보기",
    "reaction_pack": "",
    "unknown": "",
}

CAPTION_ROLES = {
    "launch_offer": "offer",
    "feature_highlight": "benefit",
    "review_trust": "trust",
    "social_proof": "proof",
    "urgency": "cta",
    "product_demo": "explanation",
    "reaction_pack": "reaction",
    "unknown": "message",
}
