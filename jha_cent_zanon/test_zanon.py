import zanon
import pandas as pd
import datetime

# Exception: filename_in = "cent_w_comm_zanon_z_" + str(1) + "_dt_7260_nGw_5_distSm_normal_maxSm_100_seed_1" #+ str(seed)

def preprocess_log_data_for_zanon(input_path, input_file):
    df_in = pd.read_csv( (input_path + input_file), sep =",")
    df_in = df_in#.iloc[0:2000]
    print(df_in.head())

    # convert timestamps to unix timestamps
    l_time = [(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")).timestamp() for t in df_in["time"] ]
    print(l_time[0:5])
    df_in.loc[:, "time"] = l_time
    print(df_in.head())

    # store data used for Jha zanon 
    z_data = pd.DataFrame({"time": df_in["time"], "ID": df_in["ID"], "value": df_in["value"]})
    z_data_file = ( "z_data_" + input_file)
    z_data.to_csv( (z_data_path + z_data_file), sep=",", index = False, header=False)
    print(z_data_file)
    print(z_data.head())
    return z_data_file


####################
####################
input_path = "./data/log_data/"
z_data_path = "./data/log_data/"
anon_path = "./data/anonymized_data/jha_impl/"

#z_val = 100

prefix = "simu_log_"
scenario_params = "_dt_7260_nGw_150_distSm_normal_maxSm_20"
dez_scenario = "cent_w_comm_zanon_z_"

for seed in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    for z_val in [1, 5, 10, 25, 50, 100]:
        

        scenario = dez_scenario + str(z_val) + scenario_params + "_seed_" + str(seed)
        input_filename = prefix + scenario 
        input_file = input_filename + ".csv"

        z_data_file = preprocess_log_data_for_zanon(input_path, input_file)

        #df_in = pd.read_csv( (input_path + input_file), sep =",")
        #df_in = df_in#.iloc[0:2000]
        #print(df_in.head())

        # convert timestamps to unix timestamps
        #l_time = [(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")).timestamp() for t in df_in["time"] ]
        #print(l_time[0:5])
        #df_in.loc[:, "time"] = l_time
        #print(df_in.head())

        # store data used for orig zanon 
        #z_data = pd.DataFrame({"time": df_in["time"], "ID": df_in["ID"], "value": df_in["value"]})
        #z_data_filename_in = ( "z_data_" + input_file)
        #z_data.to_csv( (z_data_path + z_data_filename_in), sep=",", index = False, header=False)
        #print(z_data_filename_in)
        #print(z_data.head())


        deltat = 7260 #in seconds
        
        
        anon_z_data_filename = ( "z_data_" + input_filename)
        #anon_z_data_file = (anon_path + z_data_file)

        z = zanon.zanon(deltat, z_val, anon_path, anon_z_data_filename)
        print("zanon files")
        print(z_data_file + "\n")
        for line in open( (z_data_path + z_data_file), 'r'):
            t,u,a = line.split(",")
            z.anonymize((t,u,a))
        z.endFiles()
        z.duration()



