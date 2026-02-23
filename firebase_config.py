import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    try:
        # 1. 환경 변수에서 서비스 계정 JSON 확인
        firebase_json = os.environ.get('FIREBASE_CONFIG_JSON')
        
        if firebase_json:
            try:
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized with environment variable.")
                return firestore.client()
            except Exception as e:
                logger.error(f"Failed to initialize Firebase with environment variable: {e}")
        
        # 2. 로컬 파일 확인 (개발용)
        if os.path.exists('firebase-key.json'):
            cred = credentials.Certificate('firebase-key.json')
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with local JSON file.")
            return firestore.client()
        
        logger.warning("No Firebase credentials found. Applications requiring DB will fail.")
        return None
    except Exception as e:
        logger.error(f"Critical error during Firebase initialization: {e}")
        return None

# 글로벌 객체들
db_fs = initialize_firebase()
# firestore 모듈 자체를 내보내어 쿼리 상수(DESCENDING 등) 사용 가능하게 함
firestore_module = firestore
