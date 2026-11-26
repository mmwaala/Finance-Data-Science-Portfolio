import dash

from components import dimension_page

dash.register_page(__name__, path="/biodiversity", name="Biodiversity and Ecosystem Health", order=6)
layout = dimension_page("biodiversity", "E", "Biodiversity and Ecosystem Health", "E08")
