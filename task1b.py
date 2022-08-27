'''
    Problem Statement : Web Crawling and Extracting Information [ Task 2 ]
    Author : Adarsh G Krishnan [21CS60R55]
    Run command : python task2.py
    operating system : Linux (UBUNTU 20.04)
    Time stamp : 13/02/2022
'''
#!/usr/bin/python3
from numpy import double
import ply.lex as lex
import ply.yacc as yacc
import warnings
warnings.filterwarnings("ignore")

def t_error(t):
    t.lexer.skip(1)

def p_error(t):
    pass

curr_name=""
name=""
date=[]
countrySpecialDetails={}
active=[]
rec=[]
death=[]
newc=[]

#Function to fetch Yesterday's data.
def fetchYesterdayData():

    #Fetching yesterday's data.
    f1=open("Main.html","r")
    f2=open("Yesterday.html","w")
    ctr=0
    for line in f1:
        if line.strip() == """<div class="tab-pane " id="nav-yesterday" role="tabpanel" aria-labelledby="nav-yesterday-tab">""":
            ctr = 1
            continue
        if line.strip() == """<div class="tab-pane " id="nav-yesterday2" role="tabpanel" aria-labelledby="nav-yesterday2-tab">""":
            ctr = 0
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

#Function to fetch World data.
def fetchingWorldData():

    import ply.lex as lex
    import ply.yacc as yaac

    worldDetails=[]
    f1=open("Yesterday.html","r")
    f2=open("World.html","w")
    ctr=0
    for line in f1:
        if line.strip() == """<td style="text-align:left;">World</td>""":
            ctr = 1
            continue
        if line.strip() == """<td style="display:none" data-continent="all">All</td>""":
            ctr = 0
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open('World.html','r')
    content=file.read()
    file.close()


    #Defining Grammer
    t_ignore = " \t "


    def t_L1tag(t):
        r'''<td>'''
        #print(t.value+'*')
        return t
    
    def t_L2tag(t):
        r'''[A-Za-z0-9\, \" \"\/\+ \"\.\.\" \- \# \+ ]+'''
        return t
    
    def p_Wtag1(p):
        '''Wtag1 : L1tag L2tag'''
        p[0]=p[2]
        p[0]=str(p[0]).replace("+","")
        p[0]=str(p[0]).replace("/td","N/A")
        worldDetails.append(p[0])
    
    
    tokens=['L1tag','L2tag']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    #print(worldDetails)

    worldData={}
    worldData['Total Cases']=worldDetails[0]
    worldData['Active Cases']=worldDetails[6]
    worldData['Total Deaths']=worldDetails[2]
    worldData['Total Recovered']=worldDetails[4]
    worldData['Total Tests']='N/A'
    worldData['Death per Million']=worldDetails[9]
    worldData['Tests per Million']='N/A'
    worldData['New Cases']=worldDetails[1]
    worldData['New Deaths']=worldDetails[3]
    worldData['New Recovered']=worldDetails[5]

    return worldData

#Function to fetch Continent data.
def fetchingContinentData(worldData):

    import ply.lex as lex
    import ply.yacc as yaac

    continentDetails={}
    
    continents=['Asia','North America','South America','Europe','Africa','Australia/Oceania']
    f1=open("Yesterday.html","r")
    f2=open("Continent.html","w")

    ctr=0
    for line in f1:
        if line.strip() == """<tbody>""":
            ctr = 1
            continue
        if line.strip() == """<tr class="total_row_world">""":
            ctr = 0
            continue
        if(ctr==1):
            f2.write(line)

    f1.close()
    f2.close()

    file=open('Continent.html','r')
    content=file.read()
    file.close()


    def t_LContinent(t):
        r'<tr\sclass\=\"total_row_world\srow_continent"\sdata-continent='
        return t
    
    def t_NContinent(t):
        r'''[A-Za-z0-9\, \" \"\/\+ \"\.\.\" \- \# \+ ]+'''
        return t
    
    def t_Ltag1(t):
        r'''<td'''
        #print(t.value+'*')
        return t

    def t_Ltag2(t):
        r'''>[A-Za-z0-9\, \" \"\/\+ \"\.\.\" \- \# \+ ]+'''
        return t

    def p_start(p):
        '''start : Continent
                 | tag1'''
    
    def p_Continent(p):
        '''Continent : LContinent NContinent'''
        p[0]=p[2]
        name=p[0]
        name=str(name).replace(" style","")
        name=str(name).replace("\"","")
        global curr_name
        if name in continents:
            curr_name=name
            continentDetails[name]=[]
    
    def p_tag1(p):
        '''tag1 : Ltag1 Ltag2'''
        p[0]=p[2]
        p[0]=str(p[0]).replace("/td","")
        p[0]=str(p[0]).replace("+","")
        p[0]=str(p[0]).replace(">","")
        #print(p[0]+'*')
        
        #continentDetails[name].append(p[0])
        if curr_name in continents:
            continentDetails[curr_name].append(p[0])
    
    tokens=['LContinent','NContinent','Ltag1','Ltag2']
    #Defining Lexer
    lexer1=lex.lex()
    lexer1.input(content)

    #defining parser.
    parser1 = yacc.yacc()
    parser1.parse(content,lexer=lexer1)


    continentData={}
    for key in continentDetails:
        continentData[key]={}
        continentData[key]['Total Cases']=continentDetails[key][0]
        continentData[key]['Active Cases']=continentDetails[key][6]
        continentData[key]['Total Deaths']=continentDetails[key][2]
        continentData[key]['Total Recovered']=continentDetails[key][4]
        continentData[key]['Total Tests']='N/A'
        continentData[key]['Death per Million']='N/A'
        continentData[key]['Tests per Million']='N/A'
        continentData[key]['New Cases']=continentDetails[key][1]
        continentData[key]['New Deaths']=continentDetails[key][3]
        continentData[key]['New Recovered']=continentDetails[key][5]


    return continentData

