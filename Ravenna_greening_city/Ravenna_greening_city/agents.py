from mesa import Agent
from mesa.time import BaseScheduler
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
import random

class GreenedAreasAgent(GeoAgent):
    #the number of these are determined by actions of other agents, which create them.
    def __init__(self, unique_id, model, shape, agent_type=None):
        super().__init__(unique_id, model, shape)
        self.condition = "Paved"
        self.health = 1.0
        self.new_green_areas = 0
        self.soil_water_content = 0.1
        self.cells_flooded = 0
        self.water_pooling = 0
        self.max_water_pooling = 5
        self.max_water_content = 0.8

    def coefficient_of_permeability(self):
        if self.percent_green >= 80:
            return 0.1
        elif self.percent_green >= 70:
            return 0.2
        elif self.percent_green >= 60:
            return 0.3
        elif self.percent_green >= 50:
            return 0.4
        elif self.percent_green >= 50:
            return 0.5
        elif self.percent_green >= 30:
            return 0.6
        elif self.percent_green >= 20:
            return 0.7
        elif self.percent_green >= 10:
            return 0.8
        else:
            return 0.9

    def change_in_water_pooling(self):
        water_pooling_change = 0.0
        if self.water_pooling <1.0:
            water_pooling_change += self.model.get_rainfall_volume() * self.coefficient_of_permeability()
        elif self.water_pooling >= 1.0:
            water_pooling_change += self.model.get_rainfall_volume()
        self.water_pooling += water_pooling_change
        return self.water_pooling


    def change_in_soil_moisture(self):
        water_pooling_influx = 0.0

        if self.water_pooling < 1.0:
            self.soil_moisture_influx = self.model.get_rainfall_volume() * self.coefficient_of_permeability() - self.transpiration_coefficient() / 1000    # - self.water_runoff

        else:
            water_pooling_influx += self.water_pooling * (1 - self.coefficient_of_permeability())
            self.soil_moisture_influx += water_pooling_influx / 1000   # to convert to m3

        self.water_pooling -= water_pooling_influx
        self.soil_water_content += self.soil_moisture_influx


    def transpiration_coefficient(self):
        m = 0.0
        if self.percent_green >= 70:
            m = 0.3
        elif self.percent_green >= 30:
            m = 0.2
        else:
            m = 0.01
        transpiration_equation = m * min(1.0, (4.0 / (3.0 * (self.soil_water_content / 0.8) / 0.4))) * self.model.get_PET()
        return transpiration_equation


    def is_this_cell_flooded(self):
        """
        Returns true if the cell is flooded, or false if it is not
        """
        if self.water_pooling >= self.max_water_pooling or self.soil_water_content >= self.max_water_content:
            return True
        else:
            return False


    def step(self):
        self.change_in_water_pooling()
        self.change_in_soil_moisture()
        # print(self.water_pooling)
        # neighbors = self.model.grid.get_neighbors(self)
        # self.is_this_cell_flooded()
        # self.agentsdatacollector.collect(self)