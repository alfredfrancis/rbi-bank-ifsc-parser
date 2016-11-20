from mongoengine import *


connect("iky_ifsc_repo")

class BankList(Document):
    bank = StringField(required=True)
    shortCode = StringField(required=True)
    ifsc = StringField(required=True,unique=True,primary_key=True)
    micrCode = StringField()
    branch = StringField(required=True)
    address = StringField()
    contact = StringField()
    city = StringField()
    district = StringField()
    state = StringField()

    meta = {'indexes': [
        {'fields': ['$branch',"$city","shortCode"],
         'default_language': 'english',
         'weights': {'shortcode': 10, 'branch': 5,'city':3}
        }
    ]}


    def save(self, **kwargs):
        self.shortCode = self.ifsc[:4]
        return super(BankList, self).save(**kwargs)

class Settings(Document):
    settingsID = StringField(default="datesettings")
    lastUpdated = DateTimeField(required=True)
    yomLastFetched = DateTimeField(required=True)