#Function to fetch Country data.
def fetchCountryData(worldData):

    import ply.lex as lex
    import ply.yacc as yaac

    countryDetails={}

    countries=['France','UK','Russia','Italy','Germany','Spain','Poland','Netherlands','Ukraine','Belgium','USA','Mexico','Canada','Cuba',\
        'Costa Rica','Panama','India','Turkey','Iran','Indonesia','Philippines','Japan','Israel','Malaysia','Thailand','Vietnam','Iraq','Bangladesh',\
            'Pakistan','Brazil','Argentina','Colombia','Peru','Chile','Bolivia','Uruguay','Paraguay','Venezuela','South Africa','Morocco','Tunisia',\
                'Ethiopia','Libya','Egypt','Kenya','Zambia','Algeria','Botswana','Nigeria','Zimbabwe','Australia','Fiji','Papua New Guinea','New Caledonia','New Zealand']


    file=open('Yesterday.html','r')
    content=file.read()
    file.close()

    def t_LCountry(t):
        r'\<td\sstyle\=\"font\-weight\:\sbold\;\sfont\-size\:15px\;\stext\-align\:left\;\"\>\<a\sclass\=\"mt\_a\"\shref\=\"country/[a-z A-Z-_]*/"\>'
        return t
        
    def t_NCountry(t):
        r'[A-Za-zA-Z ]+'
        return t

    def t_ept(t):
        r'''(<td\sstyle="text-align:right;font-weight:bold;">N/A)|(<td\sstyle="font-weight:\sbold;\stext-align:right">N/A)|(<td\sstyle="font-weight:\sbold;\stext-align:right;">N/A)'''
        return t
    
    def t_nullFind(t):
        r'''(<td\sstyle="text-align:right;font-weight:bold;"><)|(<td\sstyle="font-weight:\sbold;\stext-align:right"><)|(<td\sstyle="font-weight:\sbold;\stext-align:right;"><)|\
            (<td\sstyle="font-weight:\sbold;\stext-align:right;background-color:\#FFEEAA;"><)|(<td\sstyle="font-weight:\sbold;\s\n[\s]+text-align:right;background-color:red;\scolor:white"><)|\
            (<td\sstyle="font-weight:\sbold;\stext-align:right;background-color:\#c8e6c9;\scolor:\#000"><)'''
        return t

    def t_LTotalCases(t):
        r'''<td\sstyle="font-weight:\sbold;\stext-align:right">'''
        return t

    def t_NTotalCases(t):
        r'[0-9,]+'
        return t

    def t_LTotalDeaths(t):
        r'''<td\sstyle="font-weight:\sbold;\stext-align:right;"'''
        #print(t.value)
        return t

    def t_NTotalDeaths(t):
        r'>[0-9,]+'
        return t
    
    def t_LNewCases(t):
        r'''<td\sstyle="font-weight:\sbold;\stext-align:right;background-color:\#FFEEAA;">'''
        #print(t.value)
        return t

    def t_NNewCases(t):
        r'\+[0-9,]+'
        
        return t

    def t_LActiveCases(t):
        r'''<td\sstyle="text-align:right;font-weight:bold;">[0-9,]+'''
        #print(t.value +'*')
        return t

    def t_LNewDeaths(t):
        r'''<td\sstyle="font-weight:\sbold;\s\n[\s]+text-align:right;background-color:red;\scolor:white"'''
        #print(t.value)
        return t

    def t_NNewDeaths(t):
        r'\>\+[0-9,]+'
        return t

    def t_LNewRecovered(t):
        r'''<td\sstyle="font-weight:\sbold;\stext-align:right;background-color:\#c8e6c9;\scolor:\#000">\+[0-9,]+'''
        #print(t.value+'*')
        return t

    def p_start3(p):
        '''start3 : Country 
             | TotalCases
             | TotalDeaths
             | NewCases
             | ActiveCases
             | NewDeaths
             | NewRecovered
             | Emptystr
             | nullFinder'''

    def p_Country(p):
        '''Country : LCountry NCountry'''
        p[0]=p[2]
        global name
        #countryDetails[p[0]]=[]
        name=p[0]
        if name in countries:
            #print(p[0])
            countryDetails[name]=[]

    def p_TotalCases(p):
        '''TotalCases : LTotalCases NTotalCases'''
        p[0]=p[2]
        if name in countries:
            countryDetails[name].append(p[0])
        
    def p_Emptystr(p):
        '''Emptystr : ept'''
        p[0]=p[1]
        if name in countries:
            countryDetails[name].append('N/A')
    
    def p_nullFinder(p):
        '''nullFinder : nullFind'''
        p[0]=p[1]
        if name in countries:
            countryDetails[name].append('N/A')

    def p_TotalDeaths(p):
        '''TotalDeaths : LTotalDeaths NTotalDeaths'''
        p[0]=p[2]
        if name in countries:
            countryDetails[name].append(p[0][1:])
    
    def p_NewCases(p):
        '''NewCases : LNewCases NNewCases'''
        p[0]=p[2]
        if name in countries:
            countryDetails[name].append(p[0][1:])
    
    def p_ActiveCases(p):
        '''ActiveCases : LActiveCases'''
        p[0]=p[1][47:]
        #print(p[0])
        if name in countries:
            countryDetails[name].append(p[0])
    
    def p_NewDeaths(p):
        '''NewDeaths : LNewDeaths NNewDeaths'''
        p[0]=p[2]
        if name in countries:
            countryDetails[name].append(p[0][2:])
    
    def p_NewRecovered(p):
        '''NewRecovered : LNewRecovered'''
        p[0]=p[1][86:]
        if name in countries:
            countryDetails[name].append(p[0])

    tokens=['LCountry','NCountry','ept','LTotalCases','NTotalCases',\
        'LTotalDeaths','NTotalDeaths','LNewCases','NNewCases',\
            'LActiveCases','LNewDeaths','NNewDeaths','LNewRecovered','nullFind']

    #Defining Lexer
    lexer=lex.lex()
    lexer.input(content)

    #defining parser.
    parser = yacc.yacc()
    parser.parse(content,lexer=lexer)

    #print(countryDetails)

    for key,value in countryDetails.items():
        #print(key,len(countryDetails[key]))
        break

    countryData={}
    for key,value in countryDetails.items():
        countryData[key]={}
        countryData[key]['Total Cases']=value[0]
        countryData[key]['Active Cases']=value[6]
        countryData[key]['Total Deaths']=value[2]
        countryData[key]['Total Recovered']=value[4]
        countryData[key]['Total Tests']=value[10]
        countryData[key]['Death per Million']=value[9]
        countryData[key]['Tests per Million']=value[11]
        countryData[key]['New Cases']=value[1]
        countryData[key]['New Deaths']=value[3]
        countryData[key]['New Recovered']=value[5]
        
    #print(countryData)

    return countryData

