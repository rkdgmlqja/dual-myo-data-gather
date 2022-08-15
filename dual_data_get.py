# Simplistic data recording
import time
import multiprocessing
import numpy as np
import pandas as pd
from pyomyo import Myo, emg_mode
from pyomyo1 import Myo1, emg_mode1

b_q = multiprocessing.Queue()
m = Myo(tty='COM5',mode=emg_mode.PREPROCESSED)
m.connect()

def data_worker(q1):
   collect = True

   # ------------ Myo Setup ---------------
   def add_to_queue(emg, movement):
      q1.put(emg)

   m.add_emg_handler(add_to_queue)

   def print_battery(bat):
      print("Battery level:", bat)

   m.add_battery_handler(print_battery)

    # Its go time
   m.set_leds([0, 128, 0], [0, 128, 0])
   # Vibrate to know we connected okay
   m.vibrate(3)

   print("Data Worker started to collect")
   # Start collecing data.

b_p = multiprocessing.Process(target=data_worker, args=(b_q,))
b_p.start()

time.sleep(5)

#second myo
q = multiprocessing.Queue()
m1 = Myo1(tty='COM6',mode=emg_mode1.PREPROCESSED)
m1.connect()



def data_worker1(q):
   collect = True
# ------------ Myo Setup ---------------
   def add_to_queue1(emg, movement):
      q.put(emg)


   m1.add_emg_handler(add_to_queue1)

   def print_battery(bat):
      print("Battery level:", bat)

   m1.add_battery_handler(print_battery)

    # Its go time
   m1.set_leds([128, 0, 0], [128, 0, 0])
   # Vibrate to know we connected okay
   m1.vibrate(3)

   print("Data Worker started to collect")
   # Start collecing data.

p = multiprocessing.Process(target=data_worker1, args=(q,))
p.start()

start_time = time.time()

#data
myo_blue_data = []
myo_raw_data = []

# -------- Main Program Loop -----------

try:
	print("Waiting for both to connect.")
	# Wait to get data from both Myos to know they are connected
    
	q.get() # Block until q has an item

 	# Myo raw usually takes longer, wait for that first.
	b_q.get()
	print("Both should be connected")

	# Empty both queues once
	while ( (not b_q.empty()) or (not q.empty()) ):
		if ((not q.empty())): q.get()
		if (not b_q.empty()): b_q.get()

	# Both devices should now be reporting data, and be empty 

	while True:
		# Get data from the first Myo
		while not(b_q.empty()):
			# Get the new data from the Myo queue
			emg = list(b_q.get())
			#print('Myo 1', emg)
			myo_blue_data.append(emg)

		# Get data from the second Myo
		while not(q.empty()):
			# Get the new data from the Myo queue
			emg = list(q.get())
			#print('Myo 2', emg)
			myo_raw_data.append(emg)

except KeyboardInterrupt:
	end_time = time.time()
	print(f"Quitting, after {end_time} seconds.")
	m.set_leds([255, 0, 64], [255, 0, 64])
	m.disconnect()

	print('Saving')
	print(f"Blue Myo {len(myo_blue_data)}")
	print(f"Raw Myo {len(myo_raw_data)}")

	myo1_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7", "Channel_8"]
	myo2_cols = ["Channel_9", "Channel_10", "Channel_11", "Channel_12", "Channel_13", "Channel_14", "Channel_15", "Channel_16"]

	myo1_df = pd.DataFrame(myo_blue_data, columns=myo1_cols)
	myo2_df = pd.DataFrame(myo_raw_data, columns=myo2_cols)

	df = myo1_df.join(myo2_df)
	df.to_csv("dual_emg.csv", index=False)
	print("CSV Saved", "dual_emg.csv")

#----------------------------------------------------

   