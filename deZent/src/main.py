import simpy
import random
import numpy as np
import pandas as pd
from datetime import datetime
import sys

from network import Network
from zanon import zAnon
from logging_utils import RecordLog, PubLog, SimuLog
#from central_zanon import zAnon_central


###############
'''
    * model distributed z-anon
    * this shall go on until simulation is stopped
'''
def decent_zanon(env, zanon_env, network, start_time):
    yield env.process(zanon_env.decent_zanon_w_comm(network, start_time))

def cent_zanon(env, zanon_env, network, start_time):
    yield env.process(zanon_env.central_zanon_w_cnt_struct(network, start_time))

def fully_decent_zanon(env, zanon_env, network, start_time):
    yield env.process(zanon_env.fully_decent_zanon_wo_coord(network, start_time))


###############
'''
    * create zanon instance 
    * parameters and functions needed for anonymization
'''
def set_zanon_params(env, delta_t, zeta):
    zanon_env = zAnon(env, delta_t, zeta)
    return zanon_env


'''
    * create simulation network
    * create GWs and open connections
    * add smart meters to network and connect with GWs
'''
def create_network(n_gws, dist_num_sms, max_n_sms_at_gw):
    # init instance of network with x GWs and y SMs
    network = Network( n_gws)
    print("__create nw__: created network instance")

    # open connections with SMs for GWs within network following a predefined distribution
    network.init_network(dist_num_sms, max_n_sms_at_gw)

    return network

""""""
def clear_network_logs(nw):
    nw.ce.record_log = RecordLog()
    nw.ce.pub_records = PubLog()#pd.DataFrame(columns = ["key", "orig_measurement", "GW", "time", "ID", "type"])
    nw.ce.simu_log = SimuLog()
    for gw in nw.l_gws:
        gw.record_log = RecordLog()


###############
def get_user_input(n_gw, n_sm, z):
    num_gws = int(n_gw) #5 #input("Input # of GWs working: ")#
    #max_n_gw_sm_conn = 2 #input("Input # of connections per GW working: ")  #
    distribution_num_sms = "normal" # determine distribution to sample number of SMs per GW
    max_num_sm_at_gw = int(n_sm) #100 # determine maximum number of SMs per GW to pass as a parameter to distribution
    delta_t = 121 # [minutes]
    zeta = int(z) #100 # TODO: check user input to be [0, inf]
    

    params = [num_gws, distribution_num_sms, max_num_sm_at_gw, delta_t, zeta]
    '''
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 GW.",
        )
    '''
    return params


def generate_log_index(z_env, l_col):
    index_array = [['msg_count_gw', 'msg_cnt_gw_ce', l_col[0]]] + [[str(z_env.msg_cnt), str(z_env.msg_cnt_gw_ce), l_col[1]]] + [['', '', f'{l_col[i]}'] for i in np.arange(2,len(l_col))]
    idx = pd.MultiIndex.from_tuples(index_array)
    return idx
