import os
import json
import snowflake.connector

def execute_snowflake_query():
    # Get environment variables
    search_term = os.environ['SEARCH_TERM']
    market_code = os.environ['MARKET_CODE']
    language_code = os.environ['LANGUAGE_CODE']
    
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        database=os.environ['SNOWFLAKE_DATABASE']
    )

    try:
        # Create cursor
        cursor = conn.cursor()

        # Execute query
        query = f"""
            SELECT 
                NAME as TITLE,
                SUPPORT_CENTER_URL,
                CONTENTFUL_URL,
                BODY as CONTENT,
                ARTICLE_ID
            FROM APP_SUPPORT.APP_SUPPORT.CDT_CONTENTFUL_CONTENT_V2 
            WHERE LOWER(HTML_REMOVED_BODY) ILIKE '%{search_term.lower()}%'
            AND ARTICLE_OR_MACRO_IS_MOST_RECENT_VERSION = true 
            AND BODY_IS_MOST_RECENT_VERSION = true 
            AND COUNTRY_CODE = '{market_code}'
            AND LANGUAGE_CODE = '{language_code}'
            AND PUBLISHED_STATUS = 'published'
            AND CONTENT_TYPE = 'Article'
            ORDER BY NAME
        """
        
        cursor.execute(query)
        
        # Fetch results
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Convert to list of dictionaries
        formatted_results = [
            dict(zip(columns, row))
            for row in results
        
        # Write results to file
        with open('results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'results': formatted_results,
                'metadata': {
                    'search_term': search_term,
                    'market_code': market_code,
                    'language_code': language_code,
                    'total_results': len(formatted_results)
                }
            }, f, ensure_ascii=False, indent=2)
            
    finally:
        conn.close()

if __name__ == '__main__':
    execute_snowflake_query()