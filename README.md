# PhishingEmailDetection

# How to setup data?

**Works ONLY on Mac**

- Install One Drive with SMU id
- Keep a link to CapstoneA One Drive Shared Drive on your home dir
- On your Mac Finder, select Data directory under CapstoneA directory and choose "Choose a local copy" option
- Thats all

## How do I run?

- Create a Python notebook
- include the following two lines 
 ``` 
  # Import data and models
  %run CapsoneData.ipynb
  %run PhishingModels.ipynb
 ```
 
 To get the entire dataset as dataframe, just run this:
 
 ```
 email_df = get_capstonedata_as_df()
 
 # This will run faiss model
 faiss = run_faiss()
 
 ```
 
 ### Train and Test data
 The dataframe contains a column `istestdata`, which is 1 for test data and 0 for train data. 
 
 _Push to Origin only after models runs and version if there are significant differences_
