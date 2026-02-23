import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    # 1. 환경 변수에서 서비스 계정 JSON 확인
    firebase_json = os.environ.get('FIREBASE_CONFIG_JSON')
    
    if firebase_json:
        try:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized with environment variable.")
        except Exception as e:
            print(f"Failed to initialize Firebase with environment variable: {e}")
            return None
    # 2. 로컬 파일 확인 (개발용)
    elif os.path.exists('firebase-key.json'):
        cred = credentials.Certificate('firebase-key.json')
        firebase_admin.initialize_app(cred)
        print("Firebase initialized with local JSON file.")
    else:
        print("WARNING: Firebase credentials not found. Default app may fail.")
        return None
    
    return firestore.client()

# 글로벌 Firestore 클라이언트
db_fs = initialize_firebase()
