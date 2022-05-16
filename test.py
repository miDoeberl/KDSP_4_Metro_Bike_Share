import dash
import dash_html_components as html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State

app = dash.Dash()
app.layout = html.Div([
   dl.Map([dl.TileLayer(), dl.LayerGroup(id="container", children=[])], id="map",
           center=(56, 10), zoom=10, style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
           html.Button(id="marker_context", children="Set as starting location")])
        
@app.callback(Output("container", "children"), [Input("map", "click_lat_lng")], [State("container", "children")])
def add_marker(click_lat_lng, children):
    children.append(dl.Marker(position=click_lat_lng))
    return children

@app.callback(Output("marker_context", "children"), [Input("marker_context", 'n_clicks')])
def play_pause(n):
    print(n)
    return str(n % 2 == 1)

if __name__ == '__main__':
    app.run_server()
