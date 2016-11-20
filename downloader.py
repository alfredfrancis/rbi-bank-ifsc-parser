from requests import get
import cookielib
from bs4 import BeautifulSoup
import re
import glob
import xlrd
from datetime import datetime
from models import BankList,Settings

def runProcess():
    jar = cookielib.CookieJar()
    u = get("https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=2009", cookies=jar)
    pattern = re.compile(r'<th>.*as on\s(.*)</th>')
    dateString = pattern.findall(u.content)[0]
    rbiLastModifiedDate = datetime.strptime(dateString.strip(), '%B %d, %Y')

    if(Settings.objects(settingsID="datesettings").first()):
        settings = Settings.objects.get(settingsID="datesettings")
        if rbiLastModifiedDate > settings.lastUpdated:
            print ("Data modified in rbi website.\nDownloading new data..")
            settings.lastUpdated = rbiLastModifiedDate
            settings.save()

            #Download files from rbi and save to xls/
            downloadFiles()

            #Parse details from xls files and insert into mongodb
            parseFiles()
        else:
            print ("Data is up to date.\n")
    else:
        print ("Running for the first time.")
        settings = Settings()
        settings.lastUpdated = rbiLastModifiedDate
        settings.yomLastFetched = rbiLastModifiedDate
        settings.save()

        downloadFiles()
        parseFiles()

    return True

def downloadFiles():
    jar = cookielib.CookieJar()
    u = get("https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=2009", cookies=jar)
    soup = BeautifulSoup(u.content, "html.parser")

    ulist = soup.findAll("a", href=re.compile('xls$'))
    for xl in ulist:
        dataurl = xl['href']
        if dataurl.startswith("http://"):
            dataurl = 'https://' + dataurl[7:]
        print ("downloading {0}".format(dataurl[7:]))
        xlfd = get(dataurl, cookies=jar)
        writefd = open("xls/{0}.xls".format(xl.string), 'w+')
        writefd.write(xlfd.content)
        writefd.close

def parseFiles():
    path = "xls/*.xls"
    for filename in glob.glob(path):
        print ("Processing {0}".format(filename))
        workbook = xlrd.open_workbook(filename)
        worksheet = workbook.sheet_by_index(0)
        for i in xrange(1,worksheet.nrows):
            try:
                bank = BankList()
                bank.bank = unicode(worksheet.row(i)[0].value)
                bank.ifsc =unicode(worksheet.row(i)[1].value)
                bank.micrCode = unicode(worksheet.row(i)[2].value)
                bank.branch = unicode(worksheet.row(i)[3].value)
                bank.address = unicode(worksheet.row(i)[4].value)
                bank.contact = unicode(worksheet.row(i)[5].value)
                bank.city = unicode(worksheet.row(i)[6].value)
                bank.district = unicode(worksheet.row(i)[7].value)
                bank.state = unicode(worksheet.row(i)[8].value)
                bank.save()
            except:
                print("error")
        print ("Finished {0}".format(filename))
if __name__=="__main__":
    runProcess()