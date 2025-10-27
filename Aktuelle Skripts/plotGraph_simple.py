import pandas as pd
import matplotlib.pyplot as plt

filename = "Test_data_cleaned"


#### preperations, no need to change this #######
df = pd.read_csv(filename+".csv")
print(df)
df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S.%f")
start_time = df["time"].iloc[0]
df["runtime"] = (df["time"] - start_time).dt.total_seconds()



# prepare value from imported csv for displaying in graph
print("calculating Values")
df["C_CH0"] = (df["C_CH0"].abs())*1E6 #convert A to µA
df["C_CH1"] = (df["C_CH1"].abs())*1E6 #convert A to µA
df["C_CH2"] = (df["C_CH2"].abs())*1E6 #convert A to µA
df["extractionVoltage"] = df["V_CH1"] - df["V_CH0"]
df["collectorVoltage"] = df["V_CH2"] - df["V_CH0"]

print(df["C_CH0"])
print(df["extractionVoltage"])



#fig is the object that creates the window/graph
#ax1 is the main coordinate system
#figsize sets the size of the window in inches
fig, ax1 = plt.subplots(figsize=(16, 8))
fig.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.1) #adjust the borders of the graph inside the window

##### Voltage Plot #########################
ax1.set_xlabel("Runtime [s]")
ax1.set_ylabel("Voltage [V]")
#ax1.plot(df["runtime"], df["V_CH0"], label="V_CH0", color="tab:blue", linestyle="-")
#ax1.plot(df["runtime"], df["V_CH1"], label="V_CH1", color="tab:blue", linestyle="--")
#ax1.plot(df["runtime"], df["V_CH2"], label="V_CH2", color="tab:blue", linestyle=":")
ax1.plot(df["runtime"], df["extractionVoltage"], label="Extraction Voltage", color="tab:orange")
ax1.plot(df["runtime"], df["collectorVoltage"], label="Collector Voltage", color="tab:pink")
ax1.tick_params(axis="y")
ax1.set_ylim(0, 2500) #voltage range in V


##### Current Plot ###########
ax2 = ax1.twinx()
ax2.set_ylabel("Current [µA]")
ax2.plot(df["runtime"], df["C_CH0"], label="C_CH0", color="tab:blue")
#ax2.plot(df["runtime"], df["C_CH0"], label="C_CH0", color="tab:red", linestyle="-")
#ax2.plot(df["runtime"], df["C_CH1"], label="C_CH1", color="tab:red", linestyle="--")
ax2.plot(df["runtime"], df["C_CH2"], label="C_CH2", color="tab:purple")
ax2.tick_params(axis="y")
ax2.set_ylim(0, 500) #current range in µA #comment out for auto scaling



##### Temperature Plot #############
ax3 = ax1.twinx()
ax3.set_ylabel("Temperature [°C]")
ax3.plot(df["runtime"], df["temperature"], label="silicon temperature", color="tab:red")
ax3.tick_params(axis="y")
ax3.set_ylim(0, 250) #current range in °C #comment out for auto scaling



##### Pressure Plot #############
ax4 = ax1.twinx()
ax4.set_ylabel("Pressure [mBar]")
ax4.plot(df["runtime"], df["pressure"], label="pressure", color="tab:cyan")
ax4.tick_params(axis="y")
ax4.set_yscale('log')
#ax4.set_ylim(0, 1E-10) #pressure range



##### PPM Plot #############
# For Plotting Molecule Concentration measured by the mass spectrometer
##ax5 = ax1.twinx()
##ax5.set_ylabel("Molecule detected [ppm]")
##ax5.plot(df["runtime"], df["2_amu_(Hydrogen)"], label="2_amu_(Hydrogen)", color="tab:pink")
##ax5.tick_params(axis="y")
##ax5.set_ylim(0, 1E-10)





##### Dont change after this ######################################################################################################

##### handle axis positions #######
offset_pos = 0
for ax in fig.axes:
    if offset_pos != 0:
        ax.spines.right.set_position(("axes", offset_pos))
        offset_pos = offset_pos + 0.1
    else:
        offset_pos = 1.0
    


##### draw legend ##############
handles, labels = [], []
for ax in fig.axes:
    h, l = ax.get_legend_handles_labels()
    handles.extend(h)
    labels.extend(l)

ax1.legend(handles, labels, loc="upper right")


title_name = filename.removesuffix('_data_cleaned')
plt.title(title_name)
plt.tight_layout()
plt.show()





