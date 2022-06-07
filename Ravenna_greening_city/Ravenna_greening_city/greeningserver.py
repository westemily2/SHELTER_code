from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule

from mesa_geo.visualization.MapModule import MapModule
from Ravenna_greening_city.agents import GreenedAreasAgent
from Ravenna_greening_city.model import GreeningCity


COLORS = {"Greened": "#03B303", "Paved": "#A0A6A6"}

#next set up visualisation elements
funds = ChartModule(
    [{"Label": "total_money", "Color": "Green"}],
)

rainfall_and_flood = ChartModule(
    [{"Label": "current_rainfall", "Color": "Blue"}],
)
just_flood = ChartModule(
    [{"Label": "total_flooding", "Color": "Red"}],
)

number_cells_greened = ChartModule(
    [{"Label": "number_cells_greened", "Color": "Green"}]
)

flooding_by_greened_amount = ChartModule(
    [{"Label": "runoff_5_percent", "Color": "#283128"}, {"Label": "runoff_10_percent", "Color": "#364c36"},
    {"Label": "runoff_20_percent", "Color": "#3e6c3e"}, {"Label": "runoff_30_percent", "Color": "#397c39"},
    {"Label": "runoff_40_percent", "Color": "#3ea33e"}, {"Label": "runoff_50_percent", "Color": "#7bca7b"},
    {"Label": "runoff_60_percent", "Color": "#40c740"}, {"Label": "runoff_60plus_percent", "Color": "#0aea0a"}],
)


def agent_vis(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if agent.is_this_cell_flooded():
        portrayal["color"] = "Blue"
    elif agent.percent_green >= 70:
        portrayal["color"] = "#04470a"
    elif agent.percent_green >= 60:
        portrayal["color"] = "#078012"
    elif agent.percent_green >= 50:
        portrayal["color"] = "#0bc11c"
    elif agent.percent_green >= 40:
        portrayal["color"] = "#0ff124"
    elif agent.percent_green >= 30:
        portrayal["color"] = "#64f672"
    elif agent.percent_green >= 20:
        portrayal["color"] = "#86f791"
    elif agent.percent_green >= 10:
        portrayal["color"] = "#c3e6c7"
    else:
        portrayal["color"] = "Grey"
    return portrayal

model_parameters = {
    "car_parks_to_green": UserSettableParameter("slider", "car_parks_to_green", 20, 0, 42, 1),
    "streets_to_green": UserSettableParameter("slider", "streets_to_green", 20, 0, 231, 1),
    "pedestrian_areas_to_green": UserSettableParameter("slider", "pedestrian_areas_to_green", 1, 0, 21, 1),
}

map_element = MapModule(agent_vis, [44.41, 12.20], 13, 500, 700) #set the zoom + coordinate focus of the map

server = ModularServer(GreeningCity,
                       [
                           rainfall_and_flood,
                           number_cells_greened,
                           just_flood,
                           flooding_by_greened_amount,
                           map_element,
                       ],
                       "greening city model",
                       model_parameters
                       )