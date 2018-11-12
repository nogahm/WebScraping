#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import the library used to query a website
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup


# specify the url
wiki = "https://en.wikipedia.org/wiki/Gal_Gadot"
# Query the website and return the html to the variable 'page'
page = urllib.request.urlopen(wiki)
# import the Beautiful soup functions to parse the data returned from the website
# Parse the html in the 'page' variable, and store it in Beautiful Soup format

soup = BeautifulSoup(page, "html.parser")

# In[2]:


# find films table
right_table = soup.find('table', class_='wikitable sortable')

# Question 1:

# In[3]:


import re

# Generate lists
A = []
B = []
C = []
D = []
moviesLinks = []  # for Question2
year = ''
role = ''
yearIndex = -1
roleIndex = -1

for row in right_table.findAll("tr"):
    cells = row.findAll('td')
    # all cells
    if len(cells) == 5:
        A.append(cells[0].find(text=True))
        B.append(cells[1].find(text=True))
        C.append(cells[2].find(text=True))
        D.append(cells[3].find(text=True))
        # check rowspan
        if cells[0].has_attr('rowspan'):
            year = cells[0].find(text=True)
            yearIndex = int(cells[0].attrs['rowspan']) - 1
        if cells[2].has_attr('rowspan'):
            role = cells[2].find(text=True)
            roleIndex = int(cells[2].attrs['rowspan']) - 1
        # save link to movie page
        a = cells[1].find_all('a')
        if len(a) > 0:
            moviesLinks.append(a[0].get('href'))
    # year or role not exist
    if len(cells) == 4:
        # no year
        if yearIndex > 0:
            A.append(year)
            yearIndex = yearIndex - 1
            B.append(cells[0].find(text=True))
            C.append(cells[1].find(text=True))
            D.append(cells[2].find(text=True))
            # check role rowspan
            if cells[1].has_attr('rowspan'):
                role = cells[1].find(text=True)
                roleIndex = int(cells[1].attrs['rowspan']) - 1
            # save link to movie page
            a = cells[0].find_all('a')
            if len(a) > 0:
                moviesLinks.append(a[0].get('href'))
        if roleIndex > 0:
            A.append(cells[0].find(text=True))
            B.append(cells[1].find(text=True))
            C.append(role)
            D.append(cells[2].find(text=True))
            roleIndex = roleIndex - 1
            # check year rowspan
            if cells[0].has_attr('rowspan'):
                year = cells[0].find(text=True)
                yearIndex = int(cells[0].attrs['rowspan']) - 1
            # save link to movie page
            a = cells[1].find_all('a')
            if len(a) > 0:
                moviesLinks.append(a[0].get('href'))
    # year and role not in row
    if len(cells) == 3:
        A.append(year)
        B.append(cells[0].find(text=True))
        C.append(role)
        D.append(cells[1].find(text=True))
        yearIndex = yearIndex - 1
        roleIndex = roleIndex - 1
        # save link to movie page
        a = cells[0].find_all('a')
        if len(a) > 0:
            moviesLinks.append(a[0].get('href'))

# In[5]:


# import pandas and convert list to data frame

df = pd.DataFrame()
df['Year'] = A
df['Title'] = B
df['Role'] = C
df['Director(s)'] = D
df

# Question 2:

# In[6]:


# find all cast
castLinks = []
# collect all cast members links
for link in moviesLinks:
    moviePage = urllib.request.urlopen("https://en.wikipedia.org" + link)
    movieSoup = BeautifulSoup(moviePage, "lxml")
    if (movieSoup.find(id="Cast")):
        cast = (movieSoup.find(id="Cast").parent).find_next('ul')
    if (movieSoup.find(id="Voice_cast")):
        cast = (movieSoup.find(id="Voice_cast").parent).find_next('ul')
    lines = cast.find_all('li')
    # cast members in different ul
    uls = False
    while (len(lines) == 1) and (cast.find_next('ul')):
        uls = True
        for line in lines:
            a = line.find_all('a')
            if len(a) > 0:
                castLinks.append(a[0].get('href'))
        cast = cast.find_next('ul')
        lines = cast.find_all('li')
    # regular
    if uls == False:
        for line in lines:
            a = line.find_all('a')
            if len(a) > 0:
                castLinks.append(a[0].get('href'))
# print(castLinks)
print(len(castLinks))

# Question 3:

