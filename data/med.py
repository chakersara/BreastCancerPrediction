from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import dataBase


class DataMed:

    def __init__(self,url="http://197.13.14.115:90/?ville=Toute%20la%20Tunisie"):
        self.driver=webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.get(url)
        self.cancerologue="Carcinologie médicale"
        self.genycologue="Gynécologie obstétrique"
        self.db=dataBase.DataMed()

    def quit(self):
        self.driver.quit()

    def gouvernorats(self):
        gouvernorat=self.driver.find_elements_by_xpath('//area')
        return list(map(lambda g:g.get_attribute('href'),gouvernorat))

    @property
    def medecins(self):
        listMed=self.driver.find_elements_by_xpath("//select[@id='GuidSpecialite']//option")
        return list(map(lambda doc:doc.text,listMed))


    def choixSpec(self,spec):
        sel=Select(self.driver.find_element_by_xpath("//select[@name='GuidSpecialite']"))
        sel.select_by_visible_text(spec)

    def __gouvName(self):
        return self.driver.find_element_by_xpath("//h1").text.split('(')[-1].replace(')',"")


    def getContent(self):
        pass

    def contentOnePage(self):
        with self.db.connection() as con:
            trs=self.driver.find_elements_by_xpath("//table[@class='dxgvTable_MetropolisBlue']//tr[@class='dxgvDataRow_MetropolisBlue']")
            for tr in trs:
                tds=[elem.text for elem in tr.find_elements_by_xpath('.//*')]
                if self.__gouvName()=="GAB":
                    tds[-1]="Gabès"
                else:
                    tds[-1]=self.__gouvName()
                self.db.insert_data(con,tuple(tds))
                

                
    def numTabs(self,spec=True):
        for gouvHref in self.gouvernorats():
            self.driver.get(gouvHref)
            if spec in self.medecins:
                self.choixSpec(spec)
                self.contentOnePage()
                pages=self.driver.find_elements_by_xpath("//a[@class='dxp-num']")
                for elem in pages:
                    try:
                        elem.click()
                        self.contentOnePage()
                    except Exception as ex:
                        print(ex)
                    

            
           
            
            

        #pprint(driver.find_elements_by_xpath("//table[@class='dxgvTable_MetropolisBlue']//tbody//tr[@class='dxgvDataRow_MetropolisBlue']"))



if __name__=="__main__":
    driver=DataMed("http://197.13.14.115:90/?ville=Toute%20la%20Tunisie")
    driver.numTabs(driver.genycologue)
    driver.quit()
    


#l=driver.find_elements_by_xpath("//a[@class='dxp-num']")
#pprint(driver.find_elements_by_xpath("//table[@class='dxgvTable_MetropolisBlue']//tbody//tr[@class='dxgvDataRow_MetropolisBlue']"))


