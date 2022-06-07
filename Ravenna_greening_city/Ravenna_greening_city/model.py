# imports
from mesa import Model
import geojson
from shapely.geometry.base import BaseGeometry
from mesa_geo import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
from pathlib import Path
from mesa.datacollection import DataCollector
import random
from .agents import GreenedAreasAgent
from .schedule import RandomActivationGreening
import csv
from datetime import datetime
import requests
import pyproj
import geopandas as gpd

shapefile_folder = Path("C:\\Python\\anaconda\\envs\\SHELTERCONDA\\Ravenna_greening_city")
MAP_COORDS = [44.414703, 12.194655]
clipfile = shapefile_folder / "ravenna_three.geojson"
with open(clipfile) as f:
    geojson_states = geojson.load(f)

with open("ravenna_pet.csv", encoding='utf-8-sig') as f:    #load the climatic data CSV file.
    reader = csv.DictReader(f)
    rainfall_by_date = []
    PET_by_date = []
    TMEAN_by_date = []
    for row in reader:
        rainfall_by_date.append(float(row["RAINFALL"]))
        TMEAN_by_date.append(float(row["TMEAN"]))
        PET_by_date.append((1.6 * (15.5 / 12.0) * pow((float(row["PET"])) * 10.0 / 6.6, 0.6075)))

