import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import numpy as np
from scipy.signal import find_peaks


filename = "250826_EC33_Messung2_data_cleaned"

df = pd.read_csv(filename+".csv")
print(df)

#zeitformat für pandas lesbar machen
df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S.%f")
start_time = df["time"].iloc[0]
df["runtime"] = (df["time"] - start_time).dt.total_seconds()

#daten interpolieren
df = df.set_index("time")
full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq="100ms")
df = df.reindex(full_index)
for column in df.columns:
    if column != "time":
        df[column] = df[column].interpolate(method="time")
df = df.reset_index().rename(columns={"index": "time"})
df = df.reset_index(drop=True)

print(df)


df["C_CH0"] = (df["C_CH0"].abs())*1E6 #convert A to µA
df["C_CH1"] = (df["C_CH1"].abs())*1E6 #convert A to µA
df["C_CH2"] = (df["C_CH2"].abs())*1E6 #convert A to µA
df["extractionVoltage"] = df["V_CH1"] - df["V_CH0"]


df["voltagePeak"] = 0
df["currentPeak"] = 0
df["pressurePeak"] = 0

#######################################   detektion von peaks  ##########################
y = df["C_CH0"].to_numpy()
fs = 10 #aufnahme frequenz
median_baseline = pd.Series(y).rolling(window=int(30*fs), center=True, min_periods=1).median() #median aus einem fenster von 300 Werten ermitteln
df["baseline_current"] = median_baseline.rolling(window=(1*fs), center=True, min_periods=1).mean() #weiter glätten durch den durchschnitt aus einem Fenster von 10 Werten

df["onlyPeaks"] = df["baseline_current"] - df["C_CH0"] #erfasse nur negative Peaks
#df["onlyPeaks"] = abs(df["C_CH0"] - df["baseline_current"])

df["currentPeak"] = pd.Series(dtype=float)

#als erstes finden aller Peaks
peaks, props = find_peaks(
    df["onlyPeaks"].to_numpy(),
    height=5,
    prominence=5,    # Mindesthöhe über Umgebung
    #width=3,          # Mindestbreite
)
df.loc[peaks, "currentPeak"] = 1

#dann finden aller kleineren Plateaus
peaks, props = find_peaks(
    df["onlyPeaks"].to_numpy(),
    height=5,
    #prominence=5,    # Mindesthöhe über Umgebung
    #width=3,          # Mindestbreite
    plateau_size=(2, None)
)
df.loc[peaks, "currentPeak"] = 1
for plateauCounter in range(0, len(props["left_edges"])):
    df.loc[props["left_edges"][plateauCounter]:props["right_edges"][plateauCounter], "currentPeak"] = 1


#dieses mal nur die großen Peaks um Plateaus zu finden
roundedValues = np.floor(df["onlyPeaks"].to_numpy() / 100) * 100 #runden anpassen je nach größeren Ausschlägen
peaks, props = find_peaks(
    roundedValues,
    height=5,
    prominence=10,    # Mindesthöhe über Umgebung
    #width=3,          # Mindestbreite
    plateau_size=(1, None)
)
for plateauCounter in range(0, len(props["left_edges"])):
    df.loc[props["left_edges"][plateauCounter]:props["right_edges"][plateauCounter], "currentPeak"] = 1   



markedSpots = df["currentPeak"].notna() #alle Stellen auswählen die als peak markiert wurden
df.loc[markedSpots, "currentPeak"] = abs(df.loc[markedSpots, "C_CH0"] - df.loc[markedSpots, "baseline_current"]) #höhe der Peak Trainingsdaten abhängig vom tatsächlichen Peak
#df["currentPeak"] = df["currentPeak"] / 2 + 10 #Verändern der Peak Höhe zum stärkeren Berücksichtigen kleinerer Peaks
df["currentPeak"] = df["currentPeak"].fillna(0) #NaN durch 0 ersetzen
print(df["currentPeak"])

filename = filename.removesuffix("_data_cleaned")
df.to_csv(filename+"_marked_peaks.csv", float_format='%.16f', index=False)



################### GRAPH ######################
#fig, (ax1, ax_text) = plt.subplots(
#    2, 1, figsize=(8, 6), gridspec_kw={"height_ratios": [4, 1]}
#)
fig, (ax1) = plt.subplots(figsize=(10, 5))

fig.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.1) #adjust the borders of the graph inside the windo

##### Voltage Plot #########################
#ax1.tick_params(axis="y")
#ax1.set_ylim(0, 2500) #voltage range in V
#ax1.set_xlabel("Runtime [s]")
#ax1.set_ylabel("Voltage [V]")
#ax1.plot(df["runtime"], df["extractionVoltage"], label="Extraction Voltage", color="tab:orange")
#ax1.plot(df["runtime"], df["collectorVoltage"], label="Collector Voltage", color="tab:pink")
#ax1.plot(df["runtime"], df["V_CH0"], label="V_CH0", color="tab:blue")
#ax1.plot(df["runtime"], df["V_CH1"], label="V_CH1", color="tab:blue")
#ax1.plot(df["runtime"], df["V_CH2"], label="V_CH2", color="tab:pink")



##### Current Plot ###########
ax2 = ax1.twinx()
ax2.tick_params(axis="y")
ax2.set_ylim(0, 800) #current range in µA #comment out for auto scaling
ax2.set_ylabel("Current [µA]")
ax2.plot(df["runtime"], df["C_CH0"], label="C_CH0", color="tab:blue")
#ax2.plot(df["runtime"], df["C_CH1"], label="C_CH1", color="tab:grey")
#ax2.plot(df["runtime"], df["C_CH2"], label="C_CH2", color="tab:purple")
ax2.plot(df["runtime"], df["currentPeak"], label="current peak detected", color="black")
#ax2.plot(df["runtime"], df["baseline_current"], label="baseline_current", color="black")




##### Temperature Plot #############
#ax3 = ax1.twinx()
#ax3.tick_params(axis="y")
#ax3.set_ylim(0, 250) #current range in °C #comment out for auto scaling
#ax3.set_ylabel("Temperature [°C]")
#ax3.plot(df["runtime"], df["temperature"], label="silicon temperature", color="tab:red")




##### Pressure Plot #############
#ax4 = ax1.twinx()
#ax4.tick_params(axis="y")
#ax4.set_yscale('log')
#ax4.set_ylim(0, 1E-10) #pressure range
#ax4.set_ylabel("Pressure [mBar]")
#ax4.plot(df["runtime"], df["pressure"], label="pressure", color="tab:cyan")


offset_pos = 0
for ax in fig.axes:
    print(ax)
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

title_name = filename.removesuffix('_data_cleaned')
plt.title(title_name)
#plt.tight_layout()
plt.show()
