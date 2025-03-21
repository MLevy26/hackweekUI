# hackweekUI
UI for searching content in Snowflake

## Content Compass Setup

A tool for searching and managing Square Help content through Snowflake, with SSO authentication.

### Prerequisites

1. Python 3.11 or higher
2. Square LDAP account with access to Snowflake and App_suppor tables
3. Git (for cloning the repository)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MLevy26/hackweekUI.git
   cd hackweekUI
   ```

2.** Make sure dev environment is set up correctly
   ```bash
        # Run bootstrap if needed to install brew
        /usr/bin/curl -fsSL https://artifactory.global.square/artifactory/devenv/bootstrap/sq-bootstrap | /bin/bash
        # Set up pip config
        rm -f ~/.pip/pip.conf ~/.config/pip/pip.conf
        python3 -m pip config set global.index-url https://pypi.block-artifacts.com/block-pypi/simple
        # Install poetry and setup certs
        curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.3.1 python3 -
        export PATH="${PATH}:${HOME}/.local/bin"
        echo 'PATH="${PATH}:${HOME}/.local/bin"' >> ~/.zshrc
        poetry config certificates.artifactory.cert /opt/homebrew/etc/openssl@1.1/cert.pem
   ```

3.  **Create Backend Directory**
   ```bash
   mkdir content-compass-backend
   cd content-compass-backend
   ```

4. **Set Up Python Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # .\venv\Scripts\activate
   ```

5. **Install Required Packages**
   ```bash
   pip install flask==2.0.1
   pip install flask-cors==3.0.10
   pip install snowflake-connector-python[pandas]
   pip install python-dotenv
   ```

6. **Create Flask Backend File**
   Create a new file named `app.py` with the provided Flask backend code.

7. **Start the Flask Server**
   ```bash
   python app.py
   ```
   The server will start on http://localhost:5000

### Using the Application

1. Access the UI at: https://mlevy26.github.io/hackweekUI/Support_Center_Search.html

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

3. **Common Errors**
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
