from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from ppadb.client import Client as AdbClient
from smsactivate.api import SMSActivateAPI
from urllib3.exceptions import NewConnectionError
import random, os , time, subprocess, csv, sys, requests, string, json, traceback, pandas as pd, undetected_chromedriver as uc
from unidecode import unidecode
from shutil import rmtree
from glob import glob

def main():

    class The_time:

        def __init__(self) -> None:
            self.the_time = time.strftime("%H:%M:%S", time.localtime())

        def __repr__(self) -> str:
            return self.the_time

    class Forwarding:

        def __init__(self, row) -> None:
            if 'task_status' in row.keys():
                if 'forward' in row['task_status']:
                    self.need_to_set_filter = True
                else:
                    self.need_to_set_filter = False
            else:
                self.need_to_set_filter = False
            if 'recovery_email' in row.keys():
                self.recovery_email = row['recovery_email']
            else:
                self.recovery_email = ''
            self.email = row['email']
            self.password = row['password']
            self.logged_in = False
            if row['forwarded_to'] == '':
                self.forwarded_to = Tasks.settings['master_mail']
            else:
                self.forwarded_to = row['forwarded_to']
            self.task_status = 'In Progress'

        def _dummy_send(self, element, word):    
            for character in word:
                element.send_keys(character)
                time.sleep(random.uniform(0.03,0.275))

        def start_webdriver(self):
            option = uc.ChromeOptions()
            option.add_argument('--disable-infobars')
            option.add_argument('--disable-notifications')
            option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            option.add_argument('--disable-gpu')
            option.add_argument('--no-sandbox')
            option.add_argument(f"--window-size={random.randint(1280,1320)},{random.randint(1080,1140)}")
            self.driver = uc.Chrome(options=option)
            
        def login(self):
            self.driver.get("https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLog")
            time.sleep(random.uniform(2.5,3.5))
            
            print(f'[{The_time()}] - Logging in.')

            email_input = self.driver.find_element(By.XPATH, '//input[@id="identifierId"]')
            self._dummy_send(email_input, self.email)
            time.sleep(random.uniform(1.5, 2.5))
            email_input.send_keys(Keys.ENTER)

            while not "challenge" not in self.driver.current_url:
                time.sleep(0.5)
            time.sleep(random.uniform(2.5,3.5))

            password_input = self.driver.find_element(By.XPATH, '//div[@id="password"]//input')
            self._dummy_send(password_input, self.password)
            time.sleep(random.uniform(1.5, 2.5))
            password_input.send_keys(Keys.ENTER)
            time.sleep(random.uniform(4.25,6.5))

            if 'myaccount.google.com' in self.driver.current_url:
                print(f'[{The_time()}] - Successfully logged in!')
                self.logged_in = True
            elif 'speedbump/idvreenable' in self.driver.current_url:
                print(f'[{The_time()}] - Phone verifaction needed!')
            elif 'challenge/selection' in self.driver.current_url:
                print(f'[{The_time()}] - Phone verifaction needed!')
                choose_email_confirmation = self.driver.find_element(By.XPATH, "//div[@data-challengetype='12']")
                choose_email_confirmation.click()
            elif 'disabled' in self.driver.current_url:
                print(f'[{The_time()}] - Account banned!')
            else:
                print(f"[{The_time()}] - Couldn't log in.")

        def to_gmail_page(self):
            settings = self.driver.find_elements(By.XPATH, "//header//a[@role='button']//..")[0]
            self.driver.execute_script('arguments[0].click()', settings)
            time.sleep(random.uniform(2.5,3.75))

            self.driver.get('https://mail.google.com/mail/u/0/')
            time.sleep(random.uniform(4.0,5.25))

        def is_already_forwarded(self):
            try:
                self.driver.find_element(By.XPATH, '//header//..//..//span//a')
                return True
            except NoSuchElementException:
                return False

        def get_mail_page_and_accept_settings(self, first_try = True, from_navigating_to_settings = False):

            if first_try:
                print(f'[{The_time()}] - Getting mail page.')

            self.driver.get("https://mail.google.com/mail/u/0/")
            time.sleep(4)

            try:

                first_step_choose = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]//label//span')[0]
                self.driver.execute_script('arguments[0].click()', first_step_choose)
                time.sleep(random.uniform(1.5,2.5))

                submit_button = self.driver.find_element(By.XPATH, '//div[@role="dialog"]//button')
                submit_button.click()
                time.sleep(random.uniform(2.0,3.0))

                second_step_chose = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]//label//span')[2]
                self.driver.execute_script('arguments[0].click()', second_step_chose)
                time.sleep(random.uniform(1.5,2.5))

                submit_button_2 = self.driver.find_element(By.XPATH, '//div[@role="dialog"]//button[@name="data_consent_dialog_done"]') 
                submit_button_2.click()
                time.sleep(random.uniform(4.0,6.0))

                self.driver.refresh()
                time.sleep(random.uniform(2.0,3.0))
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                time.sleep(random.uniform(2.0,3.0))

            except (NoSuchElementException, IndexError):
                if from_navigating_to_settings:
                    pass
                else:
                    self.driver.refresh()
                    time.sleep(random.uniform(2.0,3.0))
                    self.get_mail_page_and_accept_settings(first_try=False)

        def navigate_to_settings(self, first_try = True):

            if first_try:
                print(f'[{The_time()}] - Navigating to settings.')

            try:
                settings_button = self.driver.find_element(By.XPATH, "//a[@role='button' and @class='FH']")
                settings_button.click()
                time.sleep(random.uniform(2.5,3.5))
                try:
                    all_settings_button = self.driver.find_element(By.XPATH, "//button[ @class='Tj']")
                    all_settings_button.click()
                    time.sleep(random.uniform(3.5,4.5))
                except NoSuchElementException:
                    self.navigate_to_settings(first_try=False)
            except (ElementClickInterceptedException, NoSuchElementException):
                self.get_mail_page_and_accept_settings(first_try=False, from_navigating_to_settings = True)
                self.navigate_to_settings(first_try=False)

            while 'settings' not in self.driver.current_url:
                time.sleep(0.5)

        def forwarding_step_one(self):

            print(f'[{The_time()}] - Starting first step of forwarding.')

            add_forward_in_row_button = self.driver.find_elements(By.XPATH, '//div[@class="f2"]//div[@class="f1"]')[4]
            add_forward_in_row_button.click()
            WebDriverWait(self.driver, 30).until(EC.url_contains('fwdandpop'))
            time.sleep(random.uniform(2.0,3.0))

            try:
                if self.forwarded_to in self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="verifyText"]//..//..//b').text:
                    resend_code = self.driver.find_element(By.XPATH, '//span[@act="resend"]')
                    self.driver.execute_script('arguments[0].click()', resend_code)
            except NoSuchElementException:

                add_forward_in_tab_button = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="add"]')
                add_forward_in_tab_button.click()
                time.sleep(random.uniform(1.75,3.0))

                email_input = self.driver.find_element(By.XPATH, '//div[@role="alertdialog"]//input[@type="text"]')
                self._dummy_send(email_input, self.forwarded_to)
                time.sleep(random.uniform(1.25,1.75))
                email_input.send_keys(Keys.ENTER)
                time.sleep(random.uniform(1.75,2.25))

                WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))

                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(random.uniform(2.75,3.5))
                submitting = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//input[@type="submit"]')))
                submitting.click()
                time.sleep(random.uniform(1.5,2.25))

                self.driver.switch_to.window(self.driver.window_handles[0])
                confirm_1 = self.driver.find_element(By.XPATH, "//div[@role='alertdialog']//button[@name='ok']")
                confirm_1.click()
                time.sleep(random.uniform(2.0,3.0))

        def forwarding_step_two(self, code):

            print(f'[{The_time()}] - Confirming forward.')

            send_code_input = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="verifyText"]')
            send_code_input.clear()
            time.sleep(random.uniform(1.0,1.5))
            self._dummy_send(send_code_input, code)
            time.sleep(random.uniform(1.25,1.75))

            submit_the_code_button = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@name="verify"]')
            submit_the_code_button.click()
            time.sleep(random.uniform(2.25,3.25))
            
            choose_email_forwarding = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="add"]//..//..//table[2]//input')
            self.driver.execute_script('arguments[0].click()', choose_email_forwarding)
            
            time.sleep(random.uniform(2.25,3.25))
            total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

            for i in range(1, total_height, random.randint(4,7)):
                self.driver.execute_script("window.scrollTo(0, {});".format(i))
            time.sleep(random.uniform(2.25,3.25))
            
            save_the_changes = self.driver.find_element(By.XPATH, '//div[@role="main"]//button[@guidedhelpid="save_changes_button"]') 
            self.driver.execute_script('arguments[0].click()', save_the_changes)
            WebDriverWait(self.driver, 30).until(EC.url_contains('inbox'))
            time.sleep(random.uniform(2.75,4.25))

            try:
                self.driver.find_element(By.XPATH, '//header//..//..//span//a')
                self.task_status = 'Gmail forwarded!'
            except NoSuchElementException:
                self.task_status = 'Something went wrong at the end.'        

    class Gmail_gen_forward:

        def __init__(self, gender, master_mail = '') -> None:
            self.gender = gender
            self.first_name = Tasks.get_random_first_name(gender)
            self.last_name = Tasks.get_random_last_name(gender)
            self.year = str(random.randint(1995,2003))
            self.day = str(random.randint(1,28))
            self.month = str(random.randint(1,12))
            self.username = self._generate_username(self.first_name, self.last_name, self.year, first_try=True)
            self.password = self._generate_password()
            self.api = Tasks.settings['sms_activate_api_key']
            if Tasks.settings['recovery_email'] == 'random':
                year = str(random.randint(1995,2003))
                if gender == 'm':
                    first_name = Tasks.get_random_first_name('m')
                    last_name = Tasks.get_random_last_name('m')
                    self.recovery_email = self._generate_username(first_name, last_name, year, recovery = True) + '@gmail.com'
                else:
                    first_name = Tasks.get_random_first_name('f')
                    last_name = Tasks.get_random_last_name('f')                    
                    self.recovery_email = self._generate_username(first_name, last_name, year, recovery = True) + '@gmail.com'
            else:
                self.recovery_email = Tasks.settings['recovery_email']
            if Tasks.settings['master_mail'] == 'in_profile' or '@' not in Tasks.settings['master_mail']:
                self.forwarded_to = master_mail
            else:
                self.forwarded_to = Tasks.settings['master_mail']
            self.username_validation_retries = 0
            self.task_status = 'In Progress'

        def _generate_username(self, first_name, last_name, year, first_try = False, recovery = False):
            
            if first_try or recovery:
                return unidecode(first_name + last_name).lower()
        
            possibilities = [
                first_name + last_name + year,
                first_name + last_name + year[2:],
                last_name + first_name + year,
                last_name + first_name + year[2:],
                first_name + year + last_name,
                first_name + year[2:] + last_name,
                last_name + year + first_name,
                last_name + year[2:] + first_name,
            ]
            
            return unidecode(random.choice(possibilities)).lower()

        def _generate_password(self):
        
            possibilities = [
                self.first_name + self.last_name + self.year,
                self.first_name + self.last_name + self.year[2:],
                self.last_name + self.first_name + self.year,
                self.last_name + self.first_name + self.year[2:],
                self.first_name + self.year + self.last_name,
                self.first_name + self.year[2:] + self.last_name,
                self.last_name + self.year + self.first_name,
                self.last_name + self.year[2:] + self.first_name,
                self.year + self.first_name.capitalize() + self.last_name,
                self.year[2:] + self.first_name.capitalize() + self.last_name,
                self.year + self.last_name.capitalize() + self.first_name,
                self.year[2:] + self.last_name.capitalize() + self.first_name,
            ]

            return unidecode(random.choice(possibilities)).capitalize() + random.choice(string.punctuation)

        def _is_username_valid(self):
            try:
                if self.driver.find_element(By.XPATH, '//*[@id="username"]').get_attribute("aria-invalid") == 'false':
                    return True
                else: return False
            except:
                return True
            
        def _update_username(self, random_username = False):
            if self.username_validation_retries < 4:
                if random_username:
                    new_username = self.first_name[:len(self.first_name)-1] + self.last_name[:len(self.first_name)-1] + self.year[2:]
                else:
                    new_username = self._generate_username(self.first_name, self.last_name, self.year)
                if new_username != self.username:
                    self.username_validation_retries += 1
                    self.username = new_username
                    username_input = self.driver.find_element(By.XPATH, '//input[@id="username"]')
                    username_input.clear()
                    time.sleep(1)
                    self._dummy_send(username_input, self.username)
                    username_input.send_keys(Keys.ENTER)
                    time.sleep(random.uniform(1.25,2.25))
                    if self._is_username_valid():
                        pass
                    else:
                        self._update_username()
                else:
                    self._update_username()

        def _dummy_send(self, element, word):    
            for character in word:
                element.send_keys(character)
                time.sleep(random.uniform(0.03,0.25))

        def start_webdriver(self):
            option = uc.ChromeOptions()
            option.add_argument('--disable-infobars')
            option.add_argument('--disable-notifications')
            option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            option.add_argument('--disable-gpu')
            option.add_argument('--no-sandbox')
            option.add_argument(f"--window-size={random.randint(1280,1320)},{random.randint(1080,1140)}")
            self.driver = uc.Chrome(options=option)

        def first_step_register(self):

            self.driver.get("https://accounts.google.com/signup")
            time.sleep(random.uniform(2.5,3.5))

            print(f'[{The_time()}] - Sending data.')

            first_name_input = self.driver.find_element(By.XPATH, '//input[@id="firstName"]')
            last_name_input = self.driver.find_element(By.XPATH, '//input[@id="lastName"]')
            username_input = self.driver.find_element(By.XPATH, '//input[@id="username"]')
            password_inputs = self.driver.find_elements(By.XPATH, '//input[@type="password"]')
            pass_1_input = password_inputs[0]
            pass_2_input = password_inputs[1]

            to_send_data = [
                [first_name_input, self.first_name],
                [last_name_input, self.last_name],
                [username_input, self.username],
            ]   

            to_send_password = [
                [pass_1_input, self.password],
                [pass_2_input, self.password],
            ]          

            random.shuffle(to_send_data)
            for x in range(len(to_send_data)):
                self._dummy_send(to_send_data[x][0], to_send_data[x][1])
                time.sleep(random.uniform(1.0,2.0))

            for x in range(len(to_send_password)):
                self._dummy_send(to_send_password[x][0], to_send_password[x][1])
                time.sleep(random.uniform(1.0,2.0))

            print(f'[{The_time()}] - Validating data.')

            if self._is_username_valid():
                print(f'[{The_time()}] - Data valdated.')
                next_step_button = self.driver.find_element(By.XPATH, '//div[@id="accountDetailsNext"]/div/button')
                next_step_button.click()
            else:
                self._update_username()

            time.sleep(3)

        def sms_verification(self):
            try: 
                sa = SMSActivateAPI(self.api)
                operators = ['megafon', 'rostelecom', 'tele2', 'yota']
                number_data = sa.getNumberV2(service='go', country='0', operator=random.choice(operators))
                activation_id = number_data['activationId']
                number = number_data["phoneNumber"]

                print(f'[{The_time()}] - Phone number: +{number}')

                phone_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="phoneNumberId"]')))
                phone_input.clear()

                time.sleep(random.uniform(0.25, 1.0))
                self._dummy_send(phone_input, f'+{number}')
                time.sleep(random.uniform(0.25, 1.0))

                submit_button = self.driver.find_elements(By.XPATH, '//div[@id="view_container"]//div[@data-is-touch-wrapper="true"]//button[@type="button"]')[0]
                submit_button.click()

                try:
                    WebDriverWait(self.driver, 5).until(EC.url_contains('webgradsidvverify'))
                    print(f'[{The_time()}] - Waiting for sms.')
                    sa.setStatus(activation_id, status=1)
                    is_successfull = False
                    timeout = time.time() + 50
                    while True:
                        time.sleep(3)
                        if time.time() > timeout:
                            break
                        else:
                            status = sa.getStatus(activation_id)
                            if 'STATUS_OK' in status:
                                activation_code = status.split(":")[1]
                                print(f'[{The_time()}] - Received code: {activation_code}')
                                code_input = self.driver.find_element(By.XPATH, '//*[@id="code"]')
                                self._dummy_send(code_input, activation_code)
                                time.sleep(random.uniform(1.25, 2.25))
                                code_input.send_keys(Keys.ENTER)
                                time.sleep(random.uniform(4.25, 5.0))
                                if EC.url_contains('webpersonaldetails')(self.driver):
                                    sa.setStatus(activation_id, status=6)
                                    is_successfull = True
                                break
                    if is_successfull:
                        print(f'[{The_time()}] - Gmail verified.')
                        time.sleep(3)
                    else:
                        print(f'[{The_time()}] - Sms timeout or something went wrong, getting new phone.')
                        sa.setStatus(activation_id, status=8)
                        self.driver.back()
                        time.sleep(random.uniform(2.75, 3.5))
                        self.sms_verification()               
                except TimeoutException:
                    print(f'[{The_time()}] - Blocked, getting new phone.')
                    sa.setStatus(activation_id, status=8)
                    self.sms_verification()
            except NoSuchElementException:
                print(f'[{The_time()}] - Gmail verified.')
            except KeyError:
                self.sms_verification()

        def complete_personal_details(self):

            print(f'[{The_time()}] - Completing personal details.')

            phone_input = self.driver.find_element(By.XPATH, '//*[@id="phoneNumberId"]')
            optional_email_input = self.driver.find_element(By.XPATH, '//div[@id="view_container"]//input[@type="email"]')
            day_input = self.driver.find_element(By.XPATH, '//*[@id="day"]')
            month_input = Select(self.driver.find_element(By.XPATH, '//*[@id="month"]'))
            year_input = self.driver.find_element(By.XPATH, '//*[@id="year"]')
            gender = Select(self.driver.find_element(By.XPATH, '//*[@id="gender"]'))

            phone_input.clear()
            time.sleep(random.uniform(1.0,2.0))

            self._dummy_send(optional_email_input, self.recovery_email)
            time.sleep(random.uniform(1.0,2.0))
            self._dummy_send(day_input, self.day)
            time.sleep(random.uniform(1.0,2.0))
            month_input.select_by_value(self.month)
            time.sleep(random.uniform(1.0,2.0))
            self._dummy_send(year_input, self.year)
            time.sleep(random.uniform(1.0,2.0))
            if self.gender == 'm':
                gender.select_by_value("1")
            else:
                gender.select_by_value("2")

            time.sleep(random.uniform(1.0,2.0))

            day_input.send_keys(Keys.ENTER)

        def complete_personalization(self):

            WebDriverWait(self.driver, 30, poll_frequency=random.uniform(0.3,0.7)).until(EC.url_contains('webpersonalizationchoice'))

            time.sleep(random.uniform(3.0,3.5))

            print(f'[{The_time()}] - Completing personalization.')
            personalization = self.driver.find_elements(By.XPATH, '//span[@role="presentation"]//div[@role="radio"]')[0]
            self.driver.execute_script('arguments[0].click()', personalization)
            time.sleep(random.uniform(1.0,2.0))
            submit_button = self.driver.find_element(By.XPATH, '//*[@id="view_container"]//button')
            submit_button.click()

        def complete_reccomended_settings(self):

            WebDriverWait(self.driver, 30, poll_frequency=random.uniform(0.3,0.7)).until(EC.url_contains('webrecommendedsettings'))

            time.sleep(random.uniform(3.0, 4.0))

            print(f'[{The_time()}] - Completing reccomended settings.')

            submit_button = self.driver.find_elements(By.XPATH, '//div[@data-is-consent="true"]//button')[1]

            total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

            for i in range(1, total_height, random.randint(3,7)):
                self.driver.execute_script("window.scrollTo(0, {});".format(i))

            time.sleep(1.5)
            submit_button.click()

        def complete_tos(self):

            WebDriverWait(self.driver, 30, poll_frequency=random.uniform(0.3,0.7)).until(EC.url_contains('webtermsofservice'))

            time.sleep(random.uniform(3.0,3.5))

            print(f'[{The_time()}] - Completing ToS.')

            submit_button = self.driver.find_elements(By.XPATH, '//div[@data-is-consent="true"]//button')[0]

            total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

            for i in range(1, total_height, random.randint(4,7)):
                self.driver.execute_script("window.scrollTo(0, {});".format(i))

            time.sleep(random.uniform(1.5,2.5))
            submit_button.click()
            time.sleep(random.uniform(3.0,3.5))

            self.task_status = 'Gmail Generated'

        def get_mail_page_and_accept_settings(self, first_try = True, from_navigating_to_settings = False):

            if first_try:
                print(f'[{The_time()}] - Getting mail page.')

            self.driver.get("https://mail.google.com/mail/u/0/")
            time.sleep(random.uniform(2.5, 3.5))

            try:

                first_step_choose = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]//label//span')[0]
                self.driver.execute_script('arguments[0].click()', first_step_choose)
                time.sleep(random.uniform(1.5,2.5))

                submit_button = self.driver.find_element(By.XPATH, '//div[@role="dialog"]//button')
                submit_button.click()
                time.sleep(random.uniform(2.0,3.0))

                second_step_chose = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]//label//span')[2]
                self.driver.execute_script('arguments[0].click()', second_step_chose)
                time.sleep(random.uniform(1.5,2.5))

                submit_button_2 = self.driver.find_element(By.XPATH, '//div[@role="dialog"]//button[@name="data_consent_dialog_done"]') 
                submit_button_2.click()
                time.sleep(random.uniform(4.0,6.0))

                self.driver.refresh()
                time.sleep(random.uniform(2.0,3.0))
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                time.sleep(random.uniform(2.0,3.0))

            except (NoSuchElementException, IndexError):
                if from_navigating_to_settings:
                    pass
                else:
                    self.driver.refresh()
                    time.sleep(random.uniform(2.0,3.0))
                    self.get_mail_page_and_accept_settings(first_try=False)

        def get_main_mail_page(self):

            try:
                main_page_button = self.driver.find_element(By.XPATH, '//div[@role="button"]//..//a[@aria-label="Gmail"]')
                main_page_button.click()
            except:
                self.driver.get("https://mail.google.com/mail/u/0/")

            time.sleep(random.uniform(3.5,4.5))

        def navigate_to_settings(self, first_try = True):

            if first_try:
                print(f'[{The_time()}] - Navigating to settings.')

            try:
                settings_button = self.driver.find_element(By.XPATH, "//a[@role='button' and @class='FH']")
                settings_button.click()
                time.sleep(random.uniform(2.5,3.5))
                try:
                    all_settings_button = self.driver.find_element(By.XPATH, "//button[ @class='Tj']")
                    all_settings_button.click()
                    time.sleep(random.uniform(3.5,4.5))
                except NoSuchElementException:
                    self.navigate_to_settings(first_try=False)
            except (ElementClickInterceptedException, NoSuchElementException):
                self.get_mail_page_and_accept_settings(first_try=False, from_navigating_to_settings = True)
                self.navigate_to_settings(first_try=False)

            WebDriverWait(self.driver, 30).until(EC.url_contains('settings'))

        def adding_filter(self):

            self.navigate_to_settings()
            time.sleep(random.uniform(1.0,2.0))

            print(f'[{The_time()}] - Adding filter.')

            filtering_button = self.driver.find_elements(By.XPATH, '//div[@class="f2"]//div[@class="f1"]')[3]
            filtering_button.click  ()
            WebDriverWait(self.driver, 30).until(EC.url_contains('filters'))
            time.sleep(random.uniform(2.0,3.0))

            add_filter_button = self.driver.find_elements(By.XPATH, "//span[@class='sA']")[-2]
            add_filter_button.click()
            time.sleep(random.uniform(3.5,4.5))

            add_star = self.driver.find_elements(By.XPATH, "//div[@class='ZZ']//input")[0]
            add_star.send_keys("*")
            time.sleep(random.uniform(1.0,1.75))

            create_filter = self.driver.find_element(By.XPATH, '//div[@class="acM"]')
            create_filter.click()
            time.sleep(random.uniform(1.0,1.75))

            confirm_1 = self.driver.find_element(By.XPATH, "//div[@role='alertdialog']//button[@name='ok']")
            confirm_1.click()
            WebDriverWait(self.driver, 30).until(EC.url_contains('from=*'))
            time.sleep(random.uniform(2.0,3.0))

            not_send_to_spam = self.driver.find_elements(By.XPATH, "//div[@class='ZZ']//div[@class='nH']//input")[6]
            self.driver.execute_script("arguments[0].click()", not_send_to_spam)
            time.sleep(random.uniform(1.75,2.75))

            final_button = self.driver.find_element(By.XPATH, "//div[@class='ZZ']//div[@role='button']")
            final_button.click()
            WebDriverWait(self.driver, 30).until(EC.url_contains('filters'))
            time.sleep(random.uniform(2.0,3.0))

            self.task_status = 'Gmail with filter added'

        def forwarding_step_one(self):

            print(f'[{The_time()}] - Starting first step of forwarding.')

            add_forward_in_row_button = self.driver.find_elements(By.XPATH, '//div[@class="f2"]//div[@class="f1"]')[4]
            add_forward_in_row_button.click()
            WebDriverWait(self.driver, 30).until(EC.url_contains('fwdandpop'))
            time.sleep(random.uniform(2.0,3.0))
            
            add_forward_in_tab_button = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="add"]')
            add_forward_in_tab_button.click()
            time.sleep(random.uniform(1.75,3.0))

            email_input = self.driver.find_element(By.XPATH, '//div[@role="alertdialog"]//input[@type="text"]')
            self._dummy_send(email_input, self.forwarded_to)
            time.sleep(random.uniform(1.25,1.75))
            email_input.send_keys(Keys.ENTER)
            time.sleep(random.uniform(1.75,2.25))

            WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be(2))

            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(random.uniform(1.75,2.25))
            submitting = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]')))
            submitting.click()
            time.sleep(random.uniform(1.5,2.25))

            self.driver.switch_to.window(self.driver.window_handles[0])
            confirm_1 = self.driver.find_element(By.XPATH, "//div[@role='alertdialog']//button[@name='ok']")
            confirm_1.click()
            time.sleep(random.uniform(2.0,3.0))

        def forwarding_step_two(self, code):

            print(f'[{The_time()}] - Confirming forward.')

            send_code_input = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="verifyText"]')
            send_code_input.clear()
            time.sleep(random.uniform(1.0,1.5))
            self._dummy_send(send_code_input, code)
            time.sleep(random.uniform(1.25,1.75))

            submit_the_code_button = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@name="verify"]')
            submit_the_code_button.click()
            time.sleep(random.uniform(2.25,3.25))
            
            for x in range(3):
                try:
                    choose_email_forwarding = self.driver.find_element(By.XPATH, '//div[@role="main"]//input[@act="add"]//..//..//table[2]//input')
                    self.driver.execute_script('arguments[0].click()', choose_email_forwarding)
                    time.sleep(random.uniform(2.25,3.25))
                    total_height = int(self.driver.execute_script("return document.body.scrollHeight"))

                    for i in range(1, total_height, random.randint(4,7)):
                        self.driver.execute_script("window.scrollTo(0, {});".format(i))
                    time.sleep(random.uniform(2.25,3.25))
                    
                    save_the_changes = self.driver.find_element(By.XPATH, '//div[@role="main"]//button[@guidedhelpid="save_changes_button"]') 
                    self.driver.execute_script('arguments[0].click()', save_the_changes)
                    
                    WebDriverWait(self.driver, 8).until(EC.url_contains('inbox'))
                    time.sleep(random.uniform(2.75,4.25))
                    break
                except TimeoutException:
                    pass

            try:
                self.driver.find_element(By.XPATH, '//header//..//..//span//a')
                self.task_status = 'Gmail generated and forwarded!'
            except NoSuchElementException:
                self.task_status = 'Gmail generated and probably forwarded!'

    class Tasks:

        settings = json.load(open('settings.json', 'r', encoding="utf-8"))
        m_names = list(csv.DictReader(open('names/m_names.csv', 'r', encoding="utf-8")))
        f_names = list(csv.DictReader(open('names/f_names.csv', 'r', encoding="utf-8")))

        @classmethod
        def get_random_first_name(cls, gender):
            if gender == 'm':
                return random.choice(cls.m_names)["first_name"]
            else:
                return random.choice(cls.f_names)["first_name"]

        @classmethod
        def get_random_last_name(cls, gender):
            if gender == 'm':
                return random.choice(cls.m_names)["last_name"]
            else:
                return random.choice(cls.f_names)["last_name"]

        def __init__(self, to_do, hm=0, hm_for_master=0, masters=[]) -> None:
            self.what_we_do = to_do
            if self.what_we_do == 'gen':
                self.tasks = [Gmail_gen_forward('f') if x%8 == 0 else Gmail_gen_forward('m') for x in range(hm)]
                random.shuffle(self.tasks)
            elif self.what_we_do == 'gen_and_forward':
                self.tasks = [Gmail_gen_forward('f', master_mail=master) if x%8 == 0 else Gmail_gen_forward('m',master_mail=master) for master in masters for x in range(hm_for_master)]
                self.current_master_mail = ''
            elif to_do == 'forward':
                print("")
                dir_name = os.path.dirname(sys.executable)
                files = [z[len(dir_name)+12:] for z in glob(f"{dir_name}/to forward/*.csv")]
                for i,file in enumerate(files):
                    print(f'{i+1}. {file}')
                the_file = files[int(input('\nChoose file with mails you would like to forward: '))-1]
                to_forward = pd.read_csv(open(f'to forward/{the_file}', 'r', encoding="utf-8"))
                if 'task_status' in to_forward.keys():
                    to_forward.drop(to_forward.index[to_forward['task_status'].str.contains("Forward")], inplace=True)
                    to_forward.drop(to_forward.index[to_forward['task_status'].str.contains("forward")], inplace=True)
                self.tasks = [Forwarding(row) for index, row in to_forward.iterrows()]
                self.current_master_mail = ''
            self.today = "-".join((time.strftime("%D_%H-%M-%S", time.localtime())).split("/"))

        def __len__(self):
            return len(self.tasks)

        def data(self, task_number):
            return self.tasks[task_number]
            
        def master_webdriver(self, email=settings['master_mail']):

            try:

                self.current_master_mail = email

                print(f'\n[{The_time()}] - Starting master driver.')

                option = uc.ChromeOptions()
                option.add_argument('--disable-infobars')
                option.add_argument('--disable-notifications')
                option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
                option.add_argument('--disable-gpu')
                option.add_argument('--no-sandbox')
                option.add_argument(f"--window-size={random.randint(1250,1300)},{random.randint(1060,1130)}")
                option.add_argument('--user-data-dir={}\\masters profiles\\{}'.format(os.path.dirname(sys.executable), email))
                driver = uc.Chrome(options=option)
                
                driver.get('https://mail.google.com/mail/u/0/')

                time.sleep(random.uniform(3.0, 4.5))
                print(f'\n[{The_time()}] - Adding filter to master driver.')

                filter = WebDriverWait(driver, timeout=20, poll_frequency=random.uniform(0.5,1.0)).until(EC.element_to_be_clickable((By.XPATH, "//header//form//button[@role='button' and @type='button']")))
                filter.click()
                
                try:
                    WebDriverWait(driver, timeout=random.uniform(7.25, 8.5)).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ZZ']//input")))
                except TimeoutException:
                    driver.refresh()
                    filter = WebDriverWait(driver, timeout=20, poll_frequency=random.uniform(0.5,1.0)).until(EC.element_to_be_clickable((By.XPATH, "//header//form//button[@role='button' and @type='button']")))
                    filter.click()
                    WebDriverWait(driver, timeout=random.uniform(7.25, 8.5)).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ZZ']//input")))
                finally:
                    time.sleep(random.uniform(3.0, 3.75))

                add_from_who_mail_is_expected = driver.find_elements(By.XPATH, "//div[@class='ZZ']//input")[0]
                Gmail_gen_forward._dummy_send(driver, add_from_who_mail_is_expected, 'forwarding-noreply@google.com')
                try:
                    WebDriverWait(driver, timeout=random.uniform(2.25, 3.5)).until(EC.presence_of_element_located((By.XPATH, '//ul[@role="listbox"]//div')))
                    time.sleep(random.uniform(1.0, 1.75))
                    add_from_who_mail_is_expected.send_keys(Keys.ENTER)
                    was_pop_up = True
                except TimeoutException:
                    was_pop_up = False

                time.sleep(random.uniform(1.5, 2.25))
                if was_pop_up:
                    list_of_type = driver.find_elements(By.XPATH, '//div[@role="option"]')[4]
                else:
                    list_of_type = driver.find_elements(By.XPATH, '//div[@role="option"]')[3]
                list_of_type.click()

                time.sleep(random.uniform(1.5, 2.25))

                unread = driver.find_elements(By.XPATH, '//div[@role="option" and @title]')[10]
                unread.click()

                time.sleep(random.uniform(1.5, 2.25))

                submit_button = driver.find_element(By.XPATH, "//div[@class='ZZ']//div[@role='button']")
                submit_button.click()

                self.driver = driver
            except:
                try:
                    driver.quit()
                except:
                    pass
                finally:
                    self.master_webdriver(email=self.current_master_mail)

        def getting_forwarding_code(self, email):

            print(f'[{The_time()}] - Getting the code.')

            time.sleep(random.uniform(8.5,10.0))
    
            retries = 0
            while retries < 10:  ## gettings forwarding code
                try:                
                    email_table  = self.driver.find_elements(By.XPATH, "//div[@role='main']//tr[@role='row']//td[@role='gridcell']")[0]
                    check_email = self.driver.find_elements(By.XPATH, "//div[@role='main']//tr[@role='row']//td[@role='gridcell']//span//span[@data-thread-id]")[0]
                    if email in check_email.text:
                        break
                    self.driver.refresh()
                except (NoSuchElementException,ElementClickInterceptedException, IndexError):
                    self.driver.refresh()
                    time.sleep(random.uniform(3.0,4.5))
                    retries += 1
                except (TimeoutException, NewConnectionError):
                    try:
                        self.driver.quit()
                    except: pass 
                    self.master_webdriver(email = self.current_master_mail)
                except Exception as e:
                    print(e)

            time.sleep(random.uniform(2.5,4.0))
            while retries < 10:
                try:
                    url = self.driver.current_url
                    email_table.click()
                    time.sleep(random.uniform(3.0,4.5))
                    if url != self.driver.current_url:
                        break
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    try:
                        menu_button = self.driver.find_element(By.XPATH, '//header//div[@data-ogmb="1"]')
                        menu_button.click()
                        time.sleep(random.uniform(2.25,3.5))
                        email_table  = self.driver.find_elements(By.XPATH, "//div[@role='main']//tr[@role='row']//td[@role='gridcell']")[0]
                        email_table.click()
                        time.sleep(random.uniform(3.5,4.5))
                        if url != self.driver.current_url:
                            break
                    except IndexError:
                        self.driver.refresh()
                    self.driver.refresh()

            time.sleep(random.uniform(3.5,4.5))

            the_code = self.driver.find_element(By.XPATH, "//div[@role='main']//h2").text.split("#")[1][:9].split(")")[0]

            self.driver.back()
                
            return the_code

        def delete_all_emails(self):
            
            if not self.driver.current_url == 'https://mail.google.com/mail/u/0/#advanced-search/from=forwarding-noreply%40google.com&subset=unread&within=1d&sizeoperator=s_sl&sizeunit=s_smb&query=is%3Aunread+from%3A(forwarding-noreply%40google.com)':
                self.driver.get('https://mail.google.com/mail/u/0/#advanced-search/from=forwarding-noreply%40google.com&subset=unread&within=1d&sizeoperator=s_sl&sizeunit=s_smb&query=is%3Aunread+from%3A(forwarding-noreply%40google.com)')
            else:
                self.driver.refresh()
            time.sleep(random.uniform(3.0,5.0))

            try:
                select_all = self.driver.find_element(By.XPATH, '//span[@role="checkbox" and @dir="ltr"]')
                self.driver.execute_script('arguments[0].click()', select_all)
                remove = self.driver.find_elements(By.XPATH, '//div[@role="button" and @act="10"]')[1]
                self.driver.execute_script('arguments[0].click()', remove)

                print(f'[{The_time()}] - Reseted master mail.')
            except:
                var = traceback.format_exc()
                print(var)

        def logs(self):
            if self.what_we_do == 'gen_and_forward':
                headers = ['task_status', 'first_name', 'last_name', 'gender', 'email', 'password', 'recovery_email', 'forwarded_to']
                log_name = f'logs/gen-and-forward-logs-{self.today}.csv'
            elif self.what_we_do == 'gen':
                headers = ['task_status', 'first_name', 'last_name', 'gender', 'email', 'password', 'recovery_email',]
                log_name = f'logs/gen-logs-{self.today}.csv'
            else:
                headers = ['task_status', 'first_name', 'last_name', 'gender', 'email', 'password', 'recovery_email', 'forwarded_to']
                log_name = f'logs/forward-logs-{self.today}.csv'

            with open(log_name, 'w', newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                for task in self.tasks:
                    to_save_data = task.__dict__
                    if self.what_we_do == 'gen_and_forward' or self.what_we_do == 'gen':
                        to_save_data['email'] = to_save_data['username'] + '@gmail.com'
                    writer.writerow(to_save_data)

        def single_task_log(self, task):
            if 'orward' in task.task_status:
                headers = ['first_name', 'last_name', 'gender', 'email', 'password', 'recovery_email', 'forwarded_to']
                if not os.path.isfile(f'{os.path.dirname(sys.executable)}\\mails forwarded to by masters\\{task.forwarded_to}.csv'):
                    with open(f'{os.path.dirname(sys.executable)}\\mails forwarded to by masters\\{task.forwarded_to}.csv', 'w', newline='', encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                        writer.writeheader()
                        to_save_data = task.__dict__
                        if self.what_we_do == 'gen_and_forward':
                            to_save_data['email'] = to_save_data['username'] + '@gmail.com'
                        writer.writerow(to_save_data)
                else:
                    with open(f'{os.path.dirname(sys.executable)}\\mails forwarded to by masters\\{task.forwarded_to}.csv', 'a', newline='', encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                        to_save_data = task.__dict__
                        if self.what_we_do == 'gen_and_forward':
                            to_save_data['email'] = to_save_data['username'] + '@gmail.com'
                        writer.writerow(to_save_data)

    def get_masters():
            print('\n0. Select all')
            folder = f'{os.path.dirname(sys.executable)}\\masters profiles'
            all_masters = {}
            was_mastercsv = False
            for x,filename in enumerate(os.listdir(folder)):
                if filename != 'masters.csv':
                    if was_mastercsv:
                        print(f'{x}. {filename}')
                        all_masters.update({f'{x}': filename})
                    else:
                        print(f'{x+1}. {filename}')
                        all_masters.update({f'{x+1}': filename})
                else:
                    was_mastercsv = True
            masters = input('\nChoose masters (For example: 1,4,5): ').split(",")
            if '0' in masters:
                return [value for value in all_masters.values()]
            return [all_masters[z] for z in masters if z in all_masters.keys()]

    def changing_ip(return_to_menu = False):

        def internet_ip_check():
            url = "https://api.ipify.org"
            timeout = 5
            while True:
                try:
                    ip = requests.get(url, timeout=timeout)
                    return ip.text
                except (requests.ConnectionError, requests.Timeout):
                    pass

        def turn_on_airplane_mode():
            print(f'[{The_time()}] - Turning on Airplane Mode...')
            cmd_one = "adb shell settings put global airplane_mode_on 1"
            subprocess.call(cmd_one, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            time.sleep(0.5)
            cmd_one = "adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true"
            subprocess.call(cmd_one, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        def turn_off_aiplane_mode():

            print(f'[{The_time()}] - Turning off Airplane Mode...')

            cmd_two = "adb shell settings put global airplane_mode_on 0"
            subprocess.call(cmd_two, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            time.sleep(0.5)
            cmd_two = "adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false"
            subprocess.call(cmd_two, shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        ip_before = internet_ip_check()
        turn_on_airplane_mode()
        time.sleep(2)
        turn_off_aiplane_mode()
        ip_after = internet_ip_check()

        if ip_before != ip_after:
            print(f'[{The_time()}] - Successfully prepared new IP Adress!')
        else:
            print(f'[{The_time()}] - IP not changed! Retrying...')
            changing_ip()        
        if return_to_menu:
            what_to_do()

    def connect_device():
        print(f"\n[{The_time()}] - Connecting...")

        subprocess.call('adb.exe devices', shell=True, cwd='platform-tools', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        time.sleep(3)
        
        client = AdbClient(host="127.0.0.1", port=5037)

        devices = client.devices()

        if len(devices) != 0:
            device = devices[0]
            print(f'[{The_time()}] - Connected to {device}')
        else:
            print(f'[{The_time()}] - No device attached')

        time.sleep(2)
        os.system('CLS')
            
        what_to_do()

    def create_and_forward_gmails():

        masters = get_masters()
        n_of_tasks = int(input("Input how much emails do you want to generate and forward for each master: "))
        tasks = Tasks('gen_and_forward', hm_for_master = n_of_tasks, masters=masters)
        for x in range(len(tasks)):
            print(f'\n[{The_time()}] Task [{x+1}] - Generating and forwarding gmail.\n')
            try:
                task = tasks.data(x)
                if tasks.current_master_mail != task.forwarded_to:
                    if tasks.current_master_mail == '':
                        tasks.master_webdriver(email=task.forwarded_to)
                    else:
                        tasks.driver.quit()
                        tasks.master_webdriver(email=task.forwarded_to)
                changing_ip()
                task.start_webdriver()
                task.first_step_register()
                task.sms_verification()
                task.complete_personal_details()
                task.complete_personalization()
                task.complete_reccomended_settings()
                task.complete_tos()
                task.get_mail_page_and_accept_settings()
                task.adding_filter()
                task.forwarding_step_one()
                task.forwarding_step_two(tasks.getting_forwarding_code(task.username))
                task.driver.quit()
                print(f'\n[{The_time()}] - Successfully generated and forwarded!.\n')
            except:
                var = traceback.format_exc()
                print(var)
                try:
                    task.driver.quit()
                except:
                    pass
                if task.task_status == 'Gmail Generated':
                    print(f'\n[{The_time()}] - Successfully generated gmail (no filtering was set).\n')
                elif task.task_status == 'Gmail with filter added':
                    print(f'\n[{The_time()}] - Successfully generated and set filter!.\n')
                elif task.task_status == 'Gmail generated and probably forwarded!':
                    tasks.delete_all_emails()

            tasks.logs()
            tasks.single_task_log(task)

    def create_accounts():

        n_of_tasks = int(input("Input how much emails do you want to generate: "))
        tasks = Tasks('gen', hm = n_of_tasks)
        for x in range(len(tasks)):
            print(f'\n[{The_time()}] Task [{x+1}] - Generating gmail.\n')
            try:
                task = tasks.data(x)
                changing_ip()
                task.start_webdriver()
                task.first_step_register()
                task.sms_verification()
                task.complete_personal_details()
                task.complete_personalization()
                task.complete_reccomended_settings()
                task.complete_tos()
                task.get_mail_page_and_accept_settings()
                task.adding_filter()
                task.driver.quit()
                print(f'\n[{The_time()}] - Successfully generated and set filter!.\n')
            except Exception as e:
                print(e)
                try:
                    task.driver.quit()
                except:
                    pass
                if task.task_status == 'Gmail Generated':
                    print(f'\n[{The_time()}] - Successfully generated gmail (no filtering was set).\n')

            tasks.logs()

    def forward_gmails():
        tasks = Tasks(to_do='forward')
        print(f'\n[{The_time()}] - Forwarding {len(tasks)} emails!.\n')
        for x in range(len(tasks)):
            try:
                task = tasks.data(x)
                if tasks.current_master_mail != task.forwarded_to:
                    if tasks.current_master_mail == '':
                        tasks.master_webdriver(email=task.forwarded_to)
                    else:
                        tasks.driver.quit()
                        tasks.master_webdriver(email=task.forwarded_to)
                print(f'\n[{The_time()}] Task [{x+1}] - Forwarding gmail.\n')
                changing_ip()
                task.start_webdriver()
                task.login()
                task.to_gmail_page()
                if not task.is_already_forwarded():
                    task.navigate_to_settings()
                    task.forwarding_step_one()
                    task.forwarding_step_two(tasks.getting_forwarding_code(task.username)) 
                else:
                    task.task_status =  'Gmail forwarded!'
                task.driver.quit()
                print(f'\n[{The_time()}] - Successfully forwarded!.\n')
            except Exception as e:
                task.task_status = 'Failed'
                print(e)
                print(f'\n[{The_time()}] - Forwarding Failed.\n')

            tasks.logs()
            tasks.single_task_log(task)

    def create_master_gmail_profiles():

        masters_to_do = list(csv.DictReader(open('masters profiles/masters.csv', 'r', encoding="utf-8")))
        masters_that_exist = os.listdir(f'{os.path.dirname(sys.executable)}\\masters profiles')

        for x in range(len(masters_to_do)):
            if masters_to_do[x]['email'] not in masters_that_exist:
                try:
                    print(f"{x+1}. Making {masters_to_do[x]['email']} profile.")
                    option = uc.ChromeOptions()
                    option.add_argument(f"--window-size={random.randint(1250,1300)},{random.randint(1060,1130)}")
                    option.add_argument('--user-data-dir={}\\masters profiles\\{}'.format(os.path.dirname(sys.executable),masters_to_do[x]['email']))
                    option.add_argument('--keep_user_data_dir=true')
                    driver = uc.Chrome(options=option)
                    driver.get('https://accounts.google.com/signin')
                    time.sleep(random.uniform(1.5, 3.5))
                    email_input = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]')))
                    Gmail_gen_forward._dummy_send(driver, email_input, masters_to_do[x]['email'])
                    email_input.send_keys(Keys.ENTER)
                    time.sleep(random.uniform(1.5, 3.5))
                    password_input = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]')))
                    Gmail_gen_forward._dummy_send(driver, password_input, masters_to_do[x]['password'])
                    password_input.send_keys(Keys.ENTER)
                    WebDriverWait(driver, timeout=10).until(EC.url_contains('myaccount.google.com'))
                    time.sleep(random.uniform(3.75, 5.5))
                    driver.close()
                except:
                    driver.keep_user_data_dir = False
                    driver.quit()
                    print(f"{x+1}. Error making {masters_to_do[x]['email']} profile.")
        what_to_do()

    def open_master_gmail_profiles():
        masters = get_masters()
        for x,email in enumerate(masters):
            print(f'\n[{The_time()}] Task [{x+1}] - Starting {email} profile.\n')

            option = uc.ChromeOptions()
            option.add_argument('--disable-infobars')
            option.add_argument('--disable-notifications')
            option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            option.add_argument('--disable-gpu')
            option.add_argument('--no-sandbox')
            option.add_argument(f"--window-size={random.randint(1250,1300)},{random.randint(1060,1130)}")
            option.add_argument('--user-data-dir={}\\masters profiles\\{}'.format(os.path.dirname(sys.executable), email))
            option.add_argument('--keep_user_data_dir=true')
            driver = uc.Chrome(options=option)
            input("Click anything when done.")
            try:
                driver.quit()
            except:
                pass
        what_to_do()

    def delete_master_gmail_profiles():
        folder = f'{os.path.dirname(sys.executable)}\\masters profiles'
        for filename in os.listdir(folder):
            if not filename == 'masters.csv':
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        print(f"\n[{The_time()}] - Successfully deleted profile.")
        what_to_do()

    def test():
        masters = get_masters()
        for x,email in enumerate(masters):
            print(f'\n[{The_time()}] Task [{x+1}] - Starting {email} profile.\n')

            option = uc.ChromeOptions()
            option.add_argument('--disable-infobars')
            option.add_argument('--disable-notifications')
            option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            option.add_argument('--disable-gpu')
            option.add_argument('--no-sandbox')
            option.add_argument(f"--window-size={random.randint(1250,1300)},{random.randint(1060,1130)}")
            option.add_argument('--user-data-dir={}\\masters profiles\\{}'.format(os.path.dirname(sys.executable), email))
            option.add_argument('--keep_user_data_dir=true')
            driver = uc.Chrome(options=option)
            print(Tasks.getting_forwarding_code(driver))
        
        what_to_do()

    def what_to_do():
        print("\nWhat do you want to do?\n")
        print("1. Connect Device.")
        print("2. Try changing ip.")
        print("3. Create and forward accounts.")
        print("4. Create accounts.")
        print("5. Forward Gmails.")
        print("6. Create master gmail profiles.")
        print("7. Open master gmail profiles.")
        print("8. Delete master gmail profiles.")
        choose = input("\nChoose one option: ")
        if choose == "1":
            connect_device()
        elif choose == "2":
            changing_ip(return_to_menu = True)
        elif choose == "3":
            create_and_forward_gmails()
        elif choose == "4":
            create_accounts()
        elif choose == "5":
            forward_gmails()
        elif choose == '6':
            create_master_gmail_profiles()
        elif choose == '7':
            open_master_gmail_profiles()
        elif choose == '8':
            delete_master_gmail_profiles()
        elif choose == '666':
            test()
        else:
            print("\nWrong input!")
            what_to_do()

    what_to_do()

if __name__ == "__main__":
    main()