#Function to fetch special Country data.
def fetchCountrySpecial(worldData,countryData):

    import ply.lex as lex
    import ply.yacc as yaac

   
    for key in countryData.keys():
        
        countrySpecialDetails[key]={}
        countrySpecialDetails[key]['ActiveCases']={}
        countrySpecialDetails[key]['DailyDeath']={}
        countrySpecialDetails[key]['NewRecovered']={}
        countrySpecialDetails[key]['NewCases']={}

        fname=str(key)+'1.html'
        #fname="temp.html"
        #file=open(fname,"r")
        file = open(fname, "r",encoding="utf-8")
        content=file.read()
        file.close()
        # print(content)


        def t_CActases(t):
            r'''[\s]+name:\s\'Currently\sInfected\'\,\n[\s]+color:\s'\#00DDDD\'\,\n[\s]+lineWidth:\s5,\n[\s]+data:\s\['''
            #print(t.value)
            return t
        
        def t_CDailyDeath(t):
            r'''[\s]+name:\s\'Daily\sDeaths\'\,\n[\s]+color:\s'\#999\'\,\n[\s]+lineWidth:\s4,\n[\s]+showCheckbox:\sfalse,\n[\s]+data:\s\['''
            #print(t.value)
            return t
        
        def t_CNewRecovered(t):
            r'''[\s]+name:\s\'Recovery\sRate\'\,\n[\s]+color:\s'\#8ACA2B\'\,\n[\s]+lineWidth:\s5,\n[\s]+data:\s\['''
            #print(t.value)
            return t
        
        def t_CNewCases(t):
            r'''[\s]+name:\s\'Daily\sCases\'\,\n[\s]+color:\s'\#999\'\,\n[\s]+lineWidth:\s4,\n[\s]+showCheckbox:\sfalse,\n[\s]+data:\s\['''
            #print(t.value)
            return t

        def t_Value(t):
            #r"[A-Za-z0-9':.,\-() \"]+"
            r'[null,.0-9,0-9-]+'
            #print(t.value)
            return t
        
        def t_endValue(t):
            r'''\]'''
            return t

        def t_CDATE(t):
            #r'''[\s]+categories:\s\['''
            r'''[\s]+xAxis:\s{\n[\s]+categories:\s\['''
            #print(t.value)
            return t
        
        def t_DValue(t):
            r'''[\",A-Za-z0-9\s\"]+'''
            return t

        def p_start4(p):
            '''start4 : CDate
                      | CActive
                      | CDailydeath
                      | CNewRec
                      | CDailyCases'''
        
        #| CNewRec| CNewCase| CDate
        def p_CDate(p):
            '''CDate : CDATE DValue'''
            p[0]=p[2]
            #print(p[0])
            p[0]=str(p[0]).replace('"',"")
            p[0]=str(p[0]).replace(', ',"/")
            p[0]=str(p[0]).replace(' ',"/")

            lis1=str(p[0]).split(",")
            global date
           
            date=lis1
            
            for item in date:
                countrySpecialDetails[key]['ActiveCases'][item]=0
                countrySpecialDetails[key]['DailyDeath'][item]=0
                countrySpecialDetails[key]['NewRecovered'][item]=0
                countrySpecialDetails[key]['NewCases'][item]=0


        def p_CActive(p):
            '''CActive : CActases Value endValue'''
            p[0]=p[2]
            #print(p[0])
            
            lis2=str(p[0]).split(",")
            #print(lis2)
            global countrySpecialDetails,active
            
            active=lis2

        def p_CDailydeath(p):
            '''CDailydeath : CDailyDeath Value endValue'''
            p[0]=p[2]
            #print(p[0])
            
            lis2=str(p[0]).split(",")
            #print(lis2)
            global countrySpecialDetails,death
            death=lis2
                
        def p_CNewRec(p):
            '''CNewRec : CNewRecovered Value endValue'''
            p[0]=p[2]
            #print(p[0])
            
            lis2=str(p[0]).split(",")
            #print(lis2)
            global countrySpecialDetails,rec
            rec=lis2

        def p_CDailyCases(p):
            '''CDailyCases : CNewCases Value endValue'''
            p[0]=p[2]
            #print(p[0])
            
            lis2=str(p[0]).split(",")
            #print(lis2)
            global countrySpecialDetails,newc
            newc=lis2
              

        tokens=['CActases','CDailyDeath','CNewRecovered','CNewCases','Value','CDATE','DValue','endValue']

        #Defining Lexer
        lexer=lex.lex()
        lexer.input(content)

        #defining parser.
        parser = yacc.yacc()
        parser.parse(content,lexer=lexer)


        for i in range(0,len(date)):
            countrySpecialDetails[key]['ActiveCases'][date[i]]=active[i]
            countrySpecialDetails[key]['DailyDeath'][date[i]]=death[i]
            countrySpecialDetails[key]['NewRecovered'][date[i]]=rec[i]
            countrySpecialDetails[key]['NewCases'][date[i]]=newc[i]
          
    
         
    return countrySpecialDetails

