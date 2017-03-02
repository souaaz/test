from urllib.request import urlopen, urlretrieve
import os
from bs4 import BeautifulSoup
import html5lib



def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def prepare_folders(base_folder='data', app_folder='', list_dirs=[]):

    try:       
        dirpath=''

        if base_folder != '':
            dirpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_folder)         
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)            
        else:
            dirpath = os.path.abspath(__file__)        

        if app_folder != '':
            dirpath = os.path.join(dirpath, app_folder)        
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

        if list_dirs and len(list_dirs) > 0:            
            for i in list_dirs:
                newpath = os.path.join(dirpath, i)                            
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
    
    except Exception as e:
        print ( ' Error ', str(e))

    return dirpath
        
#http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
def download_url(url, base_folder='', fname='text.txt'):
   
    try:
        if base_folder !='':
            dirpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_folder) 
            fname =  os.path.join(dirpath, fname)

        urlretrieve(url, fname)

    except Exception as e:
        print ( ' Error ', str(e))


def read_local_file(base_folder='', fname='text.txt'):
    try:
        prefix='file:'

        if base_folder !='':
            dirpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_folder) 
            fname =  os.path.join(dirpath, fname)

        fullname = "".join( [prefix, fname])

        if os.path.isfile(fname):
            r = urlopen(fullname).read()
            s = BeautifulSoup(r, 'html5lib')
            #print(r)
            l = s.find_all('tr')
            if l :
                print(l)

            l = s.find_all('td')
            if l :
                print(l)

    except Exception as e:
        print ( ' Error ', str(e))


'''
    flst = [
     u"http://www.tpsgc-pwgsc.gc.ca/cgi-bin/proactive/cl.pl?lang=eng;SCR=D;Sort=0;PF=CL201617Q3.txt;LN=622",
      u'https://www.google.ca/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8#q=OPEN+GOC+GITHUB&*'
      u'http://www.tpsgc-pwgsc.gc.ca/cgi-bin/proactive/cl.pl?lang=eng;SCR=D;Sort=0;PF=CL201617Q3.txt;LN=622',
    u'http://www.tpsgc-pwgsc.gc.ca/cgi-bin/proactive/cl.pl?lang=eng&SCR=Q&Sort=0',
    ]

'''

fname='html_pw.html'
#url=u'http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus'
url=u'http://www.tpsgc-pwgsc.gc.ca/cgi-bin/proactive/cl.pl?lang=eng&SCR=Q&Sort=0'
mypath=os.path.join('data', 'fin')

def test_url():
    try:     
        prepare_folders(base_folder='data', app_folder='fin',  list_dirs=['files', 'json', 'master_files'])
        download_url(url, base_folder=mypath, fname=fname)
        read_local_file(base_folder=mypath, fname=fname)
    except Exception as e:
       print ( ' Error ', str(e))        




#read_local_filetest_url()
#read_local_file(base_folder=mypath, fname=fname)

if __name__ == '__main__':
    #test_url()
    read_local_file(base_folder=mypath, fname=fname)