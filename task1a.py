'''
    Problem Statement : Web Crawling and Extracting Information [ Task 1 ]
    Author : Adarsh G Krishnan [21CS60R55]
    Run command : python task1.py
    operating system : Linux (UBUNTU 20.04)
    Time stamp : 10/02/2022
'''

#!/usr/bin/python3
from urllib.request import Request, urlopen

#Function to fetch HTML File.
def getHTML(url,filename):
    req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    webpage = web_byte.decode('utf-8')
    f = open(filename, 'w',encoding="utf-8")
    f.write(webpage)
    f.close

#Function to fetch Main page as HTML File.
def fetchMainHTML(url):
    getHTML(url,"Main.html")

#Function to fetch Individual Country HTML File.
def fetchCountryHTML(url):
    f=open("worldometers_countrylist.txt","r")
    continent=["Europe:","North America:","Asia","South America","Africa","Oceania"]
    for line in f:
        if(line=='\n' or '-' in line or line[:-1] in continent):
            continue
        line=line.replace(' ','-')
        line=line.replace('\n','')

        #print(line+'*')
        url1=url+line+'/'
        #print(url1)
        line=line.replace('-',' ')
        link=line+'1.html'
        #print(link)
        if line.lower() in "usa":
            url1=url+'us/'
        elif line.lower() in "vietnam":
            url1=url+'viet-nam/'
        
        getHTML(url1,link)

#Driver Function
def main():

    #Fetching Main website HTML.
    url = 'https://www.worldometers.info/coronavirus/'
    fetchMainHTML(url)

    #Fetching countrywise HTML.
    url=url+'/country/'
    fetchCountryHTML(url)

if __name__ == "__main__":
	main()