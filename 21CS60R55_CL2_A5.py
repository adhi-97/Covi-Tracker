
'''
    Problem Statement : Web Crawling and Extracting Information Part 2
    Author : Adarsh G Krishnan [21CS60R55]
    Run command : python3 21CS60R55_CL2_A5.py
    Time stamp : 28/02/2022
'''

#!/usr/bin/python3
from urllib.request import Request, urlopen
import os
from pandas import to_datetime
import ply.lex as lex
import ply.yacc as yacc
import re
import datetime
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
from task1b import fetchCountryData
warnings.filterwarnings("ignore")

def t_error(t):
    t.lexer.skip(1)

def p_error(t):
    pass

#Defining Grammer
t_ignore = " \t "

currDate=""
key = ""
filtered_date=""
unfiltered_date=""
currYear=""
currMonth=""
currDay=""
count=0
countryRange={}
today=datetime.datetime.now()

#Function to fetch HTML File.
def getHTML(url,filename):

    req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    webpage = web_byte.decode('utf-8')
    f = open(filename, 'w',encoding="utf-8")
    f.write(webpage)
    f.close

#Function to fetch Main page as HTML File.
def fetchMainWikiHTML(url):
    getHTML(url,"MainWiki.html")

#Function to fetch worldwidde timelines & Response by month and year.
def wikiDataInTimeRange():

    #Fetching data from Main wiki.html's.
    f1=open("MainWiki.html","r")
    f2=open("wikiDataInTimeRange.html","w")
    ctr=0
    for line in f1:
        if line.strip() == """<h2><span class="mw-headline" id="Worldwide_timelines_by_month_and_year">Worldwide timelines by month and year</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic&amp;action=edit&amp;section=1" title="Edit section: Worldwide timelines by month and year">edit</a><span class="mw-editsection-bracket">]</span></span></h2>""":
            ctr = 1
            continue
        if line.strip() == """<dl><dt>Responses</dt></dl>""":
            ctr = 0
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open('wikiDataInTimeRange.html','r')
    content=file.read()
    file.close()

    TimelineFileNames=[]
    ResponseFileNames=[]

    url1='https://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic_in_'
    url2='https://en.wikipedia.org/wiki/Responses_to_the_COVID-19_pandemic_in_'


    def t_LMandY(t):
        r'''(<ul><li><a\shref\=\"[A-Za-z0-9\,\_ \= \" \"\/\+ \"\.\.\" \- \# \+]+>) | (<li><a\shref\=\"[A-Za-z0-9\,\_ \= \" \"\/\+ \"\.\.\" \- \# \+]+>)'''
        #print(t.value+'*')
        return t
    
    def t_Name(t):
        r'''[A-Z,a-z, 0-9]+'''
        #print(t.value+'*')
        return t

    def p_start(p):
        '''start : wikiMandY'''
    
    def p_wikiMandY(p):
        '''wikiMandY : LMandY Name'''

        p[0]=p[2]
        filename=p[0]
        filename=str(filename).replace(" ","_")
        link1=url1+filename
        link2=url2+filename
        filename1=filename+'_Timeline'+'.html'
        filename2=filename+'_Response'+'.html'
        #print(filename)
        getHTML(link1,filename1)
        getHTML(link2,filename2)

        TimelineFileNames.append(filename1)
        ResponseFileNames.append(filename2)


    tokens=['LMandY','Name']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    return TimelineFileNames,ResponseFileNames

#Function to handle Special Date.
def handleSpecialKey(content):
    
    line='<h3><span id="11.E2.80.9312_January"></span><span class="mw-headline" id="11–12_January">'

    end=line[0:3]
    pattern = re.compile(line)
    result = pattern.search(content)

    strt = result.start()
    content[result.start()]

    index = strt + 1
    news = ''
    while (content[index:index + 3] != end):

        index += 1

        if(key[6:10]!='2019'):
            if(key[3:5]=='04' or key[3:5]=='06' or key[3:5]=='09' or key[3:5]=='11'):
                if(key[0:2]=='30'):
                    end='<h2'

            elif(key[3:5]=='02'):
                if(key[6:10]!='2020'):
                    if(key[0:2]=='29'):
                        end='<h2'
                else:
                    if(key[0:2]=='28'):
                        end='<h2'
            else:
                if(key[0:2]=='31'):
                    end='<h2'
                
    
    news = content[strt:index]
    tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
    news = re.sub(tag_re, '', news)
    news=news.replace('11–12 January',"")

    return news

#Function to handle Special Date.
def handleSpecialKey1(content,mode):

    
    if(mode==1):
        line='<li><b>8 January:</b>'
    if(mode==2):
        line='<li><b>30 December:</b>'

    pattern = re.compile(line)
    result = pattern.search(content)

    strt = result.start()
    content[result.start()]

    index = strt + 7
    news = ''
    if mode==1:
        while (content[index:index + 5] != '</li>'):
            index += 1
    else:
        while ((content[index:index + 3] != '<h3')):
                    index += 1
    
    news = content[strt:index]
    tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
    news = re.sub(tag_re, '', news)
    if mode==1:
        news=news.replace('8 January:',"")
    else:
        news=news.replace('30 December:',"")
    
    return news

#Function to find Date Range of a country.
def FindRange(chosenCountry):

    global countryRange

    return countryRange[chosenCountry]

#Function to compare 2 dates.
def comparator(date1,date2):

    day1=int(date1[0:2])
    month1=int(date1[3:5])
    year1=int(date1[6:10])

    day2=int(date2[0:2])
    month2=int(date2[3:5])
    year2=int(date2[6:10])

    if(year2<year1):
        return 0
    elif(year2==year1):
        if(month2<month1):
            return 0
        elif(month2==month1):
            if(day2<day1):
                return 0
            elif(day2==day1):
                return 0
    
    return 1

#Function to get text from the responses and timeline html files for each day.
def fetchTimelineData(TimelineFileNames):

    TimelineContent={}

    AvailableMonth=['January','February','March','April','May','June','July','August','September','October','November','December']

    i=0
    
    #TimelinesContentFetch.
    for item in TimelineFileNames:

        if item=='March_2022_Timeline.html':
            continue

        f1=open(item,"r")
        f2=open("temp.html","w")
        ctr=0
        for line in f1:
            if line.strip() == """<li class="toclevel-1 tocsection-22"><a href="#External_links"><span class="tocnumber">15</span> <span class="toctext">External links</span></a></li>""" or "Pandemic chronology" in line.strip():
                ctr = 1
                continue
            if line.strip()=="""<ul><li><a href="/wiki/Timeline_of_the_COVID-19_pandemic" title="Timeline of the COVID-19 pandemic">Timeline of the COVID-19 pandemic</a></li></ul>""" or """<table class="wikitable sortable">""" in line.strip() or '''"Summary"''' in line.strip():
                ctr = 0
                if '''"Summary"''' in line.strip():
                    f2.write("<h2")
                continue
            if(ctr==1):
                f2.write(line)

        f1.close()
        f2.close()

        file=open("temp.html",'r')
        content=file.read()
        file.close()
        
        year=""
        ls=str(item).split("_")
        if(len(ls)==2):
            year='2019'
        else:
            year=ls[1]

        #print(item)

        def t_LTimeline(t):
            r'''(<h2><span\sclass="mw-headline"\sid="[0-9]+[\_A-Za-z]+">) | (<h3><span\sclass="mw-headline"\sid="[0-9]+[\_A-Za-z]+">)'''
            #print(t.value+'*')
            return t
        
        def t_Date(t):
            r'''([0-9]+\s[A-Z,a-z]+)'''
            #print(t.value+'*')
            return t

        def p_start1(p):
            '''start1 : Timeline'''

        def p_Timeline(p):
            '''Timeline : LTimeline Date'''
            
            p[0]=p[2]
            #print(p[0])
            
            global filtered_date,unfiltered_date

            unfiltered_date=str(p[0])
            filtered_date=unfiltered_date.replace(' ','_')

            date=str(p[0]).split(" ")
            if(len(date[0])==1):
                date[0]='0'+date[0]
            
            day=date[0]
            month=AvailableMonth.index(date[1])+1
            month=str(month)
            if(len(month)==1):
                month='0'+month
            
            global currDate,key

            key=day+'-'+month+'-'+year

            TimelineContent[key]=[]

            specialKey=""
            if(('12-01-2020' not in TimelineContent.keys()) and year=='2020' and month=='01' and day=='11'):
                TimelineContent['12-01-2020']=[]
                specialKey=specialKey+"12-01-2020"

            currDate=key
            #print(key)

            
            line='<h3><span class="mw-headline" id="' +filtered_date + '">'+unfiltered_date+'</span>'
            if key[6:10]=='2019':
                line='<h2><span class="mw-headline" id="'+filtered_date+'">'+unfiltered_date+'</span>'
            if key=='12-01-2020':
                line='<h3><span id="11.E2.80.9312_January"></span><span class="mw-headline" id="11–12_January">'

            end=line[0:3]
            pattern = re.compile(line)
            result = pattern.search(content)

            strt = result.start()
            content[result.start()]

            index = strt + 1
            news = ''
            while (content[index:index + 3] != end):

                index += 1

                ToDay=today.day
                ToMonth=today.month

                if(ToDay<10):
                    ToDay='0'+str(ToDay)
                else:
                    ToDay=str(ToDay)

                if(ToMonth<10):
                    ToMonth='0'+str(ToMonth)
                else:
                    ToMonth=str(ToMonth)
                

                if(key[6:10]!='2019'):
                    if(key[3:5]=='04' or key[3:5]=='06' or key[3:5]=='09' or key[3:5]=='11'):
                        if(key[0:2]=='30'):
                            #print("I'm Here1")
                            end='<h2'

                    elif(key[3:5]=='02'):
                        if(key[6:10]=='2020'):
                            if(key[0:2]=='29'):
                                #print("I'm Here2")
                                end='<h2'
                        else:
                            if(key[0:2]=='28'):
                                #print(key[0:2])
                                end='<h2'
                    else:
                        if(key[0:2]=='31'):
                            #print("I'm Here4")
                            end='<h2'
                        elif(key[0:2]==ToDay and str(today.year)==key[6:10] and key[3:5]==ToMonth):
                            print("I'm Here")
                            end='<h2'
                        elif (key[0:2]=='0'+str(today.day-1) and str(today.year)==key[6:10] and key[3:5]==ToMonth):
                            end='<h2'
            
            news = content[strt:index]
            tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
            news = re.sub(tag_re, '', news)
            news=news.replace(unfiltered_date,"")
            TimelineContent[key].append(news)
            #print(news+'*')

            if(specialKey=='12-01-2020'):
                #print(specialKey)
                specialNews=handleSpecialKey(content)
                #print(specialNews+'*')
                TimelineContent['12-01-2020'].append(specialNews)
                specialKey=""
            
        tokens=['LTimeline','Date']

        #Defining Lexer
        lexer=lex.lex()
        lexer.input(content)

        #defining parser.
        parser = yacc.yacc()
        parser.parse(content,lexer=lexer)

        i+=1

    return TimelineContent

#Function to get text from the responses and timeline html files for each day.
def fetchResponseData(ResponseFileNames):

    AvailableMonth=['January','February','March','April','May','June','July','August','September','October','November','December']
    ResponseContent={}

    i=0
    #ResponseContentFetch.
    for item in ResponseFileNames:
        if item=='March_2022_Response.html':
            continue
        f1=open(item,"r")
        f2=open("temp.html","w")
        ctr=0
        for line in f1:
            if '''<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>''' in line.strip():
                ctr = 1
                continue
            if '''<h2><span class="mw-headline" id="See_also">See also''' in line.strip():
                ctr = 0
                if '''"See_also"''' in line.strip():
                    f2.write("<h3")
                continue
            if(ctr==1):
                f2.write(line)

        f1.close()
        f2.close()

        file=open("temp.html",'r')
        content=file.read()
        file.close()
        
        year=""
        ls=str(item).split("_")
        if(len(ls)==2):
            year='2019'
        else:
            year=ls[1]
        
        #print(item)

        def t_LTimeline2(t):
            r'''(<h2><span\sclass="mw-headline"\sid="[0-9]+[\_A-Za-z]+">)|(<h3><span\sclass="mw-headline"\sid="[0-9]+[\_A-Za-z0-9]+">)|(<h3><span\sclass="mw-headline"\sid="[0-9]+[\_A-Za-z]+">)'''
            #print(t.value+'*')
            return t
        
        def t_Date2(t):
            r'''([0-9]+\s[A-Z,a-z]+)'''
            #print(t.value+'*')
            return t

        def p_start2(p):
            '''start2 : Timeline2'''
        
        def p_Timeline2(p):
            '''Timeline2 : LTimeline2 Date2'''
            
            p[0]=p[2]
            #print(p[0])

            global filtered_date,unfiltered_date

            unfiltered_date=str(p[0])
            filtered_date=str(p[1][34:-2])
            #print(filtered_date)

            date=str(p[0]).split(" ")
            if(len(date[0])==1):
                date[0]='0'+date[0]
            
            day=date[0]
            month=AvailableMonth.index(date[1])+1
            month=str(month)
            if(len(month)==1):
                month='0'+month
            
            global currDate,key

            key=day+'-'+month+'-'+year
            #print(key)

            if(key not in ResponseContent.keys()):
                ResponseContent[key]=[]

            currDate=key

            if key[6:10]!='2019':
                line='<h3><span class="mw-headline" id="' +filtered_date + '">'+unfiltered_date+'</span>'
                end=line[0:3]
                pattern = re.compile(line)
                result = pattern.search(content)

                strt = result.start()
                content[result.start()]

                index = strt + 1
                news = ''

                while (content[index:index + 3] != end):
        
                    index += 1

                    ToDay=today.day
                    ToMonth=today.month

                    if(ToDay<10):
                        ToDay='0'+str(ToDay)
                    else:
                        ToDay=str(ToDay)

                    if(ToMonth<10):
                        ToMonth='0'+str(ToMonth)
                    else:
                        ToMonth=str(ToMonth)

                    if(key[6:10]!='2019'):
                        if(key[3:5]=='04' or key[3:5]=='06' or key[3:5]=='09' or key[3:5]=='11'):
                            if(key[0:2]=='30'):
                                #print("I'm Here1")
                                end='<h3'

                        elif(key[3:5]=='02'):
                            if(key[6:10]=='2020'):
                                if(key[0:2]=='29'):
                                    #print("I'm Here2")
                                    end='<h3'
                            else:
                                if(key[0:2]=='28'):
                                    #print(key[0:2])
                                    end='<h3'
                        else:
                            if(key[0:2]=='31'):
                                #print("I'm Here4")
                                end='<h3'
                            elif(key[0:2]==ToDay and str(today.year)==key[6:10] and key[3:5]==ToMonth):
                                #print("I'm Here")
                                end='<h3'
                            
                news = content[strt:index]
                tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
                news = re.sub(tag_re, '', news)
                tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
                news = re.sub(tag_re, '', news)
                tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
                news = re.sub(tag_re, '', news)
                
                ResponseContent[key].append(news)

            else:
                ResponseContent[key].append('N/A')


        
        tokens=['LTimeline2','Date2']

        #Defining Lexer
        lexer=lex.lex()
        lexer.input(content)

        #defining parser.
        parser = yacc.yacc()
        parser.parse(content,lexer=lexer)

        i+=1
    
    return ResponseContent

#Function to plot the word cloud
def plotWordCloud(text):

    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