#Utility function to check if a year is leap year or not.
def CheckValid(startDate,EndDate):

    month=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    day1=startDate[4:6]
    month1=startDate[0:3]
    year1=startDate[7:11]

    day2=EndDate[4:6]
    month2=EndDate[0:3]
    year2=EndDate[7:11]  

    if(year1>year2):
        return 0
    else:
        index1=month.index(month1)
        index2=month.index(month2)
        if(index1>index2):
            return 0
        else:
            if(day1>day2):
                return 0
        return 1

#Utility Function to check if the given date is valid or not.
def checker(date,countrySpecialData,currCountry):

    if(len(date)!=11):
        return 0
    day=date[0:2]
    month=date[3:6]
    year=date[7:11]

    Date=month+'/'+day+'/'+year

    if(Date not in countrySpecialData[currCountry]['ActiveCases'].keys()):
        return 0
    else:
        return 1
                          
#Function to find closest country.
def findClosestCountry(countrySpecialData,query,currentValue,start,end,currCountry):

    closestCountry=""
    diff=1000000
    for country in countrySpecialData.keys():
        if(country!=currCountry):
            in1=countrySpecialData[country][query][start]
            in2=countrySpecialData[country][query][end]
            if(in1=='0' or in1== 'null'):
                in1=0.001
            if(in2=='0' or in2== 'null'):
                in2=0.001
            in1=double(in1)
            in2=double(in2)
            output=(in2-in1)*100/in1

            if(currentValue-output)<diff:
                closestCountry=country
                diff=currentValue-output

    return diff,closestCountry
    
