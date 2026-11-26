import dash

from components import dimension_page

dash.register_page(__name__, path="/carbon", name="Carbon Emissions and Climate Change", order=2)
layout = dimension_page("carbon", "A", "Carbon Emissions and Climate Change", "A01")