#Function to Fetch Timeline or Response data between a date range.
def fetchTDDR(Data,Mode,DateRange,setMode):

    content=""
    status=0

    startDate=DateRange[1:11]
    endDate=DateRange[12:22]
    # if((startDate not in Data.keys()) or (endDate not in Data.keys())):
    #     return content,status
    # else:
    #     status=1

    if Mode==1:
        ctr=0
        for key,value in Data.items():
            if(comparator(startDate,key)==1 and comparator(endDate,key)==0):
                ctr=1
                status=1
            else:
                ctr=0
            if ctr==1:
                if setMode==1:
                    print("\nWorldwide News for Date : " + key)
                    print('\n'+str(value[0])+'\n')
                content=content+str(value[0])
    else:
        ctr=0
        for key,value in Data.items():
            if(comparator(startDate,key)==1 and comparator(endDate,key)==0):
                ctr=1
                status=1
            else:
                ctr=0
            if ctr==1:
                if setMode==1:
                    print("\nWorldwide Response for Date : " + key)
                
                if(len(value)==1):
                    if setMode==1:
                        print('\n'+str(value[0])+'\n')
                    content=content+str(value[0])
                else:
                    for i in range(0,len(value)):
                        if setMode==1:
                            print('\n'+str(value[i]))
                        content=content+str(value[i])
                    if setMode==1:
                        print('\n')
        

    return content,status

#Function to fetch CountryCovidData between a date Range.
def fetchCCD(Data,DateRange,Mode):

    content=""
    status=0

    startDate=DateRange[1:11]
    endDate=DateRange[12:22]
    # if((startDate not in Data.keys()) or (endDate not in Data.keys())):
    #     return content,status
    # else:
    #     status=1
    

    ctr=0
    for key,value in Data.items():
        #print(startDate,key,endDate)
        if(len(key)!=10):
            continue
        if(comparator(startDate,key)==1 and comparator(endDate,key)==0):
            ctr=1
            status=1
        else:
            ctr=0
        if ctr==1:
            if Mode==1:
                print("\nCountry Covid News for Date : " + key)
            
            if(len(value)==1):
                if Mode==1:
                    print('\n'+str(value[0])+'\n')
                content=content+str(value[0])
            else:
                for i in range(0,len(value)):
                    if Mode==1:
                        print('\n'+str(value[i]))
                    content=content+str(value[i])
                if Mode==1:
                    print('\n')

    
    return content,status

#Function to remove stop Words from text.
def removeStopWords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = []
 
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)

    output=""
    for item in filtered_sentence:
        output=output+' '+str(item)
    
    output=output.replace(',',"")
    output=output.replace('.',"")
    output=output.replace('(',"")
    output=output.replace(')',"")
    output=output.replace(';',"")
    output=output.replace('-',"")
    output=output.replace('!',"")
    
    for i in output:
        if i in '0123456789':
            output=output.replace(i,"")

    return output

#Function to find CommonWords.
def findCommonWords(data1,data2,Mode):
    common=[]

    if Mode==1:
        data1=removeStopWords(data1)
        data2=removeStopWords(data2)
        data1=data1.split(' ')
        data2=data2.split(' ')

        for item1 in data1:
            for item2 in data2:
                if(item1==item2):
                    item1=str(item1).lower()
                    common.append(item1)
    else:
        covidCommon=[]
        f=open('covid_word_dictionary.txt',"r")
        for line in f:
            line=line.replace("\n","")
            line=line.lower()
            covidCommon.append(line)
        f.close()
        
        # for item1 in data1:
        #     for item2 in covidCommon:
        #         if(item1==item2):
        #             item1=str(item1).lower()
        #             common.append(item1)
        
        CoCo=""
        for item2 in covidCommon:
            CoCo+=item2

        for item1 in data1:
            if(item1 in CoCo):
                item1=str(item1).lower()
                common.append(item1)

    
    label, counts = np.unique(common, return_counts=True)

    n=len(counts)
    for i in range(n):
        for j in range(0,n-i-1):
            if(counts[j]>counts[j+1]):
                counts[j],counts[j+1]=counts[j+1],counts[j]
                label[j],label[j+1]=label[j+1],label[j]

    output=""
    for item in label:
        output=output+' '+str(item)

    #print(label)
    #print(common)
    return label,output

#Function to check if 2 dates are overlapping or not.
def checkDateOverlap(DateRange1,DateRange2):

    day1=int(DateRange1[12:14])
    month1=int(DateRange1[15:17])
    year1=int(DateRange1[18:22])

    day2=int(DateRange2[1:3])
    month2=int(DateRange2[4:6])
    year2=int(DateRange2[7:11])

    if(year1>year2):
        return 0
    elif(year1==year2):
        if(month1>month2):
            return 0
        elif(month1==month2):
            if(day1>day2):
                return 0
            elif(day1==day2):
                return 0
    
    return 1

#Function to check if 2 dates are valid or not.
def checkDateOverlap1(DateRange1,DateRange2):

    day2=int(DateRange1[12:14])
    month2=int(DateRange1[15:17])
    year2=int(DateRange1[18:22])

    day1=int(DateRange2[1:3])
    month1=int(DateRange2[4:6])
    year1=int(DateRange2[7:11])

    if(year1>year2):
        return 0
    elif(year1==year2):
        if(month1>month2):
            return 0
        elif(month1==month2):
            if(day1>day2):
                return 0
            elif(day1==day2):
                return 0
    
    return 1

#Function to check Date Validity.
def checkDateValid(DateRange):

    if(DateRange[0]!='[' and DateRange[len(DateRange)-1]=='['):
        return 0
    if(len(DateRange)!=23):
        return 0
    if(DateRange[3]!='-' and DateRange[6]!='-' and DateRange[14]!='-' and DateRange[17]!='-' and DateRange[11]!=','):
        return 0
    
    if(checkDateOverlap1(DateRange,DateRange)!=1):
        return 0

    return 1

#Function to fetch Country Covid HTML Page.
def fetchCountryCovidHTML(url):

    CountryCovidNames=[]

    f=open("covid_country_list.txt","r")

    for line in f:
        if(line=='\n'):
            continue
        

        line=line.replace(' ','_')
        line=line.replace('\n','')
        url1=url+line

        
        if(('Philippines' in line) or ('United_States' in line)):
            
            url1=url+'the_'+line+'_(2020)'
            url2=url+'the_'+line+'_(2021)'

            link1='the_'+line+'_(2020)'+'.html'
            link2='the_'+line+'_(2021)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)

            if('Philippines' in line):
                url3=url+'the_'+line+'_(2022)'
                link3='the_'+line+'_(2022)'+'.html'
                getHTML(url3,link3)
                CountryCovidNames.append(link3)
            

            continue

        if('England' in line):
            url1=url+line+'_(January-June_2020)'
            url2=url+line+'_(July-December_2020)'
            url3=url+line+'_(2021)'
            url4=url+line+'_(2022)'

            link1=line+'_(January-June_2020)'+'.html'
            link2=line+'_(July-December_2020)'+'.html'
            link3=line+'_(2021)'+'.html'
            link4=line+'_(2022)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)
            getHTML(url4,link4)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            CountryCovidNames.append(link4)

            continue
        
        if('Australia' in line):
            url1=url+line+'_(January-June_2021)'
            url2=url+line+'_(July-December_2021)'
            url3=url+line+'_(2020)'
            url4=url+line+'_(2022)'

            link1=line+'_(January-June_2021)'+'.html'
            link2=line+'_(July-December_2021)'+'.html'
            link3=line+'_(2020)'+'.html'
            link4=line+'_(2022)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)
            getHTML(url4,link4)
            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            CountryCovidNames.append(link4)

            continue

        if('Russia' in line):
            url1=url+line+'_(January-June_2020)'
            url2=url+line+'_(July-December_2020)'

            link1=line+'_(January-June_2020)'+'.html'
            link2=line+'_(July-December_2020)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            
            continue
        
        
        if('Ghana' in line):
            url1=url+line+'_(March-July_2020)'
            url2=url+line+'_(August-December_2020)'
            url3=url+line+'_(2021)'

            link1=line+'_(March-July_2020)'+'.html'
            link2=line+'_(August-December_2020)'+'.html'
            link3=line+'_(2021)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            
            continue

        if('India' in line):
            url1=url+line+'_(January-May_2020)'
            url2=url+line+'_(June-December_2020)'
            url3=url+line+'_(2021)'

            link1=line+'_(January-May_2020)'+'.html'
            link2=line+'_(June-December_2020)'+'.html'
            link3=line+'_(2021)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            
            continue

        if(('Indonesia' in line) or ('Malaysia' in line) or ('New_Zealand' in line) or ('Singapore' in line)):
            url1=url+line+'_(2020)'
            url2=url+line+'_(2021)'

            link1=line+'_(2020)'+'.html'
            link2=line+'_(2021)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            

            if(('Philippines' in line)or ('New_Zealand' in line) or ('Singapore' in line) or ('Malaysia' in line)):
                url3=url+line+'_(2022)'
                link3=line+'_(2022)'+'.html'
                getHTML(url3,link3)
                CountryCovidNames.append(link3)

            continue

        if('Ireland' in line):
            url1=url+'the_Republic_of_'+line+'_(January-June_2020)'
            url2=url+'the_Republic_of_'+line+'_(July-December_2020)'
            url3=url+'the_Republic_of_'+line+'_(January-June_2021)'
            url4=url+'the_Republic_of_'+line+'_(July-December_2021)'
            url5=url+'the_Republic_of_'+line+'_(2022)'

            link1='the_Republic_of_'+line+'_(January-June_2020)'+'.html'
            link2='the_Republic_of_'+line+'_(July-December_2020)'+'.html'
            link3='the_Republic_of_'+line+'_(January-June_2021)'+'.html'
            link4='the_Republic_of_'+line+'_(July-December_2021)'+'.html'
            link5='the_Republic_of_'+line+'_(2022)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)
            getHTML(url4,link4)
            getHTML(url5,link5)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            CountryCovidNames.append(link4)
            CountryCovidNames.append(link5)

            continue

        if('Nigeria' in line):
            url1=url+line+'_(February-June_2020)'
            url2=url+line+'_(July-December_2020)'
            url3=url+line+'_(2021)'

            link1=line+'_(February-June_2020)'+'.html'
            link2=line+'_(July-December_2020)'+'.html'
            link3=line+'_(2021)'+'.html'

            getHTML(url1,link1)
            getHTML(url2,link2)
            getHTML(url3,link3)

            CountryCovidNames.append(link1)
            CountryCovidNames.append(link2)
            CountryCovidNames.append(link3)
            
            continue
        
        link=line+'.html'

        getHTML(url1,link)
        CountryCovidNames.append(link)
    
    return CountryCovidNames

#utility Function for country data fetch.
def fileReader1(item,s1,s2,s3):
    
    ctr = 0
    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    for line in f1:
        if (s1 in line.strip() or ctr == 1):
            dateFetch = line.split(s2)
            if (s3 in dateFetch[0]):
                ctr = 0
                f2.write(dateFetch[0])
            else:
                ctr = 1
                f2.write(line)
    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()

    return content

#utility Function for country data fetch.
def fileReader2(item,s1,s2,s3):
    ctr=0
    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    for line in f1:
        dateFetch = line.split(s1)
        if (s2 in dateFetch[0].strip() or ctr == 1):
            dateFetch1 = line.split("</span>")
            if (s3 in dateFetch1[0]):
                ctr = 0
                f2.write(dateFetch1[0])
            else:
                ctr = 1
                f2.write(line)
    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()

    return content

#Functions to fetch Argentina Data.
def Argentina(item,AvailableMonth):

    Argentina={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if line.strip() == """<div style="clear:both;"></div>""":
            ctr = 1
            continue
        if '''<h2><span class="mw-headline" id="Notes">''' in line.strip():
            ctr = 0
            if '''"Notes"''' in line.strip():
                f2.write("</b")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()

    def t_LCC3(t):
        r'''(<ul><li><b>)|(<li><b>)'''
        #print(t.value+'*')
        return t
    
    def t_DayMon3(t):
        r'''([0-9]+\s[A-Za-z]+:)'''
        #print(t.value+'*')
        return t

    def t_LCovidCountry3(t):
        r'''(<h3><span\sclass="mw-headline"\sid="[A-Za-z]+[\_0-9]+">)'''
        #print(t.value+'*')
        return t
    
    def t_Year3(t):
        r'''([A-Z,a-z]+\s[0-9]+)'''
        #print(t.value+'*')
        return t

    def p_start3(p):
        '''start3 : CC1
                    | CC2'''

    def p_CC1(p):
        '''CC1 : LCovidCountry3 Year3'''
        
        p[0]=p[2]
        #print(p[0])
        global currYear,count
        date=str(p[0]).split(" ")
        currYear=str(date[1])
        count=0
    
    def p_CC2(p):
        '''CC2 : LCC3 DayMon3'''
        
        p[0]=p[2]
        #print(p[0])

        unfiltered_date=str(p[0])
        date=str(p[0]).split(" ")

        if(len(date[0])==1):
            date[0]='0'+date[0]
        
        day=date[0]
        month=AvailableMonth.index(date[1][:-1])+1
        month=str(month)
        if(len(month)==1):
            month='0'+month
        
        global currYear,count

        key=day+'-'+month+'-'+currYear

        Argentina[key]=[]

        specialKey=""
        if(('08-01-2021' not in Argentina.keys()) and currYear=='2021' and month=='01' and day=='06'):
            Argentina['08-01-2021']=[]
            specialKey=specialKey+"08-01-2021"
        
        if(('30-12-2020' not in Argentina.keys()) and currYear=='2020' and month=='12' and day=='29'):
            Argentina['30-12-2020']=[]
            specialKey=specialKey+"30-12-2020"

        if(count==0):
            line='<ul><li><b>'+unfiltered_date+'</b>'
            count+=1
        else:
            line='<li><b>'+unfiltered_date+'</b>'
        

        pattern = re.compile(line)
        result = pattern.search(content)

        strt = result.start()
        content[result.start()]


        index = strt+7
        news = ''
        if count==0:
            while(content[index:index + 5] != '</li>'):
                #print(content[index:index + 11])
                index += 1
        else:
            while ((content[index:index + 5] != '</li>')):
                index += 1
        
        news = content[strt:index]
        tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        news=news.replace(unfiltered_date,"")
        Argentina[key].append(news)

        if(specialKey=='08-01-2021'):
            # print(specialKey)
            specialNews=handleSpecialKey1(content,1)
            #print(specialNews+'*')
            Argentina[specialKey].append(specialNews)
            specialKey=""
        if(specialKey=='30-12-2020'):
            # print(specialKey)
            specialNews=handleSpecialKey1(content,2)
            #print(specialNews+'*')
            Argentina[specialKey].append(specialNews)
            specialKey=""


    tokens=['LCovidCountry3','Year3','LCC3','DayMon3']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)


    return Argentina

