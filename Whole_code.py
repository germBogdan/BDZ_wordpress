import urllib, re, sys
import selenium.common
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
    else:
        if not netloc:
            url=scheme+"://"+url
        else:
            url=scheme+"://"+netloc
    if "//localhost" in url or "//127.0.0.1" in url:
        url="http://127.0.0.1/wordpress"
    return url

def Check_WP_and_search_version (url):
    

    agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {}
    headers['User-Agent'] = agent
    #Вводим адрес сервиса
    #print("Введите адрес (пример: 127.0.0.1/wordpress или example.com)\n")
    #url = input()
    print("Make sure it's WordPress.")
   
    #Проверяем, является ли эта CMS Wordpress-ом
    req = urllib.request.Request(url+"/wp-config.php")
    try:
        htmltext = urlopen(req, timeout=3).read()
        if htmltext == b'':
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
            print("Time out. Probobly this is not Wordpress")
            sys.exit()
    #Определяем версию ворд пресса
    print("Recognizing version. Pleas wait...")
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
            print("Can't find version using HTML code of padge.")
            sys.exit()
        else:
            print("Wordpress Version: "+version[0])
            return version[0] 
    except (urllib.error.HTTPError, IndexError) as e:
        print("Can't find version using HTML code of padge.")
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
            sys.exit()
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
url=input("Enter URL(e.g. 127.0.0.1/wordpress or example.com):\n")
url=Check_URL(url)
version=Check_WP_and_search_version(url)
Search_vulnerabilities(version)

