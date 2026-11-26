import dash

from components import dimension_page

dash.register_page(__name__, path="/forests", name="Deforestation and Forest Resources", order=4)
layout = dimension_page("forests", "C", "Deforestation and Forest Resources", "C03")
