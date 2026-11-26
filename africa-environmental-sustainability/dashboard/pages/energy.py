import dash

from components import dimension_page

dash.register_page(__name__, path="/energy", name="Renewable Energy Transition", order=3)
layout = dimension_page("energy", "B", "Renewable Energy Transition", "B10E")
