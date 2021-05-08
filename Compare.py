import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json # library to handle JSON files
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
import requests # library to handle requests
import numpy as np
import folium # map rendering library
from streamlit_folium import folium_static
from plotly.subplots import make_subplots


class Compare:
    def __init__(self, dataUrl):
        self.url = dataUrl
        self.dataframes = []
        
    def getData(self):
        return pd.read_csv(self.url)
    
    def makeDataframe(self, all_dist, select_year, cate):
        df = self.getData()
        for i in all_dist:
            df4 = df[(df['District.Name'] == i) 
                & (df['Year'] == select_year)]
            # & (df['Neighborhood Name'] == selected_neighborhood)]
            df4 = df4.groupby(df4[cate].rename(cate))["Number"].sum().rename(i)
            self.dataframes.append(df4)
            
    def showFigure(self, titleShow, col, graphBar='bar'):      
        if(len(self.dataframes) > 0):
            newDF = pd.concat(self.dataframes, axis=1)
            df6 = newDF.T
            if graphBar == 'bar':      
                df6.plot.bar(rot=15, title=titleShow)
            elif graphBar == 'barh':
                df6.plot.barh(rot=15, title=titleShow)
            elif graphBar == 'line':
                df6.plot.line(rot=15, title=titleShow)
            elif graphBar == 'hist':
                df6.plot.hist(rot=15, title=titleShow)
            plt.show(block=True)
            col.pyplot()
            
class DesignSideBarText:
    
    def __init__(self):
        super().__init__()
        
    def get_data(self):
        return pd.read_csv('./archive/unemployment.csv')

    def making_textbox(self):
        num_dist = st.sidebar.text_input('Number of district(Max 9)', value="2", max_chars=1)
        df = self.get_data()
        district_names = df['District.Name'].unique()
        all_dist = [] 
        if num_dist == "":
            num_dist = "2"
        for i in range(0, int(num_dist)):
            all_dist.append(st.sidebar.selectbox('District.Name '+str(i), district_names))
        return all_dist
    
    
        