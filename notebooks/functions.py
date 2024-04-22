import plotly.express as px
import plotly.io as pio
import pandas as pd

def plot_feature_importance(pipeline, save_as=False):
    """Parameters:
    - pipeline: must be an sklearn object (or something that supports sklearn API) that combines a preprocessor and a model
    - save_as: False if you don't wanna save the figure, filename if you do
    Returns:
    - fig: a plotly bar plot (horizontal bars)
    """
    feat_imp = pipeline.steps[-1][1].feature_importances_
    feat_names = pipeline[:-1].get_feature_names_out()

    feature_importance = pd.DataFrame().from_records(
        data={'Features': [name.split('__')[-1] for name in feat_names], 'Importance': feat_imp})
    feature_importance = feature_importance.sort_values('Importance', ascending=True)
    fig = px.bar(feature_importance, 
                 y='Features', x='Importance',
                 orientation='h', height=800, width=800
                        )
    if save_as:
        pio.write_image(fig, save_as)
    return fig