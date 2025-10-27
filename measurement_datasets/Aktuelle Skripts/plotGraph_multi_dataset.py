import pandas as pd
import matplotlib.pyplot as plt

# ["filename", dataset_offset_in_s]
files = [
    ["Test_data_cleaned", 0],
    ["Test2_data_cleaned", 0]
]

styles = ["-", ":", "-.", "--"]

#### preperations, no need to change this #######
dataframes = []
for file in files:
    df = pd.read_csv(file[0]+".csv")
    print(df)
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S.%f")
    start_time = df["time"].iloc[0]
    df["runtime"] = (df["time"] - start_time + pd.to_timedelta(file[1], unit='s')).dt.total_seconds()
    df.attrs["name"] = str(file[0]).removesuffix('_data_cleaned')
    dataframes.append(df)
#################################################



##### prepare value from imported csv for displaying in graph ##############
for df in dataframes:
    print("calculating Values")
    df["C_CH0"] = (df["C_CH0"].abs())*1E6 #convert A to µA
    df["C_CH1"] = (df["C_CH1"].abs())*1E6 #convert A to µA
    df["C_CH2"] = (df["C_CH2"].abs())*1E6 #convert A to µA
    df["extractionVoltage"] = df["V_CH1"] - df["V_CH0"]
    df["collectorVoltage"] = df["V_CH2"] - df["V_CH0"]
############################################################################

##### prepare graph window #################################################
#fig is the object that creates the window/graph
#ax1 is the main coordinate system
#figsize sets the size of the window in inches
fig, ax1 = plt.subplots(figsize=(16, 8))
fig.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.1) #adjust the borders of the graph inside the window
############################################################################

##### Voltage Plot #########################
ax1.set_xlabel("Runtime [s]")
ax1.set_ylabel("Voltage [V]")
style_counter = 0
for df in dataframes:
    ax1.plot(df["runtime"], df["V_CH2"], label=str(df.attrs["name"])+": V_CH2", color="tab:pink", linestyle=styles[style_counter])
    ax1.plot(df["runtime"], df["extractionVoltage"], label=str(df.attrs["name"])+": Extraction Voltage", color="tab:orange", linestyle=styles[style_counter])
    #ax1.plot(df["runtime"], df["V_CH0"], label="V_CH0", color="tab:blue")
    #ax1.plot(df["runtime"], df["V_CH1"], label="V_CH1", color="tab:blue")
    #ax1.plot(df["runtime"], df["collectorVoltage"], label=str(df.attrs["name"])+": Collector Voltage", color="tab:pink", linestyle=styles[style_counter])
    style_counter = style_counter+1
ax1.tick_params(axis="y")
ax1.set_ylim(0, 2500) #voltage range in V




##### Current Plot ###########
ax2 = ax1.twinx()
ax2.set_ylabel("Current [µA]")
ax2.tick_params(axis="y")
ax2.set_ylim(0, 500) #current range in µA #comment out for auto scaling
style_counter = 0
for df in dataframes:
    ax2.plot(df["runtime"], df["C_CH0"], label=str(df.attrs["name"])+": C_CH0", color="tab:blue", linestyle=styles[style_counter])
    ax2.plot(df["runtime"], df["C_CH1"], label=str(df.attrs["name"])+": C_CH1", color="tab:grey", linestyle=styles[style_counter])
    ax2.plot(df["runtime"], df["C_CH2"], label=str(df.attrs["name"])+": C_CH2", color="tab:purple", linestyle=styles[style_counter])
    style_counter = style_counter+1




##### Temperature Plot #############
ax3 = ax1.twinx()
ax3.set_ylabel("Temperature [°C]")
ax3.tick_params(axis="y")
ax3.set_ylim(0, 250) #current range in °C #comment out for auto scaling
style_counter = 0
for df in dataframes:
    ax3.plot(df["runtime"], df["temperature"], label=str(df.attrs["name"])+": silicon temperature", color="tab:red", linestyle=styles[style_counter])
    style_counter = style_counter+1




##### Pressure Plot #############
ax4 = ax1.twinx()
ax4.set_ylabel("Pressure [hPa]")
ax4.tick_params(axis="y")
ax4.set_yscale('log')
#ax4.set_ylim(0, 1E-10) #pressure range
style_counter = 0
for df in dataframes:
    ax4.plot(df["runtime"], df["pressure"], label=str(df.attrs["name"])+": pressure", color="tab:cyan", linestyle=styles[style_counter])
    style_counter = style_counter+1




####### PPM Plot #############
### For Plotting Molecule Concentration measured by the mass spectrometer
##ax5 = ax1.twinx()
##ax5.set_ylabel("Molecule detected [ppm]")
##ax5.tick_params(axis="y")
##ax4.set_yscale('log')
###ax5.set_ylim(0, 1E-10)
##style_counter = 0
##for df in dataframes:
##    ax5.plot(df["runtime"], df["2_amu_(Hydrogen)"], label=str(df.attrs["name"])+": 2_amu_(Hydrogen)", color="tab:pink", linestyle=styles[style_counter])
##    style_counter = style_counter+1






##### Dont change after this ######################################################################################################

##### handle axis positions #######
offset_pos = 0
for ax in fig.axes:
    if offset_pos != 0:
        ax.spines.right.set_position(("axes", offset_pos))
        offset_pos = offset_pos + 0.08
    else:
        offset_pos = 1.0
    


##### draw legend ##############
handles, labels = [], []
for ax in fig.axes:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)

ax1.legend(handles, labels, loc="upper right")

title_name = ""
for file in files:
    title_name = title_name + file[0].removesuffix('_data_cleaned') + " "
    
plt.title(title_name)
plt.tight_layout()
plt.show()





