# -*- coding: utf-8 -*-
"""
Created on Tue Jun 07 12:50:27 2016

@author: MDian
"""

from PyQt4.QtCore import  Qt
from PyQt4.QtGui import   QApplication,  QMessageBox
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar

import os
import os.path

#chek if scipy is installed
try:
    import scipy as sp
except:
    print "scipy is not installed"
    
try:
    from scipy.signal import savgol_filter
except:
    print "scipy.signal.savgol_filter is not installed"

try:
    from scipy import interpolate
except:
    print "scipy.interpolate is not installed"
#function that I made or modify
from function_data_raster import open_data, write_data
from metriquePheno import metrique_pheno_vito,metrique_pheno_greenbrown,metrique_pheno_param,metrique_pheno_derivative
from clip import clipRaster
from wh_filter import whfilter
from TVDI import TVDI_function
from my_aggregate import block_reduce

       
def test_existe_lien(dlg,lienDonnee, nomRepertoire):
    """    
    verify the existence of a connection and displays a message if the link does not exist.
    
     Parameters:
     ----------
     lienDonnee: check link
     nomRpertoire: the name of the corresponding directory to the specified link
     
     Returns:
     ------
     returns 1 if the link exists 0 otherwise    """
    if not (os.path.exists(str(lienDonnee))) :        
    
    #teste si le lien fournit pour le NDVI et /ou du DOY existe
          QMessageBox.warning(dlg, u'Warning ', nomRepertoire + u" doesn't exist ")
              
          return 0
                
    return 1

def test_existe_data(dlg,lienDonnee, nomRepertoire):
    """
     verifies the existence of data in the specified directory
     parameters:
     ----------
     lienDonnee: check link
     nomRpertoire: the name of the corresponding directory to the specified link
     Returns:
     --------
     list: list of images contained in the directory .tif
     ok: it returns 1 if the link exists 0 otherwise    
    """
    liste=[]
    donnee= os.listdir(str(lienDonnee))
    ok=0
    if len(donnee)<1:
          QMessageBox.warning(dlg, u'Warning', nomRepertoire + u" is empty")
          return liste,ok
          
    
    for element in donnee:
        if element.endswith('.tif'):                       
            liste.append(element);
    
    if len(liste)<1:
          QMessageBox.warning(dlg, u'Warning', nomRepertoire + u" doesn't have  .tif files")
          return liste,ok
    
    ok=1      
    return liste,ok

def test_bande_data(dlg,data,liste, nomRepertoire,checked,imageParAn,iDebut,iFin,):
    """
     verifies that the supplied data type corresponds to what was in the directory
     parameters:
     -----------
         data: data
         list: list data
         dirname: directory name
         checked: to know the data type specified by the user (single band, a picture by year, multi-annual)
         imageParAn: number of images per year
         iDebut: index of the first image from the list
         IFIN: index of the last image
     Returns:
     --------
         lList: the list corresponding to the processing period specified by the user
         Nyear: Duration in year of treatment
         ok: 1 if all goes well, otherwise 0    
    """
    lListe=[]    
    nYear=0
    ok=0
    if checked==0  :   
        try:
            [x,y,z]=data.shape
        except:
            [x,y]=data.shape
            z=0
        if z >1 :
            
              QMessageBox.warning(dlg, u'Warning',  nomRepertoire + "', the files are not monoband ")
              return lListe,nYear,ok
              
        nYear=len(liste)/imageParAn
        lListe=liste[iDebut*imageParAn:(iFin+1)*imageParAn]    
    if checked>0 :                   
        
        try:
            [x,y,z]=data.shape
        except:
            [x,y]=data.shape
            z=0
            
        if z <2 :            
              QMessageBox.warning(dlg, u'Warning ', nomRepertoire + "', The files are monoband")
              return lListe,nYear,ok
        if checked==1:
            if data.shape[2] != imageParAn:
              QMessageBox.warning(dlg, u'Warning ', u"Images/Year is not correct")
              return lListe,nYear,ok
            nYear=len(liste)
            lListe=liste[iDebut:(iFin+1)]
        if checked==2:
            nYear=data.shape[2]/imageParAn
            lListe=liste
    ok=1
    return lListe,nYear,ok

def test_date (dlg,debutSerie,finSerie,debutT,finT,dureeSerie,dureeT,nYear,checked,nomRepertoire="11"):
    """
     verifies that the length of the data entered by the user matches the data in the directory, it also vérife that start dates <end dates
    
     Parameters:
     ----------
         debutSerie: year of the beginning of the series
         finSerie: year-end of the series
         debutT: early treatment
         Fint: end of treatment
         dureeSerie: the series time
         Nyear: number of years of data available in the directory
         checked: type specifier data
         dirname: directory name
     Returns:
     --------
         ok: boolean 1 if all goes well and 0 otherwise        
    
    """
    if debutT<debutSerie:
          QMessageBox.warning(dlg, u'Warning ', u" date of processing start("+str(debutT)+u" < start date of the data "+str(debutSerie))
          return 0
    
    if debutSerie>finSerie:
          QMessageBox.warning(dlg, u'Warning ', u"start date > date de fin de série ")
          return 0
          
    if debutT>finSerie:
          QMessageBox.warning(dlg, u'Warning ', u"date of processing start > end date of the data set ")
          return 0
    if finT<debutT:
          QMessageBox.warning(dlg, u'Warning ', u"date of processing end < date of processing start ")
          return 0
    
    if finT>finSerie:
          QMessageBox.warning(dlg, u'Warning', u"date of processing end > end date of the data set ")
          return 0
    
    
    if dureeT>dureeSerie:
          QMessageBox.warning(dlg, u'Warning', u"Processing duration > the data set duration ")
          return 0
        
    if nYear> dureeSerie:
        if checked<2:
          QMessageBox.warning(dlg, u'Warning ', u"the duration of the data set is less than what is available in the directory "+nomRepertoire+ " ("+str(nYear)+">"+str( dureeSerie)+")")
          return 0
        if checked==2:
          QMessageBox.warning(dlg, u'Warning ', u"the duration of the series is less than the number of bands of the multi-annual Images"+nomRepertoire+ " ("+str(nYear)+">"+str( dureeSerie)+")")
          return 0
    if nYear < dureeSerie:
        if checked<2:
          QMessageBox.warning(dlg, u'Warning ', u"the duration of the series exceeds the data available in the directory "+nomRepertoire+ " ("+str(nYear)+"<"+str( dureeSerie)+")")
          return 0
        if checked==2:
          QMessageBox.warning(dlg, u'Warning ', u"the duration of the series exceeds the number of bands of the multi-annual Images"+nomRepertoire+ " ("+str(nYear)+"<"+str( dureeSerie)+")")
          return 0
    
    return 1

def test_lien_data_date(dlg,lienNdvi,nomRepertoire,imageParAn,checked,iDebut,iFin,debutSerie,finSerie,debutT,finT,dureeSerie,dureeT):
    
    """
    used to test the existence of the links, the presence of data and tests 
    the dates entered and returns a list corresponding to the processing time required.    

    """    
    liste=[]
    lListe=[]
    ok=0
    nYear=0
    if not test_existe_lien(dlg,lienNdvi,nomRepertoire):
        return lListe,nYear,ok
        
    liste,ok_data=test_existe_data(dlg,lienNdvi,nomRepertoire)
    
    if not ok_data:            
        return lListe,nYear,ok
    
    
    imageNDVI=os.path.join(lienNdvi , str(liste[0]))#lien qui permet d'acceder à la 1ere image                    
    [sample,GeoTransform,Projection]=open_data(imageNDVI) #stockage du NDVI dans un tableau
     
        
    lListe,nYear,ok_bande=test_bande_data(dlg,sample,liste, nomRepertoire,checked,imageParAn,iDebut,iFin)
    
    if not ok_bande:
        return lListe,nYear,ok
    ok_date=test_date (dlg,debutSerie,finSerie,debutT,finT,dureeSerie,dureeT,nYear,checked,nomRepertoire)
    
    if not ok_date:
        return lListe,nYear,ok
    ok=1    
    return lListe,nYear,ok

def gestion_temperature(inData,inUnit,inMin,inMax):
    
    """
    allows to add a specific treatment to temperature data.
    if the data are in ° K are converted to C and management of extreme values is éffectuée to reduce noise
    Parameters:
    ----------
         InData: data
         inUnit: unit temperature data (° C or ° K)
         Inmin: the lowest value for the area
         INMAX: temperature value highest in the area
     Returns:
     --------
         Outdata: data converted into ° C and management of extreme values    """
    outData=inData
    if inUnit==0:
        
        outData=(inData)-273.15
    test=sp.array(outData<inMin)
    if test.sum()>0:
        [x,y,z]=sp.where(outData<inMin)
        outData[x,y,z]=inMin
    test=sp.array(outData>inMax)
    if test.sum()>0:
        [x,y,z]=sp.where(outData>inMax)
        outData[x,y,z]=inMax
    
    return outData
        
