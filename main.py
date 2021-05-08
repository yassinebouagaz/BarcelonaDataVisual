###################################################
#How do we divide data into different files so that we can each work independently?
#Data in different in files has different column names.(District Name vs District.Name). WTF?!?
#https://towardsdatascience.com/how-to-build-interactive-dashboards-in-python-using-streamlit-1198d4f7061b

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
from Compare import Compare, DesignSideBarText
from Fact import fact_table
import plotly.express as px

st.set_page_config(layout="wide", page_title='Barcelona Data')

# @st.cache
def load_csv():
    df_unemployment = pd.read_csv('./archive/unemployment.csv')
    df_population = pd.read_csv('./archive/population.csv')
    df_immigrants_by_nationality = pd.read_csv('./archive/immigrants_by_nationality.csv')
    df_immigrants_emigrants_by_age = pd.read_csv('./archive/immigrants_emigrants_by_age.csv')
    df_immigrants_emigrants_by_sex = pd.read_csv('./archive/immigrants_emigrants_by_sex.csv')
    df_deaths = pd.read_csv('./archive/deaths.csv')
    df_births = pd.read_csv('./archive/births.csv')
    df_geo = pd.read_csv("barcelona_geo.csv")
    return df_unemployment, df_population, df_immigrants_by_nationality, df_immigrants_emigrants_by_age, df_immigrants_emigrants_by_sex,df_deaths,df_births,df_geo

df_unemployment, df_population, df_immigrants_by_nationality, df_immigrants_emigrants_by_age,df_immigrants_emigrants_by_sex,df_deaths,df_births,df_geo = load_csv()


x = fact_table(df_population,df_unemployment,df_deaths,
               df_immigrants_by_nationality,df_immigrants_emigrants_by_age,
               df_immigrants_emigrants_by_sex,df_births)

@st.cache(suppress_st_warning=True)
def makingProgressBar():
    my_bar = st.progress(0)
    for i in range(100):
        my_bar.progress(i + 1)
        time.sleep(0.01)
    my_bar.empty()  # Remove the progress bar

makingProgressBar()
# I was thinking it would be good for performance to read 
# all files at the start(What do you guys think?).
# All dataframes begin with "df" for ease in autocomplete (CTRL + Space)

# Hard coded names and dataframe names for categories
category_dict = {
    "Population" : df_population,
    #"Unemployment": df_unemployment,
    "Immigrants": df_immigrants_by_nationality
    # "Immigrants By Age": df_immigrants_emigrants_by_age,
    # "Immigrants By Sex": df_immigrants_emigrants_by_sex
}


categories = list(category_dict.keys())
districts = df_population["District.Name"].unique()
year_min = int(df_population.Year.min())
year_max = int(df_population.Year.max())
gender = df_population["Gender"].unique()
nationalities = np.sort(df_immigrants_by_nationality["Nationality"].unique())
age = np.sort(df_immigrants_emigrants_by_age['Age'].unique())


#Generate Sidebar for user selection.
#All variables start with "select" for ease in autocomplete
select_category = st.sidebar.selectbox("Category", categories)
selected_dataframe = category_dict.get(select_category)


if select_category == "Population":
    select_year = st.sidebar.slider("Year", 
                                min_value= int(2015), 
                                max_value= int(df_population.Year.max()))
    select_gender = st.sidebar.radio("Gender",("Both", "Male", "Female"))
    select_age = st.sidebar.selectbox("Age", age)

    if  select_gender == "Both":
        selected_data = selected_dataframe[(selected_dataframe['Year'] == select_year)
        & (selected_dataframe['Age'] == select_age)]
    else:
        selected_data = selected_dataframe[(selected_dataframe['Year'] == select_year)
        & (selected_dataframe['Gender'] == select_gender)
        & (selected_dataframe['Age'] == select_age)]
    
    year_data = df_unemployment.groupby(['Year'])['Number'].sum()
    age_data = df_population.groupby(['Age'])['Number'].sum()
    gender_data = df_unemployment.groupby(['District.Name'])['Number'].sum()


