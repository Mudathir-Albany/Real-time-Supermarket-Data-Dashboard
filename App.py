# get_ipython().system('pip install plotly-express')
# get_ipython().system('pip install open')


import pandas as pd
import plotly.express as px
import streamlit as st
# import openpyxl

st.set_page_config(page_title = "Sales Dashboard", page_icon = ":bar_chart", layout = "wide")
##############################################################################################

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# # Authenticate PyDrive
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# # Create a GoogleDrive instance
# drive = GoogleDrive(gauth)

#############################
from oauth2client.service_account import ServiceAccountCredentials
gauth = GoogleAuth()
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'sales-dashboard-Service-act-key-editor.json', 
    ['https://www.googleapis.com/auth/drive']
)
drive = GoogleDrive(gauth)
###################

# Get the ID of the Google Drive folder containing your data
folder_id = '1PPPV9qQ7Qp-ePOxgi5_Sg4LTHZRMonmu'

def update_data():
    # Get a list of all files in the folder
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
    # Filter the list to include only the files you want to visualize
    data_files = [file for file in file_list if file['title'].endswith('.csv') or file['title'].endswith('.xlsx')]
    if not data_files:
        raise ValueError("No data files found in folder.")
    # Load the first CSV file in the list
    data_file = data_files[0]
    data_file.GetContentFile(data_file['title'])
    df = pd.read_excel(data_file['title'])
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

# def select_data():
#     # Get a list of all files in the folder
#     file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
#     # Filter the list to include only the files you want to visualize
#     data_files = [file for file in file_list if file['title'].endswith('.csv') or file['title'].endswith('.xlsx')]
#     if not data_files:
#         raise ValueError("No data files found in folder.")
#     # Create a Streamlit dropdown with the file names
#     selected_file = st.selectbox('Select a file', [file['title'] for file in data_files])
#     # Get the selected file
#     file_id = [file['id'] for file in data_files if file['title'] == selected_file][0]
#     file = drive.CreateFile({'id': file_id})
#     file.GetContentFile(selected_file)  # save the selected file locally
#     # Load the selected file as a pandas dataframe
#     df = pd.read_excel(selected_file)
#     # Display the updated DataFrame in Streamlit
#     # st.write(df)
#     return df



##############################################################################################


# sales_df = pd.read_excel("supermarkt_sales.xlsx")
sales_df = update_data()


#### SideBar Menu
st.sidebar.header("Filters")
city = st.sidebar.multiselect(
    "Select the city",
    options = sales_df["City"].unique(),
    default = sales_df["City"].unique()
)
customer_type = st.sidebar.multiselect(
    "Select the Customer Type",
    options = sales_df["Customer_type"].unique(),
    default = sales_df["Customer_type"].unique()
)
gender = st.sidebar.multiselect(
    "Select the Gender",
    options = sales_df["Gender"].unique(),
    default = sales_df["Gender"].unique()
)
# Create functionality for the menu options
df_selection = sales_df.query("City == @city & Customer_type == @customer_type & Gender == @gender")


#### Main Page
st.title(":bar_chart: Real-time Supermarket Data Dashboard")
st.markdown("##")

#### Top KPI's
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_tansaction = round(df_selection["Total"].mean(), 2)

#### Main Page Cards
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US ${total_sales}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Avg Sales Per Transaction:")
    st.subheader(f"US ${average_sale_by_tansaction}")

st.markdown("---")

# Add a Streamlit button to fetch the latest data when clicked
if st.button('Refresh Data'):
    sales_df = update_data()

#### Bar Charts
sales_by_product_line = (df_selection.groupby(by=["Product line"]).sum()
                         [["Total"]].sort_values(by="Total"))

#### Plot Bar of Product Sales
fig_product_sales = px.bar(
    sales_by_product_line,
    x = "Total",
    y=sales_by_product_line.index,
    orientation = "h",
    title = "<b>Sales by Product Line </b>",
    color_discrete_sequence = ["#0083B8"] * len(sales_by_product_line),
    template = "plotly_white",
)
# st.plotly_chart(fig_product_sales)

fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

#### Show Dataframe
st.dataframe(df_selection)

# # ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

