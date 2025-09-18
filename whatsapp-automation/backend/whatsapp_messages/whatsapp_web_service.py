"""
WhatsApp Web Service using Selenium (Alternative to Twilio)
Based on the working sc.py script
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import urllib.parse
import logging
import os
import shutil
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppWebService:
    """Service class for WhatsApp Web integration using Selenium"""
    
    def __init__(self):
        self.session_dir = os.path.join(settings.BASE_DIR, 'whatsapp_session')
        os.makedirs(self.session_dir, exist_ok=True)
    
    def send_message(self, to_phone, message_content):
        """
        Send a WhatsApp message using WhatsApp Web
        Improved method based on sc.py implementation
        
        Args:
            to_phone (str): Recipient phone number with country code
            message_content (str): Message content
            
        Returns:
            dict: Result with success status and message details
        """
        try:
            # Clean phone number (remove whatsapp: prefix if present)
            if to_phone.startswith('whatsapp:'):
                to_phone = to_phone.replace('whatsapp:', '')
            
            phone_clean = to_phone.replace('+', '').replace(' ', '').replace('-', '')
            
            logger.info(f"Sending WhatsApp Web message to {to_phone}")
            
            # Setup Chrome options with improved detection avoidance
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-data-dir={self.session_dir}')
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            try:
                # Add script to avoid detection (improved from sc.py)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Check if session is active with longer timeout
                driver.get('https://web.whatsapp.com')
                time.sleep(10)  # Increased wait time like in sc.py
                
                # Check if logged in with better error handling
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "side"))
                    )
                    logger.info("WhatsApp Web session is active")
                except Exception as session_error:
                    # Check if we need to scan QR code
                    try:
                        qr_code = driver.find_element(By.CSS_SELECTOR, "[data-testid='qr-code']")
                        if qr_code:
                            logger.warning("WhatsApp Web session expired. Attempting to recreate...")
                            driver.quit()
                            
                            # Attempt to recreate the session automatically
                            success = self._recreate_session_automatically()
                            if not success:
                                return {
                                    'success': False,
                                    'message_sid': None,
                                    'status': 'failed',
                                    'error': 'WhatsApp Web session expired and auto-recreation failed. Please run: python manage.py setup_whatsapp --force'
                                }
                            
                            # Try again with new session
                            driver = webdriver.Chrome(service=service, options=options)
                            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            driver.get('https://web.whatsapp.com')
                            time.sleep(10)
                            
                            try:
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.ID, "side"))
                                )
                                logger.info("WhatsApp Web session recreated successfully!")
                            except:
                                return {
                                    'success': False,
                                    'message_sid': None,
                                    'status': 'failed',
                                    'error': 'WhatsApp Web session could not be restored'
                                }
                    except:
                        pass
                    
                    if 'qr_code' not in locals():
                        logger.warning(f"WhatsApp Web session check failed: {str(session_error)}")
                        logger.info("Attempting to recreate session...")
                        driver.quit()
                        
                        # Attempt to recreate the session automatically
                        success = self._recreate_session_automatically()
                        if not success:
                            return {
                                'success': False,
                                'message_sid': None,
                                'status': 'failed',
                                'error': f'WhatsApp Web session not active and auto-recreation failed: {str(session_error)}'
                            }
                        
                        # Try again with new session
                        driver = webdriver.Chrome(service=service, options=options)
                        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        driver.get('https://web.whatsapp.com')
                        time.sleep(10)
                        
                        try:
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.ID, "side"))
                            )
                            logger.info("WhatsApp Web session recreated successfully!")
                        except:
                            return {
                                'success': False,
                                'message_sid': None,
                                'status': 'failed',
                                'error': 'WhatsApp Web session could not be restored'
                            }
                
                # Open chat with encoded message
                encoded_message = urllib.parse.quote(message_content)
                chat_url = f'https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_message}'
                driver.get(chat_url)
                
                # Wait for page to load (increased from sc.py)
                time.sleep(15)
                
                # Check if chat opened successfully with more flexible selectors
                try:
                    # Wait for chat to load - try multiple possible indicators
                    WebDriverWait(driver, 20).until(
                        EC.any_of(
                            # New WhatsApp Web selectors
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[contenteditable="true"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"]')),
                            # Error message selectors
                            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Phone number shared via url is invalid")]')),
                            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Couldn\'t send message")]')),
                            # Fallback - just check if we're on a chat page
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat"]')),
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'header[data-testid="conversation-header"]'))
                        )
                    )
                    
                    # Check for invalid number error
                    try:
                        invalid_number = driver.find_element(By.XPATH, '//div[contains(text(), "Phone number shared via url is invalid")]')
                        if invalid_number:
                            logger.error(f"Invalid phone number: {to_phone}")
                            return {
                                'success': False,
                                'message_sid': None,
                                'status': 'failed',
                                'error': f'Invalid phone number: {to_phone}'
                            }
                    except:
                        pass
                    
                except Exception as chat_error:
                    logger.error(f"Chat failed to load for {to_phone}: {str(chat_error)}")
                    return {
                        'success': False,
                        'message_sid': None,
                        'status': 'failed',
                        'error': f'Chat failed to load: {str(chat_error)}'
                    }
                
                # Try to find and click send button with improved selectors
                try:
                    # First, make sure the message is in the input box
                    logger.info("Looking for message input box...")
                    
                    # Find the message input and make sure text is there
                    message_input = None
                    try:
                        message_input = driver.find_element(By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]')
                    except:
                        try:
                            message_input = driver.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
                        except:
                            try:
                                message_input = driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]')
                            except:
                                pass
                    
                    if message_input:
                        # Use JavaScript to set the message content to avoid emoji issues
                        logger.info("Setting message content using JavaScript...")
                        
                        # Use JavaScript to set the text content
                        driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];
                            element.innerHTML = '';
                            element.focus();
                            document.execCommand('insertText', false, text);
                        """, message_input, message_content)
                        
                        time.sleep(2)
                        logger.info("Message set using JavaScript")
                    
                    # Now look for send button with multiple strategies
                    logger.info("Looking for send button...")
                    send_button = WebDriverWait(driver, 30).until(
                        EC.any_of(
                            # Most common selectors
                            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]')),
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="send"]')),
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]/..')),
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')),
                            # Fallback selectors
                            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "send")]')),
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="button"][@data-tab="11"]')),
                            # Generic send button finder
                            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Send") or contains(@title, "Send")]'))
                        )
                    )
                    
                    logger.info("Send button found, clicking...")
                    send_button.click()
                    
                    logger.info(f"WhatsApp Web message sent successfully to {to_phone}")
                    time.sleep(8)  # Wait after sending like in sc.py
                    
                    return {
                        'success': True,
                        'message_sid': f"whatsapp_web_{int(time.time())}",
                        'status': 'sent',
                        'error': None
                    }
                    
                except Exception as send_error:
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"/tmp/whatsapp_error_{int(time.time())}.png"
                        driver.save_screenshot(screenshot_path)
                        logger.error(f"Screenshot saved to: {screenshot_path}")
                    except:
                        pass
                    
                    logger.error(f"Could not send message to {to_phone}: {str(send_error)}")
                    return {
                        'success': False,
                        'message_sid': None,
                        'status': 'failed',
                        'error': f'Could not find send button: {str(send_error)}'
                    }
                    
            finally:
                try:
                    driver.quit()
                except:
                    pass  # Ignore errors when closing driver like in sc.py
                
        except Exception as error:
            logger.error(f"Failed to send WhatsApp Web message: {str(error)}")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed',
                'error': str(error)
            }
    
    def send_bulk_messages(self, recipients, message_content):
        """
        Send bulk WhatsApp messages using optimized batch processing
        Based on the efficient approach from sc.py
        
        Args:
            recipients (list): List of recipient phone numbers
            message_content (str): Message content
            
        Returns:
            list: List of results for each message
        """
        results = []
        
        logger.info(f"Starting bulk message sending to {len(recipients)} recipients")
        
        # Setup Chrome options once for all messages
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-data-dir={self.session_dir}')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            
            # Add script to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Check if session is active first
            driver.get('https://web.whatsapp.com')
            time.sleep(10)
            
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )
                logger.info("WhatsApp Web session is active for bulk sending")
            except:
                logger.warning("WhatsApp Web session expired. Attempting to recreate session...")
                driver.quit()
                
                # Attempt to recreate the session automatically
                success = self._recreate_session_automatically()
                if not success:
                    logger.error("Failed to recreate WhatsApp Web session automatically.")
                    # Return failed results for all recipients
                    for phone_number in recipients:
                        results.append({
                            'success': False,
                            'message_sid': None,
                            'status': 'failed',
                            'error': 'WhatsApp Web session expired and auto-recreation failed. Please run setup manually.',
                            'recipient': phone_number
                        })
                    return results
                
                # Try again with new session
                try:
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    driver.get('https://web.whatsapp.com')
                    time.sleep(10)
                    
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "side"))
                    )
                    logger.info("WhatsApp Web session recreated successfully!")
                except:
                    logger.error("WhatsApp Web session still not active after recreation attempt.")
                    # Return failed results for all recipients
                    for phone_number in recipients:
                        results.append({
                            'success': False,
                            'message_sid': None,
                            'status': 'failed',
                            'error': 'WhatsApp Web session could not be restored',
                            'recipient': phone_number
                        })
                    return results
            
            # Send messages to each recipient
            for phone_number in recipients:
                try:
                    # Clean phone number
                    if phone_number.startswith('whatsapp:'):
                        phone_number = phone_number.replace('whatsapp:', '')
                    
                    phone_clean = phone_number.replace('+', '').replace(' ', '').replace('-', '')
                    
                    logger.info(f"Sending message to {phone_number}...")
                    
                    # Open chat with encoded message
                    encoded_message = urllib.parse.quote(message_content)
                    driver.get(f'https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_message}')
                    
                    # Wait for the page to load
                    time.sleep(15)
                    
                    # Try to find and click send button
                    try:
                        send_button = WebDriverWait(driver, 30).until(
                            EC.any_of(
                                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]')),
                                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')),
                                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "send")]')),
                                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="send"]')),
                                EC.element_to_be_clickable((By.XPATH, '//div[@role="button"][@data-tab="11"]'))
                            )
                        )
                        send_button.click()
                        
                        logger.info(f"✓ Message sent to {phone_number}")
                        results.append({
                            'success': True,
                            'message_sid': f"whatsapp_web_{int(time.time())}_{phone_clean}",
                            'status': 'sent',
                            'error': None,
                            'recipient': phone_number
                        })
                        
                        time.sleep(8)  # Wait between messages like in sc.py
                        
                    except Exception as send_error:
                        logger.error(f"✗ Could not find send button for {phone_number}: {str(send_error)}")
                        results.append({
                            'success': False,
                            'message_sid': None,
                            'status': 'failed',
                            'error': f'Could not find send button: {str(send_error)}',
                            'recipient': phone_number
                        })
                        
                except Exception as e:
                    logger.error(f"✗ Failed to send to {phone_number}: {str(e)}")
                    results.append({
                        'success': False,
                        'message_sid': None,
                        'status': 'failed',
                        'error': str(e),
                        'recipient': phone_number
                    })
                    # Continue with next number instead of crashing
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize driver for bulk sending: {str(e)}")
            # Return failed results for all recipients
            for phone_number in recipients:
                results.append({
                    'success': False,
                    'message_sid': None,
                    'status': 'failed',
                    'error': f'Driver initialization failed: {str(e)}',
                    'recipient': phone_number
                })
        finally:
            try:
                driver.quit()
            except:
                pass  # Ignore errors when closing driver
        
        logger.info(f"Bulk message sending completed. Success: {sum(1 for r in results if r['success'])}/{len(results)}")
        return results
    
    def setup_session(self):
        """
        Setup WhatsApp Web session with QR code scanning
        This should be run once to establish the session
        """
        logger.info("Setting up WhatsApp Web session...")
        
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-data-dir={self.session_dir}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get('https://web.whatsapp.com')
            
            print("\n" + "="*50)
            print("IMPORTANT: Scan the QR code in the browser window")
            print("="*50 + "\n")
            
            # Wait for user to scan QR code
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.ID, "side"))
            )
            
            logger.info("WhatsApp Web logged in successfully!")
            time.sleep(5)
            
            # Create a backup of the successful session
            self.create_session_backup()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WhatsApp Web session: {str(e)}")
            return False
            
        finally:
            driver.quit()
    
    def _recreate_session_automatically(self):
        """
        Attempt to recreate WhatsApp Web session automatically by clearing session data
        and trying to restore from backup if available
        """
        try:
            logger.info("Attempting to recreate WhatsApp Web session...")
            
            # Remove existing session data to force fresh start
            if os.path.exists(self.session_dir):
                shutil.rmtree(self.session_dir)
                os.makedirs(self.session_dir, exist_ok=True)
                logger.info("Cleared existing session data")
            
            # Try to restore from backup if it exists
            backup_dir = os.path.join(settings.BASE_DIR, 'whatsapp_session_backup')
            if os.path.exists(backup_dir):
                logger.info("Found session backup, attempting to restore...")
                shutil.copytree(backup_dir, self.session_dir, dirs_exist_ok=True)
                
                # Test if restored session works
                if self._test_session_validity():
                    logger.info("Session restored successfully from backup!")
                    return True
                else:
                    logger.warning("Restored session is not valid")
                    # Clear the invalid session again
                    shutil.rmtree(self.session_dir)
                    os.makedirs(self.session_dir, exist_ok=True)
            
            # If no backup or backup failed, try to setup fresh session with QR code
            logger.info("No valid backup found. Opening QR code scanner for fresh setup...")
            return self._setup_fresh_session_with_qr()
            
        except Exception as e:
            logger.error(f"Failed to recreate session automatically: {str(e)}")
            return False
    
    def _setup_fresh_session_with_qr(self):
        """
        Setup a fresh WhatsApp Web session with QR code scanning
        Similar to setup_session but with shorter timeout for campaign use
        """
        try:
            logger.info("Setting up fresh WhatsApp Web session with QR code...")
            
            # Use non-headless mode so user can see the QR code
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-data-dir={self.session_dir}')
            # Remove headless mode for QR code scanning
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            try:
                driver.get('https://web.whatsapp.com')
                
                print("\n" + "="*60)
                print("🔄 WHATSAPP SESSION EXPIRED - QR CODE REQUIRED")
                print("="*60)
                print("📱 Please scan the QR code in the Chrome window that just opened")
                print("⏱️  You have 60 seconds to scan the code")
                print("🔄 The campaign will continue automatically after scanning")
                print("="*60 + "\n")
                
                # Wait for user to scan QR code (shorter timeout for campaigns)
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )
                
                logger.info("✅ WhatsApp Web QR code scanned successfully!")
                print("✅ QR Code scanned successfully! Continuing with campaign...")
                
                # Create a backup of the successful session
                self.create_session_backup()
                
                time.sleep(3)  # Brief wait for session to stabilize
                return True
                
            except Exception as e:
                logger.error(f"❌ QR code scanning failed or timed out: {str(e)}")
                print(f"❌ QR code scanning failed: {str(e)}")
                print("💡 Please try running: python manage.py setup_whatsapp --force")
                return False
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Failed to setup fresh session with QR: {str(e)}")
            return False
    
    def _test_session_validity(self):
        """
        Test if the current session is valid by checking if we can access WhatsApp Web
        """
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-data-dir={self.session_dir}')
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            try:
                driver.get('https://web.whatsapp.com')
                time.sleep(10)
                
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )
                return True
            except:
                return False
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error testing session validity: {str(e)}")
            return False
    
    def create_session_backup(self):
        """
        Create a backup of the current session for automatic restoration
        """
        try:
            if not os.path.exists(self.session_dir):
                logger.warning("No session to backup")
                return False
            
            backup_dir = os.path.join(settings.BASE_DIR, 'whatsapp_session_backup')
            
            # Remove existing backup
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            # Create new backup
            shutil.copytree(self.session_dir, backup_dir)
            logger.info("Session backup created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session backup: {str(e)}")
            return False
