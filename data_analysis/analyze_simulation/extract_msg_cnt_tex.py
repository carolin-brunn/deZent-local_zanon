import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})


input_path = "./data_analysis/simulation_stats/"
output_path = "./data_analysis/simulation_stats/"

l_sce_label = ["centralized", "deZent", "fully_decentralized"]

# load message counting stats
df_cnt = pd.read_csv((input_path + "msg_cnt_analysis.csv"), sep = ",", header=0)


### GW - CE ###
# extract specific count data
gwce_cnt = df_cnt.loc[:, ["n_gw", "msg_cnt_gw_ce", "z", "scenario"]]

# average message count across runs, all z, all runs included
gwce_avg = gwce_cnt.groupby(["n_gw", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
gwce_avg.to_csv((output_path + "avg_msg_cnt_gw_ce.dat"), sep = " ", index = False)

for sce in l_sce_label:
    # msg count per scenario
    tmp_gwce = gwce_cnt.loc[gwce_cnt["scenario"] == sce]
    tmp_gwce.to_csv((output_path + "msg_cnt_gw_ce_" + sce + ".dat"), sep = " ", index = False)

    # average message count across runs
    tmp_gwce_avg = tmp_gwce.groupby(["n_gw", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
    tmp_gwce_avg.to_csv((output_path + "avg_msg_cnt_gw_ce_" + sce + ".dat"), sep = " ", index = False)

    # get mean value per z
    tmp_gwce_z = tmp_gwce.groupby(["n_gw", "z", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
    print(tmp_gwce_z.head())
    tmp_gwce_z.to_csv((output_path + "msg_cnt_gw_ce_" + sce + "avg_per_z.dat"), sep = " ", index = False)


### GW - GW ###
# extract specific count data
gwgw_cnt = df_cnt.loc[:, ["n_gw", "msg_cnt_gw_gw", "z", "scenario"]]

# average message count across runs, all z, all runs included
gwgw_avg = gwgw_cnt.groupby(["n_gw", "scenario"]).mean().reset_index().rename(columns={0:'avg_msg_count'})
gwgw_avg.to_csv((output_path + "avg_msg_cnt_gw_gw.dat"), sep = " ", index = False)

for sce in l_sce_label:

    tmp_gwgw = gwgw_cnt.loc[gwgw_cnt["scenario"] == sce]
    tmp_gwgw.to_csv((output_path + "msg_cnt_gw_gw_" + sce + ".dat"), sep = " ", index = False)

"""
###### Seaborn PGF PLOTS #####
## GW - CE ##
fig, ax =  plt.subplots()

ax = sns.barplot(data = df_cnt, x = "n_gw", y = "msg_cnt_gw_ce", hue = "scenario", errorbar="sd")
ax.set_xlabel("Number of GWs")
ax.set_ylabel("Number of messages (GW-CE)")
ax.set_title("")
#fig.tight_layout()
fig.set_size_inches(w=2.38, h=1.2)
plt.savefig('sns_msg_cnt_gw_ce_bar_3sce.pgf')

## GW - GW
fig, ax =  plt.subplots()

ax = sns.barplot(data = df_cnt, x = "n_gw", y = "msg_cnt_gw_gw", hue = "scenario", errorbar="sd")
ax.set_xlabel("Number of GWs")
ax.set_ylabel("Number of messages (GW-GW/SN)")
ax.set_title("")
#fig.tight_layout()
fig.set_size_inches(w=2.38, h=1.2)
plt.savefig('sns_msg_cnt_gw_gw_bar_3sce.pgf')
"""