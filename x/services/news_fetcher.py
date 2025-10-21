"""
News Fetcher Service - Handles fetching news from NewsAPI
"""
import requests
import json


class NewsFetcher:
    """Service class for fetching news from NewsAPI"""

    def __init__(self):
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.api_key = "ec69e2af6cef4574a7d34d50ca107034"

    def fetch_top_headlines(self, country='us'):
        """
        Fetch top headlines from NewsAPI

        Args:
            country: Country code (default: 'us')

        Returns:
            dict: Response containing status, article count, and data
        """
        try:
            # Prepare request parameters
            params = {
                'country': country,
                'apiKey': self.api_key
            }

            # Make API request
            response = requests.get(self.base_url, params=params)

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Print JSON to console (pretty formatted)
            print("\n" + "="*60)
            print("NEWS API RESPONSE:")
            print("="*60)
            print(json.dumps(data, indent=2))
            print("="*60 + "\n")

            # Extract article count
            article_count = len(data.get('articles', []))

            return {
                'success': True,
                'article_count': article_count,
                'data': data
            }

        except requests.exceptions.RequestException as e:
            # Handle any request-related errors
            error_msg = f"Error fetching news: {str(e)}"
            print(f"\n❌ {error_msg}\n")

            return {
                'success': False,
                'error': error_msg,
                'article_count': 0
            }

        except Exception as e:
            # Handle any other unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            print(f"\n❌ {error_msg}\n")

            return {
                'success': False,
                'error': error_msg,
                'article_count': 0
            }