class GreeningCity(Model):    # create the model class
    """This is a model which simulates a flood event in the city of Ravenna, Italy.
    Various amounts of greening can be tested within the city to simulate how this may change the runoff, and therefore
    flooding severity, of the city. """

    def __init__(
            self,
            initial_private_owners=200,
            total_funds=50000,
            car_parks_to_green=0,
            streets_to_green=0,
            pedestrian_areas_to_green=0,
            PET = 0.10,
            number_cells_greened = 0,
            is_cell_flooded = False
        ):

            super().__init__()
            self.grid = GeoSpace()
            self.total_funds = total_funds
            self.step_number = 1
            self.car_parks_to_green = car_parks_to_green
            self.streets_to_green = streets_to_green
            self.pedestrian_areas_to_green = pedestrian_areas_to_green
            self.PET = PET
            self.running = True
            self.number_cells_greened = number_cells_greened # to be used as data collector
            self.is_cell_flooded = is_cell_flooded

            state_agent_kwargs = dict(model=self)
            AC = AgentCreator(agent_class=GreenedAreasAgent, agent_kwargs=state_agent_kwargs)
            self.cityoutline = AC.from_GeoJSON(GeoJSON=geojson_states, unique_id = "fid")
            self.grid.add_agents(self.cityoutline)
            self.schedule = RandomActivationGreening(self)
            for agent in self.cityoutline:
                self.schedule.add(agent)
            self.datacollector = DataCollector(
                model_reporters={
                    "total_money": lambda model: model.total_funds,
                    "step_number": lambda model: model.step_number,
                    "current_rainfall": lambda model: model.get_rainfall_volume(),
                    "number_cells_greened": lambda model: model.number_cells_greened,
                    "total_flooding": lambda a: a.total_pooling(),
                    "runoff_5_percent": lambda m: m.runoff_5_percent,
                    "runoff_10_percent": lambda m: m.runoff_10_percent,
                    "runoff_20_percent": lambda m: m.runoff_20_percent,
                    "runoff_30_percent": lambda m: m.runoff_30_percent,
                    "runoff_40_percent": lambda m: m.runoff_40_percent,
                    "runoff_50_percent": lambda m: m.runoff_50_percent,
                    "runoff_60_percent": lambda m: m.runoff_60_percent,
                    "runoff_60plus_percent": lambda m: m.runoff_60plus_percent,
                },
                agent_reporters={},
            )


    def get_rainfall_volume(self):
        return rainfall_by_date[self.step_number]     # call this every time something needs to know rainfall volume!!!

    def get_PET(self):
        return PET_by_date[self.step_number]   # returns one current value instead of whole list.

    ## the greening part of the model:
    def random_carpark_greening(self):
        cells_to_be_greened = []
        change_to_greenness = 0
        for state in self.cityoutline:
            if state.percent_green < 70 and state.car_parks >= 10 and state.pedestrian_areas <10:
                cells_to_be_greened.append(state)

        selected = random.sample(cells_to_be_greened, self.car_parks_to_green)
        car_parks_greened_factor = 0.3
        for cell in selected:
            self.number_cells_greened += 1
            change_to_greenness += cell.percent_green + (cell.car_parks * car_parks_greened_factor)
            cell.percent_green += (cell.car_parks * car_parks_greened_factor)
            cost = 20 * (change_to_greenness * state.area)
            self.total_funds -= change_to_greenness * cost


    def random_street_greening(self):
        cells_to_be_greened = []
        change_to_greenness = 0
        for state in self.cityoutline:
            if state.percent_green < 70 and state.streets >= 10 and state.pedestrian_areas <5 and state.car_parks <10:
                cells_to_be_greened.append(state)
        selected = random.sample(cells_to_be_greened, self.streets_to_green)
        streets_greened_factor = 0.8
        for cell in selected:
            self.number_cells_greened += 1
            change_to_greenness += cell.percent_green + (cell.streets * streets_greened_factor)
            cell.percent_green += (cell.streets * streets_greened_factor)
            cost = 60 * (change_to_greenness * state.area)
            self.total_funds -= change_to_greenness * cost


    def random_pedestrian_greening(self):
        cells_to_be_greened = []
        change_to_greenness = 0

        for state in self.cityoutline:
            if state.percent_green < 70 and state.pedestrian_areas >= 5:
                cells_to_be_greened.append(state)
        selected = random.sample(cells_to_be_greened, self.pedestrian_areas_to_green)
        pedestrian_areas_greened_factor = 0.15
        for cell in selected:
            self.number_cells_greened += 1
            change_to_greenness += cell.percent_green + (cell.pedestrian_areas * pedestrian_areas_greened_factor)
            cell.percent_green += (cell.pedestrian_areas * pedestrian_areas_greened_factor)
            cost = 20 * (change_to_greenness * state.area)
            self.total_funds -= change_to_greenness * cost

    def total_pooling(self):
        self.total_excess = 0
        agent: GreenedAreasAgent
        for agent in self.cityoutline:
            if agent.is_this_cell_flooded():
                self.total_excess += agent.water_pooling / 1000 * agent.area
        return self.total_excess

    def runoff_per_category(self):
        self.runoff_5_percent = 0.0
        self.total_5_percent = 0
        self.runoff_10_percent = 0.0
        self.total_10_percent = 0
        self.runoff_20_percent = 0.0
        self.total_20_percent = 0
        self.runoff_30_percent = 0.0
        self.total_30_percent = 0
        self.runoff_40_percent = 0.0
        self.total_40_percent = 0
        self.runoff_50_percent = 0.0
        self.total_50_percent = 0
        self.runoff_60_percent = 0.0
        self.total_60_percent = 0
        self.runoff_60plus_percent = 0.0
        self.total_60plus_percent = 0
        for cell in self.cityoutline:
            if cell.percent_green <=5:
                self.total_5_percent += 1
                self.runoff_5_percent += (cell.water_pooling / 1000 * cell.area) / self.total_5_percent
            elif cell.percent_green <=10:
                self.total_10_percent += 1
                self.runoff_10_percent += (cell.water_pooling / 1000 * cell.area) / self.total_10_percent
            elif cell.percent_green <=20:
                self.total_20_percent += 1
                self.runoff_20_percent += (cell.water_pooling / 1000 * cell.area) / self.total_20_percent
            elif cell.percent_green <=30:
                self.total_30_percent += 1
                self.runoff_30_percent += (cell.water_pooling / 1000 * cell.area) / self.total_30_percent
            elif cell.percent_green <=40:
                self.total_40_percent += 1
                self.runoff_40_percent += (cell.water_pooling / 1000 * cell.area) / self.total_40_percent
            elif cell.percent_green <=50:
                self.total_50_percent += 1
                self.runoff_50_percent += (cell.water_pooling / 1000 * cell.area) / self.total_50_percent
            elif cell.percent_green <=60:
                self.total_60_percent += 1
                self.runoff_60_percent += (cell.water_pooling / 1000 * cell.area) / self.total_60_percent
            elif cell.percent_green >=61:
                self.total_60plus_percent += 1
                self.runoff_60plus_percent += (cell.water_pooling / 1000 * cell.area) / self.total_60plus_percent


    def step(self):
        self.schedule.step()
        self.get_PET()
        self.runoff_per_category()
        self.total_pooling()
        if self.step_number == 1:
            self.random_carpark_greening()
        if self.step_number == 2:
            self.random_street_greening()
        if self.step_number == 3:
            self.random_pedestrian_greening()
        self.datacollector.collect(self)
        self.get_rainfall_volume()
        self.step_number += 1



