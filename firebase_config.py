import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_db_fs = None

def get_firestore_client():
    """Firebase Admin SDK 초기화 및 클라이언트 반환 (Lazy Loading)"""
    global _db_fs
    if _db_fs is not None:
        return _db_fs

    try:
        # 1. 환경 변수에서 서비스 계정 JSON 확인
        firebase_json = os.environ.get('FIREBASE_CONFIG_JSON')
        
        if firebase_json:
            firebase_json = firebase_json.strip()
            if firebase_json.startswith("'") and firebase_json.endswith("'"):
                firebase_json = firebase_json[1:-1]
            if firebase_json.startswith('"') and firebase_json.endswith('"'):
                firebase_json = firebase_json[1:-1]
                
            try:
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully with environment variable.")
                _db_fs = firestore.client()
                return _db_fs
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with environment variable: {e}")
        
        # 2. 로컬 파일 확인 (개발용)
        if os.path.exists('firebase-key.json'):
            cred = credentials.Certificate('firebase-key.json')
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with local JSON file.")
            _db_fs = firestore.client()
            return _db_fs
        
        logger.warning("No Firebase credentials found.")
        return None
    except Exception as e:
        logger.error(f"Critical error during Firebase initialization: {e}")
        return None

# firestore 모듈 자체를 내보내어 쿼리 상수 사용 가능하게 함
firestore_module = firestore

# 클라이언트 접근용 프라퍼티 느낌의 함수 (기본적으로 None 반환 방지 위해 래퍼 제공 가능)
@property
def db_fs():
    return get_firestore_client()
