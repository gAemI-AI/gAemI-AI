# backend-pjt/stocks/utils.py
from jamo import h2j, j2hcj

# 초성 리스트
CHOSUNG_LIST = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

def get_chosung(text):
    """
    한글 문자열 -> 초성 추출
    영어 문자열 -> 소문자 변환
    예: "SK하이닉스" -> "skㅎㅇㄴㅅ"
    """
    if not text:
        return ""
    
    # 1. 소문자 변환 (대소문자 무시를 위해)
    text = text.lower()
    
    result = ""
    for char in text:
        # 한글인 경우 초성 추출
        if '가' <= char <= '힣':
            chosung_index = (ord(char) - 0xAC00) // 588
            result += CHOSUNG_LIST[chosung_index]
        # 한글 자음만 있는 경우 (ㄱ, ㄴ..)
        elif 'ㄱ' <= char <= 'ㅎ':
            result += char
        # 영어/숫자/특수문자는 그대로 (소문자 상태)
        else:
            result += char
            
    return result