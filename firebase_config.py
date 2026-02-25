import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_db_fs = None

def get_db():
    """Firebase Admin SDK 초기화 및 Firestore 클라이언트 반환 (Lazy Loading)"""
    global _db_fs
    if _db_fs is not None:
        return _db_fs

    try:
        firebase_json = os.environ.get('FIREBASE_CONFIG_JSON')
        
        if firebase_json:
            firebase_json = firebase_json.strip()
            # 앞뒤 따옴표 제거
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
