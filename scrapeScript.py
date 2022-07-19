import requests

from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
from .credentials import PATH_TO_DRIVER
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')


NicknameToCheck = []

stopButtonXpath = "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/div[1]/div/div[5]/section/div/header/div[2]/div[2]/button[1]"
storyContentXpath = "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/div[1]/div/div[5]/section/div/div[1]/div/div/img"
nextButtonXpath = "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/div[1]/div/div[5]/section/div/button[2]"
closeButtonXpath = "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/div[3]/button"
storyVideoXpath = "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/div[1]/div/div[5]/section/div/div[1]/div/div/video/source"
nextMenuButtonInit ="/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/main/section/div/div[2]/div/div/button"
nextMenuButtonAfter ="/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div[1]/section/div/div[2]/div/div/button[2]"

class instaBot:
    def __init__(self,nicknameToCheck = NicknameToCheck,login = "", pw =""):
        self.nicknameToCheck = nicknameToCheck
        self.LOGIN = login
        self.PW = pw
        self.driver =None
        self.firstClicked = False
        self.nextMenuButton = None
    def changeNames(self , nicknameToCheck):
        self.nicknameToCheck = nicknameToCheck

    def login(self):
        self.driver = Chrome(executable_path=PATH_TO_DRIVER,chrome_options=chrome_options)
        self.driver.get("https://instagram.com")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/button[1]"))).click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    "input[name='username']"))).send_keys(self.LOGIN)
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    "input[name='password']"))).send_keys(self.PW)
        sleep(1)
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/section/main/div/div/div/div/button"))).click()
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[3]/button[2]"))).click()
        except:
            pass
        sleep(2)

    def checkStories(self) -> dict:
        nicknamesToBeChecked = set(self.nicknameToCheck)
        nicknamesToStories = {name: [] for name in nicknamesToBeChecked}
        self.nextMenuButton = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
        while (len(nicknamesToBeChecked) != 0):
            checkedNames = set()
            sleep(2)

            for name in nicknamesToBeChecked:
                result = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Story by " + name + ", not seen']")
                if (len(result) != 0):
                    try:
                        result[0].click()
                    except:
                        break

                    nextButton = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.
                                                                                                XPATH,
                                                                                                nextButtonXpath)))
                    closeButton = self.driver.find_element(By.XPATH, closeButtonXpath)
                    stopButton = self.driver.find_element(By.XPATH, stopButtonXpath)

                    while (len(self.driver.find_elements(By.CSS_SELECTOR, f"a[href='/{name}/']")) != 0):
                        stopButton.click()
                        content = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.
                                                XPATH,storyContentXpath))).get_attribute("srcset").split(",")[0][:-5]
                        videoContent = self.driver.find_elements(By.XPATH, storyVideoXpath)
                        if(len(videoContent) != 0):
                            content = videoContent[0].get_attribute("src")
                        nicknamesToStories[name].append(content)
                        sleep(0.1)
                        nextButton.click()
                    else:
                        closeButton.click()
                    checkedNames.add(name)
                    self.firstClicked = False
                    self.nextMenuButton = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                    sleep(1)
            for name in checkedNames:
                nicknamesToBeChecked.remove(name)

            if ((not self.firstClicked)):
                if(len(self.driver.find_elements(By.XPATH, nextMenuButtonAfter)) != 0):
                    self.nextMenuButton = self.driver.find_elements(By.XPATH, nextMenuButtonAfter)[0]
                    self.firstClicked = True
                    print("Transfer to alternative")
                else:

                    #print("XPATH:"+str(self.driver.find_elements(By.XPATH, nextMenuButtonAfter)))
                    try:
                        self.nextMenuButton = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                    except:
                        print("Error - refreshing the page")
                    print("Back to orig")

            try:
                self.nextMenuButton.click()
                sleep(1)
            except Exception as e:
                self.firstClicked =False
                print("Exception:"+str(e))
                print('No new stories')
                break

        self.driver.get("https://instagram.com")
        return nicknamesToStories