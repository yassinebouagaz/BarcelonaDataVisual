import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json # library to handle JSON files
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
import requests # library to handle requests
import numpy as np
import folium # map rendering library
from streamlit_folium import folium_static
from plotly.subplots import make_subplots
import time
import plotly.express as px

pd.set_option('display.max_columns', None)
class fact_table:

  def __init__(self,df_pop,df_unemp,df_deaths,df_nation,df_age,df_sex,df_births):
    self.df_pop = df_pop
    self.df_unemp = df_unemp
    self.df_nation = df_nation
    self.df_age = df_age
    self.df_sex = df_sex
    self.df_deaths = df_deaths
    self.df_births = df_births
    self.df_immig_facts = pd.DataFrame(columns= ['Fact', 'Category', 'Count'])
    self.df_pop_facts = pd.DataFrame(columns= ['Fact', 'District', 'Count'])
    self.df_merge = pd.DataFrame()

  def __init__(self,df_pop,df_unemp,df_deaths,df_nation,df_age,df_sex,df_births):
    self.df_pop = df_pop
    self.df_unemp = df_unemp
    self.df_nation = df_nation
    self.df_age = df_age
    self.df_sex = df_sex
    self.df_deaths = df_deaths
    self.df_births = df_births
    self.df_immig_facts = pd.DataFrame(columns= ['Fact', 'Category', 'Count'])
    self.df_pop_facts = pd.DataFrame(columns= ['Fact', 'District', 'Count'])
    self.df_merge = pd.DataFrame()

  def merge_df(self):
    df1 = self.df_pop.groupby(['Year','District.Code','District.Name'])['Number'].sum().reset_index()
    df1.columns = ['Year','District.Code','District.Name','Population']
    df2 = self.df_unemp.groupby(['Year','District.Code','District.Name'])['Number'].sum().reset_index()
    df2.columns = ['Year','District.Code','District.Name','Unemployment']
    df3 = self.df_deaths.groupby(['Year','District.Code','District.Name'])['Number'].sum().reset_index()
    df3.columns = ['Year','District.Code','District.Name','Deaths']
    df4 = self.df_nation.groupby(['Year','District.Code','District.Name'])['Number'].sum().reset_index()
    df4.columns = ['Year','District.Code','District.Name','Immigrants']
    df5 = self.df_births.groupby(['Year','District Code','District Name'])['Number'].sum().reset_index()
    df5.columns = ['Year','District.Code','District.Name','Births']
    df6 = df1.merge(
      df2,
      left_on=['Year','District.Code','District.Name'],
      right_on=['Year','District.Code','District.Name'],
      how = 'left'
    )

    df7 = df6.merge(
        df3,
        left_on=['Year','District.Code','District.Name'],
        right_on=['Year','District.Code','District.Name'],
        how = 'left'
    )
    df8 = df7.merge(
        df4,
        left_on=['Year','District.Code','District.Name'],
        right_on=['Year','District.Code','District.Name'],
        how = 'left'
    )
    df9 = df8.merge(
        df5,
        left_on=['Year','District.Code','District.Name'],
        right_on=['Year','District.Code','District.Name'],
        how = 'left'
    )
    df9 = df9.assign(unemp_perc = lambda row: (row['Unemployment'] / row['Population']) * 100)
    df9 = df9.assign(immigration_perc = lambda row: (row['Immigrants'] / row['Population']) * 100)
    df9 = df9.assign(birth_perc = lambda row: (row['Births'] / row['Population']) * 100)
    self.df_merge = df9.assign(mortality_rate = lambda row: (row['Deaths'] / row['Population']) * 100)
    return self.df_merge

  def get_pop_facts(self,year):
    self.merge_df()
    self.df_year = self.df_merge[(self.df_merge['Year']== year)]

