"""
News Service Model - Handles fetching news from NewsAPI
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class NewsFetcher:
    """Service class for fetching news from NewsAPI"""

    def __init__(self):
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.api_key = os.getenv("NEWSAPI_KEY") or "ec69e2af6cef4574a7d34d50ca107034"

    def fetch_top_headlines(self, country='us'):
        #אחראית להביא את החדשות, ולחת בקשת גט לניוז-אייפיאיי
        
        try:
            params = {
                'country': country,
                'apiKey': self.api_key
            }

            response = requests.get(self.base_url, params=params, verify=False)
            response.raise_for_status()
            data = response.json()

            print("\n" + "="*60)
            print("NEWS API RESPONSE:")
            print("="*60)
            print(json.dumps(data, indent=2))
            print("="*60 + "\n")

            article_count = len(data.get('articles', []))

            return {
                'success': True,
                'article_count': article_count,
                'data': data
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching news: {str(e)}"
            print(f"\n Error: {error_msg}\n")

            return {
                'success': False,
                'error': error_msg,
                'article_count': 0
            }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"\n Error: {error_msg}\n")

            return {
                'success': False,
                'error': error_msg,
                'article_count': 0
            }
