import pandas as pd

input_path = "./data_analysis/simulation_stats/"
output_path = "./data_analysis/simulation_stats/"

scenario = "deZent"
l_n_gw = [5, 75, 150]
l_styles = ["1p_household", "2p_household", "3p_household", "4p_household", "store", "restaurant", "workshop", "hair_dresser", "bakery"]

# load message counting stats
df_smtype_pub = pd.read_csv((input_path + "smtype_pub_ratio_analysis.csv"), sep = ",", header=0)
# analyze data only for deZent
df_smtype_pub = df_smtype_pub.loc[df_smtype_pub["scenario"] == scenario]
# extract rlevant columns
df_smtype_pub = df_smtype_pub.loc[:, ["z", "pub_ratio", "type", "n_gw"]]

for gw in l_n_gw:
    # extract data per number of GWs
    tmp_df = df_smtype_pub.loc[df_smtype_pub["n_gw"] == gw]
    tmp_df = tmp_df.loc[:, ["z", "pub_ratio", "type"]]
    tmp_df.to_csv((output_path + "smtype_pub_ratio_ngw" + str(gw) + ".dat"), sep = " ", index = False)

    # average publication ratio
    tmp_df_avg = tmp_df.groupby(["z", "type"]).mean().reset_index().rename(columns={0:'avg_pub_ratio'})
    tmp_df_avg.to_csv((output_path + "avg_smtype_pub_ratio_ngw" + str(gw) + ".dat"), sep = " ", index = False)