def concatenation_serie(lienDonnee,lListe,dureeT,imageParAn,checked_multi,iDebut,iFin):
    """
    create a series containing all the images that are in the specified directory    
    """
    imageNDVI=os.path.join(lienDonnee , lListe[0])
    [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
    [nL,nC,i]=NDVI.shape
    nZ=dureeT*imageParAn #23images par années * le nombre d'années
    sortie=sp.zeros((nL,nC,nZ),dtype='float16') #variable qui stocke le  NDVI après interpolation
    
    if checked_multi==1:

        for k in range(dureeT):
            deb=k*imageParAn
            fin=(k+1)*imageParAn
            imageNDVI=os.path.join(lienDonnee , lListe[k])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI)                    
            
            sortie[:,:,deb:fin]=NDVI
    if checked_multi==0:
         for k in range(nZ):
             
            imageNDVI=os.path.join(lienDonnee , lListe[k])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI) 
            sortie[:,:,k]=NDVI[:,:,0]
    if checked_multi==2:
            imageNDVI=os.path.join(lienDonnee , lListe[0])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI) 
            sortie=NDVI[:,:,iDebut*imageParAn:(iFin+1)*imageParAn]
    return sortie
        
    
class ProgressBar:
    """
    This class allows to manage a number of features depending on the progress bar    
    """
    def __init__(self,progress_bar):
        """
        Constructor.
        """
        self.bar=progress_bar
        self.bar.setEnabled(0)
        self.bar.setValue(0) #initilise la valeur de la barre

    def active(self,ok):
        
        """
        allows to activate and deactivate the bar
        Parameters:
        ----------
         ok: is a boolean indicating whether the bar should be enabled or not
        Returns:
        --------
         nothing--
        """
        
        self.bar.setEnabled(ok)
        self.set_value(0)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if ok==0:
            self.set_value(0)
            QApplication.restoreOverrideCursor()
            QApplication.processEvents()
            
        
    def set_value(self,value):
        """
        replace the value of the progress bar by the setting input  
        Parameters:
        ----------
         value: new value of the progression bar
        Returns:
         nothing--
        """
        
        self.bar.setValue(value)
        QApplication.processEvents()
    def progression(self,add):
       """
        Helps move the progress bar by replacing its value by the input value 
        if it is less than 100.
        Parameters:
        ----------
         add: new value of the progress bar
        Returns:
         nothing--
        """
       QApplication.processEvents()
       if (add<100):
           self.set_value(add)

