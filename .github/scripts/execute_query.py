import os
import json
import snowflake.connector
import sys

def main():
    print("Python version:", sys.version)
    
    # Get environment variables
    search_term = os.environ.get('SEARCH_TERM')
    market_code = os.environ.get('MARKET_CODE')
    language_code = os.environ.get('LANGUAGE_CODE')
    
    print(f"Got environment variables: {search_term}, {market_code}, {language_code}")
    
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=os.environ['SNOWFLAKE_ACCOUNT'],
            user=os.environ['SNOWFLAKE_USER'],
            password=os.environ['SNOWFLAKE_PASSWORD'],
            warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
            database=os.environ['SNOWFLAKE_DATABASE']
        )
        
        cursor = conn.cursor()
        
        query = """
            SELECT 
                NAME as TITLE,
                SUPPORT_CENTER_URL,
                CONTENTFUL_URL,
                BODY as CONTENT,
                ARTICLE_ID
            FROM APP_SUPPORT.APP_SUPPORT.CDT_CONTENTFUL_CONTENT_V2 
            WHERE LOWER(HTML_REMOVED_BODY) ILIKE %s
            AND ARTICLE_OR_MACRO_IS_MOST_RECENT_VERSION = true 
            AND BODY_IS_MOST_RECENT_VERSION = true 
            AND COUNTRY_CODE = %s
            AND LANGUAGE_CODE = %s
            AND PUBLISHED_STATUS = 'published'
            AND CONTENT_TYPE = 'Article'
            ORDER BY NAME
        """
        
        params = (f"%{search_term.lower()}%", market_code, language_code)
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        formatted_results = [dict(zip(columns, row)) for row in results]
        
        output = {
            'results': formatted_results,
            'metadata': {
                'search_term': search_term,
                'market_code': market_code,
                'language_code': language_code,
                'total_results': len(formatted_results)
            }
        }
        
        with open('results.json', 'w') as f:
            json.dump(output, f, indent=2)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()