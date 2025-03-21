# hackweekUI
UI for searching Squareup Center Content via Snowflake

### Prerequisites

1. Square LDAP account with access to Snowflake and App_support tables
2. Git (for cloning the repository)
3. Goose, to follow the installation instructions, with computer controller enabled

### Installation Steps
Non Technical Users: Copy Paste the below instructions into Goose and it can set up most of the backend for you! 
It may require you to open terminal and copy paste steps over

1. **Make sure dev environment is set up correctly: install brew**
   ```bash
        /usr/bin/curl -fsSL https://artifactory.global.square/artifactory/devenv/bootstrap/sq-bootstrap | /bin/bash
       
   ```

2. **Make sure dev environment is set up correctly:  Set up pip config**
    ```bash
        rm -f ~/.pip/pip.conf ~/.config/pip/pip.conf
        python3 -m pip config set global.index-url https://pypi.block-artifacts.com/block-pypi/simple      
     ```

3.  **Make sure dev environment is set up correctly: Install poetry and setup certs**
       ```bash
        curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.3.1 python3 -
        export PATH="${PATH}:${HOME}/.local/bin"
        echo 'PATH="${PATH}:${HOME}/.local/bin"' >> ~/.zshrc
        poetry config certificates.artifactory.cert /opt/homebrew/etc/openssl@1.1/cert.pem
       ```
4.   **Create Backend Directory**
   ```bash
   mkdir content-compass-backend
   cd content-compass-backend
   ```
5. **Set Up Python Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # .\venv\Scripts\activate
   ```
6. **Install Required Packages**
   ```bash
   pip install flask==2.0.1
   pip install flask-cors==3.0.10
   pip install snowflake-connector-python[pandas]
   pip install python-dotenv
   ```
7. **Create Flask Backend File**
   Create a new file named `app.py` with the provided Flask backend code.
   Make sure to include the CORS context
      ```bash
      from flask import Flask, request, jsonify
      from flask_cors import CORS
      import snowflake.connector
      from dotenv import load_dotenv
      import os
   
      # Load environment variables
      load_dotenv()

      app = Flask(__name__)
      # Configure CORS
      CORS(app, resources={
          r"/*": {
              "origins": ["https://mlevy26.github.io", "http://localhost:*"],
              "methods": ["GET", "POST", "OPTIONS"],
              "allow_headers": ["Content-Type"],
          }
      })
      
      @app.route('/health', methods=['GET'])
      def health_check():
          return jsonify({'status': 'healthy'})
      
      @app.route('/search', methods=['POST', 'OPTIONS'])
      def search():
          # Handle preflight request
          if request.method == 'OPTIONS':
              return '', 204
              
          try:
              data = request.json
              if not data:
                  return jsonify({'error': 'No data provided'}), 400
      
              required_fields = ['searchTerm', 'marketCode', 'languageCode', 'userLdap']
              if not all(field in data for field in required_fields):
                  return jsonify({'error': 'Missing required fields'}), 400
      
              search_term = data['searchTerm']
              market_code = data['marketCode']
              language_code = data['languageCode']
              user_ldap = data['userLdap'].lower().strip()
      
              # Configure Snowflake with user-specific details
              snowflake_config = {
                  'user': f"{user_ldap}@squareup.com",
                  'account': 'square',
                  'warehouse': 'ADHOC__MEDIUM',
                  'database': 'APP_SUPPORT',
                  'role': user_ldap.upper(),
                  'authenticator': 'externalbrowser'
              }
      
              print(f"Connecting to Snowflake with user: {snowflake_config['user']}")
              # Connect to Snowflake using SSO
              conn = snowflake.connector.connect(**snowflake_config)
              print("Connected successfully!")
              
              try:
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
                  
                  print(f"Executing query with params: {search_term}, {market_code}, {language_code}")
                  cursor.execute(query, (f"%{search_term.lower()}%", market_code, language_code))
                  results = cursor.fetchall()
                  columns = [desc[0] for desc in cursor.description]
                  
                  formatted_results = [dict(zip(columns, row)) for row in results]
                  print(f"Found {len(formatted_results)} results")
                  
                  return jsonify({
                      'results': formatted_results,
                      'metadata': {
                          'searchTerm': search_term,
                          'marketCode': market_code,
                          'languageCode': language_code,
                          'totalResults': len(formatted_results)
                      }
                  })
                  
              finally:
                  cursor.close()
                  conn.close()
                  print("Connection closed")
                  
          except snowflake.connector.errors.ProgrammingError as e:
              print(f"Snowflake error: {str(e)}")
              return jsonify({'error': f'Snowflake error: {str(e)}'}), 500
          except Exception as e:
              print(f"Server error: {str(e)}")
              return jsonify({'error': f'Server error: {str(e)}'}), 500
      
      if __name__ == '__main__':
          app.run(debug=True, port=5000)
    ```
8. **Start the Flask Server**
   ```bash
   python app.py
   ```
   The server will start on http://localhost:5000
   

### Using the Application

1. Access the UI at: 
   https://mlevy26.github.io/hackweekUI/Support_Center_Search.html

2. Enter your:
   - Square LDAP (without @squareup.com)
   - Select market and language
   - Enter search term

3. The application will:
   - Authenticate using your SSO
   - Search Snowflake for matching content
   - Display results with expandable sections

### Troubleshooting

1. **SSO Authentication Issues**
   - Ensure you're logged into your Square account
   - Check that your LDAP is entered correctly
   - Verify your Snowflake access

2. **Connection Issues**
   - Verify Flask server is running (http://localhost:5000)
   - Check for any error messages in the terminal
   - Ensure CORS extension is enabled in your browser
  
3. **Flast Backend Set Up Issues**
   - If you are having issues stalling or updating packages in terminal,  rerun step 1-3 to ensure that the dev environment is live. Make sure the WARP VPN is on and authenticated.
   - If you are running into an error in terminal due to requiring a password, ask the user to open terminal, run the relevant command, enter the password, and return to goose.

5. **Common Errors**
   - "Connection refused": Flask server not running
   - "CORS error": Enable CORS in your browser
   - "SSO error": Check your Square login

### Support

For issues or questions:
1. Check the error messages in browser console (Command + Option + J)
2. Check the Flask server logs in terminal
3. Reach out to the repository owner

### Security Note

This tool uses your Square SSO credentials for Snowflake access. Never share your credentials or authentication tokens.