# In[49]:


# find dups cast members and save count
A = []
B = []
C = []
D = []
# for question3:
castCount = dict()  # for Question 3 - number of films with gal gadot
for castMember in castLinks:
    if castMember != "/wiki/Gal_Gadot":
        try:
            actorPage = urllib.request.urlopen("https://en.wikipedia.org" + castMember)
            co_actor_soup = BeautifulSoup(actorPage, "lxml")
        except:  # page not open
            continue
        co_actor_vcard = co_actor_soup.find("table")
        try:
            co_actor_vcard = co_actor_soup.find("table", class_="infobox biography vcard")
            # name = co_actor_vcard.find(class_="fn")
        except:
            print()
        try:
            if (co_actor_vcard == None):
                co_actor_vcard = co_actor_soup.find("table", class_="infobox vcard plainlist")
            # name = co_actor_vcard.find(class_="fn")
        except:
            print()
        try:
            if (co_actor_vcard == None):
                co_actor_vcard = co_actor_soup.find("table", class_="infobox vcard")
            # name = co_actor_vcard.find(class_="fn")
        except:
            print("ex:  " + castMember)
            continue
        # find name
        if (co_actor_vcard != None):
            try:
                name = co_actor_vcard.find(class_="fn")
                if (name == None):
                    name = co_actor_vcard.find('th')

            except:
                name = co_actor_vcard.find('th')
        else:
            continue
        # dupes - add count
        try:
            nameT = name.text
        except:
            continue
        if name.text in castCount.keys():
            castCount[name.text] = castCount[name.text] + 1
        # first time - save info
        else:
            castCount[name.text] = 1
            #use more pormats - eugine brave rock
            birthday = co_actor_vcard.find(class_="bday")
            birthplace = co_actor_vcard.find(class_="birthplace")
            if birthplace == None and birthday != None:
                birthplaceText = (birthday.parent.parent).get_text()
                if len((birthday.parent.parent).find_all('a'))==0:
                    arr=None
                else:
                    arr = birthplaceText.split(",")
            elif birthplace != None :
                arr = birthplace.text.split(",")
            else:
                arr=None
                # if(len(arr)>0):
                #     birthplace=arr[len(arr)-1]
            try:
                A.append(name.text)
            except:
                A.append("NULL")
            try:
                B.append(birthday.text[:4])
            except:
                B.append("NULL")
            try:
                #ger country
                length = len(arr)
                country=arr[length - 1]
                r=re.compile('[^a-zA-Z. ]')
                country=r.sub('',country)
                C.append(country)
            except:
                C.append("NULL")
            awards = 0
            # actorName.append(name.text)
            # filmsCount.appenf(castCount[actorLink])

            #get wins from tables
            awards = len(co_actor_soup.find_all(class_="yes table-yes2"))
            #get wins also from links
            awardsLink=co_actor_soup.find(href=re.compile("List_of_awards"))
            #if link exist
            if awardsLink is not None:
                #find the correct link
                awardsLink = awardsLink.get('href')
                #open awards page and count the wins
                awardsPage = urllib.request.urlopen("https://en.wikipedia.org" + awardsLink)
                awards_soup = BeautifulSoup(awardsPage, "lxml")
                temp1=len(awards_soup.find_all(text='Won'))
                temp2 = len(awards_soup.find_all(text='Won\n'))
                awards =awards+ temp1+temp2
            D.append(awards)




# In[ ]:


# import pandas as pd
df2 = pd.DataFrame()
df2['Name'] = A
df2['Birth Year'] = B
df2['Birth Country'] = C
df2['D']=D
df2=df2.sort_values('Name')
df2

writer = pd.ExcelWriter('output.xlsx')
df2.to_excel(writer,'Sheet2')
writer.save()

# Question 3:

# In[57]:


# create data frame and show for each co-actor number of films with gal gadot
coActorsDF = pd.DataFrame()
coActorsDF['Name'] = castCount.keys()
coActorsDF['# films with Gal Gadot'] = castCount.values()
coActorsDF

# In[71]:


import matplotlib.pyplot as plt

# create histogram
# fig=plt.figure(figsize=(160,5))
fig = coActorsDF.hist(column="# films with Gal Gadot")
plt.xlabel("Number Of Films", fontsize=15)
plt.ylabel("Actors Frequency", fontsize=15)

# In[ ]:
