#Application that logs into a website using requests and lxml.html libraries
#Resources:
#https://brennan.io/2016/03/02/logging-in-with-requests/
#http://kazuar.github.io/scraping-tutorial/
#http://docs.python-guide.org/en/latest/scenarios/scrape/
#https://www.w3schools.com/xml/xpath_intro.asp

import requests, lxml.html

login_url = 'https://www.revitcity.com/login.php'
logoff_url = 'https://www.revitcity.com/logoff.php'
user_login = 'bkkoech'
user_password = '8XEQWRUGd'
#initiate session
s = requests.session()
#make GET request to login page
login = s.get(login_url)
print("Page received successfully...")

#convert login text to html
login_html = lxml.html.fromstring(login.text)

#find hidden cookies
hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

#print cookies
print("cookies:", form)

#reached here, still testing everything, use Command + / to uncomment
# #login
# #append login and password to form(login and pass are page specific)
# form['login'] = user_login
# form['pass'] = user_password

# print("form updated:\n", form)
# #send the form
# response = s.post(login_url, data = form)

# print(response.url)

# #check if login is successful

# #scrape response url
# print("scraping index.html...")
# result = s.get('https://www.revitcity.com/index.php')
# #create tree
# tree = lxml.html.fromstring(result.text)
# print("Resulting tree:", tree)
# #extract welcome username from tree using xpath
# welcome_username = tree.xpath('//*[@id="container"]/table[1]/tbody/tr[2]/td/p[2]')
# print("Welcome username!", welcome_username)

# if(welcome_username == 'Welcome bkkoech!'):
# 	print("Login successful")
# else:
# 	print("Failed to log in")

# print("logging off...")
# logoff_response = s.get(logoff_url)

"""
def main():
    #Main entry point for the script.


if __name__ == '__main__':
    main()
"""