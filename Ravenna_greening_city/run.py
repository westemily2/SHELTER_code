from Ravenna_greening_city.greeningserver import server
# from Ravenna_greening_city import greeningserver #greeningserver import greeningserver
server.port = 8523

server.launch()

# do not delete this - it is uncommented when the model is run as a batch rather than on the server.
"""
from Ravenna_greening_city.model import *  # import everything, all classes and functions.
from Ravenna_greening_city.agents import *

from numpy import arange  # allows us to create evenly spaced numbers within a given interval
import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner  # import the batchrunner itself
from mesa.datacollection import DataCollector
from datetime import date
#next we have to specify the fixed parameter values which we do not want to change.

fixed_params = {
                "initial_private_owners": 200,
                "total_funds":50000,
}
#and similarly after this we set up a dictionary specifying the parameters we DO want to change.
variable_params = {"car_parks_to_green":range(0, 42, 10),
                   "streets_to_green": range(0,231, 50),
                   "pedestrian_areas_to_green": range(0, 21, 5)}   # all the combinations of this amount in this increment
num_iterations = 100 #runs each possible combination 10 times - useful to do multiple times when randomness involved.
num_steps = 61 #number of time steps run per model run.

batch_run = BatchRunner(GreeningCity,  #note this might have to be the name of model class but I have put name of file
                        fixed_parameters = fixed_params,
                        variable_parameters = variable_params,
                        iterations = num_iterations,
                        max_steps = num_steps,
                        model_reporters=
                        {
                            "total_money": lambda model: model.total_funds,
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
                        })
batch_run.run_all()  # tell the batch runner to run
run_data = batch_run.get_model_vars_dataframe()  # store the results in a Pandas dataframe
run_data.to_csv('floodingrun_final_' + date.today().isoformat() + '.csv')
# plt.scatter(run_data.public_funding_allocation, private_funding_allocation)"""