#Functions to fetch Australia Data.
def Australia(item1,item2,item3,item4,AvailableMonth):
    
    Australia={}
    Australia['2020'] = {}
    Australia['2021'] = {}
    Australia['2022'] = {}
    yearAvailable=['2020','2021','2021','2022']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)
    links.append(item4)

    for j in range(0,4):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>""" or line.strip() == """<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>"""  in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<li class="toclevel-1 tocsection-28"><a href="#References"><sass="tocnumber">5""" in dateFetch[0] or """<li class="toclevel-1 tocsection-12"><a href="#References"><span class="tocnumber">9""" in dateFetch[0] or """<li class="toclevel-1 tocsection-7"><a href="#See_also"><span class="tocnumber">7""" in dateFetch[0] or """<li class="toclevel-1 tocsection-6"><a href="#External_links"><span class="tocnumber">5""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry25(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year25(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start23(p):
            '''start23 : CC25'''

        def p_CC25(p):
            ''' CC25 : LCovidCountry25 Year25'''

            p[0] = p[2]
            list_1 = p[0].split()
            setbit=0
            if (len(list_1) == 2):
                Australia[yearAvailable[j]][list_1[0]] = {}
            elif(len(list_1) == 1):
                if (p[0] in AvailableMonth):
                    Australia[yearAvailable[j]][p[0]] = {}
                
                
        tokens = ['LCovidCountry25', 'Year25']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<li class="toclevel-1 tocsection-18"><a href="#Notes"><span class="tocnumber">13""" in dateFetch[0].strip() or '''<li class="toclevel-1 tocsection-12"><a href="#References">''' in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-7"><a href="#See_also"><span class="tocnumber">7""" in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-6"><a href="#External_links"><span class="tocnumber">5""" in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-6"><a href="#References">"""  in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0] or '<h2><span class="mw-headline" id="See_also">See also</span>' in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()


        for month in Australia[yearAvailable[j]].keys():

            line = '<h2><span class="mw-headline" id="' + month + '_' + yearAvailable[j] + '">'
            if (yearAvailable[j] == '2022'):
                line = '<h2><span class="mw-headline" id="' + month + '">'

            pattern = re.compile(line)
            result = pattern.search(content)
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                setbit=1
                pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
                result = pattern.search(content[a:])
                i = a + 1
                news = ''
                while (content[i:i + 3] != '<h2'):
                    i += 1

                news = content[a:i]
                setbit=1
                Australia[yearAvailable[j]][month] = news

        def processor(data_dict):
            index = 0
            temp = 0
            i = 0
            import re
            data_1 = str(data_dict)

            date_dict = {}

            while (index < len(data_1) - 2):
                pattern = re.compile('<p>On [0-9 A-Za-z]*|<p>By [0-9 A-Za-z]*|<p>As of [0-9 A-Za-z]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)
                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    index_1 = len(list_1[1])

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''

                    while ((data_1[i:i + len('<p>On')] != '<p>On' and data_1[i:i + len('<p>By')] != '<p>By' and data_1[i:i + len('<p>As of')] != '<p>As of' and data_1[i:i + 3] != '<h2') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    list_date = []
                    date_key = news[3:index_1 - 2]

                    tag_re = re.compile('On|,|2020|By|As of|2021')
                    date_key = re.sub(tag_re, '', date_key)

                    list_date = date_key.split()
                    if (len(list_date) >= 2):
                        date_key = list_date[0] + ' ' + list_date[1]

                    index = i
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news)
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=1
                    news = re.sub(tag_re, '', news)
                    
                    if (date_key.strip() in date_dict.keys()):
                        date_dict[date_key.strip()] = date_dict[date_key.strip()] + news.replace('\n','')
                    else:
                        date_dict[date_key.strip()] = news.replace('\n','')
                    
                    if(date_key[0].isdigit()):
                        date_dict[date_key] = news.replace('\n','')

                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key.strip()])
                        
                else:
                    return date_dict

            return date_dict

        for month in Australia[yearAvailable[j]].keys():
            date_Dict = processor(Australia[yearAvailable[j]][month])

            Australia[yearAvailable[j]][month] = date_Dict        
    
    return FinalDict

#Functions to fetch Bangladesh Data.
def Bangladesh(item,AvailableMonth):

    Bangladesh={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if """<h2><span class="mw-headline" id="Timeline">""" in line.strip():
            ctr = 1
            continue
        if '''<h2><span class="mw-headline" id="See_also">''' in line.strip():
            ctr = 0
            if '''<h2><span class="mw-headline" id="See_also">''' in line.strip():
                f2.write("<h4")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()


    def t_LCovidCountry4(t):
        r'''(<h3><span\sclass="mw-headline"\sid="[A-Za-z]+">)|(<h4><span\sclass="mw-headline"\sid="[\_0-9]+[A-Za-z]+">)'''
        #print(t.value+'*')
        return t
    
    def t_Year4(t):
        r'''([0-9]+\s[A-Z,a-z]+)|([A-Z,a-z]+)'''
        #print(t.value+'*')
        return t

    def p_start4(p):
        '''start4 : CC3'''
    
    def p_CC3(p):
        '''CC3 : LCovidCountry4 Year4'''
        
        p[0]=p[2]
        
        global currYear,count
        date=str(p[0]).split(" ")
        if(len(date)==1):
            currYear='2020'
        
            unfiltered_date=str(p[0])
            date=str(p[0]).split(" ")

            day='01'
            month=AvailableMonth.index(date[0])+1
            month=str(month)
            if(len(month)==1):
                month='0'+month

        
            line='''<h3><span class="mw-headline" id="'''+unfiltered_date+'''">'''
            

            pattern = re.compile(line)
            result = pattern.search(content)

            strt = result.start()
            content[result.start()]


            index = strt+7
            news = ''
            while(content[index:index + 2] != '<h'):
                #print(content[index:index + 11])
                index += 1
            
            news = content[strt:index]
            tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
            news = re.sub(tag_re, '', news)

            key=''

            if(len(news)!=0):
                len(news)
                indexer=0
                while(news[indexer:indexer+1]!=','):
                    indexer+=1
                dateFetch=news[3:indexer].split(" ")
                day=dateFetch[0]

                if(len(day)==1):
                    day='0'+day

                key=day+'-'+month+'-'+currYear
                # print(key)
                Bangladesh[key]=[]

                Bangladesh[key].append(news)
                # print(news)
        else:
            unfiltered_date=str(p[0])
            filtered_date=unfiltered_date.replace(" ","_")
            date=str(p[0]).split(" ")

            if(len(date[0])==1):
                date[0]='0'+date[0]
            
            day=date[0]
            month=AvailableMonth.index(date[1])+1
            month=str(month)
            if(len(month)==1):
                month='0'+month
            key=day+'-'+month+'-'+currYear
            # print(key)
            Bangladesh[key]=[]

            line='<h4><span class="mw-headline" id="'+filtered_date+'">'
            pattern = re.compile(line)
            result = pattern.search(content)

            strt = result.start()
            content[result.start()]

            index = strt+7
            news = ''

            while(content[index:index + 3] != '<h4'):
                #print(content[index:index + 11])
                index += 1

            news = content[strt:index]
            tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
            news = re.sub(tag_re, '', news)
            tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
            news = re.sub(tag_re, '', news)
            # print(news)

            Bangladesh[key].append(news)

    tokens=['LCovidCountry4','Year4']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    return Bangladesh

#Functions to fetch Brazil Data.
def Brazil(item,AvailableMonth):

    Brazil={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if '''"#References"''' in line.strip():
            ctr = 1
            continue
        if '''"References"''' in line.strip():
            ctr = 0
            if '''"References"''' in line.strip():
                f2.write("<h2")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()


    def t_LCC5(t):
        r'''(<ul><li><b>)|(<li><b>)'''
        #print(t.value+'*')
        return t
    
    def t_DayMon5(t):
        r'''([0-9]+\s[A-Za-z]+:)'''
        # print(t.value+'*')
        return t

    def t_LCovidCountry5(t):
        r'''<h2><span\sclass="mw-headline"\sid="[A-Za-z\_]+[0-9]+">'''
        #print(t.value+'*')
        return t
    
    def t_Year5(t):
        r'''[A-Z,a-z]+\s[0-9]+'''
        #print(t.value+'*')
        return t

    def p_start5(p):
        '''start5 : CC4
                  | CC5'''
    
    def p_CC4(p):
        '''CC4 : LCovidCountry5 Year5'''
        
        p[0]=p[2]
        #print(p[0])
        global currYear,count
        date=str(p[0]).split(" ")
        currYear=str(date[1])
        count=0
    
    def p_CC5(p):
        '''CC5 : LCC5 DayMon5'''
        
        p[0]=p[2]
        #print(p[0])

        unfiltered_date=str(p[0])
        date=str(p[0]).split(" ")  
        if(len(date[0])==1):
            date[0]='0'+date[0]
        
        day=date[0]
        month=AvailableMonth.index(date[1][:-1])+1
        month=str(month)
        if(len(month)==1):
            month='0'+month
        
        global currYear,count

        key=day+'-'+month+'-'+currYear

        if(key not in Brazil.keys()):
            Brazil[key]=[]

        if(count==0):
            line='<ul><li><b>'+unfiltered_date+'</b>'
            count+=1
        else:
            line='<li><b>'+unfiltered_date+'</b>'

        pattern = re.compile(line)
        result = pattern.search(content)

        strt = result.start()
        content[result.start()]


        index = strt+7
        news = ''
        if count==0:
            while(content[index:index + 5] != '</li>'):
                #print(content[index:index + 11])
                index += 1
        else:
            while ((content[index:index + 5] != '</li>')):
                index += 1
        
        news = content[strt:index]
        tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        news=news.replace(unfiltered_date,"")
        Brazil[key].append(news)


    tokens=['LCovidCountry5','Year5','LCC5','DayMon5']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)


    return Brazil

#Functions to fetch Canada Data.
def Canada(item,AvailableMonth):

    Canada={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if '''<h2><span class="mw-headline" id="2019">2019</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Canada&amp;action=edit&amp;section=12" title="Edit section: 2019">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''' in line.strip():
            ctr = 1
            f2.write('''<h2><span class="mw-headline" id="2019">2019</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Canada&amp;action=edit&amp;section=12" title="Edit section: 2019">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''')
            continue
        if '''<h2><span class="mw-headline" id="See_also">''' in line.strip():
            ctr = 0
            if '''<h2><span class="mw-headline" id="See_also">''' in line.strip():
                f2.write("<h3")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()


    def t_LCovidCountry6(t):
        r'''<h2><span\sclass="mw-headline"\sid="[0-9]+">'''
        #print(t.value+'*')
        return t
    
    def t_Year6(t):
        r'''[0-9]+'''
        #print(t.value+'*')
        return t
    
    def t_LCovCoun7(t):
        r'''<h3><span\sclass="mw-headline"\sid="'''
        #print(t.value+'*')
        return t
    
    def t_Month7(t):
        r'''[A-Za-z\_0-9]+'''
        #print(t.value+'*')
        return t

    def p_start6(p):
        '''start6 : CC6
                  | CC7'''
    
    def p_CC6(p):
        '''CC6 : LCovidCountry6 Year6'''
        
        p[0]=p[2]
        global currYear
        currYear=str(p[0])
        
    
    def p_CC7(p):
        '''CC7 : LCovCoun7 Month7'''
        p[0]=p[2]
        global currMonth,currYear,count

        unfiltered_date=str(p[0])
        month=str(p[0]).split("_")[0]  
        #month=str(month)
        month=AvailableMonth.index(month)+1
        month=str(month)
        if(len(month)==1):
            month='0'+month
        
        count=0
        
        #key=day+'-'+month+'-'+currYear

        if(count==0):
            line='<h3><span class="mw-headline" id="'+unfiltered_date+'">'
            count+=1
        else:
            line='</p><p>'

        pattern = re.compile(line)
        result = pattern.search(content)

        strt = result.start()
        content[result.start()]

        index = strt+5
        news = ''
        if count==0:
            while(content[index:index + 11] != '</h3>\n</p>'):
                #print(content[index:index + 11])
                index += 1
        else:
            while ((content[index:index + 4] != '</p>')):
                index += 1

        news = content[strt:index]
        tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        #Canada[key].append(news)

        indexer=0
        while(news[indexer:indexer+1]!=','):
            indexer+=1
        dateFetch=news[3:indexer].split(" ")
        # print(dateFetch)
        if(len(dateFetch)==1):
            day='1'
        else:
            if(len(dateFetch)>1):
                try:
                    day=int(dateFetch[len(dateFetch)-1])
                    day=str(day)
                except:
                    day='1'
                
            else:
                day=dateFetch[1]

        if(len(day)==1):
            day='0'+day

        key=day+'-'+month+'-'+currYear
        # print(key)
        Canada[key]=[]

        Canada[key].append(news)

        #print(news)


    tokens=['LCovidCountry6','Year6','LCovCoun7','Month7']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    return Canada

#Functions to fetch Ghana Data.
def Ghana(item1,item2,item3,AvailableMonth):
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)
    Ghana={}
    Ghana['2020']={}
    Ghana['2021']={}
    yearAvailable=['2020','2020','2021']
    FinalDict={}

    for j in range(0,3):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry20(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year20(t):
            r'[0-9\sA-Za-z]+'
            return t

        def p_start18(p):
            '''start18 : CC20'''

        def p_CC20(p):
            ''' CC20 : LCovidCountry20 Year20'''
            p[0] = p[2]
            
            dateR=p[0].split(' ')
            if (dateR[0] in AvailableMonth):
                Ghana[yearAvailable[j]][dateR[0]] = {}
                # print(dateR[0])
                
                
        tokens = ['LCovidCountry20', 'Year20']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-13"><a href="#See_also"><span class="tocnumber">13""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Ghana[yearAvailable[j]].keys():
            line = '<h3><span class="mw-headline" id="' + month + '_' + yearAvailable[j] + '">'
            pattern = re.compile(line)
            result = pattern.search(content)
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1
                news = ''
                while (content[i:i + 2] != '<h'):
                    i += 1
                news = content[a:i]
                Ghana[yearAvailable[j]][month] = news
        
        def processor(data_dict, month):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                pattern = re.compile(
                    '<ul><li>On <b>[ A-Z a-z 0-9]* -|<ul><li>ON <b>[ A-Z a-z 0-9-]*|<li>On <b>[ A-Z a-z 0-9]* -|<li>On <b>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])

                    tag_re = re.compile('On|<ul>|<b>|<li>')
                    str_1 = re.sub(tag_re, '', str_1)

                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp
                    setbit=0
                    i = index + 1

                    news = ''
                    setbit=0
                    stopper = '</li>\n<li>On <b>'
                    x = (len(stopper))
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + x] != stopper) and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    index = i
                    setbit=1
                    news = news.replace('<ul>', '')
                    news = news.replace('<li>', '')
                    news = news.replace('<b>', '')

                    date_key = news[2:index_1 - 1].strip()
                    setbit=0
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news[0:])
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=1

                    news = re.sub(tag_re, '', news)
                    date_dict[date_key] = news.replace('\n','')
                    setbit=0
                    curD=str(date_key.strip()).split(" ")
                    setbit=1
                    currDay=curD[0]
                    if(len(currDay)==1):
                        currDay='0'+currDay

                    month=''
                    if(curD[1] in AvailableMonth):
                        month=AvailableMonth.index(curD[1])+1
                        month=str(month)
                        if(len(month)==1):
                            month='0'+month
                    currYear=yearAvailable[j]
                    key=currDay+'-'+month+'-'+currYear
                    if key not in FinalDict.keys():
                        FinalDict[key]=[]
                    if news not in FinalDict[key]:
                        FinalDict[key].append(date_dict[date_key])
                    
                    # print(key)
                    # print(date_dict[date_key])

                else:
                    return date_dict

            return date_dict


        for month in Ghana[yearAvailable[j]].keys():
            date_Dict = processor(Ghana[yearAvailable[j]][month], month)
            Ghana[yearAvailable[j]][month] = date_Dict
    
    return FinalDict