class Pretraitement():
    
    
    """
    this class allows retrieve the information entered on the pretreatment 
    interface then applies the required pretreatment.    
    """
    
    def __init__(self,dlg,iface):
        
        """
        initialise de la classe et récupération des informations
        Parameters:
        ----------
           dlg: correspond à l'interface réaliser sur QT
           iface: permet d'interagir avec l'interface de QGIS pour afficher des messages sur l'évolution du traitement
        Returns:
        --------
         nothing--
        """
        self.interface=dlg
        self.qgisInterface=iface
        try:    
            import scipy as sp
        except:
             self.qgisInterface.messageBar().pushMessage("Error", u"Scipy is not installed", level=QgsMessageBar.CRITICAL)
             self.stop()
             return
        try:    
            from scipy.signal import savgol_filter
        except:
            self.qgisInterface.messageBar().pushMessage("Error", u"Scipy or scipy.signal.savgol_filter not installed", level=QgsMessageBar.CRITICAL)
            self.stop()
            return
        try:    
            from scipy import interpolate
        except:
            self.qgisInterface.messageBar().pushMessage("Error", u"Scipy or scipy.interpolate is not installed", level=QgsMessageBar.CRITICAL)
            self.stop()
            return
        self.on=1
        self.Bar=ProgressBar(dlg.progressBar)
        dlg.cancel.clicked.connect(self.stop)
        self.depart()
        self.lissage=dlg.filtreInterpol.currentIndex() #determine si l'image de sortie sera lissé ou pas et avec quelle filtre          
        if self.lissage==1:
            self.window=dlg.fenetre.value()
            self.order=dlg.order.value()
        if self.lissage==2:
            self.lamb=dlg.lamb.value()
            self.p=dlg.ordre.value()
            
        if dlg.temperature_oui.isChecked():
              self.inUnit=dlg.toC.isChecked()
              self.inMin=dlg.tMin.value()
              self.inMax=dlg.tMax.value()
              
        self.imageParAn=dlg.nbreImageAn.value()
        self.periodeTemporelle=dlg.frequenceJour.value()
        self.debutSerie=dlg.spinBox_debut.value()
        self.finSerie=dlg.spinBox_fin.value()
        
        self.dureeSerie=self.finSerie-self.debutSerie+1
        
        self.debutT=dlg.debutTraitement.value()
        self.finT=dlg.finTraitement.value()
        
        self.dureeT=self.finT-self.debutT+1
        
        self.iDebut=self.debutT-self.debutSerie
        self.iFin=self.finT-self.debutSerie
        
        self.nomPrefixe=dlg.prefixeOut.text()
      
        self.lienSave=dlg.cheminOut.text()     #lien d'enregistrement
      
        self.lienDonnee=dlg.cheminNDVI.text()  # repertoire des données
        self.facteureEchelle=dlg.facteurEchelle.value() #facteur d'échelle
        self.temperatureChecked=dlg.temperature_oui.isChecked()
        if dlg.radioButton_imageParAn.isChecked():
          self.pluriAnnuelle=0
      
        if dlg.radioButton_pluriAnnuelle.isChecked():
          self.pluriAnnuelle=1
          
        self.checked_multi=dlg.type_image.currentIndex()
        try:
            self.lListe,self.nYear,ok=test_lien_data_date(dlg,self.lienDonnee,u"Input 1 directory",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
            self.ok=ok
            if not ok:
                
                self.ok=0
                self.stop()
                return 
    
            ok_lien_save=test_existe_lien(dlg,self.lienSave,u"Save directory") 
            self.ok=ok_lien_save
            if not ok_lien_save:
                self.stop()    
                return   
                
            self.reechantillonage=dlg.spinBox_reechantillonage.value()       
        except:
              self.qgisInterface.messageBar().pushMessage("Error", u"a problem was encountered during the Recovery of data", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
    def stop(self):
        """
        STOP
        """
        QApplication.restoreOverrideCursor()
        self.on=0
        self.interface.pushButton_execution.setEnabled(1)
        QApplication.restoreOverrideCursor()
        self.Bar.active(0)
        QApplication.processEvents()
        
    def depart(self):
        """
        START 
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.on=1
        self.Bar.active(1)
        self.interface.pushButton_execution.setEnabled(0)
        QApplication.processEvents()
            
#%%            
    def decoupage(self) : 
          """            
            Allows to cut and save data         
          """
          
          lienZoneEtudes=self.interface.zoneEmprise.text()
          self.depart()
          ok_lien_zone=test_existe_lien(self.interface,lienZoneEtudes,u"Mask")    
          if not ok_lien_zone:
                QApplication.restoreOverrideCursor()
                self.stop()

                return 
               
          progress=1
          k=0
          imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
          [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
          self.Bar.progression(progress)
#          try:
          nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
          try:
              self.qgisInterface.messageBar().pushMessage("Info", u"Croping ...", level=QgsMessageBar.INFO, duration=3)
              #si on a des images multibandes avec un nombre de bandes= imageParAn
              if self.checked_multi==1:
                    if not self.on:
                          self.stop()
                          return 0
                    [sortie,G,P,ok,message]=clipRaster(NDVI,GeoTransform,Projection,lienZoneEtudes)
                    [nLL,nCC,i]=sortie.shape
                    serie=sp.zeros((nLL,nCC,nZ))
                    for k in range(self.dureeT):
                        progress=progress+ (1./self.dureeT *50)
                        self.Bar.progression(progress)
                        deb=k*self.imageParAn
                        fin=(k+1)*self.imageParAn
                        imageNDVI=os.path.join(self.lienDonnee , self.lListe[k])
                        [NDVI,GeoTransform,Projection]=open_data(imageNDVI)                    
                        try:
                            [sortie,G,P,ok,message]=clipRaster(NDVI,GeoTransform,Projection,lienZoneEtudes)
                        except:
                              self.qgisInterface.messageBar().pushMessage("Error", u"a problem was encountered when cutting data", level=QgsMessageBar.CRITICAL)
                              self.stop()
                              return
                        if not ok:
                              QMessageBox.warning(self.interface, u'a problem was encountered when cutting data ', message)
                              self.stop()
                              return 
                        serie[:,:,deb:fin]=sortie
              #si on a des images monobandes
              if self.checked_multi==0:
                     [sortie,G,P,ok,message]=clipRaster(NDVI,GeoTransform,Projection,lienZoneEtudes)
                     [nLL,nCC,i]=sortie.shape
                     serie=sp.zeros((nLL,nCC,nZ))
                     self.Bar.set_value(progress)
                     for k in range(nZ):
                        if not self.on:
                              self.stop()
                              return 0
                        progress=progress+ (1./nZ*50)
                        self.Bar.progression(progress)
                        imageNDVI=os.path.join(self.lienDonnee , self.lListe[k])
                        [NDVI,GeoTransform,Projection]=open_data(imageNDVI) 
                        try:
                            [sortie,G,P,ok,message]=clipRaster(NDVI,GeoTransform,Projection,lienZoneEtudes)
                        except:
                              self.qgisInterface.messageBar().pushMessage("Error", "a problem was encountered when cutting data", level=QgsMessageBar.CRITICAL)
                              QApplication.restoreOverrideCursor()
                              self.stop()
                              return
                        if not ok:
                              QMessageBox.warning(self.interface, u'a problem was encountered when cutting data ', message)
                              self.stop()
                              return 
                        serie[:,:,k]=sortie[:,:,0]
              #si on a des images multiannuel
              if self.checked_multi==2:
                        if not self.on:
                              self.stop()
                              return 0
                  
                        try:
                            [serie,G,P,ok,message]=clipRaster(NDVI[self.iDebut*self.imageParAn:(self.iFin+1)*self.imageParAn]  ,GeoTransform,Projection,lienZoneEtudes)
                        except:
                              self.qgisInterface.messageBar().pushMessage("Error", "a problem was encountered when cutting data", level=QgsMessageBar.CRITICAL)
                              self.stop()
                              return
                        if not ok:
                              QMessageBox.warning(self.interface, u'a problem was encountered when cutting data ', message)
                              self.stop()
                              return 
                        progress=progress+ 50
                        self.Bar.progression(progress)
              [nL,nC,jj]=serie.shape
              GeoTransform=G
              Projection=P
          except:
              
              self.qgisInterface.messageBar().pushMessage("Error", u"concatenation problem, check  the size of your data", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
          try:
              serie=serie*self.facteureEchelle
              if self.temperatureChecked:
                      serie=gestion_temperature(serie,self.inUnit,self.inMin,self.inMax)
          except:
              self.qgisInterface.messageBar().pushMessage("Error", u"a problem was encountered during the management of temperature data", level=QgsMessageBar.CRITICAL)
          prefixe='noFilter_'
          concat=sp.zeros((nL,nC))
          try:
              if self.reechantillonage>1:
                        for k in range(self.dureeT):
                            progress=(1.0/self.dureeT*10)+progress                            
                            self.Bar.progression(progress)
                            if not self.on:
                                  self.stop()
                                  return 0
                            deb=k*self.imageParAn
                            fin=(k+1)*self.imageParAn
                            
                            image=serie[:,:,deb:fin]
                      
                            a=block_reduce(image[:,:,1:],(1,1,self.reechantillonage),sp.mean)
                            b=sp.dstack((image[:,:,0],a[:,:,:-1]))
                            concat = sp.dstack((concat,b))                  
                            
                        lissageNdvi=concat[:,:,1:]
                        newNdvi=lissageNdvi
                        serie=lissageNdvi
                        self.imageParAn=self.imageParAn/self.reechantillonage
              else:
                  lissageNdvi=serie
                  newNdvi=serie
          except:
              self.qgisInterface.messageBar().pushMessage("Error", u"ua problem was encountered during data resampling", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
          try:
              if self.lissage>0:
                 self.qgisInterface.messageBar().pushMessage("Info", u"Smoothing ...", level=QgsMessageBar.INFO, duration=3)
                 for l in range(nL) :
                     if not self.on:
                          self.stop()
                          return 0
                     
                     progress=(1.0/len(self.lListe)*34)+progress
                     self.Bar.progression(progress)  
                     for c in range(nC):
                       
                         if (self.lissage==1):
                            lissageNdvi[l,c,:]=savgol_filter(newNdvi[l,c,:], self.window, self.order)
                            prefixe='filter_SG_'
                            
                         if(self.lissage==2):
                             
                            lissageNdvi[l,c,:]=whfilter(newNdvi[l,c,:],lamb=self.lamb,p=self.p) #recuperation des valeurs utiles                            
                            prefixe='filter_WS_'
              else: 
                     progress=95
                     
                     self.Bar.set_value(progress)
          except:
              self.qgisInterface.messageBar().pushMessage("Error", "Smoothing problem", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
          message=u"recadrage réalisé avec succès" 
          self.save(lissageNdvi,u"_crop_",prefixe,GeoTransform,Projection,progress,message)
          self.stop()
         
#%%    
    def interpolation(self):
        
        """
        Allow to interpol and save data
        """        
        
        QApplication.processEvents()
        self.depart()
#        try:
        lienDoy=self.interface.cheminDOY.text() 
        liste,nYear,ok=test_lien_data_date(self.interface,lienDoy,u"DOY",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
        self.ok=ok
        if not ok:
            
            QApplication.restoreOverrideCursor()
            self.ok=0
            self.stop()
            return 
            
        
          
        try:
            if self.interface.radioButton_interpDefaut.isChecked():
                self.periodeTemporelle=self.interface.frequenceJour.value()
                a=1
            else:
                 
                a=self.periodeTemporelle/self.interface.njours_interpolation.value()
                r=self.periodeTemporelle%self.interface.njours_interpolation.value()
                if  r>0:
                    QMessageBox.warning(self.interface, u'interpolation ', u"The value chosen for interpolation must be a divisor of the time period of data")
                    self.stop()
                    QApplication.restoreOverrideCursor()
                    return 
                self.periodeTemporelle=self.interface.njours_interpolation.value()
            imageParAn1=self.imageParAn*a
        except:
          self.qgisInterface.messageBar().pushMessage("Error", u" error on the interpolation parameters ", level=QgsMessageBar.CRITICAL)
          self.stop()
          QApplication.restoreOverrideCursor()
          return
        try:
            ndviXY=sp.zeros((self.imageParAn+2),dtype='float16')  #recupère les 23 valeurs de la serie à la position (x,y)
            doyXY=sp.zeros((self.imageParAn+2),dtype='float16')  #recupère les 23 valeurs de la serie à la position (x,y)
            
            doyTheorique=sp.arange(imageParAn1+2)*self.periodeTemporelle+1    # Creation du DOY theorique
            progress=0        
            imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
            [nL,nC,i]=NDVI.shape
            self.qgisInterface.messageBar().pushMessage("Info", u"concatenation...", level=QgsMessageBar.INFO, duration=3)
            pas=(1./(self.dureeT))*50/nL
            
            m=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
            DOY_=concatenation_serie(lienDoy,liste,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
            NDVI_=m*self.facteureEchelle
            nZ=self.dureeT*imageParAn1 #23images par années * le nombre d'années
            newNdvi=sp.zeros((nL,nC,nZ),dtype='float16') #variable qui stocke le  NDVI après interpolation
            self.qgisInterface.messageBar().pushMessage("Info", u"interpolation...", level=QgsMessageBar.INFO, duration=3)
        except:
          self.qgisInterface.messageBar().pushMessage("Error", u"concatenation problem, check the size of your data.", level=QgsMessageBar.CRITICAL)
          self.stop()
          QApplication.restoreOverrideCursor()
          return
        try:
            for k in range(self.dureeT):
                
                     QApplication.processEvents()
                     
                     
                     deb=k*self.imageParAn
                     fin=(k+1)*self.imageParAn
                     
                     deb1=k*imageParAn1
                     fin1=(k+1)*imageParAn1
                     
                     NDVI=NDVI_[:,:,deb:fin]
                     DOY=DOY_[:,:,deb:fin]
                     if self.temperatureChecked:
                         NDVI=gestion_temperature(NDVI,self.inUnit,self.inMin,self.inMax)
                     for l in range(nL) :
                         progress=progress+pas
                         self.Bar.progression(progress)
    
                         if not self.on:
                              self.stop()
                              return 0
                         for c in range(nC):
                             QApplication.processEvents()
    
                            ## réalisation de l'interpolation cyclique
                         
                             doyXY[1:-1]=DOY[l,c,:]+self.periodeTemporelle
                             ndviXY[1:-1]=NDVI[l,c,:]
                             
                             ndviXY[0]=NDVI[l,c,-1]
                             ndviXY[-1]=NDVI[l,c,0]        
                             doyXY[-1]= (imageParAn1+1)*self.periodeTemporelle+1
                             doyXY[0]=1
                            
                             interpolation=interpolate.interp1d(doyXY,ndviXY)#création de la fonction d'interpolation
                             newNDVIXY=interpolation(doyTheorique) #interpolation
                             
                             
                             newNdvi[l,c,deb1:fin1]=newNDVIXY[1:-1] +0.0 #recuperation des valeurs utiles                            
            
            prefixe='noFilter_'
        except:
          self.qgisInterface.messageBar().pushMessage("Error", u"Error on interpolation", level=QgsMessageBar.CRITICAL)
          self.stop()
          QApplication.restoreOverrideCursor()
          return

        try:
            self.imageParAn=a*self.imageParAn
            if self.reechantillonage>1:           
                
                newNdvi,progress=self.agregation_temporelle(newNdvi,progress,10)
                lissageNdvi=newNdvi
            else:
                  lissageNdvi=newNdvi
                  
            if self.lissage>0:
                 self.qgisInterface.messageBar().pushMessage("Info", u"Smoothing...", level=QgsMessageBar.INFO, duration=3)
                 for l in range(nL) :
                     progress=(1.0/len(self.lListe)*34.0)+progress
                     self.Bar.progression(progress)  
                     for c in range(nC):
                       
                         if (self.lissage==1):
                            lissageNdvi[l,c,:]=savgol_filter(newNdvi[l,c,:], self.window, self.order)
                            prefixe='filter_SG_'
                            
                         if(self.lissage==2):
                             
                            lissageNdvi[l,c,:]=whfilter(newNdvi[l,c,:],lamb=self.lamb,p=self.p) #recuperation des valeurs utiles                            
                            prefixe='filter_WS_'
            else: 
                     progress=95
                     
                     self.Bar.progression(progress)
        except:
              self.qgisInterface.messageBar().pushMessage("Error", u"resampling or smoothing problem", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
        message=u"Interpolation successfully accomplished"  
        try:
            self.qgisInterface.messageBar().pushMessage("Info", u"Saving...", level=QgsMessageBar.INFO, duration=3)
            self.save(lissageNdvi,"_interpolation_",prefixe,GeoTransform,Projection,progress,message)
            self.stop()
            QApplication.restoreOverrideCursor()
        except:
              self.qgisInterface.messageBar().pushMessage("Error", u"Error of saving", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
        
    def save(self,inData,typeTraitement,prefixe,GeoTransform,Projection,progress,message):
        
        """
        Save the processed data        
        Parameters:
        -----------
            inData: data to save
            typeTraitement: string, name of the type of pretreatement
            prefixe: sttring, type of the filter (nofilter,filter_WS_, ..)
            GeoTransform: data geotransform
            Projection: data projection
            progress: value of the progress bar
            message : message to show at the end of the save      
        Returns:
        --------
            nothing ---
            
        """
        lissageNdvi=inData
        self.qgisInterface.messageBar().pushMessage("Info", u"saving...", level=QgsMessageBar.INFO, duration=3)
        if  self.interface.resolution_spatiale.value()>1:
            
            inNdvi=lissageNdvi
            QApplication.processEvents()
            
            a=self.interface.resolution_spatiale.value() 
            G=list(GeoTransform)
            G[1]=G[1]*a
            G[5]= G[5]*a 
            GeoTransform=tuple(G)
            if self.interface.function_aggregate.currentText().lower()=="mean":
                inNdvi1=block_reduce(inNdvi,(a,a,1),sp.mean)
                
            lissageNdvi=inNdvi1
        
        if not self.pluriAnnuelle: #une image par année
                    annee=self.debutT
                    for k in range(self.dureeT):
                        progress=(1.0/self.dureeT*4)+progress
                        self.Bar.progression(progress)
                        deb=k*self.imageParAn
                        fin=(k+1)*self.imageParAn

                        if not self.on:
                              self.stop()
                              return 0
                        image=lissageNdvi[:,:,deb:fin]
                        output_name=os.path.join(self.lienSave,self.nomPrefixe+typeTraitement+prefixe +str(annee)+'.tif') #lien d'enregistrement de la serie de l'année (année)
            
                        if image.ndim>2:
                            if image.shape[2]==1:
                                out=image[:,:,0]
                                write_data(output_name,out,GeoTransform,Projection)
                            else:
                                write_data(output_name,image,GeoTransform,Projection)
                        annee=annee+1
        else:
                    if lissageNdvi.ndim>2:
                        out=lissageNdvi
                    else:
                        out=lissageNdvi[:,:,0]
                        
                    output_name=os.path.join(self.lienSave,self.nomPrefixe+typeTraitement+prefixe +str(self.debutT)+'-'+str(self.finT)+'.tif') #lien d'enregistrement de la serie de l'année (année)
                    write_data(output_name,out,GeoTransform,Projection)
                              
                                 
            
        self.Bar.set_value(100)
        QMessageBox.information(self.interface, u'Done', message)
                
        self.stop()
        
    def agregation_temporelle(self,newNdvi,progress,pourcent):
        """
        allows to bring the data to no regular time by aggregating data.
        Parameters:
        -----------
             newNdvi: input data to aggregate
             percent: how many percent the progress bar should be between advanced during this treatment
             progress: the state of the progress bar
        
        Returns:
        --------
             out: aggregating data according to the chosen value by the interface
             progress: new value of the progress bar       
        """
        concat=sp.zeros((newNdvi.shape[0],newNdvi.shape[1]))
        
        for k in range(self.dureeT):
            progress=(1.0/(self.dureeT)*pourcent)+progress
            self.Bar.progression(progress)  
            deb=k*self.imageParAn
            fin=(k+1)*self.imageParAn            
            image=newNdvi[:,:,deb:fin]
      
            a=block_reduce(image[:,:,1:],(1,1,self.reechantillonage),sp.mean)
            b=sp.dstack((image[:,:,0],a[:,:,:-1]))
            concat = sp.dstack((concat,b))                  
        out=concat[:,:,1:]
        self.imageParAn=self.imageParAn/self.reechantillonage
        return out , progress       

    def lisser(self):
        
            """
            smoothes the data and  to create multi-time series            
            """
        
            self.depart()
            
            if (self.lissage==0):
                 
                QMessageBox.information(self.interface, u'Lissage', u"if the type of smoothing is not selected, the output you will get not smoothed data saved according to the type of images selected for the output data")
                
            imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
            [nL,nC,i]=NDVI.shape
            progress=5            
            self.Bar.set_value(progress)
            try:
                newNdvi=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"concatenation problem, check your the size of data", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()

                  return
            try:    
                newNdvi=newNdvi*self.facteureEchelle
                if self.temperatureChecked:
                     newNdvi=gestion_temperature(newNdvi,self.inUnit,self.inMin,self.inMax)
                    
                nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
                
                lissageNdvi=sp.empty((nL,nC,nZ),dtype='float16') #variable qui stocke la serie temporelle lissée               
                
                prefixe='noFilter_'
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", "a problem was encountered during the management of temperature", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
            try:
                if self.reechantillonage>1:                
                    
                    newNdvi,progress=self.agregation_temporelle(newNdvi,progress,10)
                    lissageNdvi=newNdvi
                else:
                      lissageNdvi=newNdvi
            except:
                 self.qgisInterface.messageBar().pushMessage("Error", u"resampling problem", level=QgsMessageBar.CRITICAL)
                 self.stop()
                 QApplication.restoreOverrideCursor()
                 return
            try:
                if self.lissage>0:
                     if not self.on:
                          self.stop()
                          return 0
                     for l in range(nL) :
                         progress=(1.0/nL*80.0)+progress
                         self.Bar.progression(progress)  
                         for c in range(nC):
                           
                             if (self.lissage==1):
                                lissageNdvi[l,c,:]=savgol_filter(newNdvi[l,c,:], self.window, self.order)
                                prefixe='filter_SG_'
                                
                             if(self.lissage==2):
                                 
                                lissageNdvi[l,c,:]=whfilter(newNdvi[l,c,:],lamb=self.lamb,p=self.p) #recuperation des valeurs utiles                            
                                prefixe='filter_WS_'
                else: 
                     if not self.on:
                          self.stop()
                          return 0
                     progress=95
                         
                     self.Bar.set_value(progress)
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"smoothing problem", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  return
            try:
                message=u"successful"         
                self.save(lissageNdvi,"Done",prefixe,GeoTransform,Projection,progress,message)
                QApplication.restoreOverrideCursor()
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"saving problem", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  return
class detection_phenologique():
    """
    Allows to retrieve the information in the interface and depending on 
    the metode of phenological metric calculation chosen and thresholds. 
    It provides the beginning of the season, end of season, the max of the 
    season and the associated anomalies    
    """
    
    def __init__(self,dlg,iface):
        
        """
        Constructor.
        """
        self.qgisInterface=iface
        try:    
            import scipy as sp
        except:
             self.qgisInterface.messageBar().pushMessage("Error", u"Scipy is not installed", level=QgsMessageBar.CRITICAL)
             self.stop()
             return
        self.interface=dlg
        dlg.cancel.clicked.connect(self.stop)
        self.on=1
        self.ok=1
        self.Bar=ProgressBar(dlg.progressBar)
        self.depart()
                  
        self.imageParAn=dlg.nbreImageAn_2.value()
        self.periodeTemporelle=dlg.frequenceJour_2.value()
        self.debutSerie=dlg.spinBox_debut_2.value()
        self.finSerie=dlg.spinBox_fin_2.value()
        
        self.dureeSerie=self.finSerie-self.debutSerie+1
        
        self.debutT=dlg.debutTraitement_2.value()
        self.finT=dlg.finTraitement_2.value()
        
        self.dureeT=self.finT-self.debutT+1
        
        self.iDebut=self.debutT-self.debutSerie
        self.iFin=self.finT-self.debutSerie
        
        self.nomPrefixe=dlg.prefixeOut_2.text()
      
        self.lienSave=dlg.cheminOut_metrique.text()     #lien d'enregistrement
      
        self.lienDonnee=dlg.cheminNDVI_metrique.text()  # repertoire des données
        self.facteureEchelle=dlg.facteurEchelle_2.value() #facteur d'échelle
        
          
        self.checked_multi=dlg.type_image_2.currentIndex()
        try:
            self.lListe,self.nYear,ok=test_lien_data_date(dlg,self.lienDonnee,u"NDVI",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
            self.ok=ok
            if not ok:
                
                self.ok=0
                self.stop()
                return 
            ok_lien_save=test_existe_lien(dlg,self.lienSave,u"Saving directory") 
            self.ok=ok_lien_save
            if not ok_lien_save:
                self.stop()
                return
            self.seuil1=dlg.seuilSOS.value()
            self.seuil2=dlg.seuilEOS.value()
            self.radioButton_defaultChecked=dlg.radioButton_default.isChecked() 
            self.methode=dlg.methode.currentIndex()
        except:
              self.qgisInterface.messageBar().pushMessage("Error", u"Links problem", level=QgsMessageBar.CRITICAL)
              self.stop()
              return
        
    def stop(self):
        """
        STOP, activate the validation button and disable progress bar 
        
        """
        QApplication.restoreOverrideCursor()
        self.on=0
        self.interface.pushButton_execution.setEnabled(1)
        QApplication.restoreOverrideCursor()
        self.Bar.active(0)
        QApplication.processEvents()
        
    def depart(self):
        """
        START, disable the validation button and the active progress bar
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.on=1
        
        self.Bar.active(1)
        self.interface.pushButton_execution.setEnabled(0)
        QApplication.processEvents()
        
        
    def estimation(self):
            """
            main function of the class, depending on the method chosen it 
            detects phenological metrics and returns images of metric cumulated 
            and anomalies            
            """
            self.qgisInterface.messageBar().pushMessage("Info", u" detection...", level=QgsMessageBar.INFO, duration=3)
            self.depart()
            imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
            [L,C,i]=NDVI.shape
            NDVI=NDVI*self.facteureEchelle
            progress=1
            
            try:
            #variable qui stocke les 11 metriques pour chaque années 
                metrique=sp.empty((L,C,11),dtype='float16') 
                #tableaux dans les quelles les differentes metriques seront stockées séparemment
                sos=sp.zeros((L,C,self.dureeT),dtype='float16')#start of season
                eos=sp.zeros((L,C,self.dureeT),dtype='float16') #end of season
                los=sp.zeros((L,C,self.dureeT),dtype='float16') #length of seaon
                maxi=sp.zeros((L,C,self.dureeT),dtype='float16')
                
                area=sp.empty((L,C,self.dureeT),dtype='float16') #integration over all season
                areaBef=sp.empty((L,C,self.dureeT),dtype='float16')# integration over growing season
                areaAft=sp.empty((L,C,self.dureeT),dtype='float16') # integration over senescence period
    
                anomalieSos=sp.empty((L,C,self.dureeT),dtype='float16') # anomaly of start of season
                anomalieEos=sp.empty((L,C,self.dureeT),dtype='float16') #anomaly of end of season
                anomalieLos=sp.empty((L,C,self.dureeT),dtype='float16') #anomaly of lenght of season
                
                anomalieArea=sp.empty((L,C,self.dureeT),dtype='float16')# anomaly of all season
                anomalieAreaBef=sp.empty((L,C,self.dureeT),dtype='float16') #anomaly of growing period
                anomalieAreaAft=sp.empty((L,C,self.dureeT),dtype='float16') #anomaly of senescence period
            except:
                QgsMessageLog.logMessage("a problem encountered when declaring variables that need to store differents parameters")
            try:
                annee=self.debutT
                NDVI_=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
                for k in range(self.dureeT):
                    progress=progress+(1.0/self.dureeT*20)
                    deb1=k*self.imageParAn
                    fin1=(k+1)*self.imageParAn            
                    NDVI=NDVI_[:,:,deb1:fin1]
                    for x in range(L):
    
                         QApplication.processEvents()
                         progress=progress+(1./self.dureeT)*70/L
                         self.Bar.progression(progress)
                         for y in range(C):
                             
                             if not self.on:
                                 self.stop()
                                 return 
                                 
                             ndvi=NDVI[x,y,:]*self.facteureEchelle
                             #method of phenology detection
                             if self.methode==1:
                                 methode="_NDVI absolute Threshold_"+str(annee)+"_seuil1_"+str(self.seuil1)+"_seuil2_"+str(self.seuil2)
                                 if self.radioButton_defaultChecked:
                                      out1= metrique_pheno_greenbrown(ndvi,"trs")
                                 else:
                                      out1= metrique_pheno_greenbrown(ndvi,"trs",self.seuil1,self.seuil2)
                             if self.methode==0:
                                 methode="_NDVI Relative Threshold _"+str(annee)+"_seuil1_"+str(self.seuil1)+"_seuil2_"+str(self.seuil2)
                                 if self.radioButton_defaultChecked:
                                     out1= metrique_pheno_vito(ndvi)
                                 else:
                                     out1= metrique_pheno_vito(ndvi,self.seuil1,self.seuil2)
                             if self.methode==2:
                                 methode="_auto_"
                                 out1=metrique_pheno_derivative(ndvi)
                                     
                             outListe=metrique_pheno_param(ndvi,out1[0],out1[1],out1[4])
                             parametre=out1[0:3]+outListe
                             self.Bar.progression(progress)
                             metrique[x,y,:]=sp.array(parametre)
                    
                    sos[:,:,k]=metrique[:,:,0]
                    eos[:,:,k]=metrique[:,:,1]
                    los[:,:,k]=metrique[:,:,2]
                    
                    maxi[:,:,k]=metrique[:,:,6]
                    
                    area[:,:,k]=metrique[:,:,3]
                    areaBef[:,:,k]=metrique[:,:,4]
                    areaAft[:,:,k]=metrique[:,:,5]
                            
                    #Enregistrement des metriques année/année
                    output_name=os.path.join(self.lienSave,self.nomPrefixe+u'_metric'+methode+'.tif')
                    write_data(output_name,metrique,GeoTransform,Projection)
                    annee=annee+1
                name=methode+str(self.debutT)+'-'+str(self.finT)+".tif"
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"Problem on phenology detection", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
            if not self.on:
                 self.stop()
                 return 
            try:
    #=================moyenne et ecart type=============================================================
                self.qgisInterface.messageBar().pushMessage("Info", u"anomalies ...", level=QgsMessageBar.INFO, duration=2)
                moySos=sp.nanmean(sos,2)
                moyEos=sp.nanmean(eos,2)
                moyLos=sp.nanmean(los,2)
                moyArea=sp.nanmean(area,2)
                moyAreaBef=sp.nanmean(areaBef,2)
                moyAreaAft=sp.nanmean(areaAft,2)
                     
                stdSos=sp.nanstd(sos,2)
                stdEos=sp.nanstd(eos,2)
                stdLos=sp.nanstd(los,2)
                stdArea=sp.nanstd(area,2)
                stdAreaBef=sp.nanstd(areaBef,2)
                stdAreaAft=sp.nanstd(areaAft,2)
        #==============================================================================
                pas2=(1./self.dureeT)*4
                for k in range(self.dureeT):
                    QApplication.processEvents()
                    if not self.on:
                         self.stop()
                         return 
                    anomalieSos[:,:,k]=(sos[:,:,k]-moySos)/stdSos
                    anomalieEos[:,:,k]=(eos[:,:,k]-moyEos)/stdEos
                    anomalieLos[:,:,k]=(los[:,:,k]-moyLos)/stdLos
                    
                    anomalieArea[:,:,k]=(area[:,:,k]-moyArea)/stdArea
                    anomalieAreaBef[:,:,k]=(areaBef[:,:,k]-moyAreaBef)/stdAreaBef
                    anomalieAreaAft[:,:,k]=(areaAft[:,:,k]-moyAreaAft)/stdAreaAft
                    progress=progress+pas2
                    self.Bar.progression(progress)
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"error on anomalies calculation", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  return
            try:
                #enregistrement de moyenne EOS
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_MOY_EOS_"+name),moyEos.astype(int),GeoTransform,Projection)
                #enregistrement de moyenne SOS
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_MOY_SOS_"+name),moySos.astype(int),GeoTransform,Projection)
                #enregistrement de TOS
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_TOS_"+name),maxi,GeoTransform,Projection)
                #enregistrement de sos
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_SOS_"+name),sos,GeoTransform,Projection)
                #enregistrement eos
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_EOS_"+name), eos,GeoTransform,Projection)
                #enregistrement los
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_LOS_"+name),los,GeoTransform,Projection)
                #enregistrement area
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_area_"+name),area,GeoTransform,Projection)
                #enregistrement areaAft
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_areaAfter_max_"+name),areaAft,GeoTransform,Projection)
                #enregistrement areaBef
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_areaBefore_max_"+name),areaBef,GeoTransform,Projection)
    
                #enregistrement de anomalie sos
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_SOS_"+name),anomalieSos,GeoTransform,Projection)
                #enregistrement anomalie eos
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_EOS_"+name), anomalieEos,GeoTransform,Projection)
                #enregistrement anomalielos
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_LOS_"+name),anomalieLos,GeoTransform,Projection)
                #enregistrement anomalie area
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_area_"+name),anomalieArea,GeoTransform,Projection)
                #enregistrement anomalie areaAft
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_areaAfter_max_"+name),anomalieAreaBef,GeoTransform,Projection)
                #enregistrement anomalie AreaAFT
                write_data(os.path.join(self.lienSave,self.nomPrefixe+"_anomalie_areaBefore_max_"+name),anomalieAreaAft,GeoTransform,Projection)
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"Saving error", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return

            self.Bar.set_value(100)
            QMessageBox.information(self.interface, u'Done ', u"phenology detection successfully accomplished")
            QApplication.restoreOverrideCursor()
            
            self.stop()

class CalculIndicateur():
    """
    This class has the tools that allow us to calculate 4 indicators that will allow
     us to obtain information on the evolution of vegetation and climate conditions    
    """
    
    def __init__(self,dlg,iface):
        
        """
        Constructor.
        """
        self.interface=dlg
        self.qgisInterface=iface
        #check if scipy is installed
        try:    
            import scipy as sp
        except:
             self.qgisInterface.messageBar().pushMessage("Error", u"Scipy is not installed", level=QgsMessageBar.CRITICAL)
             self.stop()
             return
        dlg.cancel.clicked.connect(self.stop)
        self.on=1
        self.ok=1
        self.Bar=ProgressBar(dlg.progressBar)
        self.depart()
              
        self.imageParAn=dlg.nbreImageAn_5.value()
        self.periodeTemporelle=dlg.frequenceJour_5.value()
        self.debutSerie=dlg.spinBox_debut_5.value()
        self.finSerie=dlg.spinBox_fin_5.value()
        
        self.dureeSerie=self.finSerie-self.debutSerie+1
        
        self.debutT=dlg.debutTraitement_5.value()
        self.finT=dlg.finTraitement_5.value()
        
        self.dureeT=self.finT-self.debutT+1
        
        self.iDebut=self.debutT-self.debutSerie
        self.iFin=self.finT-self.debutSerie
        
        self.nomPrefixe=dlg.prefixeOut_5.text()
      
        self.lienSave=dlg.cheminOut_temperature.text() #where to save     
      
        self.lienDonnee=dlg.cheminTemperature.text()  # data
        self.facteureEchelle=dlg.facteurEchelle_5.value() #scale factor
        
        self.cumuleChecked=dlg.cumule.isChecked()  
        self.checked_multi=dlg.type_image_3.currentIndex()
        try:
            self.lListe,self.nYear,ok=test_lien_data_date(dlg,self.lienDonnee,u"Temperature",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
            self.ok=ok
            if not ok:
                
                self.ok=0
                self.stop()
                QApplication.restoreOverrideCursor() 
                return 
            ok_lien_save=test_existe_lien(dlg,self.lienSave,u"Saving directory") 
            self.ok=ok_lien_save
            if not ok_lien_save:
                self.stop()
                return
        except:
              self.qgisInterface.messageBar().pushMessage("Error", u"links problem", level=QgsMessageBar.CRITICAL)
              self.stop()
              QApplication.restoreOverrideCursor()
              return
        
    def stop(self):
        """
        STOP, activate the validation button and disable progress bar 
        """
        QApplication.restoreOverrideCursor()
        self.on=0
        self.interface.pushButton_execution.setEnabled(1)
        QApplication.restoreOverrideCursor()
        self.Bar.active(0)
        QApplication.processEvents()
        
    def depart(self):
        """
        START, disable the validation button and the active progress bar       
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.on=1
        self.Bar.active(1)
        self.interface.pushButton_execution.setEnabled(0)
        QApplication.processEvents()
        
    def cumule (self,new):
            """
            Allows to preprocess sos, eos et tos           
            """
            try:
                self.qgisInterface.messageBar().pushMessage("Info", u"links of SOS EOS TOS...", level=QgsMessageBar.INFO, duration=2)
                lienSos=self.interface.cheminSOS_temperature.text()
                lienEos=self.interface.cheminEOS_temperature.text()
                lienTos=self.interface.cheminTOS_temperature.text()
                
                sos=0
                eos=0
                tos=0
                #repertoire SOS
                ok=test_existe_lien(self.interface,lienSos,"SOS")    
                if not ok:
                    self.stop()
                    QApplication.restoreOverrideCursor() 
                    return new,sos,eos,tos
                    
                #repertoire EOS
                ok=test_existe_lien(self.interface,lienEos,"EOS")    
                if not ok:
                    self.stop()
                    QApplication.restoreOverrideCursor() 
                    return new,sos,eos,tos
                    
                #repertoire TOS
                ok=test_existe_lien(self.interface,lienTos,"TOS")    
                if not ok:
                    self.stop()
                    QApplication.restoreOverrideCursor() 
                    return new,sos,eos,tos
                
                [sos,G,P]=open_data(lienSos)                 
                [eos,G,P]=open_data(lienEos)                 
                [tos,G,P]=open_data(lienTos) 
                [nL,nC,nZ]=new.shape
                if sos.shape==eos.shape and sos.shape==tos.shape :
                    pass
                else:
                    QMessageBox.warning(self.interface, u'Warning ', u"SOS, TOS and EOS must have the same size")
                    self.stop
                    QApplication.restoreOverrideCursor() 
                    return new,sos,eos,tos

                if  self.interface.aggregate_Yes.isChecked() :
                    QApplication.processEvents()
                    
                    a=self.interface.facteur_aggregate.value()  
                    
                    if self.interface.function_aggregate.currentText().lower()=="mean":
                        sos1=block_reduce(sos,(a,a,1),sp.mean).astype(int)
                        eos1=block_reduce(eos,(a,a,1),sp.mean).astype(int)
                        tos1=block_reduce(tos,(a,a,1),sp.mean).astype(int)
                    if self.interface.function_aggregate.currentText().lower()=="min":
                        sos1=block_reduce(sos,(a,a,1),sp.min)
                        eos1=block_reduce(eos,(a,a,1),sp.min)
                        tos1=block_reduce(tos,(a,a,1),sp.min)
                        
                        
                    if self.interface.function_aggregate.currentText().lower()=="max":
                        sos1=block_reduce(sos,(a,a,1),sp.max)
                        eos1=block_reduce(eos,(a,a,1),sp.max)
                        tos1=block_reduce(tos,(a,a,1),sp.max)
                        
                    if self.interface.function_aggregate.currentText().lower()=="median":
                        sos1=block_reduce(sos,(a,a,1),sp.median).astype(int)
                        eos1=block_reduce(eos,(a,a,1),sp.median).astype(int)
                        tos1=block_reduce(tos,(a,a,1),sp.median).astype(int)
                        
                    [nLL,nCC,nZZ]=tos1.shape
                    
                    if nL > nLL :
                        nLLL=nLL
                    else:
                        nLLL=nL
                    if nC > nCC :
                        nCCC=nCC
                    else:
                        nCCC=nC
                    sos=sos1[:nLLL,:nCCC,:]
                    eos=eos1[:nLLL,:nCCC,:]
                    tos=tos1[:nLLL,:nCCC,:]
                    new1=new[:nLLL,:nCCC,:]
                    new=new1
                else:
                    [nLL,nCC,nZZ]=tos.shape
                    if nL > nLL or nL < nLL or nC > nCC or nC < nCC :
                        QMessageBox.warning(self.interface, u'Warning ', u" data must have the same size ")
                    
                    if nL > nLL :
                        nLLL=nLL
                    else:
                        nLLL=nL
                    if nC > nCC :
                        nCCC=nCC
                    else:
                        nCCC=nC
                    sos=sos[:nLLL,:nCCC,:]
                    eos=eos[:nLLL,:nCCC,:]
                    tos=tos[:nLLL,:nCCC,:]
                    new=new[:nLLL,:nCCC,:]
                        
                
                if sos.ndim>2 and eos.ndim>2 and tos.ndim>2:
                    
                    if sos.shape[2]> self.dureeSerie or sos.shape[2]< self.dureeSerie:
                        QMessageBox.warning(self.interface, u'Warning ', u"the number of band of SOS is different from the duration of the data set ")
                        self.stop()
                        QApplication.restoreOverrideCursor() 
                        return new,sos,eos,tos
                         
                    if eos.shape[2]> self.dureeSerie or eos.shape[2]< self.dureeSerie:
                        QMessageBox.warning(self.dlg, u'Warning', u"the number of band of EOS is different from the duration of the data set ")
                        self.stop()
                        QApplication.restoreOverrideCursor() 
                        return new,sos,eos,tos
                        
                    if tos.shape[2]> self.dureeSerie or tos.shape[2]< self.dureeSerie:
                        QMessageBox.warning(self.dlg, u'Warning ', u"the number of band of TOS is different from the duration of the data set ")
                        self.stop()
                        QApplication.restoreOverrideCursor() 
                        return new,sos,eos,tos
                    
                else:
                    
                    if sos.ndim<3:
                        QMessageBox.warning(self.interface, u'WARNING ', u"the number of band of SOS is different from the duration of the data set ")
                        self.stop()
                        QApplication.restoreOverrideCursor() 
                        return new,sos,eos,tos
                    
                    if eos.ndim<3:
                        QMessageBox.warning(self.interface, u'WARNING ', u"the number of band of EOS is different from the duration of the data set ")
                        self.stop()                    
                        return new,sos,eos,tos
                    
                    if tos.ndim<3:
                        QMessageBox.warning(self.interface, u'WARNING ', u"the number of band of TOS is different from the duration of the data set ")
                        self.stop()  
                        QApplication.restoreOverrideCursor() 
                        return new,sos,eos,tos
                return new,sos,eos,tos
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"error on integration during growing season", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor() 
                  return
    def cwsi(self):
        
            """
            Allows to  calculate  crop water stress index
            """
#            try:
            self.qgisInterface.messageBar().pushMessage("Info", u"CWSI...", level=QgsMessageBar.INFO, duration=3)
            imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
            [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
            [nL,nC,i]=NDVI.shape
            
            nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
            out=sp.zeros((nL,nC,nZ))
            new=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
            sos=0
            eos=0
            tos=0
            if self.cumuleChecked:
                M,sos,eos,tos=self.cumule(new)
                new=M
            progress=1
            prefixe="cwsi_"
            for t in range(nZ):
                 if not self.on:
                     self.stop()
                     return
                 progress=progress+(1.0/nZ*75)
                 self.Bar.progression(progress)
                     
                 mini=sp.nanmin(new[:,:,t])
                 maxi=sp.nanmax(new[:,:,t]) 
                 out[:,:,t]=(new[:,:,t]-mini)/(maxi-mini)
            self.save(out,sos,eos,tos,prefixe,progress,GeoTransform,Projection,)
            QApplication.restoreOverrideCursor()                
#            except:
#                  self.qgisInterface.messageBar().pushMessage("Error", u"a problem was detected when calculating CSWI", level=QgsMessageBar.CRITICAL)
#                  self.stop()
#                  return
    def tci(self):
            """
            Allows to calculate the TCI (temperature conditions index)  
            """
            try:
                self.qgisInterface.messageBar().pushMessage("Info", u"TCI...", level=QgsMessageBar.INFO, duration=3)
                self.depart()
                imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
                [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
                [nL,nC,i]=NDVI.shape
                
                nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
                out=sp.zeros((nL,nC,nZ))
                new=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
                sos=0
                eos=0
                tos=0
                if self.cumuleChecked:
                    new,sos,eos,tos=self.cumule(new)
                progress=1
                prefixe="tci_"
                mini=sp.empty((nL,nC))
                maxi=sp.empty((nL,nC))
                out=sp.zeros((nL,nC,nZ))
                for m in range(self.imageParAn):
                     
                     for x in range(nL):
                         if not self.on:
                             self.stop()
                             return
                         progress=progress+(1.0/nL*75/self.imageParAn)
                         self.Bar.progression(progress)
                         
                         for y in range(nC):
                             mini[x,y]=sp.nanmin(new[x,y,sp.arange(m,nZ,self.imageParAn)])+0.0
                             maxi[x,y]=sp.nanmax(new[x,y,sp.arange(m,nZ,self.imageParAn)]) +0.0
                             
                     for ll in range(m,nZ,self.imageParAn): 
                         if not self.on:
                             self.stop()
                             return
                         out[:,:,ll]=(maxi-new[:,:,ll])/(maxi-mini+0.0000001)
                #saving
                self.save(out,sos,eos,tos,prefixe,progress,GeoTransform,Projection,1)
                QApplication.restoreOverrideCursor()
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"a problem was detected when calculating TCI", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
        
    def vhi(self):
            """
            Allows to calculate  the VHI (vegetation health index)
            """
            try:
                self.depart()
                self.qgisInterface.messageBar().pushMessage("Info", u" VHI...", level=QgsMessageBar.INFO, duration=3)
                imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
                [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
                [nL,nC,i]=NDVI.shape
                sos=0
                eos=0
                tos=0
                nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
                out=sp.zeros((nL,nC,nZ))
                new=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
                if self.cumuleChecked:
                    new,sos,eos,tos=self.cumule(new)
                if not self.on:
                     self.stop()
                     return
                progress=1
                prefixe="vhi_"
                lienNdvi=self.interface.cheminNDVI_temperature.text()
                lListe=[]   
                try:
                    lListe,nYear,ok=test_lien_data_date(self.interface,lienNdvi,"NDVI",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
                except:
                    QgsMessageLog.logMessage(u"problem on NDVI data")
                    
                if not ok:
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
              
                imageNDVI=os.path.join(lienNdvi , lListe[0])
                [temp,GeoTransform1,Projection1]=open_data(imageNDVI)                 
                inNdvi=concatenation_serie(lienNdvi,lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
                
                if  self.interface.aggregate_Yes.isChecked() :
                    QApplication.processEvents()
                    
                    a=self.interface.facteur_aggregate.value()  
                    
                    if self.interface.function_aggregate.currentText().lower()=="mean":
                        inNdvi1=block_reduce(inNdvi,(a,a,1),sp.mean)
                        
                    if self.interface.function_aggregate.currentText().lower()=="min":
                        inNdvi1=block_reduce(inNdvi,(a,a,1),sp.min)
                        
                    if self.interface.function_aggregate.currentText().lower()=="max":
                        inNdvi1=block_reduce(inNdvi,(a,a,1),sp.max)
                        
                    if self.interface.function_aggregate.currentText().lower()=="median":
                        inNdvi1=block_reduce(inNdvi,(a,a,1),sp.median)
                        
                    [nLL,nCC,nZZ]=inNdvi1.shape
                    
                    if nL > nLL :
                        nLLL=nLL
                    else:
                        nLLL=nL
                    if nC > nCC :
                        nCCC=nCC
                    else:
                        nCCC=nC
                    inV=inNdvi1[:nLLL,:nCCC,:]
                    inT=new[:nLLL,:nCCC,:]
                    out=sp.zeros((nLLL,nCCC,nZ))
                    miniT=sp.zeros((nLLL,nCCC))
                    maxiT=sp.zeros((nLLL,nCCC))
                    miniV=sp.zeros((nLLL,nCCC))
                    maxiV=sp.zeros((nLLL,nCCC))
                    outTci=sp.zeros((nLLL,nCCC,nZ),dtype='float16')
                    outVci=sp.zeros((nLLL,nCCC,nZ),dtype='float16')
                else:
                    [nLL,nCC,nZZ]=inNdvi.shape
                    if nL > nLL :
                        nLLL=nLL
                    else:
                        nLLL=nL
                    if nC > nCC :
                        nCCC=nCC
                    else:
                        nCCC=nC
                    
                    inV=inNdvi[:nLLL,:nCCC,:]
                    inT=new[:nLLL,:nCCC,:]
                    out=sp.zeros((nLLL,nCCC,nZ))
                    miniT=sp.zeros((nLLL,nCCC))
                    maxiT=sp.zeros((nLLL,nCCC))
                    miniV=sp.zeros((nLLL,nCCC))
                    maxiV=sp.zeros((nLLL,nCCC))
                    outTci=sp.zeros((nLLL,nCCC,nZ),dtype='float16')
                    outVci=sp.zeros((nLLL,nCCC,nZ),dtype='float16')
                for m in range(self.imageParAn):
                     
                     for x in range(nL):
                         
                         progress=progress+(1.0/nL*75/self.imageParAn)
                         
                         self.Bar.progression(progress)
                         
                         for y in range(nC):
                             miniT[x,y]=sp.nanmin(inT[x,y,sp.arange(m,nZ,self.imageParAn)])+0.0000001
                             maxiT[x,y]=sp.nanmax(inT[x,y,sp.arange(m,nZ,self.imageParAn)]) 
                             
                             miniV[x,y]=sp.nanmin(inV[x,y,sp.arange(m,nZ,self.imageParAn)])+0.0000001
                             maxiV[x,y]=sp.nanmax(inV[x,y,sp.arange(m,nZ,self.imageParAn)]) 
                             
                     for ll in range(m,nZ,self.imageParAn):
                         
                         outVci[:,:,ll]=(inV[:,:,ll] - miniV)/(maxiV-miniV)
                         outTci[:,:,ll]=(maxiT-inT[:,:,ll])/(maxiT-miniT)
                         
                out=0.5*(outVci + outTci)
                self.save(out,sos,eos,tos,prefixe,progress,GeoTransform,Projection,)
                QApplication.restoreOverrideCursor()   
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"a problem was detected when calculating VHI", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
            
    def tvdi (self):
            
            """
            Allows to calculate the TVDI (temperature-vegetation dryness index)
            """
            self.qgisInterface.messageBar().pushMessage("Info", u" TVDI...", level=QgsMessageBar.INFO, duration=3)
            self.depart()
            try:
                    imageNDVI=os.path.join(self.lienDonnee , self.lListe[0])
                    [NDVI,GeoTransform,Projection]=open_data(imageNDVI)
                    [nL,nC,i]=NDVI.shape
                    sos=0
                    eos=0
                    tos=0
                    nZ=self.dureeT*self.imageParAn #23images par années * le nombre d'années
                    out=sp.zeros((nL,nC,nZ))
                    new=concatenation_serie(self.lienDonnee,self.lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)
                    if self.cumuleChecked:
                        new,sos,eos,tos=self.cumule(new)
                    if not self.on:
                         self.stop()
                         QApplication.restoreOverrideCursor()
                         return
                    progress=1
                
                    prefixe="tvdi"
                    lienNdvi=self.interface.cheminNDVI_temperature.text()
                    lListe=[]
                     
                    out=sp.zeros((nL,nC,nZ))
                    try:
                        lListe,nYear,ok=test_lien_data_date(self.interface,lienNdvi,"NDVI",self.imageParAn,self.checked_multi,self.iDebut,self.iFin,self.debutSerie,self.finSerie,self.debutT,self.finT,self.dureeSerie,self.dureeT)    
                    except:
                        QgsMessageLog.logMessage(u"problem on NDVI data")
                        
                    if not ok:
                        self.stop()
                        QApplication.restoreOverrideCursor()
                        return
                    
                    
                    imageNDVI=os.path.join(lienNdvi , lListe[0])
                    [temp,GeoTransform1,Projection1]=open_data(imageNDVI)                 
                    inNdvi=concatenation_serie(lienNdvi,lListe,self.dureeT,self.imageParAn,self.checked_multi,self.iDebut,self.iFin)                
                    if not self.on:
                         self.stop()
                         return
                    if  self.interface.aggregate_Yes.isChecked() :
                        QApplication.processEvents()
                        
                        a=self.interface.facteur_aggregate.value()  
                        
                        if self.interface.function_aggregate.currentText().lower()=="mean":
                            inNdvi1=block_reduce(inNdvi,(a,a,1),sp.mean)
                            
                        if self.interface.function_aggregate.currentText().lower()=="min":
                            inNdvi1=block_reduce(inNdvi,(a,a,1),sp.min)
                            
                        if self.interface.function_aggregate.currentText().lower()=="max":
                            inNdvi1=block_reduce(inNdvi,(a,a,1),sp.max)
                            
                        if self.interface.function_aggregate.currentText().lower()=="median":
                            inNdvi1=block_reduce(inNdvi,(a,a,1),sp.median)
                            
                        [nLL,nCC,nZZ]=inNdvi1.shape
                        
                        if nL > nLL :
                            nLLL=nLL
                        else:
                            nLLL=nL
                        if nC > nCC :
                            nCCC=nCC
                        else:
                            nCCC=nC
                        inV=inNdvi1[:nLLL,:nCCC,:]
                        inT=new[:nLLL,:nCCC,:]
                        out=sp.zeros((nLLL,nCCC,nZ))
                        
                    #if aggregate is not checked    
                    else:
                        
                        [nLL,nCC,nZZ]=inNdvi.shape
                        if nL > nLL :
                            nLLL=nLL
                        else:
                            nLLL=nL
                        if nC > nCC :
                            nCCC=nCC
                        else:
                            nCCC=nC
                            
        					
                        inV=inNdvi[:nLLL,:nCCC,:]
                        inT=new[:nLLL,:nCCC,:]
                        out=sp.zeros((nLLL,nCCC,nZ))
                        
                    for kk in range(nZ):
                        if not self.on:
                             self.stop()
                             return
                        progress=progress+(1.0/nZ*75)
                        self.Bar.progression(progress)
                        out[:,:,kk]=TVDI_function(inV[:,:,kk],inT[:,:,kk])
                    self.save(out,sos,eos,tos,prefixe,progress,GeoTransform,Projection,)
                    QApplication.restoreOverrideCursor()
            except:
                  self.qgisInterface.messageBar().pushMessage("Error", u"a problem was detected when calculating TVDI", level=QgsMessageBar.CRITICAL)
                  self.stop()
                  QApplication.restoreOverrideCursor()
                  return
                                
    def save(self,out,sos,eos,tos,prefixe,progress,GeoTransform,Projection,tci=0):
        """
        saves the calculated indicators with the corresponding anomalies        
        """
        self.qgisInterface.messageBar().pushMessage("Info", u"anomalies...", level=QgsMessageBar.INFO, duration=3)
        [xx,yy,zz]=out.shape
        nZ=self.dureeT*self.imageParAn
        moy=sp.zeros((xx,yy))
        ecartT=sp.zeros((xx,yy))
        anomalie=sp.zeros((xx,yy,zz))
        #to be sure that the eos sos and TOS are Integers
        try:
            eos=eos.astype(int)
            sos=sos.astype(int)
            tos=tos.astype(int)
        except:
            pass
        for m in range(self.imageParAn):
             
             for x in range(xx):
                 for y in range(yy):
                     progress=progress+(1.0/self.dureeT*10/yy*1/xx)
                     if not self.on:
                         self.stop()
                         return
                     self.Bar.progression(progress)
                     moy[x,y]=sp.nanmean(out[x,y,sp.arange(m,nZ,self.imageParAn)])+0.0
                     ecartT[x,y]=sp.nanstd(out[x,y,sp.arange(m,nZ,self.imageParAn)]) +0.0
                     
             for ll in range(m,nZ,self.imageParAn): 
             
                 anomalie[:,:,ll]=(out[:,:,ll]-moy)/(ecartT+0.0000001)
                 
        if self.cumuleChecked:
            #Start of season - End of season
            tSosEos=sp.zeros((xx,yy,self.dureeT))
            #Start of season - Top of season
            tSosTos=sp.zeros((xx,yy,self.dureeT))
            #Top of season - End of season
            tTosEos=sp.zeros((xx,yy,self.dureeT))
            for kk in range(self.dureeT):
                for x in range(xx):
                    for y in range(yy):
                        if not self.on:
                             self.stop()
                             return
                        
                        progress=progress+(1.0/self.dureeT*10/yy*1/xx)
                        self.Bar.progression(progress)
                        
                        deb= kk*self.imageParAn+sos[x,y,kk] 
                        fin= kk *self.imageParAn + tos[x,y,kk]
                        #mean SOS_TOS
                        tSosTos[x,y,kk]=sp.nanmean(out[x,y,deb:fin ])
                        
                        deb= kk*self.imageParAn+tos[x,y,kk] 
                        fin= kk *self.imageParAn + eos[x,y,kk]
                        #mean TOS_EOS
                        tTosEos[x,y,kk]=sp.nanmean(out[x,y,deb:fin ])
                        
                        deb= kk*self.imageParAn+sos[x,y,kk] 
                        fin= kk *self.imageParAn + eos[x,y,kk]
                        #mean SOS_EOS
                        tSosEos[x,y,kk]=sp.nanmean( out[x,y, deb:fin ])
                        
            #Anomaly
            
            anomalieTsos_tos=(tSosTos-sp.nanmean(tSosTos))/sp.nanstd(tSosTos)
            
            anomalieTsos_eos=(tTosEos-sp.nanmean(tTosEos))/sp.nanstd(tTosEos)
            
            anomalieTtos_eos=(tTosEos-sp.nanmean(tTosEos))/sp.nanstd(tTosEos)
            
            #saving mean and anomalies
            output_name3=os.path.join(self.lienSave,self.nomPrefixe+'_moy_tSosTos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            output_name4=os.path.join(self.lienSave,self.nomPrefixe+'_moy_tTosEos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            output_name5=os.path.join(self.lienSave,self.nomPrefixe+'_moy_tSosEos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            output_name6=os.path.join(self.lienSave,self.nomPrefixe+'_anomalie_tSosTos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            output_name7=os.path.join(self.lienSave,self.nomPrefixe+'_anomalie_tTosEos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            output_name8=os.path.join(self.lienSave,self.nomPrefixe+'_anomalie_tSosEos_'+prefixe +str(self.debutT)+'_'+str(self.finT)+'.tif') 
            
            write_data(output_name3,tSosTos,GeoTransform,Projection)
            write_data(output_name4,tTosEos,GeoTransform,Projection)
            write_data(output_name5,tSosEos,GeoTransform,Projection)
            
            write_data(output_name6,anomalieTsos_tos,GeoTransform,Projection)
            write_data(output_name7,anomalieTsos_eos,GeoTransform,Projection)
            write_data(output_name8,anomalieTtos_eos,GeoTransform,Projection)
                    
        annee=self.debutT
        self.qgisInterface.messageBar().pushMessage("Info", u"Saving...", level=QgsMessageBar.INFO, duration=3)
        
        for ll in range(0,self.imageParAn):
            
            output_name2=os.path.join(self.lienSave,self.nomPrefixe+'_anomaly_'+prefixe +str(ll)+'.tif') 
            write_data(output_name2,anomalie[:,:,sp.arange(ll,nZ,self.imageParAn)],GeoTransform,Projection)  
            
        if tci==0:
            for k in range(self.dureeT):
                progress=progress+(1.0/self.dureeT*3)
                self.Bar.progression(progress)
                QApplication.processEvents()
                self.Bar.progression(progress)
                deb=k*self.imageParAn
                fin=(k+1)*self.imageParAn
                if not self.on:
                     self.stop()
                     return
                image=out[:,:,deb:fin]
                output_name=os.path.join(self.lienSave,self.nomPrefixe+prefixe +str(annee)+'.tif') #lien d'enregistrement de la serie de l'année (année)
                write_data(output_name,image,GeoTransform,Projection)
                
                
                annee=annee+1
        else:
            for ll in range(0,self.imageParAn):
                
                output_name=os.path.join(self.lienSave,self.nomPrefixe+prefixe +str(ll)+'.tif') #lien d'enregistrement de la serie de l'année (année)
                write_data(output_name,out[:,:,sp.arange(ll,nZ,self.imageParAn)],GeoTransform,Projection)  
                annee=annee+1
                
    
        self.Bar.set_value(100)
        QMessageBox.information(self.interface, u'Done', u"sucessfull")
        
        self.stop()
        QApplication.restoreOverrideCursor()