#Function to take user input.
def userInputFn(WorldData,continentData,countryData,countrySpecialData):

    availableData=['Total Cases','Active Cases','Total Deaths','Total Recovered','Total Tests',\
        'Death per Million','Tests per Million','New Cases','New Deaths','New Recovered']
    
    specialData=['Change in Active Cases in %','Change in daily death in %',\
        'Change in new recovered in %','Change in new Cases in %',\
            'Closest country similiar to any query between 11-14']

    logFile=open("result.log","w")
    logFile.close()

    while(True):
        print("Details Available for : \n")
        print("[1] World")
        print("[2] Continents")
        print("[3] Countries")
        print("[-1] Back")
        print("\nEnter the option from Above (-1/1/2/3) : ",end=" ")

        while (1):
            try:
                inputUser1=int(input())
            except Exception as exception:
                print("Invalid Input!! Try Again")
                continue
            break

        if inputUser1 not in [-1,1,2,3]:
            print("Invalid input Try Again!!")
            continue

        if inputUser1==-1:
            break
        
        #World Data Request.
        if inputUser1==1:
            while(1):
                print("\nDetails Available : ")
                count=1
                for item in availableData:
                    print('['+str(count)+']'+" "+item)
                    count+=1

                print("[0] Go Back")
                print("[-1] Exit")
                
                print("\nEnter the option from Above (-1/0/1/2/3/4/5/6/7/8/9/10) : ",end=" ")
                

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

                if inputUser2 not in [-1,0,1,2,3,4,5,6,7,8,9,10]:
                    print("\nInvalid input Try Again!!")
                    continue
                else:
                    logResult="<World> <"+str(availableData[inputUser2-1])+"> <"+str(WorldData[availableData[inputUser2-1]])+">\n"
                    logFile=open("result.log","a")
                    logFile.write(logResult)
                    logFile.close()
                    print("\nResponse : "+ WorldData[availableData[inputUser2-1]])

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
                
        #Continent Data Request.
        if inputUser1==2:
            continents=[]
            while(1):
                print("\nAvailable Continents : ")
                count=1
                for key in continentData.keys():
                    print('['+str(count)+']'+" "+key)
                    count+=1
                    continents.append(key)

                print("[0] Go Back")
                print("[-1] Exit")
                print("\nEnter the option from Above (-1/0/1/2/3/4/5/6) : ",end=" ")
                
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
                
                if inputUser2 not in [-1,0,1,2,3,4,5,6]:
                    print("\nInvalid input Try Again!!")
                    continue
                else:
                    print("\nContinent Chosen : "+continents[inputUser2-1])
                    while(1):
                        print("\nDetails Available : ")
                        count=1
                        for item in availableData:
                            print('['+str(count)+']'+" "+item)
                            count+=1

                        print("[0] Go Back")
                        print("[-1] Exit")
                        print("\nEnter the option from Above (-1/0/1/2/3/4/5/6/7/8/9/10) : ",end=" ")


                        while (1):
                            try:
                                inputUser3=int(input())
                            except Exception as exception:
                                print("Invalid Input!! Try Again")
                                continue
                            break

                        if inputUser3==0:
                            break

                        if inputUser3==-1:
                            exit(0)

                        if inputUser3 not in [-1,0,1,2,3,4,5,6,7,8,9,10]:
                            print("\nInvalid input Try Again!!")
                            break
                        else:
                            #print(inputUser1,inputUser2,inputUser3,availableData[inputUser3-1])
                            print("\nResponse : "+ continentData[continents[inputUser2-1]][availableData[inputUser3-1]],end=" ")
                            logResult="<Continent:"+str(continents[inputUser2-1])+"> <"+str(availableData[inputUser3-1])+"> <"+str(continentData[continents[inputUser2-1]][availableData[inputUser3-1]])+">\n"
                            logFile=open("result.log","a")
                            logFile.write(logResult)
                            logFile.close()

                            in1=continentData[continents[inputUser2-1]][availableData[inputUser3-1]];
                            in2=WorldData[availableData[inputUser3-1]];

                            in1=str(in1).replace(",","")
                            in2=str(in2).replace(",","")

                            if(in1=='N/A'):
                                in1=0.001
                            if(in2=='N/A'):
                                in2=0.001
                            
                            in1=double(in1)
                            in2=double(in2)
                            output=(in1)*100/in2
                            if(in1==0.001 or in2==0.001):
                                    print("\nNo enough information Available to compare with world Data")
                            else:
                                print("constitutes "+str(output)+"% of World Data")
                        
                        print("\nContinue? [1] YES [2] NO")
                        while (1):
                            try:
                                inputUser4=int(input())
                            except Exception as exception:
                                print("\nInvalid Input!! Try Again")
                                continue
                            break

                        while(inputUser4 not in [1,2]):
                            print("\nInvalid input!! Enter Again")
                            inputUser4=int(input())
                        if inputUser4==2:
                            exit(0)

        #Country Data Request.
        if inputUser1==3:
            countries=[]
            while(1):
                print("\nAvailable Countries : \n")
                count=1
                for key in countryData.keys():
                    print('['+str(count)+']'+" "+key,end=" ")
                    count+=1
                    countries.append(key)

                print("[0] Go Back",end=" ")
                print("[-1] Exit\n")
                print("\nEnter the option from Above (-1/0 ",end="")

                for i in range(1,56):
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
                
                if inputUser2 not in range(0,56):
                    print("\nInvalid input Try Again!!")
                    continue
                else:
                    diff1,diff2,diff3,diff4=100000,100000,100000,100000
                    closestCountry={}
                    print("\nCountry Chosen : "+countries[inputUser2-1])
                    while(1):
                        print("\nDetails Available : ")
                        count=1
                        for item in availableData:
                            print('['+str(count)+']'+" "+item)
                            count+=1
                        for item in specialData:
                            print('['+str(count)+']'+" "+item)
                            count+=1
                    
                        print("[0] Go Back")
                        print("[-1] Exit")
                        print("\nEnter the option from Above (-1/0/1/2/3/4/5/6/7/8/9/10/11/12/13/14/15) : ",end=" ")
                        
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

                        if inputUser3 not in [-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
                            print("\nInvalid input Try Again!!")
                            break
                        else:
                            if inputUser3<11:
                                print("\nResponse : "+ countryData[countries[inputUser2-1]][availableData[inputUser3-1]])
                                logFile=open("result.log","a")
                                logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(availableData[inputUser3-1])+"> <"+str(countryData[countries[inputUser2-1]][availableData[inputUser3-1]])+">\n"
                                logFile.write(logResult)
                                logFile.close()
                                in1=countryData[countries[inputUser2-1]][availableData[inputUser3-1]];
                                in2=WorldData[availableData[inputUser3-1]];

                                in1=str(in1).replace(",","")
                                in2=str(in2).replace(",","")

                                if(in1=='N/A'):
                                    in1=0.001
                                if(in2=='N/A'):
                                    in2=0.001
                                
                                in1=double(in1)
                                in2=double(in2)
                                if(in1==0.001 or in2==0.001):
                                    print("\nNo enough information Available to compare with world Data")
                                else:
                                    output=(in1)*100/in2
                                    print("constitutes "+str(output)+"% of World Data")

                            elif(inputUser3==15):
                                minDiff=min(diff1,diff2,diff3,diff4)
                                if(minDiff not in closestCountry.keys()):
                                    print("\nNo Data Available : Run queries 11-14 to Load Data")
                                    logFile=open("result.log","a")
                                    logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+"> <"+"N/A>\n"
                                    logFile.write(logResult)
                                    logFile.close()
                                else:
                                    print("\nClosest country based on all queries from 11-14 is : " + closestCountry[minDiff])
                                    logFile=open("result.log","a")
                                    logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+"> <"+str(closestCountry[minDiff])+">\n"
                                    logFile.write(logResult)
                                    logFile.close()

                            else:
                                print("\nEnter the start date in the format <DD/MMM/YYYY> ex:19/Feb/2021")
                                startDate=input()
                                while(checker(startDate,countrySpecialData,countries[inputUser2-1])!=1):
                                    print("\nInvalid Start Date Try Again!!")
                                    startDate=input()
                                
                                sd=startDate
                                day=startDate[0:2]
                                month=startDate[3:6]
                                year=startDate[7:11]
                                startDate=month+'/'+day+'/'+year
                                
                                print("\nEnter the end date in the format <DD/MMM/YYYY> ex:19/Feb/2022")
                                endDate=input()
                                while(checker(endDate,countrySpecialData,countries[inputUser2-1])!=1):
                                    print("\nInvalid End Date Try Again!!")
                                    endDate=input()
                                
                                ed=endDate
                                day=endDate[0:2]
                                month=endDate[3:6]
                                year=endDate[7:11]
                                endDate=month+'/'+day+'/'+year

                                check=CheckValid(startDate,endDate)
                                while(check==0):
                                    print("\nDate Range not valid Try Again!!")
                                    print("\nEnter the start date in the format <DD/MMM/YYYY> ex:19/Feb/2021")
                                    startDate=input()
                                    while(checker(startDate,countrySpecialData,countries[inputUser2-1])!=1):
                                        print("\nInvalid Start Date Try Again!!")
                                        startDate=input()
                                    
                                    sd=startDate
                                    day=startDate[0:2]
                                    month=startDate[3:6]
                                    year=startDate[7:11]
                                    startDate=month+'/'+day+'/'+year
                                    
                                    print("\nEnter the end date in the format <DD/MMM/YYYY> ex:19/Feb/2022")
                                    endDate=input()
                                    while(checker(endDate,countrySpecialData,countries[inputUser2-1])!=1):
                                        print("\nInvalid End Date Try Again!!")
                                        endDate=input()
                                    
                                    ed=endDate
                                    day=endDate[0:2]
                                    month=endDate[3:6]
                                    year=endDate[7:11]
                                    endDate=month+'/'+day+'/'+year

                                    check=CheckValid(startDate,endDate)

                                if(inputUser3==11):
                                    print('\nChange in Active Cases in % for given time period : ',end=" ")
                                    
                                    in1=countrySpecialData[countries[inputUser2-1]]['ActiveCases'][startDate];
                                    in2=countrySpecialData[countries[inputUser2-1]]['ActiveCases'][endDate];
                                    if(in1=='0' or in1== 'null'):
                                        in1=0.001
                                    if(in2=='0' or in2== 'null'):
                                        in2=0.001
                                    
                                    in1=double(in1)
                                    in2=double(in2)
                                    output=(in2-in1)*100/in1
                                    if(output>0):
                                        print(str(output)+"% Increase")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(output)+">\n"
                                    elif(output==0):
                                        print("No Change")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <No Change>\n"
                                    else:
                                        print(str(-1*output)+"% Decrease")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(-1*output)+">\n"
                                    
                                    logFile=open("result.log","a")
                                    logFile.write(logResult)
                                    logFile.close()

                                    diff1,closestCountry[diff1]=findClosestCountry(countrySpecialData,'ActiveCases',output,startDate,endDate,countries[inputUser2-1])
                                    print("\nDo you wish to see the closest country w.r.t Active Cases? [1] YES [2] NO")
                                    while (1):
                                        try:
                                            inputUser4=int(input())
                                        except Exception as exception:
                                            print("\nInvalid Input!! Try Again")
                                            continue
                                        break
                                    while(inputUser4 not in [1,2]):
                                        print("\nInvalid input!! Enter Again")
                                        inputUser4=int(input())
                                    if(inputUser4==1):
                                        print("\nClosest country for the  based on current query is : " + closestCountry[diff1])
                                        logFile=open("result.log","a")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[4])+"> <"+str(closestCountry[diff1])+">\n"
                                        logFile.write(logResult)
                                        logFile.close()
  
                                if(inputUser3==12):
                                    print('\nChange in Daily Deaths in % for given time period : ',end=" ")
                                    
                                    in1=countrySpecialData[countries[inputUser2-1]]['DailyDeath'][startDate];
                                    in2=countrySpecialData[countries[inputUser2-1]]['DailyDeath'][endDate];
                                    if(in1=='0' or in1== 'null'):
                                        in1=0.001
                                    if(in2=='0' or in2== 'null'):
                                        in2=0.001
                                    
                                    in1=double(in1)
                                    in2=double(in2)
                                    output=(in2-in1)*100/in1
                                    if(output>0):
                                        print(str(output)+"% Increase")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(output)+">\n"
                                    elif(output==0):
                                        print("No Change")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <No Change>\n"
                                    else:
                                        print(str(-1*output)+"% Decrease")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(-1*output)+">\n"
                                    
                                    logFile=open("result.log","a")
                                    logFile.write(logResult)
                                    logFile.close()
                                    
                                    diff2,closestCountry[diff2]=findClosestCountry(countrySpecialData,'DailyDeath',output,startDate,endDate,countries[inputUser2-1])
                                    print("\nDo you wish to see the closest country w.r.t Daily Deaths? [1] YES [2] NO")
                                    while (1):
                                        try:
                                            inputUser4=int(input())
                                        except Exception as exception:
                                            print("\nInvalid Input!! Try Again")
                                            continue
                                        break
                                    while(inputUser4 not in [1,2]):
                                        print("\nInvalid input!! Enter Again")
                                        inputUser4=int(input())
                                    if(inputUser4==1):
                                        print("Closest country for the  based on current query is : " + closestCountry[diff2])
                                        logFile=open("result.log","a")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[4])+"> <"+str(closestCountry[diff2])+">\n"
                                        logFile.write(logResult)
                                        logFile.close()
                                
                                if(inputUser3==13):
                                    print('\nChange in New Recovered Cases in % for given time period : ',end=" ")
                                    
                                    in1=countrySpecialData[countries[inputUser2-1]]['NewRecovered'][startDate];
                                    in2=countrySpecialData[countries[inputUser2-1]]['NewRecovered'][endDate];
                                    if(in1=='0' or in1== 'null'):
                                        in1=0.001
                                    if(in2=='0' or in2== 'null'):
                                        in2=0.001
                                    
                                    in1=double(in1)
                                    in2=double(in2)
                                    output=(in2-in1)*100/in1
                                    if(output>0):
                                        print(str(output)+"% Increase")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(output)+">\n"
                                    elif(output==0):
                                        print("No Change")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <No Change>\n"
                                    else:
                                        print(str(-1*output)+"% Decrease")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(-1*output)+">\n"
                                    
                                    logFile=open("result.log","a")
                                    logFile.write(logResult)
                                    logFile.close()

                                    diff3,closestCountry[diff3]=findClosestCountry(countrySpecialData,'NewRecovered',output,startDate,endDate,countries[inputUser2-1])
                                    print("\nDo you wish to see the closest country w.r.t New Recovered Cases? [1] YES [2] NO")
                                    while (1):
                                        try:
                                            inputUser4=int(input())
                                        except Exception as exception:
                                            print("\nInvalid Input!! Try Again")
                                            continue
                                        break
                                    while(inputUser4 not in [1,2]):
                                        print("\nInvalid input!! Enter Again")
                                        inputUser4=int(input())
                                    if(inputUser4==1):
                                        print("Closest country for the  based on current query is : " + closestCountry[diff3])
                                        logFile=open("result.log","a")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[4])+"> <"+str(closestCountry[diff3])+">\n"
                                        logFile.write(logResult)
                                        logFile.close()
                                
                                if(inputUser3==14):
                                    print('\nChange in Daily Cases in % for given time period : ',end=" ")
                                    
                                    in1=countrySpecialData[countries[inputUser2-1]]['NewCases'][startDate];
                                    in2=countrySpecialData[countries[inputUser2-1]]['NewCases'][endDate];
                                    if(in1=='0' or in1== 'null'):
                                        in1=0.001
                                    if(in2=='0' or in2== 'null'):
                                        in2=0.001
                                    
                                    in1=double(in1)
                                    in2=double(in2)
                                    output=(in2-in1)*100/in1
                                    if(output>0):
                                        print(str(output)+"% Increase")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(output)+">\n"
                                    elif(output==0):
                                        print("No Change")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <No Change>\n"
                                    else:
                                        print(str(-1*output)+"% Decrease")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[inputUser3-11])+" from "+str(sd)+" to "+str(ed)+"> <"+str(-1*output)+">\n"
                                    
                                    logFile=open("result.log","a")
                                    logFile.write(logResult)
                                    logFile.close()

                                    diff4,closestCountry[diff4]=findClosestCountry(countrySpecialData,'NewCases',output,startDate,endDate,countries[inputUser2-1])
                                    print("\nDo you wish to see the closest country w.r.t New Cases? [1] YES [2] NO")
                                    while (1):
                                        try:
                                            inputUser4=int(input())
                                        except Exception as exception:
                                            print("\nInvalid Input!! Try Again")
                                            continue
                                        break
                                    while(inputUser4 not in [1,2]):
                                        print("\nInvalid input!! Enter Again")
                                        inputUser4=int(input())
                                    if(inputUser4==1):
                                        print("\nClosest country for the  based on current query is : " + closestCountry[diff4])
                                        logFile=open("result.log","a")
                                        logResult="<Country:"+str(countries[inputUser2-1])+"> <"+str(specialData[4])+"> <"+str(closestCountry[diff4])+">\n"
                                        logFile.write(logResult)
                                        logFile.close()

                        print("\nContinue? [1] YES [2] NO")
                        while (1):
                            try:
                                inputUser4=int(input())
                            except Exception as exception:
                                print("\nInvalid Input!! Try Again")
                                continue
                            break

                        while(inputUser4 not in [1,2]):
                            print("\nInvalid input!! Enter Again")
                            inputUser4=int(input())
                        if inputUser4==2:
                            exit(0)        

#Driver Function
def main():
    
    #Getting Yesterday's data from Main.html
    fetchYesterdayData()
    print("\nUpdate : Fetching Latest Data from Database . . .\n")

    #Fetching World data from Yesterday.html
    WorldData=fetchingWorldData()

    #Fetching Continent data from Yesterday.html
    ContinentData=fetchingContinentData(WorldData)

    #Fetching Country data from Yesterday.html
    countryData=fetchCountryData(WorldData)

    #Fetching Special data Country data from country.html file.
    countrySpecialData=fetchCountrySpecial(WorldData,countryData)

    print("\nUpdate : Operation successful !!! \n")

    #Taking user input.
    userInputFn(WorldData,ContinentData,countryData,countrySpecialData)


if __name__ == "__main__":
	main()
