import shutil
import sys
import subprocess
import ssl
def install_requirements():
    print("Installing required libraries...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                           "pandas", 
                           "pyngrok", 
                           "python-dotenv",
                           "google-auth",
                           "google-auth-oauthlib",
                           "google-api-python-client",
                           "gspread"])
    print("Libraries installed successfully.")


try:
    import time
    import os
    import signal
    from dotenv import load_dotenv
    from pyngrok import ngrok
except :
    install_requirements()
    import time
    import os
    import signal
    from dotenv import load_dotenv
    from pyngrok import ngrok


# Load environment variables
load_dotenv()

def check_python():
    print("Checking Python installation...")
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
        print("Python 3.6 or higher is required. Please upgrade Python and try again.")
        sys.exit(1)
    print("Python check passed.")



def run_main_script():
    print("Generating report...")
    try:
        subprocess.check_call([sys.executable, "main.py"])
        print("Report generation complete.")
        return True
    except subprocess.CalledProcessError:
        print("Error: Report generation failed.")
        return False

def start_local_server():
    print("Starting local server...")
    return subprocess.Popen([sys.executable, "-m", "http.server", "8003"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)

def start_ngrok():
    print("Starting ngrok tunnel...")
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    ngrok_domain = os.getenv("NGROK_DOMAIN")
    
    if not ngrok_auth_token or not ngrok_domain:
        print("Error: NGROK_AUTH_TOKEN or NGROK_DOMAIN not found in .env file")
        return None

    # Disable SSL verification
    print("Warning: Disabling SSL verification. This is not recommended for production use.")
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        ngrok.set_auth_token(ngrok_auth_token)
    except Exception as e:
        print(f"Error setting ngrok auth token: {e}")
        return None
    
    try:
        public_url = ngrok.connect(8003, domain=ngrok_domain)
        print(f"ngrok tunnel established: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None

def print_instructions(public_url):
    print("\nServer is running. Please follow these steps:")
    print("1. Go to Google Docs")
    print("2. Open Extensions -> Macros")
    print("3. Run the macro 'import_report'")
    print("4. If successful, a new tab with the report will be created")
    print("5. If an error occurs, delete the newly created table and try again")
    print(f"\nYour public URL is: {public_url}")
    print("\nPress Enter to stop the server when you're done...")

def copy_env_to_setup_folder():
    #.env copy to ./Setup
    shutil.copy('.env', './Setup AMAZON BORDERS FBA REPORT/.env')
    

def main():
    check_python()

    #if .env not in Setup folder 
    if not os.path.exists('./Setup AMAZON BORDERS FBA REPORT/.env'):
        copy_env_to_setup_folder()
        print('Copied .env to ./Setup AMAZON BORDERS FBA REPORT folder')
    
    if not run_main_script():
        print("Exiting due to main script failure.")
        return
    
    local_server = start_local_server()

    public_url = start_ngrok()
    
    if public_url:
        print_instructions(public_url)
        input()  # Wait for user to press Enter
    
        print("Stopping servers...")
        local_server.terminate()
        ngrok.disconnect(public_url)
        ngrok.kill()
    
    print("Servers stopped. You can close this window.")

if __name__ == "__main__":
    main()