elif select_category == "Immigrants":
    select_year = st.sidebar.slider("Year", 
                                min_value= int(df_immigrants_by_nationality.Year.min()), 
                                max_value= int(df_immigrants_by_nationality.Year.max()))
    select_nationality = st.sidebar.selectbox("Nationality", nationalities)

    selected_data = selected_dataframe[(selected_dataframe['Year'] == select_year)
        & (selected_dataframe['Nationality'] == select_nationality)]
    year_data = df_immigrants_by_nationality.groupby(['Year'])['Number'].sum()
    age_data = df_immigrants_emigrants_by_age.groupby(['Age'])['Number'].sum()
    gender_data = df_immigrants_by_nationality.groupby(['District.Name'])['Number'].sum()
    

df_pop_data = x.merge_df()
df_pop_data = df_pop_data[df_pop_data.Year == select_year]

summed_data = selected_data.groupby(['District.Code'])['Number'].sum().reset_index().rename(columns={"Number": "Selected Population"})
summed_data = summed_data.merge(right = df_geo, on = "District.Code", how = "outer")

df_map = df_pop_data.merge(right = summed_data, on = ["District.Code"], how = "outer")
df_map = df_map.fillna(0)
df_map = df_map.rename(columns={"Population": "Total Population", "Unemployment": "Total Unemployment",
                                "Deaths": "Total Deaths", "Immigrants": "Total Immigrants",
                                "Births": "Total Births", "District.Name_x" : "District.Name"})
###################################################
isCompare = st.sidebar.checkbox("Compare Mode")

