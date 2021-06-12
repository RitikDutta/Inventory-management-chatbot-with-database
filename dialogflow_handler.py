class intent_handler():
    def __init__(self,dialogresjson):
        self.resjson = dialogresjson
    def get_intent(self):
        return self.resjson["queryResult"]["intent"]["displayName"]
    def get_params(self):
        return self.resjson["queryResult"]["parameters"]
    def get_capabilities(self):
        try:
            retjson = []
            for i in self.resjson["originalDetectIntentRequest"]["payload"]["surface"]["capabilities"]:
                retjson.append(i["name"])
            print(retjson)
            return retjson
        except:
            return []
    def get_source(self):
        try:
            return self.resjson["originalDetectIntentRequest"]["source"]
        except:
            return ""

class response_handler():
    def __init__(self):
        self.gcardbtnlist = []
        self.cardbtnlist = []
    def genericResponse(self,text):
        self.ftext = text
    def genericCard(self,title,subtitle):
        self.cardtitle = title
        self.cardsubtitle = subtitle
    def genericCardNewButton(self,btntitle,btnlink):
        self.cardbtnlist.append({"text":btntitle,"postback":btnlink})
    def googleAssistantCard(self,title,subtitle,text):
        self.gcardtitle = title
        self.gcardftext = subtitle
        self.gcardspeech = text
    def googleAssistantCardNewButton(self,btntitle,btnlink):
        self.gcardbtnlist.append({"title":btntitle,"openUrlAction":{"url":btnlink}})
    def googleAssistantNewCarousel(self,text):
        self.carousellist = []
        self.carousellist.append({"simpleResponse":{"textToSpeech":text}})
        self.carousellist.append({"carouselBrowse":{"items":[]}})
    def googleAssistantCarouselNewItem(self,title,url,description,footer,imgurl,imgalt):
        try:
            self.carousellist[1]["carouselBrowse"]["items"].append({"title":title,"openUrlAction": {"url":url},"description":description,"footer":footer,"image":{"url":imgurl,"accessibilityText":imgalt}})
        except:
            raise AttributeError("googleAssistantNewCarousel is not created")
    def formResponse(self):
        ijson = []
        try:
            self.fulfiljson = {"fulfillmentText":self.ftext}
        except:
            raise AttributeError("genericResponse is required")
        try:
            ijson.append({"simpleResponse":{"textToSpeech":self.gcardspeech}})
            if self.gcardbtnlist == []:
                ijson.append({"basicCard":{"title":self.gcardtitle,"formatted_text":self.gcardftext}})
            else:
                ijson.append({"basicCard":{"title":self.gcardtitle,"formatted_text":self.gcardftext,"buttons":self.gcardbtnlist}})
        except:
            pass
        try:
            if self.cardbtnlist != []:
                self.cardjson = {"title":self.cardtitle,"subtitle":self.cardsubtitle,"buttons":self.cardbtnlist}
            else:
                self.cardjson = {"title":self.cardtitle,"subtitle":self.cardsubtitle}
            self.fulfiljson["fulfillmentMessages"] = []
            self.fulfiljson["fulfillmentMessages"].append({"card":self.cardjson})
        except:
            pass
        try:
            for i in self.carousellist:
                ijson.append(i)
        except:
            pass
        if ijson != []:
            try:
                self.fulfiljson["payload"].update({"google":{"expectUserResponse": True,"richResponse":{"items":ijson}}})
            except:
                self.fulfiljson["payload"] = {"google":{"expectUserResponse": True,"richResponse":{"items":ijson}}}
        return self.fulfiljson
