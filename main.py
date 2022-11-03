# Tutorial: https://www.justintodata.com/streamlit-python-tutorial/
# Cheatsheet: https://docs.streamlit.io/library/cheatsheet
# API Reference: https://docs.streamlit.io/library/api-reference
# AgGrid: https://towardsdatascience.com/make-dataframes-interactive-in-streamlit-c3d0c4f84ccb


import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode

import wine_type_list


def print_header():
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
    st.write(
        "2. In the second table, on the right, mark anything in your meal you think should be weighted more heavily "
        "when selecting a wine to pair.")
    st.write("3. Scroll down to see wines that match your selections. The higher the number, the better the match!")
    st.write('')
    st.write('')


def build_grid(dataframe):
    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_selection(selection_mode='multiple', use_checkbox=True, rowMultiSelectWithClick=True)
    grid_options = gb.build()
    grid = AgGrid(dataframe, gridOptions=grid_options, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    # note: many grid options available, see docs
    return grid


# def build_right_grid(selections):
#     # if user selected anything
#     if len(selections) > 0:
#         df_selection_names = df_selections[['name']]  # Make a dataframe with just the 'name' column
#         grid = build_left_grid(df_selection_names) # display selections in a grid on the right side of page
#         return grid
#     else:
#         st.write('Nothing selected to display')


# main
print_header()

col_l, col_r = st.columns([5, 3])  # col_l is larger

# ********** PRINT THE LEFT GRID *********
# convert the spreadsheet into a dataframe
df_everything = pd.read_csv("food_wine_pairing.csv", encoding='unicode_escape')
# prep the dataframe for display by parsing it into just the columns 'category' and 'name'
df = df_everything[['category', 'name']]
# and display parsed versions of the dataframe on the left side of the page
with col_l:
    with st.expander("Meat"):
        grid_meat = build_grid(df.query("category == 'meat'"))
    meat_selections = grid_meat['selected_rows']
    with st.expander("Meat Cooking Method"):
        grid_preparation = build_grid(df.query("category == 'preparation'"))
    preparation_selections = grid_preparation['selected_rows']
    with st.expander("Sauces"):
        grid_sauces = build_grid(df.query("category == 'sauces'"))
    sauces_selections = grid_sauces['selected_rows']
    with st.expander("Dairy"):
        grid_dairy = build_grid(df.query("category == 'dairy'"))
    dairy_selections = grid_dairy['selected_rows']
    with st.expander("Pizza"):
        grid_pizza = build_grid(df.query("category == 'pizza'"))
    pizza_selections = grid_pizza['selected_rows']
    with st.expander("Pasta"):
        grid_pasta = build_grid(df.query("category == 'pasta'"))
    pasta_selections = grid_pasta['selected_rows']
    with st.expander("Vegetables"):
        grid_vegetables = build_grid(df.query("category == 'vegetable'"))
    vegetables_selections = grid_vegetables['selected_rows']
    with st.expander("Seasonings"):
        grid_seasonings = build_grid(df.query("category == 'seasoning'"))
    seasonings_selections = grid_seasonings['selected_rows']
    with st.expander("Starches"):
        grid_starches = build_grid(df.query("category == 'starch'"))
    starches_selections = grid_starches['selected_rows']
    with st.expander("Sweets"):
        grid_sweets = build_grid(df.query("category == 'sweets'"))
    sweets_selections = grid_sweets['selected_rows']
    
# and display the parsed dataframe in a grid, on the left side of the page
with col_l:
    grid_main = build_grid(df)

# this line captures the items the user checked
# selections is technically a list variable, but it's in a complex form that
# can easily become a DataFrame
selections = grid_main['selected_rows']

# ********* PRINT THE RIGHT GRID **********
with col_r:
    if len(meat_selections) > 0: # if user selected any meats
        df_meat_selections = pd.DataFrame(meat_selections) # pass selected rows to new dataframe
        
    if len(selections) > 0:  # if user selected anything
        df_selections = pd.DataFrame(selections)  # pass the selected rows to a new dataframe
        # if user selected anything
        if len(selections) > 0:
            if len(meat_selections) > 0:
                df_selections = pd.concat([df_selections, df_meat_selections])
            df_selection_names = df_selections[['name']]  # Make a dataframe with just the 'name' column
            grid_selections = build_grid(df_selection_names)  # display selections in a grid on the right side of page
    else:  # user has not selected anything
        st.write('Nothing selected to display')

# ********** PRINT HEADER **********
st.write("## SPECIFIC SUGGESTIONS")

if len(selections) > 0:  # if user selected anything
    # number of items in df_selections = df_selections.shape[0]
    # so, in other words, we are looping through all the items the user selected
    for i in range(df_selections.shape[0]):
        # this line finds the 'name' cell's value for an item
        sel = df_selections.loc[i]['name']
        # this line finds the row 'sel' in df_everything
        row = df_everything.loc[df['name'] == sel]
        # this line returns a [list] to the aList variable
        aList = row['specific suggestions'].values
        # this line turns the list into a comma separated string, assuming it's not empty
        # lists that are empty, or NaN in this case, throw a KeyError
        # pd.isna(aList) returns True if the value is NaN ... we don't want those
        # we only want the ones where something is present in the 'specific suggestions' cell
        if not pd.isna(aList):
            st.markdown("**" + ','.join(aList).upper() + "** is suggested for **" + sel.upper() + "**")
else:
    st.write('No specific suggestions yet.')

# ********** PRINT HEADER **********
st.write("## GENERAL SUGGESTIONS")

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

    # * * Remove selections that don't have numbered values in 'bold red' column! * *:
    # df_out_parsed = df_out[df_out['bold red'] != ''] ... nope, had to use next line
    df_out_parsed = df_out.dropna(subset=['bold red'])

    # .sum() adds the values in each column
    # .sort_values(ascending=False) sorts the values (duh) and displays from highest to lowest
    display = df_out_parsed.sum(numeric_only=True).sort_values(ascending=False)
    # this provides a list of the wines themselves; they're the indexes on the dataframe called "display":
    wine_list = display.index.tolist()
    # and this provides a list of the numbers, i.e., the sum of the values for each wine
    value_list = display.values
    # we will go through each wine type in the wine_type_list:
    for i in range(len(wine_list)):
        match = int((value_list[i] * 100) / (df_out_parsed.shape[0] * 2))
        # example_list finds the list of examples for an individual wine type
        example_list = wine_type_list.wine_types[wine_list[i]]
        s = ""
        # we convert the list into a formatted string
        for item in example_list:
            if example_list.index(item) < len(example_list) - 1:
                s += item + ", "
            else:
                s += "and " + item
                # progress bar
        # st.progress(match)
        st.metric(label=wine_list[i], value=str(match) + "% match")
        # print the wine name, allow user to click on the name to see examples
        with st.expander(wine_list[i] + ' examples'):
            st.write(s)
except NameError:
    st.write('Nothing selected yet')
