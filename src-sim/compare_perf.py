import pandas as pd
from datetime import datetime
import shutil
import sys
import os

#Load Email File

email_csv = sys.argv[1]
bname = os.path.basename(email_csv)
st_time =datetime.now().microsecond
emails_df = pd.read_csv(email_csv, memory_map=True)
end_time =datetime.now().microsecond
time_taken = end_time - st_time

print(f"Time to load csv file from scratch: {time_taken:,} ms")


#Copy file to /dev/shm

shutil.copy(email_csv, f"/dev/shm/{bname}")

st_time =datetime.now().microsecond
emails_df = pd.read_csv(f"/dev/shm/{bname}", memory_map=True )
end_time =datetime.now().microsecond
time_taken = end_time - st_time

print(f"Time to load csv file from /dev/shm: {time_taken:,} ms")