###############
'''
    start simulation of distributed network with specified number of GWs and frequently arriving SMs
'''
def main():
    # Setup system parameters
    
    if(len(sys.argv) != 5):
        print("Usage: python3 main.py <cnt_gw> <cnt_sm> <z> <seed>")
        sys.exit(1)
    print(sys.argv)
    n_gw = sys.argv[1]
    n_sm = sys.argv[2]
    z = sys.argv[3]
    seed = sys.argv[4]

    random.seed(seed)

    params = get_user_input(n_gw, n_sm, z)
    num_gws, dist_num_sms, max_num_sm_at_gw, delta_t, zeta = params

    # set up network for simulation with GWs and Smart Meters
    #   NOTE: this takes care of the network setup and stays the same in all scenarios
    network = create_network( num_gws, dist_num_sms, max_num_sm_at_gw)

    # determine a fixed time offset for the starting time
    start_timepoint = datetime.fromisoformat("2024-01-01")
    simu_runtime = 1440

    anon_data_dir = "./anonymized_data/"

    ################################
    ###### DECENTRAL SCENARIO ######
    
    # create environment for the simulation
    decent_env = simpy.Environment()
    decent_zanon_env = set_zanon_params(decent_env, delta_t, zeta)

    # once everything is created the simulation can be started that will then model an ongoing process with regular measurements and communication between network components
    decent_env.process(decent_zanon(decent_env, decent_zanon_env, network, start_timepoint))
    # after completed setup run decentralized simulation
    decent_env.run(until = simu_runtime)
    print("__SIMULATION END__")

    # save public log as csv
    public_log = pd.DataFrame(network.ce.pub_records.log)
    column_list = public_log.columns
    # add message count at beginning of log file
    idx = generate_log_index(decent_zanon_env, column_list)
    public_log.columns = idx
    public_log_name = "decent_w_comm_zanon_z_" + str(decent_zanon_env.z) + "_dt_" + str(decent_zanon_env.delta_t.seconds) + "_nGw_" + str(network.n_gws) + "_distSm_" + dist_num_sms + "_maxSm_" + str(max_num_sm_at_gw) + "_seed_" + str(seed) + ".csv"
    public_log.to_csv((anon_data_dir + public_log_name), sep = ',', index=False)

    # save complete simulation log with all tuples that occurred for analysis purposes
    simu_log_name = "simu_log_" + public_log_name
    network.ce.simu_log.log.to_csv((anon_data_dir + simu_log_name), sep = ',', index=False)
    print("Decentral MSG CNT: ", decent_zanon_env.msg_cnt)
    
    ##############################
    ###### CENTRAL SCENARIO ######
    # create environment for the simulation
    cent_env = simpy.Environment()
    cent_zanon_env = set_zanon_params(cent_env, delta_t, zeta)
    # clear all logs from earlier results
    clear_network_logs(network)
    cent_env.process(cent_zanon(cent_env, cent_zanon_env, network, start_timepoint))

    # after completed setup run centralized simulation
    cent_env.run(until = simu_runtime)

    
    # save public log as csv
    public_log = pd.DataFrame(network.ce.pub_records.log)
    column_list = public_log.columns
    # add message count at beginning of log file
    idx = generate_log_index(cent_zanon_env, column_list)
    public_log.columns = idx
    public_log_name = "cent_w_comm_zanon_z_" + str(cent_zanon_env.z) + "_dt_" + str(cent_zanon_env.delta_t.seconds) + "_nGw_" + str(network.n_gws) + "_distSm_" + dist_num_sms + "_maxSm_" + str(max_num_sm_at_gw) + "_seed_" + str(seed) + ".csv"
    public_log.to_csv((anon_data_dir + public_log_name), sep = ',', index=False)

    # save complete simulation log with all tuples that occurred for analysis purposes
    simu_log_name = "simu_log_" + public_log_name
    network.ce.simu_log.log.to_csv((anon_data_dir + simu_log_name), sep = ',', index=False)
    print("Central MSG CNT: ", cent_zanon_env.msg_cnt)

    ###############################################
    ###### FULLY DECENTRAL SCENARIO WO COORD ######
    
    # create environment for the simulation
    ful_dec_env = simpy.Environment()
    ful_dec_zanon_env = set_zanon_params(ful_dec_env, delta_t, zeta)
    # clear all logs from earlier results
    clear_network_logs(network)
    ful_dec_env.process(fully_decent_zanon(ful_dec_env, ful_dec_zanon_env, network, start_timepoint))

    # after completed setup run centralized simulation
    ful_dec_env.run(until = simu_runtime)

    # save public log as csv
    public_log = pd.DataFrame(network.ce.pub_records.log)
    column_list = public_log.columns
    # add message count at beginning of log file
    idx = generate_log_index(ful_dec_zanon_env, column_list)

    public_log.columns = idx
    public_log_name = "fully_decent_wo_coord_zanon_z_" + str(ful_dec_zanon_env.z) + "_dt_" + str(ful_dec_zanon_env.delta_t.seconds) + "_nGw_" + str(network.n_gws) + "_distSm_" + dist_num_sms + "_maxSm_" + str(max_num_sm_at_gw) + "_seed_" + str(seed) + ".csv"
    public_log.to_csv((anon_data_dir + public_log_name), sep = ',', index=False)

    # save complete simulation log with all tuples that occurred for analysis purposes
    simu_log_name = "simu_log_" + public_log_name
    network.ce.simu_log.log.to_csv((anon_data_dir + simu_log_name), sep = ',', index=False)
    print("Fully Decentral MSG CNT: ", ful_dec_zanon_env.msg_cnt)
    


if __name__ == "__main__":
    main()

