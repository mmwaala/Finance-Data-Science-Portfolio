import dash

from components import dimension_page

dash.register_page(__name__, path="/water", name="Water Resources and Water Stress", order=5)
layout = dimension_page("water", "D", "Water Resources and Water Stress", "D05")