#Functions to fetch India Data.
def India(item,AvailableMonth):

    India={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if line.strip() == """<div style="clear:both;"></div>""":
            ctr = 1
            continue
        if '''<h2><span class="mw-headline" id="Notes">''' in line.strip():
            ctr = 0
            if '''"Notes"''' in line.strip():
                f2.write("</b")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    return India

#Functions to fetch Indonesia Data.
def Indonesia(item1,item2,AvailableMonth):
    
    links=[]
    links.append(item1)
    links.append(item2)
    Indonesia={}
    Indonesia['2020']={}
    Indonesia['2021']={}
    yearAvailable=['2020','2021']
    FinalDict={}

    for j in range(0,2):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<li class="toclevel-1 tocsection-12"><a href="#See_also"><span class="tocnumber">12""" in dateFetch[0] or """<li class="toclevel-1 tocsection-13"><a href="#See_also"><span class="tocnumber">13""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry19(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year19(t):
            r'[0-9\sA-Za-z]+'
            return t

        def p_start17(p):
            '''start17 : CC19'''

        def p_CC19(p):
            ''' CC19 : LCovidCountry19 Year19'''
            p[0] = p[2]
            
            Indonesia[yearAvailable[j]][p[0]] = {}
                

        tokens = ['LCovidCountry19', 'Year19']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<li class="toclevel-1 tocsection-12"><a href="#See_also"><span class="tocnumber">12""" in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-13"><a href="#See_also"><span class="tocnumber">13""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Indonesia[yearAvailable[j]].keys():
            line = '<h2><span class="mw-headline" id="' + month + '">'
            pattern = re.compile(line)
            result = pattern.search(content)
            a = result.start()
            i = a + 1
            news = ''
            while (content[i:i + 4] != '<h2>'):
                i += 1
            news = content[a:i]
            Indonesia[yearAvailable[j]][month] = news
        
        def processor(data_dict):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                setbit=0
                pattern = re.compile('<ul><li>[ A-Z a-z 0-9]* -|<ul><li>[ A-Z a-z 0-9-]*|<li>[ A-Z a-z 0-9]* -|<li>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')
                setbit=1

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    setbit=0
                    str_1 = str_1.replace('<ul>', '')
                    str_1 = str_1.replace('<li>', '')
                    index_1 = len(str_1)

                    temp = result.start()
                    setbit=1
                    index = index + temp

                    i = index + 1

                    news = ''
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + len('</li>\n<li>')] != '</li>\n<li>') and i <= len(data_1) - 1):
                        setbit=0
                        i += 1

                    news = data_1[index:i]
                    index = i
                    setbit=0
                    news = news.replace('<ul>', '')
                    setbit=1
                    news = news.replace('<li>', '')
                    date_key = news[0:index_1 - 2]
                    list_date = date_key.split()
                    setbit=1
                    if (len(list_date) >= 2):
                        setbit=0
                        date_key = list_date[0] + ' ' + list_date[1]

                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    setbit=0
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=1

                    news = re.sub(tag_re, '', news)
                    tag_re = re.compile('a href=.*?>')
                    news = re.sub(tag_re, '', news)
                    setbit=0
                    if (date_key[0].isdigit()):
                        split_check = date_key.split()
                        if (len(split_check) == 2):
                            setbit=1
                            date_dict[date_key.strip()] = news.replace('\n','')
                            temp_s = date_key.strip()
                        else:
                            if (temp_s != ''):
                                date_dict[temp_s] = date_dict[temp_s] + news.replace('\n','')
                    else:
                        if (temp_s != ''):
                            date_dict[temp_s] = date_dict[temp_s] + news.replace('\n','')

                    curD=str(temp_s.strip()).split(" ")
                    currDay=curD[0]
                    if(len(currDay)==1):
                        currDay='0'+currDay

                    month=''
                    if(curD[1] in AvailableMonth):
                        month=AvailableMonth.index(curD[1])+1
                        month=str(month)
                        if(len(month)==1):
                            month='0'+month
                    currYear=yearAvailable[j]
                    key=currDay+'-'+month+'-'+currYear
                    if key not in FinalDict.keys():
                        FinalDict[key]=[]
                    if news not in FinalDict[key]:
                        FinalDict[key].append(news)
                    

                else:
                    return date_dict

            return date_dict


        for month in Indonesia[yearAvailable[j]].keys():
            date_Dict = processor(Indonesia[yearAvailable[j]][month])

            Indonesia[yearAvailable[j]][month] = date_Dict
    
    return FinalDict

#Functions to fetch Ireland Data.
def Ireland(item1,item2,item3,item4,item5,AvailableMonth):
    
    Ireland={}
    Ireland['2020'] = {}
    Ireland['2021'] = {}
    Ireland['2022'] = {}
    yearAvailable=['2020','2020','2021','2021','2022']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)
    links.append(item4)
    links.append(item5)

    for j in range(0,5):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>"""  in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry27(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year27(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start25(p):
            '''start25 : CC27'''

        def p_CC27(p):
            ''' CC27 : LCovidCountry27 Year27'''

            p[0] = p[2]
            list_1 = p[0].split()
            if (list_1[0] in AvailableMonth):
                Ireland[yearAvailable[j]][list_1[0]] = {}
                
        tokens = ['LCovidCountry27', 'Year27']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline"""  in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Ireland[yearAvailable[j]].keys():
            setbit=0
            line = '<h3><span class="mw-headline" id="' + month + '_' + yearAvailable[j] + '">'
            pattern = re.compile(line)
            result = pattern.search(content)
            setbit=1
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')
            setbit=0

            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h'):
                    i += 1

                news = content[a:i]

                Ireland[yearAvailable[j]][month] = news
        
        def processor(data_dict, month):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                pattern = re.compile('<ul><li>[ A-Z a-z 0-9]* -|<ul><li>[ A-Z a-z 0-9-]*|<li>[ A-Z a-z 0-9]* -|<li>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])
                setbit=0
                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')
                setbit=1
                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    setbit=0
                    str_1 = str_1.replace('<ul>', '')
                    str_1 = str_1.replace('<li>', '')
                    setbit=0
                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + len('</li>\n<li>')] != '</li>\n<li>') and data_1[i:i+3]!='<h3' and data_1[i:i+3]!='<h2' and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    index = i
                    setbit=1
                    news = news.replace('<ul>', '')
                    news = news.replace('<li>', '')
                    setbit=1
                    date_key = news[0:index_1 - 2]
                    list_date = date_key.split()
                    setbit=1
                    if (len(list_date) >= 2):
                        setbit=1
                        date_key = list_date[0] + ' ' + list_date[1]

                    tag_re = re.compile('<sup.*?</sup>')
                    setbit=0
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=0
                    news = re.sub(tag_re, '', news)
                    tag_re=re.compile('a href=.*?>')
                    setbit=1
                    news=re.sub(tag_re,'',news)
                    if (date_key[0].isdigit()):
                        setbit=1
                        date_dict[date_key.strip()] = news.replace('\n','')
                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key.strip()])

                else:
                    return date_dict

            return date_dict

        for month in Ireland[yearAvailable[j]].keys():
            date_Dict = processor(Ireland[yearAvailable[j]][month], month)
            Ireland[yearAvailable[j]][month] = date_Dict

    return FinalDict

#Functions to fetch Malaysia Data.
def Malaysia(item1,item2,item3,AvailableMonth):
    
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)

    Malaysia={}
    Malaysia['2020']={}
    Malaysia['2021']={}
    Malaysia['2022']={}
    yearAvailable=['2020','2021','2022']
    date_list = []
    FinalDict={}
    
    for j in range(0,3):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry18(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]+"><a\shref="\#'
            return t

        def t_Year18(t):
            r'[0-9\-\sA-Za-z\_]+'
            return t

        def p_start16(p):
            '''start16 : CC18'''

        def p_CC18(p):
            ''' CC18 : LCovidCountry18 Year18'''
            p[0] = p[2]
            
            if (p[0] in AvailableMonth):
                Malaysia[yearAvailable[j]][p[0]] = {}

        tokens = ['LCovidCountry18', 'Year18']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Malaysia[yearAvailable[j]].keys():
            line = '<h3><span class="mw-headline" id="' + month + '">'

            pattern = re.compile(line)
            result = pattern.search(content)
            list_1 = ''
            itr = str(result)
            list_1 = itr.split('match=')
            setbit=0
            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1
                news = ''
                while (content[i:i + 4] != '<h2>'):
                    i += 1
                news = content[a:i]
                Malaysia[yearAvailable[j]][month] = news
        
        def processor(data_dict):

            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)

            date_dict = {}

            while (index < len(data_1) - 2):
                setbit=1
                pattern = re.compile('<p>On [0-9 A-Za-z]*|<p>By [0-9 A-Za-z]*|<p>As of [0-9 A-Za-z]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)
                list_1 = itr.split('match=')
                setbit=0

                if (str(list_1[0]) != 'None'):
                    index_1 = len(list_1[1])

                    temp = result.start()
                    index = index + temp
                    setbit=1
                    i = index + 1

                    news = ''

                    while ((data_1[i:i + len('<p>On')] != '<p>On' and data_1[i:i + len('<p>By')] != '<p>By' and data_1[i:i + len('<p>As of')] != '<p>As of' and data_1[i:i + 4] != '<h3>') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]
                    setbit=0
                    list_date = []
                    date_key = news[3:index_1 - 2]
                    tag_re = re.compile('On|,|2020|By|As of|2021')
                    date_key = re.sub(tag_re, '', date_key)
                    list_date = date_key.split()
                    setbit=1
                    date_key = list_date[0] + ' ' + list_date[1]

                    index = i
                    setbit=0
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news)
                    tag_re = re.compile('<td>.*?</td>')
                    news = re.sub(tag_re, '', news)
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                    news = re.sub(tag_re, '', news)
                    news = news.replace('\n', '')
                    setbit=1

                    date_dict[date_key.strip()] = news
                    setbit=0

                    curD=str(date_key.strip()).split(" ")
                    currDay=curD[0]
                    if(len(currDay)==1):
                        setbit=1
                        currDay='0'+currDay

                    month=''
                    if(curD[1] in AvailableMonth):
                        month=AvailableMonth.index(curD[1])+1
                        month=str(month)
                        if(len(month)==1):
                            month='0'+month
                    currYear=yearAvailable[j]
                    key=currDay+'-'+month+'-'+currYear
                    if key not in FinalDict.keys():
                        FinalDict[key]=[]
                    if news not in FinalDict[key]:
                        FinalDict[key].append(news)
                else:
                    return date_dict

            return date_dict

        for month in Malaysia[yearAvailable[j]].keys():
            date_Dict = processor(Malaysia[yearAvailable[j]][month])
            Malaysia[yearAvailable[j]][month] = date_Dict
    
    return FinalDict

#Functions to fetch Mexico Data.
def Mexico(item,AvailableMonth):

    Mexico={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if '''<h2><span class="mw-headline" id="January_2020">January 2020</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Mexico&amp;action=edit&amp;section=1" title="Edit section: January 2020">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''' in line.strip():
            ctr = 1
            f2.write('''<h2><span class="mw-headline" id="January_2020">January 2020</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Mexico&amp;action=edit&amp;section=1" title="Edit section: January 2020">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''')
            continue
        if '''<h2><span class="mw-headline" id="References">''' in line.strip():
            ctr = 0
            if '''<h2><span class="mw-headline" id="References">''' in line.strip():
                f2.write("<h2")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()

    def t_LCovidCountry7(t):
        r'''<h2><span\sclass="mw-headline"\sid="[A-Za-z]+\_[0-9]+">'''
        #print(t.value+'*')
        return t
    
    def t_Year7(t):
        r'''[A-Za-z]+\s[0-9]+'''
        #print(t.value+'*')
        return t

    def p_start7(p):
        '''start7 : CC8'''
    
    def p_CC8(p):
        '''CC8 : LCovidCountry7 Year7'''
        
        p[0]=p[2]
        global currYear,currMonth,count
        date=str(p[0]).split(" ")
        unfiltered_date=str(p[0])
        filtered_date=unfiltered_date.replace(" ","_")
        currYear=date[1]
        currMonth=date[0]
        month=AvailableMonth.index(currMonth)+1
        month=str(month)
        if(len(month)==1):
            month='0'+month
        
        count=0
        
        if(count==0):
            line='<h2><span class="mw-headline" id="'+filtered_date+'">'
            count+=1
        else:
            line='</p>'

        
        pattern = re.compile(line)
        result = pattern.search(content)
        strt = result.start()
        content[result.start()]
        
        index = strt+5
        news = ''
        while(content[index:index +3] != '<h2'):
            index += 1

        news = content[strt:index]
        
        tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([A-Za-z\s0-9]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('[A-Za-z\s0-9]+\–')
        news = re.sub(tag_re, '', news)
        news=news.replace(unfiltered_date+'[edit]',"")

        indexer=0
        while(news[indexer:indexer+1]!=','):
            indexer+=1
        dateFetch=news[3:indexer].split(" ")
        
        if(len(dateFetch)==1):
            day='1'
        else:
            if(len(dateFetch)>1):
                try:
                    day=int(dateFetch[len(dateFetch)-1])
                    day=str(day)
                except:
                    day='1'
                
            else:
                day=dateFetch[1]

        if(len(day)==1):
            day='0'+day

        key=day+'-'+month+'-'+currYear
        #print(news)

        indexer=0
        currNews=""
        prevkey=''
        for i in range(0,len(news)):
            if(news[i:i+3]=='On '):

                if(i!=0 and key[0] in '0123456789'):
                    prevkey=key

                temp=i
                while(news[temp:temp+1]!=','):
                    temp+=1
                dateFetch=news[i:temp].split(' ')
                day=dateFetch[2]
                if(len(day)==1):
                    day='0'+day

                
                if key not in Mexico.keys():
                    if(key[0] in '0123456789'):
                        Mexico[key]=[]

                if(key[0] in '0123456789'):
                    Mexico[key].append(currNews)
                else:
                    Mexico[prevkey].append(currNews)

                key=day+'-'+month+'-'+currYear
                currNews=""
            else:
                currNews+=news[i-1]


    tokens=['LCovidCountry7','Year7']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)


    return Mexico

#Functions to fetch New Zealand Data.
def New_Zealand(item1,item2,item3,AvailableMonth):
    
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)
    New_Zealand={}
    New_Zealand['2020']={}
    New_Zealand['2021']={}
    New_Zealand['2022']={}
    yearAvailable=['2020','2021','2022']
    for year in yearAvailable:
        if year=='2020':
            for month in AvailableMonth[1:]:
                New_Zealand[year][month]={}
        else:
            for month in AvailableMonth:
                New_Zealand[year][month]={}

    for j in range(0,3):

        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""</div><p><span class="anchor" id="COVID_chart"></span>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Alert_levels_timeline">Alert levels timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        if yearAvailable[j]=='2020':

            for element in AvailableMonth[1:]:

                if (element == 'April' and yearAvailable[j] == '2022'):
                    setbit=1
                    break
                if (yearAvailable[j] == '2020' or yearAvailable[j] == '2021'):
                    setbit=0
                    line = '<h3><span class="mw-headline" id="' + element + '_' + yearAvailable[j] + '">'
                else:
                    setbit=1
                    line = '<h3><span class="mw-headline" id="' + element + '">'

                pattern = re.compile(line)
                result = pattern.search(content)

                a = result.start()

                pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
                result = pattern.search(content[a:])

                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h' or content[i:i + 3] == '<h4'):
                    i += 1

                news = content[a:i]
                setbit=0
                tag_re = re.compile('<sup.*?</sup>')
                news = re.sub(tag_re, '', news)
                tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                setbit=1
                news = re.sub(tag_re, '', news)
                New_Zealand[yearAvailable[j]][element] = news

        else:
            for element in AvailableMonth[1:]:

                if (element == 'April' and yearAvailable[j] == '2022'):
                    setbit=1
                    break
                if (yearAvailable[j] == '2020' or yearAvailable[j] == '2021'):
                    setbit=0
                    line = '<h3><span class="mw-headline" id="' + element + '_' + yearAvailable[j] + '">'
                else:
                    setbit=1
                    line = '<h3><span class="mw-headline" id="' + element + '">'

                pattern = re.compile(line)
                result = pattern.search(content)

                a = result.start()

                pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
                result = pattern.search(content[a:])

                i = a + 1

                news = ''
                setbit=1
                while (content[i:i + 2] != '<h' or content[i:i + 3] == '<h4'):
                    i += 1

                news = content[a:i]
                setbit=0
                tag_re = re.compile('<sup.*?</sup>')
                news = re.sub(tag_re, '', news)
                setbit=1
                tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                setbit=0
                news = re.sub(tag_re, '', news)
                New_Zealand[yearAvailable[j]][element] = news

        def processor(data_dict):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 2):

                pattern = re.compile('On [0-9 A-Z a-z]*,|By [0-9 A-Z a-z]*,')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)
                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    index_1 = len(list_1[1])

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''
                    setbit=1
                    while ((data_1[i:i + 2] != 'On' and data_1[i:i + 2] != 'By') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    index = i
                    setbit=0
                    date_key=news[3:index_1 - 3]
                    date_key=date_key.replace(',','')
                    date_key=date_key.strip()
                    setbit=1
                    if (date_key.strip() in date_dict.keys()):
                        date_dict[date_key.strip()] = date_dict[date_key.strip()] + news.replace('\n','')
                    else:
                        date_dict[date_key.strip()] = news.replace('\n','')

                    if(date_key.strip()!='2pm'):
                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month
                        else:
                            currDay=curD[3]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[4] in AvailableMonth):
                                month=AvailableMonth.index(curD[4])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key])

                else:
                    return date_dict

            return date_dict


        if (yearAvailable[j] == '2020'):
            month_list_4 = AvailableMonth[1:]
        if (yearAvailable[j] == '2021' or yearAvailable[j] == '2022'):
            month_list_4 = AvailableMonth

        for month in month_list_4:
            if (month == 'April' and yearAvailable[j] == '2022'):
                break
            date_Dict = processor(New_Zealand[yearAvailable[j]][month])

            New_Zealand[yearAvailable[j]][month] = date_Dict
    
    return FinalDict

#Functions to fetch Nigeria Data.
def Nigeria(item1,item2,item3,AvailableMonth):
    
    Nigeria={}
    Nigeria['2020'] = {}
    Nigeria['2021'] = {}
    yearAvailable=['2020','2020','2021']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)

    for j in range(0,3):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip()  or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry22(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year22(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start20(p):
            '''start20 : CC22'''

        def p_CC22(p):
            ''' CC22 : LCovidCountry22 Year22'''
            p[0] = p[2]
            
            if (p[0] in AvailableMonth):
                Nigeria[yearAvailable[j]][p[0]] = {}
                
                
        tokens = ['LCovidCountry22', 'Year22']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Nigeria[yearAvailable[j]].keys():
            setbit=0
            line = '<h3><span class="mw-headline" id="' + month + '"'
            pattern = re.compile(line)
            result = pattern.search(content)
            setbit=1
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h'):
                    i += 1

                news = content[a:i]

                Nigeria[yearAvailable[j]][month] = news
            
        def processor(data_dict):
            index = 0
            temp = 0
            i = 0
            import re
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                pattern = re.compile('<ul><li>[0-9 A-Z a-z-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp

                    i = index + 1
                    setbit=1

                    news = ''
                    setbit=0
                    while ((data_1[i:i + 5] != '</ul>') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]
                    setbit=1

                    index = i
                    date_key = news[8:index_1 - 3].strip()
                    setbit=0

                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                    news = re.sub(tag_re, '', news)
                    date_dict[date_key] = news.replace('\n','')
                    setbit=0

                    # print(date_key.strip())


                    if(date_key.strip().split(' ')[0] in '0123456789'):
                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key])

                else:
                    return date_dict

            return date_dict

        for month in Nigeria[yearAvailable[j]].keys():
            date_Dict = processor(Nigeria[yearAvailable[j]][month])

            Nigeria[yearAvailable[j]][month] = date_Dict

    return FinalDict

#Functions to fetch Pakistan Data.
def Pakistan(item,AvailableMonth):

    Pakistan={}

    f1=open(item,"r")
    f2=open("Countrytemp.html","w")
    ctr=0
    for line in f1:
        if '''<h2><span class="mw-headline" id="January_2020">January 2020</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Pakistan&amp;action=edit&amp;section=1" title="Edit section: January 2020">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''' in line.strip():
            ctr = 1
            f2.write('''<h2><span class="mw-headline" id="January_2020">January 2020</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=Timeline_of_the_COVID-19_pandemic_in_Pakistan&amp;action=edit&amp;section=1" title="Edit section: January 2020">edit</a><span class="mw-editsection-bracket">]</span></span></h2>''')
            continue
        if '''<h2><span class="mw-headline" id="References">''' in line.strip():
            ctr = 0
            if '''<h2><span class="mw-headline" id="References">''' in line.strip():
                f2.write("<h3")
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open("Countrytemp.html",'r')
    content=file.read()
    file.close()

    def t_LCovidCountry9(t):
        r'''<h2><span\sclass="mw-headline"\sid="'''
        #print(t.value+'*')
        return t
    
    def t_Year9(t):
        r'''[A-Za-z\_]+[0-9]+'''
        #print(t.value+'*')
        return t

    def t_LCovidCountry8(t):
        r'''<h3><span\sclass="mw-headline"\sid="'''
        #print(t.value+'*')
        return t
    
    def t_Year8(t):
        r'''[0-9]+\_[A-Za-z\_0-9]+'''
        #print(t.value+'*')
        return t

    def p_start8(p):
        '''start8 : CC10
                  | CC9'''
    
    def p_CC10(p):
        '''CC10 : LCovidCountry9 Year9'''
        
        p[0]=p[2]
        #print(p[0])
        global currYear
        date=str(p[0]).split("_")
        currYear=date[1]
        count=0
    
    def p_CC9(p):
        '''CC9 : LCovidCountry8 Year8'''
        
        p[0]=p[2]
        unfiltered_date=str(p[0])
        date=str(p[0]).split("_") 
        if(len(date[0])==1):
            date[0]='0'+date[0]
        
        day=date[0]
        month=AvailableMonth.index(date[1])+1
        month=str(month)
        if(len(month)==1):
            month='0'+month
        
        global currYear,count
        
        key=day+'-'+month+'-'+currYear
    
        if(key not in Pakistan.keys()):
            Pakistan[key]=[]
        
        line='<h3><span class="mw-headline" id="'+unfiltered_date+'">'

        pattern = re.compile(line)
        result = pattern.search(content)

        strt = result.start()
        content[result.start()]

        index = strt+7
        news = ''
        if count==0:
            while(content[index:index + 3] != '<h3'):
                #print(content[index:index + 11])
                index += 1
        else:
            while ((content[index:index + 3] != '<h3')):
                index += 1
        
        news = content[strt:index]
        tag_re = re.compile('<sup.*?</sup>|<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|\n')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([0-9]+\s[A-Za-z]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        tag_re=re.compile('([A-Za-z\s]+)\[edit\]')
        news = re.sub(tag_re, '', news)
        Pakistan[key].append(news)

    tokens=['LCovidCountry8','Year8','LCovidCountry9','Year9']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    return Pakistan

#Functions to fetch Philippines Data.
def Philippines(item1,item2,item3,AvailableMonth):
    Philippines={}
    Philippines['2020'] = {}
    Philippines['2021'] = {}
    Philippines['2022'] = {}
    yearAvailable=['2020','2021','2022']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)

    for j in range(0,3):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>"""  in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry24(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year24(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start22(p):
            '''start22 : CC24'''

        def p_CC24(p):
            ''' CC24 : LCovidCountry24 Year24'''
            p[0] = p[2]
            
            if (p[0] in AvailableMonth):
                Philippines[yearAvailable[j]][p[0]] = {}
                
                
        tokens = ['LCovidCountry24', 'Year24']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Philippines[yearAvailable[j]].keys():
            line = '<h3><span class="mw-headline" id="' + month + '"'
            pattern = re.compile(line)
            result = pattern.search(content)
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h'):
                    i += 1

                news = content[a:i]

                Philippines[yearAvailable[j]][month] = news

        def processor(data_dict, month):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                setbit=0
                pattern = re.compile('<ul><li>[ A-Z a-z 0-9]* -|<ul><li>[ A-Z a-z 0-9-]*|<li>[ A-Z a-z 0-9]* -|<li>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')
                setbit=1

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    str_1 = str_1.replace('<ul>', '')
                    str_1 = str_1.replace('<li>', '')
                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp
                    setbit=0
                    i = index + 1

                    news = ''
                    stopper = '</li>\n<li>' + month
                    x = len('</li>\n<li>') + len(month)
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + x] != stopper) and i <= len(data_1) - 1):
                        setbit=1
                        i += 1

                    news = data_1[index:i]

                    index = i
                    setbit=0
                    news = news.replace('<ul>', '')
                    news = news.replace('<li>', '')
                    setbit=1
                    date_key = news[0:index_1 - 2].strip()
                    setbit=0
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=1
                    news = re.sub(tag_re, '', news)
                    date_key=date_key.replace('-','')

                    date_key=date_key.strip()
                    date_key=date_key.replace(' -','')
                    date_key=date_key.strip()
                    setbit=0
                    date_key=date_key.replace(',','')
                    list_1s=date_key.split()
                    if(len(list_1s)==3):
                        setbit=1
                        date_key=list_1s[0]+ ' ' +list_1s[1].replace('-','')
                    list_2=date_key.split()
                    if(len(list_2)==2):
                        date_key=list_2[1] +' ' + list_2[0]
                    if(date_key=='9– February'):
                        date_key='9 February'
                    setbit=1
                    if(date_key[0].isdigit()):
                        date_dict[date_key] = news.replace('\n','')

                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key])

                else:
                    return date_dict

            return date_dict

        for month in Philippines[yearAvailable[j]].keys():
            date_Dict = processor(Philippines[yearAvailable[j]][month], month)
            Philippines[yearAvailable[j]][month] = date_Dict

    return FinalDict

#Functions to fetch Russia Data.
def Russia(item1,item2,AvailableMonth):
    links=[]
    links.append(item1)
    links.append(item2)
    Russia={}
    Russia['2020']={}
    Russia['2020']['January'] = {}
    Russia['2020']['February'] = {}
    FinalDict={}
    currYear='2020'

    for j in range(0,2):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry17(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year17(t):
            r'[0-9\sA-Za-z]+'
            return t

        def p_start15(p):
            '''start15 : CC17'''

        def p_CC17(p):
            ''' CC17 : LCovidCountry17 Year17'''
            p[0] = p[2]
            dateR=str(p[0]).split()
            
            if (dateR[0] in AvailableMonth):
                Russia['2020'][dateR[0]] = {}
                

        tokens = ['LCovidCountry17', 'Year17']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)
        
        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in Russia['2020'].keys():
            setbit=0
            line = '<h3><span class="mw-headline" id="' + month + '_' + '2020' + '">'
            pattern = re.compile(line)
            setbit=1
            result = pattern.search(content)
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
                result = pattern.search(content[a:])

                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h' or content[i:i + 3] == '<h4'):
                    i += 1

                news = content[a:i]
                tag_re = re.compile('<sup.*?</sup>')
                news = re.sub(tag_re, '', news)
                setbit=0
                tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                news = re.sub(tag_re, '', news)
                Russia['2020'][month] = news

        def processor(data_dict):
            index = 0
            temp = 0
            i = 0
            
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 2):

                pattern = re.compile('On [0-9 A-Z a-z]*,|By [0-9 A-Z a-z]*,')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)
                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    index_1 = len(list_1[1])

                    temp = result.start()
                    index = index + temp

                    i = index + 1
                    setbit=0
                    news = ''
                    while ((data_1[i:i + 2] != 'On' and data_1[i:i + 2] != 'By') and i <= len(data_1) - 1):
                        i += 1


                    news = data_1[index:i]
                    index = i
                    setbit=0
                    date_value = news[3:index_1 - 3].replace(',', '')
                    date_dict[date_value] = news.replace('\n','')
                    date_dict[date_value] = date_dict[date_value].replace('\\','')
                    date_dict[date_value] = date_dict[date_value].replace('\\\'','')
                    date_dict[date_value] = date_dict[date_value].replace('\'s','')
                    
                    curD=date_value.split(" ")
                    setbit=0
                    currDay=curD[0]
                    if(len(currDay)==1):
                        currDay='0'+currDay

                    # print(curD)
                    month=''
                    if(curD[1] in AvailableMonth):
                        month=AvailableMonth.index(curD[1])+1
                        month=str(month)
                        if(len(month)==1):
                            month='0'+month
                    
                    key=currDay+'-'+month+'-'+currYear
                    if key not in FinalDict.keys():
                        FinalDict[key]=[]
                    FinalDict[key].append(date_dict[date_value])
                else:
                    return date_dict

            return date_dict        
        
        for month in Russia['2020'].keys():

            date_Dict = processor(Russia['2020'][month])
            Russia['2020'][month] = date_Dict

    return FinalDict

