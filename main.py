import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
# import geemap
import geemap.foliumap as geemap
import ee
# ee.Authenticate()

# load_dotenv()
# os.environ['LANGCHAIN_TRACING_V2'] = os.getenv('LANGCHAIN_TRACING_V2')
# os.environ['LANGCHAIN_ENDPOINT'] = os.getenv("LANGCHAIN_ENDPOINT")
# os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
# os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
# creds = {
#     "type": os.getenv("type"),
#     "project_id": os.getenv("project_id"),
#     "private_key_id": os.getenv("private_key_id"),
#     "private_key": os.getenv("private_key"),
#     "client_email": os.getenv("client_email"),
#     "client_id": os.getenv("client_id"),
#     "auth_uri": os.getenv("auth_uri"),
#     "token_uri": os.getenv("token_uri"),
#     "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
#     "client_x509_cert_url": os.getenv("client_x509_cert_url"),
#     "universe_domain": os.getenv("universe_domain"),
# }


os.environ['LANGCHAIN_TRACING_V2'] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["LANGCHAIN_ENDPOINT"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["LANGCHAIN_API_KEY"]
os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
creds = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    "universe_domain": st.secrets["universe_domain"]
    }


credentials = ee.ServiceAccountCredentials(
    email=creds["client_email"],
    key_data=creds["private_key"]
)


ee.Initialize(
    credentials=credentials,
    project=creds["project_id"]
)

print(ee.String("Hello, Earth Engine!").getInfo())


def calculate_ndvi(start_date, end_date, district_name, shapefile_asset_id):

    kerala = ee.FeatureCollection(shapefile_asset_id)

    def filter_district(district_name):
        return kerala.filter(ee.Filter.eq('NAME_1', district_name)).geometry()

    district_geometry = filter_district(district_name)

    image_collection = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterDate(start_date, end_date)
        .filterBounds(district_geometry)
    )

    def add_ndvi(image):
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        return image.addBands(ndvi)

    ndvi_collection = image_collection.map(add_ndvi)
    mean_ndvi = ndvi_collection.select('NDVI').mean()
    clipped_ndvi = mean_ndvi.clip(district_geometry)

    vis_params = {
        'min': 0,
        'max': 1,
        'palette': ['blue', 'white', 'green'],
        'opacity': 0.9

    }

    boundary_style = {
        'color': 'black',
        'width': 3,
        'lineType': 'solid',
        'opacity': 0.5
    }
    Map = geemap.Map()
    Map.centerObject(district_geometry, 8)
    Map.addLayer(clipped_ndvi, vis_params, 'Mean NDVI')
    Map.add_colorbar(vis_params, label="Mean NDVI", discrete=False, position='bottomleft',
                     font_size=10, layer_name="Mean NDVI", orientation='vertical')
    Map.addLayer(district_geometry, boundary_style,
                 f'{district_name}_boundary')
    Map.addLayerControl()

    return Map


def extract_meta_data(user_input):
    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = [SystemMessage("""You are a helpful assistant designed to extract specific information from user queries about geospatial data in the United Arab Emirates (UAE). Your task is to identify and extract the following details from the user's input:

1. **Location**: Identify the geographical location mentioned in the query within the UAE. for example polaces like the following:
   [Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah]

2. **Start Date**: Identify the starting date or time period mentioned in the query (e.g., "January 2025", "2020"). Convert dates into `yyyy-mm-dd` format, assuming the start of the year (`yyyy-01-01`) if the exact date is not specified.

3. **End Date**: Identify the ending date or time period mentioned in the query (e.g., "2023"). If no end date is mentioned, assume it is the same as the start date.

### Example Queries & Expected Output

#### Example 1
**Input:** "Show the NDVI map of Dubai for January 2025."  
**Output:** a cdictionay like
{"location": "Dubai", "start_date": "2025-01-01", "end_date": "2025-01-01"}"""),


              HumanMessage(user_input)]
    out = model.invoke(prompt)
    return eval(out.content)


def get_map(user_in):
    meta_dict = extract_meta_data(user_in)
    # lattitude,longitude=get_coordinates(meta_dict['location'])
    # del meta_dict['location']
    # meta_dict['coords'] = [longitude, lattitude]
    ndvi_image = calculate_ndvi(
        start_date=meta_dict['start_date'],
        end_date=meta_dict['end_date'],
        district_name=meta_dict['location'],
        shapefile_asset_id='projects/tessss-341107/assets/uae',
    )
    return ndvi_image


# if __name__=="__main__":
#     user_in = "Give me the NDVI of trissur for 2020 to 2023."
#     mean_ndvi, ndvi_image = get_map(user_in)
