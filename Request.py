# supress warnings
import warnings
warnings.filterwarnings('ignore') # don't output warnings

# import packages
import numpy as np
import urllib3
from bs4 import BeautifulSoup
import os


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Папка создана: {path}")
    else:
        print(f"Папка уже существует: {path}")


# reload imports
# %load_ext autoreload
# %autoreload 2
stn = '27730'


create_folder('C:\\temp\\{}'.format(stn)) # for text files
m = ['10']
h = ['00', '12']
year = ['2024']
for month in m:
    if month == '10':
        t = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31])

    for day in t:
        if day < 10:
            day = '0%s' %day

        for hour in h:


            # 1)
            # Wyoming URL to download Sounding from
            url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year[0]+'&MONTH='+month+'&FROM='+str(day)+hour+'&TO='+str(day)+hour+'&STNM='+stn


            #2)
            # Remove the html tags
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            soup = BeautifulSoup(response.data.decode('utf-8'),'lxml')
            data_text = soup.get_text()

            # 3)
            # Split the content by new line.
            spltted = data_text.split('Station information and sounding indices')[0]
            splitted = spltted.split("\n",data_text.count("\n"))


            # 4)
            # Write this splitted text to a .txt document
            Sounding_filename = 'C:\\temp\\{}\{}{}{}_{}.txt'.format(stn,year,month,day,hour)
            f = open(Sounding_filename,'w')
            for line in splitted[4:]:
                f.write(line+'\n')
            f.close()

            print('file written: {}'.format(Sounding_filename))
