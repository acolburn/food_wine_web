# Tutorial: https://www.justintodata.com/streamlit-python-tutorial/
# Cheatsheet: https://docs.streamlit.io/library/cheatsheet
# API Reference: https://docs.streamlit.io/library/api-reference
# AgGrid: https://towardsdatascience.com/make-dataframes-interactive-in-streamlit-c3d0c4f84ccb


import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode

import wine_type_list


def build_grid(dataframe):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_selection(selection_mode='multiple', use_checkbox=True, rowMultiSelectWithClick=True)
    grid_options = gb.build()
    grid = AgGrid(dataframe, gridOptions=grid_options, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    # note: many grid options available, see docs
    return grid


# main
# st.title('Cool Title or Logo Here')
# following code needed to center the image
col1, col2, col3 = st.columns(3)
with col1:
    st.write('')
with col2:
    st.image("logo.jpg")
with col3:
    st.write('')

st.write("1. In the table below, mark the elements of your meal you'd like to pair with wine. The items you select "
         "will appear in the table to the right.")
st.write("2. In the second table, on the right, mark anything in your meal you think should be weighted more heavily "
         "when selecting a wine to pair.")
st.write("3. Scroll down to see wines that match your selections. The higher the number, the better the match!")
st.write('')
st.write('')

col_l, col_r = st.columns([4, 1])  # col_l is larger

df_everything = pd.read_csv("food_wine_pairing.csv", encoding='unicode_escape')
df = df_everything[['category', 'name', 'examples']]

with col_l:
    grid_main = build_grid(df)

selections = grid_main['selected_rows']  # selected is technically a list variable, but it's in a complex form that
# can easily become a DataFrame
with col_r:
    if len(selections) > 0:
        df_selections = pd.DataFrame(selections)  # Pass the selected rows to a new dataframe df
        df_selection_names = df_selections[['name']]  # Make a dataframe with just the 'name' column
        grid_selections = build_grid(df_selection_names)
    else:
        st.write('Nothing selected to display')

# Everything user selected, as a list
# BUT if user hasn't selected anything, this throws a NameError--hence the try/except
try:
    # weighted are the items user selected, then clicked to weight extra
    weighted = grid_selections['selected_rows']
    # let's put weighted into a DataFrame
    df_weighted = pd.DataFrame(weighted)
    # and combine the DataFrames with the weighted items and all the items users selected
    # the resulting DataFrame will have everything, with weighted items counted twice
    df_selections = pd.concat([df_selections, df_weighted])
    selections_list = df_selections['name'].to_list()

    # initialize an empty dataframe that's going to have the complete rows for all selections
    df_out = pd.DataFrame()
    # go through selections one at a time, so that weighted categories will be counted twice
    for item in selections_list:
        temp = df_everything.loc[df['name'] == item]
        df_out = pd.concat([df_out, temp])
    # .sum() adds the values in each column
    # .sort_values(ascending=False) sorts the values (duh) and displays from highest to lowest
    display = df_out.sum(numeric_only=True).sort_values(ascending=False)
    # this provides a list of the wines themselves; they're the indexes on the dataframe called "display":
    wine_list = display.index.tolist()
    # and this provides a list of the numbers, i.e., the sum of the values for each wine
    value_list = display.values
    # we will go through each wine type in the wine_type_list:
    for i in range(len(wine_list)):
        match = int((value_list[i] * 100) / (len(selections_list) * 2))
        # example_list finds the list of examples for an individual wine type
        example_list = wine_type_list.wine_types[wine_list[i]]
        s = ""
        # we convert the list into a formatted string
        for item in example_list:
            if example_list.index(item) < len(example_list)-1:
                s += item + ", "
            else:
                s += "and " + item        
        # progress bar
        # st.progress(match)
        st.metric (label=wine_list[i], value=str(match)+"% match")
        # print the wine name, allow user to click on the name to see examples
        with st.expander(wine_list[i] + ' examples'):
            st.write(s)
except NameError:
    st.write('Nothing selected yet')
