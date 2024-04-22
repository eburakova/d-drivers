import pandas as pd
import plotly.graph_objects as go


# I called dft= df_full.copy()
dft = pd.read_csv('data/full_data.csv')

#  a new column for the day of the week
dft['date'] = pd.to_datetime(dft['date'])
dft['day_of_week'] = dft['date'].dt.day_name()

date_count_per_id = dft.groupby('page_id')['date'].nunique()  # group by the page ids and their unique dates

freq_amount_of_dates_above_70 = date_count_per_id[date_count_per_id >= 70]  # find out which ones had more
                                                                             # than 70 dates (otherwise doesn't help
                                                                             # in the visualization)

fig = go.Figure()

for index in freq_amount_of_dates_above_70.index:  # iterate over each index
    dft_one = dft[dft.page_id == index]
    trace = go.Scatter(
        x=dft_one['date'],
        y=dft_one['external_clicks'],
        mode='lines',
        hoverinfo='skip',
        hovertemplate=f'<b>Page ID:</b> {index}<br><b>Date:</b> %{{x}} (%{{x|%A}})<br><b>External Clicks:</b> %{{y}}<extra></extra>',
        showlegend=False)  # here is to SHUT UP the default trace info from hover

    fig.add_trace(trace)

fig.update_layout(
    title='External Clicks over Time for Different Page IDs',
    xaxis_title='Date',
    yaxis_title='External Clicks',
    hovermode='closest', 
    showlegend=False,  
    xaxis=dict(
        tickmode='auto',
        nticks=20,
        tickformat='%Y-%m-%d (%a)',  # show date with day of the week abbreviated
    )
)

# Show figure
fig.show()