data_all = df_map
st.table(data_all.head(10))
data_geo = json.load(open('shapefiles_barcelona_distrito.geojson'))
map1, map2 = st.beta_columns(2)
def center():
    address = 'Barcelona, Spain'
    geolocator = Nominatim(user_agent="id_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude

def threshold(data):
    threshold_scale = np.linspace(data_all[dicts[data]].min(),
                              data_all[dicts[data]].max(),
                              5, dtype=float)
    threshold_scale = threshold_scale.tolist() # change the numpy array to a list
    # threshold_scale[-1] = threshold_scale[-1]
    return threshold_scale

def show_maps(data, other_data, district_name, death, immigrants, births,total_pop,threshold_scale):
    maps= folium.Choropleth(
        geo_data = data_geo,
        data = data_all,
        columns=['District.Name',dicts[data], dicts[other_data], dicts[death], dicts[immigrants], dicts[births], dicts[total_pop]],
        key_on='feature.properties.n_distri',
        threshold_scale=threshold_scale,
        fill_color='PuBuGn', 
        fill_opacity=0.7, 
        line_opacity=0.5,
        legend_name=dicts[data],
        highlight=True,
        reset=True).add_to(map_sby)

    folium.LayerControl().add_to(map_sby)
    maps.geojson.add_child(folium.features.GeoJsonTooltip(fields=['n_distri','Total_Pop', 'Unemplyment', 'Deaths', 'Immigrants', 'Births', 'Total_Pop'],
                                                        aliases=['District.Name: ', dicts[data], dicts[other_data], dicts[death], dicts[immigrants], dicts[births], dicts[total_pop]],
                                                        labels=True))                                                       
    if isCompare is False:
        with map1:
            folium_static(map_sby)

centers = center()

if isCompare is False:
    with map2:
        if select_category == 'Population':
            st.table(x.get_pop_facts(select_year))
        else:
            st.table(x.get_immigration_facts(select_year))

select_data = "Total_Pop"
other_data = "Unemplyment"
district_name = "District_Name"
deaths = "Deaths"
immigrants = "Immigrants"
births = "Births"
total_pop = "Total_Population"

map_sby = folium.Map(width='100%', height='100%', left='0%', top='0%', position='relative',tiles="Stamen Terrain", location=[centers[0], centers[1]], zoom_start=12)

#map2.markdown("<h1 style='text-align: center; color: red;'>Barcelona</h1>", unsafe_allow_html=True)

data_all['District.Name'] = data_all['District.Name'].str.title()


dicts = {
    "Total_Pop":'Selected Population',
    "Unemplyment": 'Total Unemployment',
    "District_Name": 'District.Name',
    "Deaths": 'Total Deaths',
    "Immigrants": 'Total Immigrants',
    "Births": 'Total Births',
    "Total_Population": 'Total Population'
}

tooltip_text = []
for idx in range(10):
 tooltip_text.append(str(data_all['Selected Population'][idx])+ ' inhabitants')
 
 tooltip_text_total_pop = []
for idx in range(10):
 tooltip_text_total_pop.append(str(data_all['Total Population'][idx])+ ' inhabitants')
 
tooltip_text_distict = []
for idx in range(10):
 tooltip_text_distict.append(str(data_all['District.Name'][idx]))

tooltip_text_unemploy = []
for idx in range(10):
 tooltip_text_unemploy.append(str(data_all['Total Unemployment'][idx])+ ' unemployees')
 
 tooltip_text_deaths = []
for idx in range(10):
 tooltip_text_deaths.append(str(data_all['Total Deaths'][idx])+ ' deaths')
 
 tooltip_text_immigrants = []
for idx in range(10):
 tooltip_text_immigrants.append(str(data_all['Total Immigrants'][idx])+ ' immigrants')
 
 tooltip_text_births = []
for idx in range(10):
 tooltip_text_births.append(str(data_all['Total Births'][idx])+ ' births')

for idx in range(10):
    index = int(data_geo['features'][idx]['properties']['c_distri'])
    data_geo['features'][idx]['properties']['Total_Pop'] = tooltip_text[index-1]
    data_geo['features'][idx]['properties']['Unemplyment'] = tooltip_text_unemploy[index-1]
    data_geo['features'][idx]['properties']['District_Name'] = tooltip_text_distict[index-1]
    data_geo['features'][idx]['properties']['Deaths'] = tooltip_text_deaths[index-1]
    data_geo['features'][idx]['properties']['Immigrants'] = tooltip_text_immigrants[index-1]
    data_geo['features'][idx]['properties']['Births'] = tooltip_text_births[index-1]
    data_geo['features'][idx]['properties']['Total_Population'] = tooltip_text_total_pop[index-1]


show_maps(select_data, other_data, district_name,deaths,immigrants,births,total_pop,threshold(select_data))

###########################################################
## Show Home Map
###########################################################
if isCompare is False:
    col1, col2, col3 = st.beta_columns(3)
    # year_data = df_immigrants_by_nationality.groupby(['Year'])['Number'].sum()
    # age_data = df_immigrants_emigrants_by_age.groupby(['Age'])['Number'].sum()
    # gender_data = df_immigrants_by_nationality.groupby(['District.Name'])['Number'].sum()

    # year_data.plot.bar(rot=15, title='Nationality', color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10'])
    # plt.show(block=True)
    # col1.pyplot()
    
    if select_category == "Immigrants":
        with col1:
            df_unemployment_sum = df_unemployment[(df_unemployment['Year']== select_year)]
            df_unemployment_sum = df_unemployment_sum.groupby(['District.Name','Year'])['Number'].sum().reset_index()
            df_unemployment_sum.columns = ["District.Name","Year","Number"]
            fig = px.bar(df_unemployment_sum, x="Year", y="Number", color="District.Name",
                        hover_name="District.Name", barmode='group', title='Unemployment By District')

            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            df_age_sum = df_immigrants_emigrants_by_age[(df_immigrants_emigrants_by_age['Year']== select_year)]
            df_age_sum = df_age_sum.groupby(['Age'])['Number'].sum().reset_index()
            df_age_sum.columns = ["Age","Number"]
            fig = px.pie(df_age_sum, values='Number', title='Population by age group', names='Age', color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            df_gender_sum = df_immigrants_emigrants_by_sex[(df_immigrants_emigrants_by_sex['Year']== select_year)]
            df_gender_sum = df_gender_sum.groupby(['Gender','Year'])['Number'].sum().reset_index()
            df_gender_sum.columns = ["Gender","Year","Number"]
            # fig = px.bar(df_gender_sum, x="Gender", y="Number", color="Gender",
            #             hover_name="Gender", barmode='group', title='Immigrantes by Gender')
            fig = px.pie(df_gender_sum, values='Number', title='Population by gender group', names='Gender', color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
    else:
        with col1:
            if (select_year == 2013) or (select_year == 2014):
                df_death_sum = df_deaths[(df_deaths['Year']== 2015)]
                df_death_sum = df_death_sum.groupby(['District.Name','Age'])['Number'].sum().reset_index()
                df_death_sum.columns = ["District.Name","Age","Number"]
                fig = px.bar(df_death_sum, x="District.Name", y="Number", color="Age", title="Death By Population(2015-2017)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                df_death_sum = df_deaths[(df_deaths['Year']== select_year)]
                df_death_sum = df_death_sum.groupby(['District.Name','Age'])['Number'].sum().reset_index()
                df_death_sum.columns = ["District.Name","Age","Number"]
                fig = px.bar(df_death_sum, x="District.Name", y="Number", color="Age", title="Death By Population(2015-2017)")
                st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            df_population_sum = df_population[(df_population['Year']== select_year)]
            df_population_sum = df_population_sum.groupby(['Age'])['Number'].sum().reset_index()
            df_population_sum.columns = ["Age","Number"]
            #fig = px.pie(df_population_sum, values='Number', title='Population by age group', names='Age', color_discrete_sequence=px.colors.sequential.RdBu)
            fig = px.bar(df_population_sum, x='Number', y='Age', title='Population By Age Group', color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            df_population_sum = df_population[(df_population['Year']== select_year)]
            df_population_sum = df_population_sum.groupby(['District.Name','Year'])['Number'].sum().reset_index()
            df_population_sum.columns = ["District.Name","Year","Number"]
            fig = px.bar(df_population_sum, x="Year", y="Number", color="District.Name",
                        hover_name="District.Name", barmode='group', title='Population By District')
            st.plotly_chart(fig, use_container_width=True)
        
    if select_category == "Immigrants":
        df_immigrant_sum = df_immigrants_by_nationality[(df_immigrants_by_nationality['Nationality'] != 'Spain') ]
        df_immigrant_sum = df_immigrant_sum.groupby(['Nationality','Year'])['Number'].sum().reset_index()
        df_immigrant_sum.columns = ["Nationality","Year","Number"]
        fig = px.scatter(df_immigrant_sum, x="Number", y="Year",
                    size="Number", color="Nationality",
                        hover_name="Nationality", log_x=True, size_max=40, range_y=[2014, 2018])
        fig.update_xaxes(range=[2, 4])
        fig.update_yaxes(tick0=2015, dtick=1)
        st.plotly_chart(fig, use_container_width= True)
        
        df_unemployment_sum = df_unemployment.groupby(['District.Name','Year'])['Number'].sum().reset_index()
        df_unemployment_sum.columns = ["District.Name","Year","Number"]
        fig = px.line(df_unemployment_sum, x="Year", y="Number", color="District.Name",
                    hover_name="Number")
        fig.update_xaxes(tick0=2013, dtick=1)
        st.plotly_chart(fig, use_container_width= True)

###########################################################
## Compare Work
###########################################################

if isCompare is True:
    st.sidebar.header('Comparing')

    col1, col2 = st.beta_columns(2)
    making_textbox = DesignSideBarText()
    all_dist = making_textbox.making_textbox()

    st.set_option('deprecation.showPyplotGlobalUse', False)
    unemployGender = Compare('./archive/unemployment.csv')
    unemployGender.makeDataframe(all_dist, select_year, 'Gender')
    unemployGender.showFigure('Unemployment By Gender', col1)

    st.set_option('deprecation.showPyplotGlobalUse', False)
    unemployDistrict = Compare('./archive/unemployment.csv')
    unemployDistrict.makeDataframe(all_dist, select_year, 'District.Name')
    unemployDistrict.showFigure('Unemployment By District Name', col2)

    
    colNext1, colNext2 = st.beta_columns(2)
    # populationAge = Compare('./archive/immigrants_emigrants_by_age.csv')
    # populationAge.makeDataframe(all_dist, select_year, 'Age')
    # populationAge.showFigure('Population By Age', colNext1, graphBar='barh')
    
    st.set_option('deprecation.showPyplotGlobalUse', False)
    populationNeighbor = Compare('./archive/population.csv')
    populationNeighbor.makeDataframe(all_dist, select_year, 'Neighborhood.Name')
    populationNeighbor.showFigure('Population By Neighbour',  colNext1, graphBar='barh')
    
    populationSex = Compare('./archive/immigrants_emigrants_by_sex.csv')
    populationSex.makeDataframe(all_dist, select_year, 'Gender')
    populationSex.showFigure('Population By Sex', colNext2, graphBar='barh')

# population = Compare('./archive/population.csv')
# population.makeDataframe(all_dist, select_year, 'Age')
# population.showFigure('Population',col2)

# immigration = Compare('./archive/immigrants_by_nationality.csv')
# immigration.makeDataframe(all_dist, select_year, 'Nationality')
# immigration.showFigure('Nationality',col3)