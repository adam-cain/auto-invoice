from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller, ActionResult, BrowserSession, BrowserProfile
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from urllib.parse import urlparse
load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")

controller = Controller()

@controller.action('Get login credentials')
async def get_login_credentials(site_name: str, page) -> ActionResult:
    """Get email and password credentials from user for login"""
    print(f"\n🔐 LOGIN CREDENTIALS NEEDED")
    print(f"🌐 Site: {site_name}")
    print(f"🌐 Current URL: {page.url}")
    
    # Get email and password from user
    email = input("📧 Enter your email: ").strip()
    password = input("🔑 Enter your password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return ActionResult(extracted_content="Login failed - missing credentials")
    
    print("✅ Credentials received, proceeding with login...")
    return ActionResult(extracted_content=f"Credentials provided for {site_name}: email={email}, password={'*' * len(password)}")

@controller.action('Pause for human interaction')
async def pause_for_human(instruction: str, page) -> ActionResult:
    """Pause the agent and let human interact with the browser"""
    print(f"\n🛑 AGENT PAUSED")
    print(f"📋 Instruction: {instruction}")
    print(f"🌐 Current URL: {page.url}")
    print("👤 Please interact with the browser manually...")
    print("⏸️  Press Enter when you're done to continue the agent")
    
    # Wait for user to press Enter
    input()
    
    print("▶️  Resuming agent...")
    return ActionResult(extracted_content="Human interaction completed, continuing with agent")

@controller.action('Download invoice file')
async def download_invoice_file(vendor_name: str, file_url: str, page) -> ActionResult:
    """Download actual invoice file (PDF, image, etc.) from URL"""
    # Create invoices directory if it doesn't exist
    os.makedirs("invoices", exist_ok=True)
    
    try:
        # Get file extension from URL
        parsed_url = urlparse(file_url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.pdf'
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"invoices/{vendor_name.replace(' ', '_')}_{timestamp}{file_extension}"
        
        # Download the file with human-like headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        response = requests.get(file_url, stream=True, headers=headers)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"📄 Invoice file downloaded: {filename}")
        return ActionResult(extracted_content=f"Invoice file downloaded as {filename}")
        
    except Exception as e:
        print(f"❌ Error downloading invoice: {e}")
        return ActionResult(extracted_content=f"Error downloading invoice: {e}")

@controller.action('Save invoice content')
async def save_invoice_content(vendor_name: str, invoice_content: str, page) -> ActionResult:
    """Save invoice text content to a local file"""
    # Create invoices directory if it doesn't exist
    os.makedirs("invoices", exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"invoices/{vendor_name.replace(' ', '_')}_{timestamp}_content.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Invoice for: {vendor_name}\n")
            f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source URL: {page.url}\n")
            f.write("="*50 + "\n\n")
            f.write(invoice_content)
        
        print(f"💾 Invoice content saved: {filename}")
        return ActionResult(extracted_content=f"Invoice content saved as {filename}")
    except Exception as e:
        print(f"❌ Error saving invoice content: {e}")
        return ActionResult(extracted_content=f"Error saving invoice content: {e}")

@controller.action('Take screenshot of invoice')
async def screenshot_invoice(vendor_name: str, page) -> ActionResult:
    """Take a screenshot of the current invoice page"""
    # Create invoices directory if it doesn't exist
    os.makedirs("invoices", exist_ok=True)
    
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"invoices/{vendor_name.replace(' ', '_')}_{timestamp}_screenshot.png"
        
        # Take screenshot
        await page.screenshot(path=filename, full_page=True)
        
        print(f"📸 Invoice screenshot saved: {filename}")
        return ActionResult(extracted_content=f"Invoice screenshot saved as {filename}")
        
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return ActionResult(extracted_content=f"Error taking screenshot: {e}")

async def main():
    # Create a comprehensive stealth browser profile
    browser_profile = BrowserProfile(
        # Core stealth settings
        stealth=True,
        disable_security=True,  # Disable web security features that can reveal automation
        
        # Browser appearance settings
        headless=False,  # Visible browser is less detectable than headless
        
        # Human-like viewport and device settings
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        
        # Realistic user agent (latest Chrome on macOS)
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        
        # Locale and timezone settings
        locale='en-GB',
        timezone_id='Europe/London',
        
        # Additional stealth settings
        java_script_enabled=True,
        bypass_csp=True,  # Bypass Content Security Policy
        ignore_https_errors=True,
        
        # Behavioral settings to appear more human
        slow_mo=100,  # Add slight delay between actions (100ms)
        wait_between_actions=0.5,  # Wait 500ms between actions
        
        # Network settings
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        },
        
        # Disable automation indicators
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',  # Faster loading
            '--disable-javascript-harmony-shipping',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--aggressive-cache-discard',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
        ],
        
        # Rendering settings
        deterministic_rendering=False,  # Make rendering less predictable
        highlight_elements=False,  # Don't highlight elements (can be detected)
        
        # # Performance settings
        # default_timeout=30000,  # 30 seconds timeout
        # default_navigation_timeout=30000,
    )
    
    # Create browser session with the stealth profile
    browser_session = BrowserSession(browser_profile=browser_profile)

    # initial_actions = [
    #     {'open_tab': {'url': 'https://www.notion.so/login'}}
    # ]

    agent = Agent(
        task="""
        Go to notion's website and access their customer portal to retrieve invoices:
        
        1. Navigate to Notion login page
        2. Use the 'Get login credentials' action to collect email and password from the user
        3. Fill in the login form with the provided credentials and log in
        4. Go to the account/billing section (usually found in user menu or settings)
        5. Look for billing, invoices, or usage history sections
        6. Find and retrieve all available invoices
        7. Save invoices using the appropriate method:
           * If it's a PDF or downloadable file, use download_invoice_file action with the file URL
           * If it's visible content on the page, use save_invoice_content action with the text
           * If it's a complex invoice page, use screenshot_invoice action to capture the visual invoice
        
        Priority: Always try to get the actual invoice file (PDF) first, then fall back to screenshots or text content.
        
        Provide a summary of what invoices were found and saved, including file paths and types.
        """,
        controller=controller,
        # initial_actions=initial_actions,
        llm=llm,
        browser_session=browser_session,
    )
    result = await agent.run()
    print(result)

asyncio.run(main()) 