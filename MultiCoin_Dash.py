from st_pages import Page, Section, show_pages, add_page_title

add_page_title("MultiCoin_Dashboard") # By default this also adds indentation

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("MultiCoin_Dash_Old.py", "General Visualization"),
        Page("Plotting_Dash.py", "Specific Dash(3 months Version)")
    ]
)