#Functions to fetch Singapore Data.
def Singapore(item1,item2,item3,AvailableMonth):
    
    Singapore={}
    Singapore['2020'] = {}
    Singapore['2021'] = {}
    Singapore['2022'] = {}
    yearAvailable=['2020','2021','2022']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)

    for j in range(0,3):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip() or """<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext"><i>Timeline</i></span></a>""" in line.strip() or """<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>"""  in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0] or """<h2><span class="mw-headline" id="Timeline"><i>Timeline</i>""" in dateFetch[0] or """<li class="toclevel-1 tocsection-4"><a href="#References"><span class="tocnumber">4""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry23(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year23(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start21(p):
            '''start21 : CC23'''

        def p_CC23(p):
            ''' CC23 : LCovidCountry23 Year23'''
            p[0] = p[2]
            
            if (p[0] in AvailableMonth):
                Singapore[yearAvailable[j]][p[0]] = {}
                
                
        tokens = ['LCovidCountry23', 'Year23']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or """<h2><span class="mw-headline" id="Timeline"><i>Timeline</i>""" in dateFetch[0].strip() or """<li class="toclevel-1 tocsection-4"><a href="#References"><span class="tocnumber">4""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0] or """<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        if yearAvailable[j]!='2022':

            for month in Singapore[yearAvailable[j]].keys():
                setbit=0
                line = '<h3><span class="mw-headline" id="' + month + '"'
                pattern = re.compile(line)
                result = pattern.search(content)
                setbit=1
                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    a = result.start()
                    i = a + 1

                    news = ''

                    while (content[i:i + 2] != '<h'):
                        i += 1

                    news = content[a:i]

                    Singapore[yearAvailable[j]][month] = news

        else:
            for month in Singapore[yearAvailable[j]].keys():
                line = '<h2><span class="mw-headline" id="' + month + '"'
                pattern = re.compile(line)
                result = pattern.search(content)
                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    a = result.start()
                    i = a + 1

                    news = ''

                    while (content[i:i + 2] != '<h'):
                        i += 1

                    news = content[a:i]

                    Singapore[yearAvailable[j]][month] = news

        def processor(data_dict, month):
            index = 0
            count = 0
            temp = 0
            i = 0
            import re
            data_1 = str(data_dict)
            date_dict = {}

            while (index < len(data_1) - 5):
                pattern = re.compile('<ul><li><b>[ A-Z a-z 0-9]* -|<ul><li><b>[ A-Z a-z 0-9-]*|<li><b>[ A-Z a-z 0-9]* -|<li><b>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    setbit=0
                    str_1 = str_1.replace('<ul>', '')
                    str_1 = str_1.replace('<li>', '')
                    str_1 = str_1.replace('<b>', '')
                    setbit=1

                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp

                    i = index + 1
                    setbit=0
                    news = ''
                    stopper = '</li>\n<li><b>'
                    x = (len(stopper))
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + x] != stopper) and i <= len(data_1) - 1):
                        i += 1
                    setbit=1
                    news = data_1[index:i]

                    index = i
                    setbit=0
                    news = news.replace('<ul>', '')
                    news = news.replace('<li>', '')
                    news = news.replace('<b>', '')
                    date_key = news[0:index_1 - 3].strip()
                    setbit=1

                    tag_re = re.compile('<sup.*?</sup>')
                    setbit=0
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=1

                    news = re.sub(tag_re, '', news)
                    date_dict[date_key] = news.replace('\n','')
                    date_dict[date_key] = date_dict[date_key].replace('/b>','')
                    date_dict[date_key] = date_dict[date_key].replace(':','')
                    setbit=1

                    if(date_key.strip().split(' ')[0] in '0123456789'):
                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                setbit=0
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key])

                else:
                    return date_dict

            return date_dict

        for month in Singapore[yearAvailable[j]].keys():
                date_Dict = processor(Singapore[yearAvailable[j]][month], month)

                Singapore[yearAvailable[j]][month] = date_Dict

    return FinalDict

#Functions to fetch South Africa Data.
def South_Africa(item,AvailableMonth):
    
    South_Africa={}
    South_Africa['2020'] = {}
    South_Africa['2021'] = {}
    South_Africa['2022'] = {}
    FinalDict={}

    s1="""<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>"""
    s2="</span>"
    s3="""<li class="toclevel-1 tocsection-28"><a href="#References"><span class="tocnumber">5"""
    content=fileReader1(item,s1,s2,s3)

    def t_LCovidCountry13(t):
        r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
        return t

    def t_Year13(t):
        r'[0-9\-\sA-Za-z]+'
        return t

    def p_start11(p):
        '''start11 : CC13'''

    def p_CC13(p):
        ''' CC13 : LCovidCountry13 Year13'''
        p[0] = p[2]
        date = p[0].split()
        if (date[1] == '2021'):
            setbit=0
            South_Africa['2021'][date[0]] = {}
        if (date[1] == '2022'):
            setbit=1
            South_Africa['2022'][date[0]] = {}
        if (date[1] == '2020'):
            setbit=0
            South_Africa['2020'][date[0]] = {}

    tokens = ['LCovidCountry13', 'Year13']

    lexer = lex.lex()
    lexer.input(content)
    parser = yacc.yacc()
    parser.parse(content)

    s1="</span"
    s2="""<li class="toclevel-1 tocsection-28"><a href="#References"><span class="tocnumber">5"""
    s3="""<h2><span class="mw-headline" id="References">References"""
    content=fileReader2(item,s1,s2,s3)

    YearAvailable = ['2020', '2021', '2022']
    index_1 = 0
    setbit=0
    for element in South_Africa[YearAvailable[index_1]].keys():
        setbit=0
        line = '<h3><span class="mw-headline" id="' + element + '_' + YearAvailable[index_1] + '">'
        pattern = re.compile(line)
        result = pattern.search(content)
        setbit=1
        list1 = ''
        itr = str(result)
        list1 = itr.split('match=')
        setbit=0
        if (str(list1[0]) != 'None'):
            a = result.start()
            pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
            setbit=0
            result = pattern.search(content[a:])
            i = a + 1
            setbit=1
            news = ''
            while (content[i:i + 2] != '<h' or content[i:i + 3] == '<h2'):
                i += 1

            news = content[a:i]
            South_Africa[YearAvailable[index_1]][element] = news
    index_1 = 1

    for element in South_Africa[YearAvailable[index_1]].keys():
        line = '<h3><span class="mw-headline" id="' + element + '_' + YearAvailable[index_1] + '">'
        pattern = re.compile(line)
        result = pattern.search(content)
        list1 = ''
        itr = str(result)
        list1 = itr.split('match=')
        if (str(list1[0]) != 'None'):
            a = result.start()
            pattern = re.compile('On [0-9 A-Z a-z]*|By [0-9 A-Z a-z]*,')
            result = pattern.search(content[a:])
            i = a + 1
            news = ''
            while (content[i:i + 2] != '<h' or content[i:i + 3] == '<h2'):
                i += 1
            news = content[a:i]
            South_Africa[YearAvailable[index_1]][element] = news

    South_Africa['2022']['January']['31 January'] = 'On the 31st, the adjusted alert level 1 was changed by not requiring isolation for those who tested positive but have no symptoms. Those who tested positive but had symptoms, had to isolate for only 7 days (instead of the previous 10 days). Contacts did not have to isolate unless they developed symptoms. Primary, secondary, and special schools returned to daily attendance; and the requirement of social distancing of 1 meter in schools, was removed'

    def processor(data_dict,currYear,currMonth):
        index = 0
        temp = 0
        i = 0
        data_1 = str(data_dict)

        date_dict = {}

        while (len(data_1) - 2 >index):
            pattern = re.compile('<p>On [0-9 A-Za-z]*|<p>By [0-9 A-Za-z]*|<p>As of [0-9 A-Za-z]*')
            result = pattern.search(data_1[index:])

            itr = str(result)
            temp = ''
            list1 = itr.split('match=')

            if (str(list1[0]) != 'None'):
                index_1 = len(list1[1])

                temp = result.start()
                index = index + temp

                i = index + 1

                news = ''

                while ((data_1[i:i + len('<p>On')] != '<p>On' and data_1[i:i + len('<p>By')] != '<p>By' and data_1[i:i + len('<p>As of')] != '<p>As of') and i <= len(data_1) - 1):
                    i += 1

                news = data_1[index:i]

                list_date = []
                date_key = news[3:index_1 - 2]
                tag_re = re.compile('On|,|2020|By|As of|2021')
                date_key = re.sub(tag_re, '', date_key)
                list_date = date_key.split()
                date_key = list_date[0] + ' ' + list_date[1]

                index = i
                tag_re = re.compile('<sup.*?</sup>')
                news = re.sub(tag_re, '', news)
                setbit=0
                tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                news = re.sub(tag_re, '', news)
                setbit=1
                date_dict[date_key.strip()] = news.replace('\n','')
                news=news.replace('\n','')
                dayget=date_key.strip().split(" ")

                if(len(dayget[0])==1):
                    dayget[0]='0'+dayget[0]
                
                month=AvailableMonth.index(currMonth)+1
                month=str(month)
                if(len(month)==1):
                    month='0'+month

                for item in dayget[0]:
                    if item not in '0123456789':
                        dayget[0]=dayget[1][0:2]
                        if(dayget[0][-1]=='t'):
                            dayget[0]='0'+dayget[0:1]
                        break

                key=dayget[0]+'-'+month+'-'+currYear
                if(key not in FinalDict.keys()):
                    FinalDict[key]=[]
                FinalDict[key].append(news)
            else:
                return date_dict

        return date_dict

    Year_1 = ['2020', '2021']

    for year in Year_1:
        for month in South_Africa[year].keys():
            currYear=year
            currMonth=month
            date_Dict = processor(South_Africa[year][month],currYear,currMonth)
            South_Africa[year][month] = date_Dict


    return FinalDict

#Functions to fetch Spain Data.
def Spain(item,AvailableMonth):
    
    Spain={}
    Spain['2020'] = {}
    FinalDict={}

    s1="""<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>"""
    s2="</span>"
    s3="""<li class="toclevel-1 tocsection-6"><a href="#References"><span class="tocnumber">6"""
    content=fileReader1(item,s1,s2,s3)

    def t_LCovidCountry14(t):
        r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
        return t

    def t_Year14(t):
        r'[0-9\-\sA-Za-z]+'
        return t

    def p_start12(p):
        '''start12 : CC14'''

    def p_CC14(p):
        ''' CC14 : LCovidCountry14 Year14'''
        p[0] = p[2]
        Spain['2020'][p[0]] = {}

    tokens = ['LCovidCountry14', 'Year14']

    lexer = lex.lex()
    lexer.input(content)
    parser = yacc.yacc()
    parser.parse(content)

    s1="</span"
    s2="""<li class="toclevel-1 tocsection-6"><a href="#References"><span class="tocnumber">6"""
    s3="""<h2><span class="mw-headline" id="References">References"""
    content=fileReader2(item,s1,s2,s3)

    YearAvailable = ['2020']
    index_1 = 0
    for element in Spain[YearAvailable[index_1]].keys():

        setbit=1
        line = '<h2><span class="mw-headline" id="' + element + '">'
        pattern = re.compile(line)
        result = pattern.search(content)
        a = result.start()
        setbit=0
        i = a + 1
        news = ''
        while (content[i:i + 4] != '<h2>'):
            i += 1

        news = content[a:i]
        Spain[YearAvailable[index_1]][element] = news
            

    def processor(data_dict,currYear,currMonth,Mode):
        index = 0
        temp = 0
        i = 0
        data_1 = str(data_dict)

        date_dict = {}

        if(Mode==1):

            while (len(data_1) - 2 >index):
                setbit=0
                pattern = re.compile('<p>On [0-9 A-Za-z]*|<p>By [0-9 A-Za-z]*|<p>As of [0-9 A-Za-z]*')
                result = pattern.search(data_1[index:])

                itr = str(result)
                temp = ''
                list1 = itr.split('match=')

                if (str(list1[0]) != 'None'):
                    index_1 = len(list1[1])

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''

                    while ((data_1[i:i + len('<p>On')] != '<p>On' and data_1[i:i + len('<p>By')] != '<p>By' and data_1[i:i + len('<p>As of')] != '<p>As of') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    list_date = []
                    date_key = news[3:index_1 - 2]
                    tag_re = re.compile('On|,|2020|By|As of|2021')
                    date_key = re.sub(tag_re, '', date_key)
                    list_date = date_key.split()
                    date_key = list_date[0] + ' ' + list_date[1]

                    index = i
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news)
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=0
                    news = re.sub(tag_re, '', news)

                    date_dict[date_key.strip()] = news.replace('\n','')
                    news=news.replace('\n','')
                    dayget=date_key.strip().split(" ")

                    if(len(dayget[0])==1):
                        dayget[0]='0'+dayget[0]
                    
                    month=AvailableMonth.index(currMonth)+1
                    month=str(month)
                    if(len(month)==1):
                        month='0'+month

                    for item in dayget[0]:
                        if item not in '0123456789':
                            dayget[0]=dayget[1][0:2]
                            if(dayget[0][-1]=='t'):
                                dayget[0]='0'+dayget[0:1]
                            break

                    key=dayget[0]+'-'+month+'-'+currYear
                    if(key not in FinalDict.keys()):
                        FinalDict[key]=[]
                    FinalDict[key].append(news)
                else:
                    return date_dict

            return date_dict
        
        elif(Mode==0):
            while (len(data_1) - 2 >index):
                pattern = re.compile('<dl><dt>[0-9 A-Z a-z ]*|<p><b>[0-9 A-Z a-z ]*')
                result = pattern.search(data_1[index:])

                itr = str(result)
                temp = ''
                list1 = itr.split('match=')

                if (str(list1[0]) != 'None'):
                    index_1 = len(list1[1])

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''
                    while ((data_1[i:i + len('<dl><dt>')] != '<dl><dt>' and data_1[i:i + len('<p><b>')] != '<p><b>' and i <= len(data_1) - 1)):
                        i += 1

                    news = data_1[index:i]

                    list_date = []
                    date_key = news[0:index_1 - 2]
                    tag_re = re.compile('On|,|2020|By|As of|2021|<dl><dt>|<p><b>|:|<|>')
                    date_key = re.sub(tag_re, '', date_key)
                    list_date = date_key.split()
                    setbit=0
                    date_key = list_date[0] + ' ' + list_date[1]

                    index = i
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news)
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=0
                    news = re.sub(tag_re, '', news)

                    date_dict[date_key.strip()] = news.replace('\n','')
                    news=news.replace('\n','')
                    dayget=date_key.strip().split(" ")

                    if(len(dayget[0])==1):
                        dayget[0]='0'+dayget[0]
                    
                    month=AvailableMonth.index(currMonth)+1
                    month=str(month)
                    if(len(month)==1):
                        month='0'+month

                    for item in dayget[0]:
                        if item not in '0123456789':
                            dayget[0]=dayget[1][0:2]
                            if(dayget[0][-1]=='t'):
                                dayget[0]='0'+dayget[0:1]
                            break

                    key=dayget[0]+'-'+month+'-'+currYear
                    if(key not in FinalDict.keys()):
                        FinalDict[key]=[]
                    FinalDict[key].append(news)
                else:
                    return date_dict

            return date_dict

    Year_1 = ['2020']

    for year in Year_1:
        for month in Spain[year].keys():

            currYear=year
            currMonth=month

            if (month == 'March' or month == 'April' or month == 'June'):
                date_Dict = processor(Spain[year][month],currYear,currMonth,0)
                Spain[year][month] = date_Dict

            else:
                date_Dict = processor(Spain[year][month],currYear,currMonth,1)
                Spain[year][month] = date_Dict
            
    
    return FinalDict

#Functions to fetch Turkey Data.
def Turkey(item,AvailableMonth):
    
    Turkey={}
    Turkey['2020'] = {}
    Turkey['2021'] = {}
    date_list = []
    temp_list = []
    FinalDict={}

    s1="""<div id="toc" class="toc" role="navigation" aria-labelledby="mw-toc-heading"><input type="checkbox" role="button" id="toctogglecheckbox" class="toctogglecheckbox" style="display:none" /><div class="toctitle" lang="en" dir="ltr"><h2 id="mw-toc-heading">Contents</h2><span class="toctogglespan"><label class="toctogglelabel" for="toctogglecheckbox"></label></span></div>"""
    s2="</span>"
    s3="""<li class="toclevel-1 tocsection-81"><a href="#See_also"><span class="tocnumber">13"""
    content=fileReader1(item,s1,s2,s3)

    def t_LCovidCountry15(t):
        r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]+"><a\shref="\#'
        return t

    def t_Year15(t):
        r'[0-9\-\sA-Za-z\_]+'
        return t

    def p_start13(p):
        '''start13 : CC15'''

    def p_CC15(p):
        ''' CC15 : LCovidCountry15 Year15'''
        p[0] = p[2]
        
        if (p[0][0].isdigit()):
            date_list.append(p[0])
            

    tokens = ['LCovidCountry15', 'Year15']

    lexer = lex.lex()
    lexer.input(content)
    parser = yacc.yacc()
    parser.parse(content)

    flag = 1
    setbit=0
    for element in date_list:
        temp_list = element.split('_')
        if (flag == 1):
            setbit=1
            Turkey['2020'][temp_list[1]] = {}
        if (flag == 0):
            setbit=1
            Turkey['2021'][temp_list[1]] = {}
        if (element == '13_December'):
            setbit=1
            flag = 0

    flag = 1
    setbit=0
    for element in date_list:
        temp_list = element.split('_')
        if (flag == 0):
            setbit=1
            str_1 = temp_list[0] + ' ' + temp_list[1]
            Turkey['2021'][temp_list[1]][str_1] = {}
        if (flag == 1):
            setbit=1
            str_1 = temp_list[0] + ' ' + temp_list[1]
            Turkey['2020'][temp_list[1]][str_1] = {}
        if (element == '13_December'):
            setbit=1
            flag = 0
    
    Turkey['2020']['October']['2 October'] = 'The Ministry of Health released its September weekly reports with delay, approximately a month after the weekly report covering 24–30 August. The ministry, which explained the number of cases in previous reports, started to give data on the number of patients instead of cases in new reports'
    Turkey['2020']['October']['9 October'] = 'Fahrettin Koca announced the latest developments in making an indigenous vaccine and added that trials on humans would probably begin in 2 weeks.'
    Turkey['2020']['September']['30 September'] = 'The Minister of Health, Fahrettin Koca, released a statement after meeting with the Coronavirus Scientific Advisory Board and said, "Not every case is sick. Because there are those who test positive but show no symptoms, and they are the vast majority."[176] Explaining the distinction between definitions of patient and case, Koca said, "The number of new patients that are announced and focused on every day should be an issue of attention'
    Turkey['2021']['January']['1 January'] = 'Turkey detected 15 cases of the UK coronavirus variant on 1 January 2021.'
    Turkey['2021']['January']['14 January'] = 'On 14 January 2021, Turkish President Recep Tayyip Erdoğan received the COVID-19 vaccine'

    s1="</span"
    s2="""<h2><span class="mw-headline" id="January_2020">January 2020"""
    s3="""<h2><span class="mw-headline" id="January_2021">January 2021"""
    content=fileReader2(item,s1,s2,s3)


    YearAvailable = ['2020']
    index_1 = 0
    currYear='2020'

    for element in Turkey[YearAvailable[index_1]].keys():
        currMonth=element
        for date in Turkey[YearAvailable[index_1]][element].keys():
            date1=date
            date1 = date1.replace(' ', '_')
            daycur=date1.split("_")
            currDay=daycur[0]

            if(len(currDay)==1):
                currDay='0'+currDay
            month=AvailableMonth.index(currMonth)+1
            month=str(month)
            if(len(month)==1):
                month='0'+month

            key=currDay+'-'+month+'-'+currYear
            setbit=0

            line = '<h3><span class="mw-headline" id="' + date1 + '">'
            
            pattern = re.compile(line)
            result = pattern.search(content)
            setbit=1
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')
            if (str(list_1[0]) != 'None'):

                a = result.start()
                i = a + 1
                news = ''
                while (content[i:i + 2] != '<h'):
                    i += 1

                news = content[a:i]
                tag_re = re.compile('<sup.*?</sup>')
                news = re.sub(tag_re, '', news)
                setbit=1
                tag_re = re.compile('<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                setbit=0
                news = re.sub(tag_re, '', news)
                x = date + '[edit]'
                news = news.replace(x, '')
                news = news.replace('\n', '')
                # print(news)
                if key not in FinalDict.keys():
                    FinalDict[key]=[]
                if news not in FinalDict[key]:
                    FinalDict[key].append(news)       
    
    return FinalDict

#Functions to fetch England Data.
def England(item1,item2,item3,item4,AvailableMonth):
    
    England={}
    England['2020'] = {}
    England['2021'] = {}
    England['2022'] = {}
    yearAvailable=['2020','2020','2021','2022']
    FinalDict={}
    links=[]
    links.append(item1)
    links.append(item2)
    links.append(item3)
    links.append(item4)

    for j in range(0,4):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>"""  in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry26(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]*"><a\shref="[#0-9-0-9_A-Z a-z]*"><span\sclass="tocnumber">[0-9.0-90-9]*</span>\s<span\sclass="toctext">'
            return t

        def t_Year26(t):
            r'[0-9\sA-Za-z\-]+'
            return t

        def p_start24(p):
            '''start24 : CC26'''

        def p_CC26(p):
            ''' CC26 : LCovidCountry26 Year26'''

            p[0] = p[2]
            list_1 = p[0].split()
            if (list_1[0] in AvailableMonth):
                England[yearAvailable[j]][list_1[0]] = {}
                
        tokens = ['LCovidCountry26', 'Year26']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h2><span class="mw-headline" id="Timeline">Timeline"""  in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="See_also">See also""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for month in England[yearAvailable[j]].keys():
            setbit=0
            line = '<h3><span class="mw-headline" id="' + month + '_' + yearAvailable[j] + '">'
            pattern = re.compile(line)
            result = pattern.search(content)
            setbit=1
            list_1 = ''
            itr = str(result)

            list_1 = itr.split('match=')

            if (str(list_1[0]) != 'None'):
                a = result.start()
                i = a + 1

                news = ''

                while (content[i:i + 2] != '<h'):
                    i += 1

                news = content[a:i]

                England[yearAvailable[j]][month] = news


        def processor(data_dict, month):
            index = 0
            temp = 0
            i = 0
            data_1 = str(data_dict)
            date_dict = {}
            temp_s=''
            while (index < len(data_1) - 5):
                pattern = re.compile('<ul><li>[ A-Z a-z 0-9]* -|<ul><li>[ A-Z a-z 0-9-]*|<li>[ A-Z a-z 0-9]* -|<li>[ A-Z a-z 0-9-]*')
                result = pattern.search(data_1[index:])

                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')

                if (str(list_1[0]) != 'None'):
                    str_1 = str(list_1[1])
                    str_1 = str_1.replace('<ul>', '')
                    str_1 = str_1.replace('<li>', '')
                    index_1 = len(str_1)

                    temp = result.start()
                    index = index + temp

                    i = index + 1

                    news = ''
                    
                    while ((data_1[i:i + 5] != '</ul>') and (data_1[i:i + len('</li>\n<li>')] != '</li>\n<li>') and i <= len(data_1) - 1):
                        i += 1

                    news = data_1[index:i]

                    index = i
                    setbit=0
                    news = news.replace('<ul>', '')
                    news = news.replace('<li>', '')
                    date_key = news[0:index_1 - 2]
                    list_date = date_key.split()
                    setbit=0
                    if (len(list_date) >= 2):
                        setbit=1
                        date_key = list_date[0] + ' ' + list_date[1]

                    setbit=0
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news[index_1 - 2:])
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n:&#([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
                    setbit=0
                    news = re.sub(tag_re, '', news)
                    if (date_key == '10-13 March'):
                        setbit=0
                        date_key='10 March'

                    if(date_key[0].isdigit()):
                        setbit=1
                        date_dict[date_key.strip()] = news.replace('\n','')

                        curD=str(date_key.strip()).split(" ")
                        if(len(curD)==2):
                            currDay=curD[0]
                            if(len(currDay)==1):
                                currDay='0'+currDay

                            month=''
                            if(curD[1] in AvailableMonth):
                                month=AvailableMonth.index(curD[1])+1
                                month=str(month)
                                if(len(month)==1):
                                    month='0'+month

                        currYear=yearAvailable[j]
                        key=currDay+'-'+month+'-'+currYear
                        if key not in FinalDict.keys():
                            FinalDict[key]=[]
                        if news not in FinalDict[key]:
                            FinalDict[key].append(date_dict[date_key.strip()])

                else:
                    return date_dict

            return date_dict

        for month in England[yearAvailable[j]].keys():
            date_Dict = processor(England[yearAvailable[j]][month], month)
            England[yearAvailable[j]][month] = date_Dict

    return FinalDict

#Function to fetch US Data.
def US(item1,item2,AvailableMonth):
    
    links=[]
    links.append(item1)
    links.append(item2)

    US={}
    US['2020']={}
    US['2021']={}
    yearAvailable=['2020','2021']
    date_list = []
    FinalDict={}

    US['2020']['January'] = {}
    US['2020']['February'] = {}

    for j in range(0,2):
        ctr = 0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            if ("""<li class="toclevel-1 tocsection-2"><a href="#Timeline"><span class="tocnumber">2</span> <span class="toctext">Timeline</span></a>""" in line.strip() or """<li class="toclevel-1 tocsection-1"><a href="#Timeline"><span class="tocnumber">1</span> <span class="toctext">Timeline</span></a>""" in line.strip() or ctr == 1):
                dateFetch = line.split("</span>")
                if ("""<li class="toclevel-1 tocsection-117"><a href="#References"><span class="tocnumber">3""" in dateFetch[0] or """<li class="toclevel-1 tocsection-73"><a href="#References"><span class="tocnumber">2""" in dateFetch[0]):
                    ctr = 0
                    f2.write(dateFetch[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        def t_LCovidCountry16(t):
            r'<li\sclass="toclevel-[0-9]*\stocsection-[0-9]+"><a\shref="\#'
            return t

        def t_Year16(t):
            r'[0-9\-\sA-Za-z\_]+'
            return t

        def p_start14(p):
            '''start14 : CC16'''

        def p_CC16(p):
            ''' CC16 : LCovidCountry16 Year16'''
            p[0] = p[2]
            dateR=str(p[0]).split("_")
            
            if (len(dateR) == 2):
                date_list.append(p[0])

        tokens = ['LCovidCountry16', 'Year16']

        lexer = lex.lex()
        lexer.input(content)
        parser = yacc.yacc()
        parser.parse(content)

        flag = 1
        for element in date_list:

            temp_list = element.split('_')
            if (flag == 1):
                US[yearAvailable[j]][temp_list[0]] = {}

        flag = 1
        for element in date_list:
            temp_list = element.split('_')
            if (flag == 1):
                str_1 = temp_list[0] + ' ' + temp_list[1]
                US[yearAvailable[j]][temp_list[0]][str_1] = {}
        
        ctr=0
        f1=open(links[j],"r")
        f2=open("Countrytemp.html","w")
        for line in f1:
            dateFetch = line.split("</span")
            if ("""<h4><span class="mw-headline" id="March_4">March 4""" in dateFetch[0].strip() or """<h2><span class="mw-headline" id="Timeline">Timeline""" in dateFetch[0].strip() or ctr == 1):
                dateFetch1 = line.split("</span>")
                if ("""<h2><span class="mw-headline" id="References">References""" in dateFetch1[0]):
                    ctr = 0
                    f2.write(dateFetch1[0])
                else:
                    ctr = 1
                    f2.write(line)
        f1.close()
        f2.close()

        file=open("Countrytemp.html",'r')
        content=file.read()
        file.close()

        for element in US[yearAvailable[j]].keys():
            for date in US[yearAvailable[j]][element].keys():
                date1 = date
                date1 = date1.replace(' ', '_')
                setbit=0
                line = '<h4><span class="mw-headline" id="' + date1 + '">'
                pattern = re.compile(line)
                result = pattern.search(content)
                setbit=1
                list_1 = ''
                itr = str(result)

                list_1 = itr.split('match=')
                if (str(list_1[0]) != 'None'):
                    a = result.start()
                    i = a + 1

                    news = ''

                    while (content[i:i + 2] != '<h'):
                        i += 1

                    news = content[a:i]
                    tag_re = re.compile('<sup.*?</sup>')
                    news = re.sub(tag_re, '', news)
                    setbit=1
                    tag_re = re.compile('<.*?>|&\n([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

                    news = re.sub(tag_re, '', news)
                    setbit=0
                    x = date + '[edit]'
                    news = news.replace(x, '')
                    news=news.replace('\n','')
                    setbit=1

                    curD=date.split(" ")
                    currDay=curD[1]
                    if(len(currDay)==1):
                        currDay='0'+currDay

                    currYear=yearAvailable[j]
                    currMonth=element
                    month=AvailableMonth.index(currMonth)+1
                    month=str(month)
                    if(len(month)==1):
                        month='0'+month
                    
                    key=currDay+'-'+month+'-'+currYear
                    if key not in FinalDict.keys():
                        FinalDict[key]=[]
                    if news not in FinalDict[key]:
                        FinalDict[key].append(news) 

    return FinalDict

#Function to fetch country Covid Data.
def fetchCountryCovidData():
    
    CountryCovidData={}
    url='https://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic_in_'
    CountryCovidNames=fetchCountryCovidHTML(url)

    AvailableMonth=['January','February','March','April','May','June','July','August','September','October','November','December']

    global countryRange
    setbit=0

    #CountryContentFetch.
    for item in CountryCovidNames:    

        fileSplit=item.split("_")
        cname=""
        if(fileSplit[0]=='New'):
            cname='New Zealand'
        elif(fileSplit[0]=='South'):
            cname='South Africa'
        elif(fileSplit[0]=='the'):
            if(fileSplit[1]=='Philippines'):
                cname='Philippines'
            elif(fileSplit[1]=='United'):
                cname='United States'
            else:
                cname='Ireland'
        else:
            fileSplit1=fileSplit[0].split(".")
            cname=fileSplit1[0]

        if cname not in CountryCovidData.keys():
            CountryCovidData[cname]={}
            
        if(cname=='Argentina'):
            countryRange[cname]='February,2020-January,2021'
            CountryCovidData[cname]=Argentina(item,AvailableMonth)
        elif(cname=='Australia' and setbit==0):
            setbit=1
            countryRange[cname]='January,2020-February,2022'
            CountryCovidData[cname]=Australia('Australia_(2020).html','Australia_(January-June_2021).html','Australia_(July-December_2021).html','Australia_(2022).html',AvailableMonth)
        elif(cname=='Bangladesh'):
            countryRange[cname]='January,2020-June,2021'
            CountryCovidData[cname]=Bangladesh(item,AvailableMonth)
        elif(cname=='Brazil'):
            countryRange[cname]='November,2019-January,2022'
            CountryCovidData[cname]=Brazil(item,AvailableMonth)
        elif(cname=='Canada'):
            countryRange[cname]='December,2019-April,2021'
            CountryCovidData[cname]=Canada(item,AvailableMonth)
        elif(cname=='Ghana'):
            countryRange[cname]='March,2020-February,2022'
            CountryCovidData[cname]=Ghana('Ghana_(March-July_2020).html','Ghana_(August-December_2020).html','Ghana_(2021).html',AvailableMonth)   
        elif(cname=='India'):
            countryRange[cname]='January,2020-May,2021'
            CountryCovidData[cname]=India(item,AvailableMonth)
            continue
        elif(cname=='Indonesia'):
            setbit=1
            countryRange[cname]='February,2020-December,2021'
            CountryCovidData[cname]=Indonesia('Indonesia_(2020).html','Indonesia_(2021).html',AvailableMonth)  
        elif(cname=='Ireland'):
            setbit=1
            countryRange[cname]='January,2020-March,2022'
            CountryCovidData[cname]=Ireland('the_Republic_of_Ireland_(January-June_2020).html','the_Republic_of_Ireland_(July-December_2020).html','the_Republic_of_Ireland_(January-June_2021).html','the_Republic_of_Ireland_(July-December_2021).html','the_Republic_of_Ireland_(2022).html',AvailableMonth)
        elif(cname=='Malaysia'):
            setbit=1
            countryRange[cname]='January,2020-February,2022'
            CountryCovidData[cname]=Malaysia('Malaysia_(2020).html','Malaysia_(2021).html','Malaysia_(2022).html',AvailableMonth)
        elif(cname=='Mexico'):
            countryRange[cname]='January,2020-August,2020'
            CountryCovidData[cname]=Mexico(item,AvailableMonth)
        elif(cname=='New Zealand'):
            countryRange[cname]='February,2020-March,2022'
            CountryCovidData[cname]=New_Zealand('New_Zealand_(2020).html','New_Zealand_(2021).html','New_Zealand_(2022).html',AvailableMonth)
        elif(cname=='Nigeria'):
            countryRange[cname]='Feb,2020-June,2021'
            CountryCovidData[cname]=Nigeria('Nigeria_(February-June_2020).html','Nigeria_(July-December_2020).html','Nigeria_(2021).html',AvailableMonth)
        elif(cname=='Pakistan'):
            countryRange[cname]='January,2020-March,2021'
            CountryCovidData[cname]=Pakistan(item,AvailableMonth)
        elif(cname=='Philippines'):
            countryRange[cname]='January,2020-February,2022'
            CountryCovidData[cname]=Philippines('the_Philippines_(2020).html','the_Philippines_(2021).html','the_Philippines_(2022).html',AvailableMonth)
        elif(cname=='Russia'):
            countryRange[cname]='January,2020-September,2020'
            CountryCovidData[cname]=Russia('Russia_(January-June_2020).html','Russia_(July-December_2020).html',AvailableMonth)
        elif(cname=='Singapore'):
            countryRange[cname]='January,2020-March,2022'
            CountryCovidData[cname]=Singapore('Singapore_(2020).html','Singapore_(2021).html','Singapore_(2022).html',AvailableMonth)
        elif(cname=='South Africa'):
            countryRange[cname]='March,2020-January,2022'
            CountryCovidData[cname]=South_Africa(item,AvailableMonth)
        elif(cname=='Spain'):
            countryRange[cname]='January,2020-June,2021'
            CountryCovidData[cname]=Spain(item,AvailableMonth)
        elif(cname=='Turkey'):
            countryRange[cname]='January,2020-January,2021'
            CountryCovidData[cname]=Turkey(item,AvailableMonth)
        elif(cname=='England'):
            countryRange[cname]='January,2020-March,2022'
            CountryCovidData[cname]=England('England_(January-June_2020).html','England_(July-December_2020).html','England_(2021).html','England_(2022).html',AvailableMonth)
        elif(cname=='United States'):
            countryRange[cname]='January,2020-December,2021'
            CountryCovidData[cname]=US('the_United_States_(2020).html','the_United_States_(2021).html',AvailableMonth)   

    return CountryCovidData

#Function to find jaccard similarity of 2 texts.
def Jaccard(news1,news2):

    news1=removeStopWords(news1)
    news2=removeStopWords(news2)

    # List the unique words in a document
    words_doc1 = set(news1.lower().split()) 
    words_doc2 = set(news2.lower().split())
    
    # Find the intersection of words list of doc1 & doc2
    intersection = words_doc1.intersection(words_doc2)

    # Find the union of words list of doc1 & doc2
    union = words_doc1.union(words_doc2)

    #print(len(intersection),len(union))

    if(len(union)==0):
        return 0.0
        
    # Calculate Jaccard similarity score 
    # using length of intersection set divided by length of union set
    
    return float(len(intersection)) / len(union)

#Function to take user input.
def userInputFn(TimelineContent,ResponseContent,countryCovidData):

    availableData=['Worldwide News within the Time Range',\
        'Worldwide Responses within the Time Range',\
            'Given Two non-overlapping Time Ranges : Plot two different word clouds for all the common words and only covid related common words',\
                'Given Two non-overlapping Time Ranges : Print the percentage of covid related words in common words',\
                    'Given Two non-overlapping Time Ranges : Print the top-20 common words (ignore stopwords) and covid related word',\
                        'Given a country name, show the date range for which news information is available for that country',\
                            'Given a country name and date range, extract all the news between the time duration,plot a word cloud',\
                                'Provide names of the top-3 closest countries according to the Jaccard similarity of the extracted news.',\
                                    'Provide names of the top-3 closest countries according to Jaccard similarity of covid words match.']
    
    availableCountries=['Argentina','Australia','Bangladesh',\
        'Brazil','Canada','Ghana','India','Indonesia','Ireland',\
            'Malaysia','Mexico','New Zealand','Nigeria','Pakistan',\
                'Philippines','Russia','Singapore','South Africa',\
                    'Spain','Turkey','England','United States']
    
    while 1:
        print("\nData Available\n")
        print("[1] Covid Stats")
        print("[2] Covid News")
        print("[-1] Exit")
        print("\nEnter the option from Above (-1/1/2) : ",end=" ")


        while (1):
            try:
                inputUser1=int(input())
            except Exception as exception:
                print("Invalid Input!! Try Again")
                continue
            break

        if inputUser1 not in [-1,1,2]:
            print("Invalid input Try Again!!")
            continue

        if inputUser1==-1:
            break

        #covid Stats
        if inputUser1==1:
            os.system("python3 task1b.py")
            
        #Covid News
        if inputUser1==2:

            while(1):
                print("\nDetails Available : ")
                count=1
                for item in availableData:
                    print('['+str(count)+']'+" "+item)
                    count+=1

                print("[0] Go Back")
                print("[-1] Exit")
                print("\nEnter the option from Above (-1/0 ",end="")

                for i in range(1,10):
                    print("/"+str(i),end='')
                print(") :",end=" ")

                while (1):
                    try:
                        inputUser2=int(input())
                    except Exception as exception:
                        print("\nInvalid Input!! Try Again")
                        continue
                    break
                
                if inputUser2==0:
                    break

                if inputUser2==-1:
                    exit(0)
                
                if inputUser2 not in range(0,10):
                    print("\nInvalid input Try Again!!")
                    continue
                else:
                    if(inputUser2==1 or inputUser2==2):
                        print("\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                        while 1:
                            DateRange=input()
                            while(checkDateValid(DateRange)!=1):
                                print("\nInvalid Date Format Try Again!!\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                DateRange=input()

                            # print(DateRange)
                            if(inputUser2==1):
                                info,status=fetchTDDR(TimelineContent,1,DateRange,1)
                                if(status==0):
                                    print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    continue
                                else:
                                    
                                    plotWordCloud(info)
                                    break
                            else:
                                info,status=fetchTDDR(ResponseContent,2,DateRange,1)
                                if(status==0):
                                    print("Given Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    continue
                                else:

                                    plotWordCloud(info)
                                    break

                    if(inputUser2==3 or inputUser2==4 or inputUser2==5):

                        while 1:
                            print("\nEnter two Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]\n")
                            print("Enter Date Range 1 : ",end="")
                            DateRange1=input()
                            while(checkDateValid(DateRange1)!=1):
                                print("\nInvalid Date Format Try Again!!\nEnter the Date Range 1 in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                DateRange1=input()
                            print("\nEnter Date Range 2 : ",end="")
                            DateRange2=input()
                            while(checkDateValid(DateRange2)!=1):
                                print("\nInvalid Date Format Try Again!!\nEnter the Date Range 2 in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                DateRange2=input()
                            while(checkDateOverlap(DateRange1,DateRange2)!=1):
                                print("\nDate Range overlapping Try Again!!")
                                print("\nEnter two Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]\n")
                                print("Enter Date Range 1 : ",end="")
                                DateRange1=input()
                                while(checkDateValid(DateRange1)!=1):
                                    print("\nInvalid Date Format Try Again!!\nEnter the Date Range 1 in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]\n")
                                    DateRange1=input()
                                print("\nEnter Date Range 2 : ",end="")
                                DateRange2=input()
                                while(checkDateValid(DateRange2)!=1):
                                    print("\nInvalid Date Format Try Again!!\nEnter the Date Range 2 in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    DateRange2=input()


                            info1,status=fetchTDDR(TimelineContent,1,DateRange1,2)
                            if(status==0):
                                print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                continue
                            else:
                                info2,status=fetchTDDR(TimelineContent,1,DateRange2,2)
                                if(status==0):
                                    print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    continue
                                else:
                                    break
                        
                        commonWords,commonText=findCommonWords(info1,info2,1)
                        covidCommonWords,covidCommonText=findCommonWords(commonWords,[],2)

                        if(inputUser2==3):
                            plotWordCloud(commonText)
                            plotWordCloud(covidCommonText)
                        elif(inputUser2==4):
                            len1=len(commonWords)
                            len2=len(covidCommonWords)
                            # print(len1,len2)
                            percentage=(len2/len1)*100
                            print("\nPercentage of Covid Related Words in Common Words : "+str(percentage))
                        else:
                            print("\nTop 20 Common Words : \n")
                            i=0
                            for item in commonWords:
                                if i==10:
                                    break
                                if(item!=''):
                                    print(item,end=",")
                                    i+=1
                            print("\nTop 20 Covid Related Common Words: \n")
                            i=0
                            for item in covidCommonWords:
                                if i==10:
                                    break
                                if(item!=''):
                                    print(item,end=",")
                                    i+=1
                    
                    if(inputUser2==6 or inputUser2==7 or inputUser2==8 or inputUser2==9):
                        print("\nChoose a Country:")
                        print("\nAvailable Countries : \n")
                        count=1
                        for key in availableCountries:
                            print('['+str(count)+']'+" "+key,end=" ")
                            count+=1

                        print("[0] Go Back",end=" ")
                        print("[-1] Exit\n")
                        print("\nEnter the option from Above (-1/0 ",end="")

                        for i in range(1,23):
                            print("/"+str(i),end='')
                        print(") :",end=" ")
                        
                        while (1):
                            try:
                                inputUser3=int(input())
                            except Exception as exception:
                                print("\nInvalid Input!! Try Again")
                                continue
                            break
                        
                        if inputUser3==0:
                            break

                        if inputUser3==-1:
                            exit(0)
                        
                        if inputUser3 not in range(0,23):
                            print("\nInvalid input Try Again!!")
                            continue

                        chosenCountry=availableCountries[inputUser3-1]
                        if(inputUser2==6):
                            print("Chosen Country has data in the range : ",end="")
                            print(FindRange(chosenCountry))
                        
                        info=""
                        
                        if(inputUser2==7):
                            if(inputUser3==7):
                                print("\nNot Available")
                                print("\nContinue? [1] YES [2] NO")
                                while (1):
                                    try:
                                        inputUser3=int(input())
                                    except Exception as exception:
                                        print("\nInvalid Input!! Try Again")
                                        continue
                                    break

                                while(inputUser3 not in [1,2]):
                                    print("\nInvalid input!! Enter Again")
                                    inputUser3=int(input())
                                if inputUser3==2:
                                    exit(0)

                                continue   

                            print("\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                            while 1:
                                DateRange=input()
                                while(checkDateValid(DateRange)!=1):
                                    print("\nInvalid Date Format Try Again!!\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    DateRange=input()

                                info,status=fetchCCD(countryCovidData[availableCountries[inputUser3-1]],DateRange,1)
                                if(status==0):
                                    print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                    continue
                                else:
                                    plotWordCloud(info)
                                    break

                        if(inputUser2==8):

                            if(len(info)==0):
                                print("\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                while 1:
                                    DateRange=input()
                                    while(checkDateValid(DateRange)!=1):
                                        print("\nInvalid Date Format Try Again!!\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                        DateRange=input()

                                    info,status=fetchCCD(countryCovidData[availableCountries[inputUser3-1]],DateRange,2)
                                    if(status==0):
                                        print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                        continue
                                    else:
                                        break
                            topJaccard={}
                            for key in countryCovidData.keys():
                                tempInfo,tempStatus=fetchCCD(countryCovidData[key],DateRange,2)
                                # if(tempStatus==0):
                                #     continue
                                if((key!=chosenCountry) and (key not in topJaccard.keys())):
                                    topJaccard[key]=Jaccard(info,tempInfo)
                                
                                    
                            
                            print("Top 3 Closest Country as per Extracted News : ",end="")
                            JaccList = sorted(topJaccard.items(), key=lambda x:x[1],reverse=True)
                            sortedict = dict(JaccList)
                            ctr=0
                            for key in sortedict.keys():
                                if ctr==3:
                                    break
                                else:
                                    ctr+=1
                                    print(str(key),end=' ')
                            
                            #print(topJaccard)
                        info=""

                        if(inputUser2==9):
                            if(len(info)==0):
                                print("\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                while 1:
                                    DateRange=input()
                                    while(checkDateValid(DateRange)!=1):
                                        print("\nInvalid Date Format Try Again!!\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                        DateRange=input()

                                    info,status=fetchCCD(countryCovidData[availableCountries[inputUser3-1]],DateRange,2)
                                    if(status==0):
                                        print("\nGiven Date Range not Present!! Try Again\nEnter the Date Range in the format [DD-MM-YYYY,DD-MM-YYYY] ex:[19-02-2021,24-02-2021]")
                                        continue
                                    else:
                                        break

                            covidCommonWords,covidCommonText=findCommonWords(info,'',2)
                            topJaccard={}
                            for key in countryCovidData.keys():
                                tempInfo,tempStatus=fetchCCD(countryCovidData[key],DateRange,2)
                                # if(tempStatus==0):
                                #     continue
                                tempcovidCommonWords,tempcovidCommonText=findCommonWords(tempInfo,'',2)
                                #print(len(info),len(tempInfo))
                                if((key!=chosenCountry) and (key not in topJaccard.keys())):
                                    topJaccard[key]=Jaccard(covidCommonText,tempcovidCommonText)
                            
                            print("Top 3 Closest Country as per Covid Words Match : ",end="")
                            JaccList = sorted(topJaccard.items(), key=lambda x:x[1],reverse=True)
                            sortedict = dict(JaccList)
                            ctr=0
                            for key in sortedict.keys():
                                if ctr==3:
                                    break
                                else:
                                    ctr+=1
                                    print(str(key),end=' ')
                            

                print("\nContinue? [1] YES [2] NO")

                while (1):
                    try:
                        inputUser3=int(input())
                    except Exception as exception:
                        print("\nInvalid Input!! Try Again")
                        continue
                    break

                while(inputUser3 not in [1,2]):
                    print("\nInvalid input!! Enter Again")
                    inputUser3=int(input())
                if inputUser3==2:
                    exit(0)

#Driver Function
def main():

    print("\nWelcome to \"Covi-Tracker\" : An Complete information Platform on Covid Pandemic \n")

    #Fetching Database
    print("Update : Creating Database . . . [3~5 Mins] ")

    #Fetching Main website HTML.
    url = 'https://en.wikipedia.org/wiki/Timeline_of_the_COVID-19_pandemic'
    fetchMainWikiHTML(url)

    print("\nUpdate : Fetching Country Pages...")
    os.system("python3 task1a.py")
    print("\nUpdate : Country Pages Fetched !!!")
    
    #Fetching timeline & Responses by month and year.
    print("\nUpdate : Fetching Timeline & Response Pages...\n")
    TimelineFileNames,ResponseFileNames=wikiDataInTimeRange()
    print("\nUpdate : Fetching Timeline & Response Pages Fetched !!!")
    
    #Fetching timeline by month and year for paticular date.
    print("\nUpdate : Retrieving Timeline Data...\n")
    TimelineContent=fetchTimelineData(TimelineFileNames)
    print("\nUpdate : Timeline Data Retrieved !!!")

    #Fetching Responses by month and year for paticular date.
    print("\nUpdate : Retrieving Response Data...\n")
    ResponseContent=fetchResponseData(ResponseFileNames)
    print("\nUpdate : Response Data Retrieved !!!")

    #Fetching Country covid Data.
    print("\nUpdate : Retrieving Country Covid Data...")
    countryCovidData=fetchCountryCovidData()
    print("\nUpdate : Country Covid Data Retrieved !!!")

    print("\nUpdate : Database Creation Done !!!")
    #Taking user input.
    userInputFn(TimelineContent,ResponseContent,countryCovidData)


if __name__ == "__main__":
	main()