#population
    row = self.df_year.loc[self.df_year['Population'].idxmax()]
    data1 = {
      'Fact': ['Highest Population',],
      'District': [row['District.Name']],
      'Count': [row['Population']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['Population'].idxmin()]
    data1 = {
      'Fact': ['Least Population',],
      'District': [row['District.Name']],
      'Count': [row['Population']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)



# #Briths
    row = self.df_year.loc[self.df_year['Births'].idxmax()]
    data1 = {
      'Fact': ['Highest Briths',],
      'District': [row['District.Name']],
      'Count': [row['Births']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)
    row = self.df_year.loc[self.df_year['birth_perc'].idxmax()]
    data1 = {
      'Fact': ['Highest Birth %',],
      'District': [row['District.Name']],
      'Count': [row['birth_perc']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['Births'].idxmin()]
    data1 = {
      'Fact': ['Least Births',],
      'District': [row['District.Name']],
      'Count': [row['Births']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['birth_perc'].idxmin()]
    data1 = {
      'Fact': ['Least Birth %',],
      'District': [row['District.Name']],
      'Count': [row['birth_perc']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)
#Deaths
    row = self.df_year.loc[self.df_year['Deaths'].idxmax()]
    data1 = {
      'Fact': ['Highest Deaths',],
      'District': [row['District.Name']],
      'Count': [row['Deaths']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)
    row = self.df_year.loc[self.df_year['mortality_rate'].idxmax()]
    data1 = {
      'Fact': ['Highest Death %',],
      'District': [row['District.Name']],
      'Count': [row['mortality_rate']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['Deaths'].idxmin()]
    data1 = {
      'Fact': ['Least Deaths',],
      'District': [row['District.Name']],
      'Count': [row['Deaths']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)

    row = self.df_year.loc[self.df_year['mortality_rate'].idxmin()]
    data1 = {
      'Fact': ['Least Death %',],
      'District': [row['District.Name']],
      'Count': [row['mortality_rate']]
    }
    df1 = pd.DataFrame(data1)
    self.df_pop_facts = self.df_pop_facts.append(df1,ignore_index= True)

    return self.df_pop_facts
###################################################


  def get_immigration_facts(self,year):
    self.merge_df()
    #Immigration By Nationality
    self.df1  = self.df_nation.groupby(['Year','Nationality'])['Number'].sum().reset_index()
    self.df1.columns = ['Year','Nationality','Immigrants']
    self.df1 = self.df1[(self.df1['Year']== year)]
    self.df1 = self.df1[(self.df1['Nationality'] != 'Spain') ]    
    row = self.df1.loc[self.df1['Immigrants'].idxmax()]
    data1 = {
      'Fact': ['Nationality With Most Immigrants',],
      'Category': [row['Nationality']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
    row = self.df1.loc[self.df1['Immigrants'].idxmin()]
    data1 = {
      'Fact': ['Nationality With Least Immigrants',],
      'Category': [row['Nationality']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
#District By Immigrants
    self.df1  = self.df_nation.groupby(['Year','District.Name'])['Number'].sum().reset_index()
    self.df1.columns = ['Year','District','Immigrants']
    self.df1 = self.df1[(self.df1['Year']== year)]
    row = self.df1.loc[self.df1['Immigrants'].idxmax()]
    data1 = {
      'Fact': ['District With Most Immigrants',],
      'Category': [row['District']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
    row = self.df1.loc[self.df1['Immigrants'].idxmin()]
    data1 = {
      'Fact': ['District With Least Immigrants',],
      'Category': [row['District']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
#Immigrants By Age
    self.df1  = self.df_age.groupby(['Year','Age'])['Number'].sum().reset_index()
    self.df1.columns = ['Year','Age','Immigrants']
    self.df1 = self.df1[(self.df1['Year']== year)]
    row = self.df1.loc[self.df1['Immigrants'].idxmax()]
    data1 = {
      'Fact': ['Age Group With Most Immigrants',],
      'Category': [row['Age']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
    row = self.df1.loc[self.df1['Immigrants'].idxmin()]
    data1 = {
      'Fact': ['Age Group Least Immigrants',],
      'Category': [row['Age']],
      'Count': [row['Immigrants']]
    }
    self.df2 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(self.df2,ignore_index= True)
# #unemployment
    self.df_year = self.df_merge[(self.df_merge['Year']== year)]
    row = self.df_year.loc[self.df_year['Unemployment'].idxmax()]
    data1 = {
      'Fact': ['Highest Unemployment',],
      'Category': [row['District.Name']],
      'Count': [row['Unemployment']]
    }
    df1 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(df1,ignore_index= True)
    row = self.df_year.loc[self.df_year['unemp_perc'].idxmax()]
    data1 = {
      'Fact': ['Highest Unemployment %',],
      'Category': [row['District.Name']],
      'Count': [row['unemp_perc']]
    }
    df1 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['Unemployment'].idxmin()]
    data1 = {
      'Fact': ['Least Unemployment',],
      'Category': [row['District.Name']],
      'Count': [row['Unemployment']]
    }
    df1 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(df1,ignore_index= True)


    row = self.df_year.loc[self.df_year['unemp_perc'].idxmin()]
    data1 = {
      'Fact': ['Least Unemployment %',],
      'Category': [row['District.Name']],
      'Count': [row['unemp_perc']]
    }
    df1 = pd.DataFrame(data1)
    self.df_immig_facts = self.df_immig_facts.append(df1,ignore_index= True)
    return self.df_immig_facts