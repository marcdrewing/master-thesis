import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import numpy as np

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
fig, (ax1, ax_text) = plt.subplots(
    2, 1, figsize=(16, 8), gridspec_kw={"height_ratios": [4, 1]}
)
fig.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.1) #adjust the borders of the graph inside the window

##### Voltage Plot #########################
ax1.tick_params(axis="y")
ax1.set_ylim(0, 2500) #voltage range in V
ax1.set_xlabel("Runtime [s]")
ax1.set_ylabel("Voltage [V]")
ax1.plot(df["runtime"], df["extractionVoltage"], label="Extraction Voltage", color="tab:orange")
#ax1.plot(df["runtime"], df["collectorVoltage"], label="Collector Voltage", color="tab:pink")
#ax1.plot(df["runtime"], df["V_CH0"], label="V_CH0", color="tab:blue")
#ax1.plot(df["runtime"], df["V_CH1"], label="V_CH1", color="tab:blue")
ax1.plot(df["runtime"], df["V_CH2"], label="V_CH2", color="tab:pink")



##### Current Plot ###########
ax2 = ax1.twinx()
ax2.tick_params(axis="y")
ax2.set_ylim(0, 500) #current range in µA #comment out for auto scaling
ax2.set_ylabel("Current [µA]")
ax2.plot(df["runtime"], df["C_CH0"], label="C_CH0", color="tab:blue")
ax2.plot(df["runtime"], df["C_CH1"], label="C_CH1", color="tab:grey")
ax2.plot(df["runtime"], df["C_CH2"], label="C_CH2", color="tab:purple")




##### Temperature Plot #############
ax3 = ax1.twinx()
ax3.tick_params(axis="y")
ax3.set_ylim(0, 250) #current range in °C #comment out for auto scaling
ax3.set_ylabel("Temperature [°C]")
ax3.plot(df["runtime"], df["temperature"], label="silicon temperature", color="tab:red")




##### Pressure Plot #############
ax4 = ax1.twinx()
ax4.tick_params(axis="y")
ax4.set_yscale('log')
#ax4.set_ylim(0, 1E-10) #pressure range
ax4.set_ylabel("Pressure [mBar]")
ax4.plot(df["runtime"], df["pressure"], label="pressure", color="tab:cyan")




##### PPM Plot #############
# For Plotting Molecule Concentration measured by the mass spectrometer
##ax5 = ax1.twinx()
##ax5.tick_params(axis="y")
##ax5.set_ylim(0, 1E-10)
##ax5.set_ylabel("Molecule detected [ppm]")
##ax5.plot(df["runtime"], df["2_amu_(Hydrogen)"], label="2_amu_(Hydrogen)", color="tab:pink")






##### Dont change after this ######################################################################################################

##### handle axis positions #######
offset_pos = 0
for ax in fig.axes:
    print(ax)
    if ax == ax_text:
        continue
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

##### timestamp tracker ###########################
vline = ax1.axvline(0, color="black", lw=2)
lines = []
for ax in fig.axes:
    for line in ax.get_lines():
        if not line.get_label().startswith("_child"):
            lines.append(line)
# --- Eingabefeld für Sekunden ---
axbox1 = plt.axes([0.15, 0.02, 0.3, 0.05])
text_box_seconds = TextBox(axbox1, "Zeit (s): ", initial="0")

# --- Eingabefeld für Zeitstempel ---
axbox2 = plt.axes([0.55, 0.02, 0.4, 0.05])
text_box_timestamp = TextBox(axbox2, "Zeitstempel: ", initial=str(df["time"].iloc[0]))

# --- Feld für Werteanzeige ---
ax_text.axis("off")
value_display = ax_text.text(0.05, 0.5, "", fontsize=12, va="center")

def get_values_from_lines(t):
    text_lines = [f"t = {t:.3f} s"]
    for line in lines:
        xdata = np.array(line.get_xdata())  # sicherstellen, dass NumPy-Array
        ydata = np.array(line.get_ydata())
        label = line.get_label()
        if len(xdata) == 0:
            continue
        idx = (np.abs(xdata - t)).argmin()   # nächster Index
        value = ydata[idx]
        text_lines.append(f"{label}: {value:.4g}")
    return "\n".join(text_lines)

def update_display(t):
    value_display.set_text(get_values_from_lines(t))
    fig.canvas.draw_idle()

# --- deine submit-Funktion erweitern ---
def submit(text):
    try:
        t = float(text)  # Eingabe in Sekunden
        vline.set_xdata([t, t])  # Cursor verschieben
        update_display(t)        # Werte anzeigen
    except ValueError:
        print("Ungültige Eingabe")

def submit_seconds(text):
    try:
        t = float(text)
        vline.set_xdata([t, t])
        fig.canvas.draw_idle()
        # Sekunden → Timestamp
        ts = start_time + pd.to_timedelta(t, unit="s")
        text_box_timestamp.set_val(str(ts))
        # Werteanzeige aktualisieren
        update_display(t)
    except ValueError:
        print("Ungültige Eingabe für Sekunden")

def submit_timestamp(text):
    try:
        ts = pd.to_datetime(text, format="%Y-%m-%d %H:%M:%S.%f")
        seconds = (ts - start_time).total_seconds()
        vline.set_xdata([seconds, seconds])
        fig.canvas.draw_idle()
        # Timestamp → Sekunden
        text_box_seconds.set_val(str(seconds))
        # Werteanzeige aktualisieren
        update_display(seconds)
    except Exception as e:
        print("Ungültiger Zeitstempel:", e)


# Callbacks verknüpfen
text_box_seconds.on_submit(submit_seconds)
text_box_timestamp.on_submit(submit_timestamp)


title_name = filename.removesuffix('_data_cleaned')
plt.title(title_name)
#plt.tight_layout()
plt.show()





