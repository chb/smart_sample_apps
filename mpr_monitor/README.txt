04 June 2012

General Code Updates
1. Created a new directory, static/, for the drugClass data file and the logistic regression coefficients file, genLinearModel.txt. These really shouldn?t be in ?Media?. 
2. A variable was added to settings.py that contains the filename and path for each of these two files.
3. adherenceTests.py added; this file replaces adherence_check.py, adherence_predict.py and gap_check.py. These are no longer used or needed.

views.py
1. State variables used in view.py, Global_PATIENT_ID and Global_ADHERE_VARS, were added to eliminate the need for equivalent variables in settings. 
2. Changed imports to be consistent: from *** import ***
3. names={} replaced with a simple list, names = []
4. Code for initialization of SmartClient has been abstracted to a single function.
5. Imports are all consistent now: from *** import ***, rather than import *** as ***

settings.py
1. State variables PATIENT_ID and ADHERE_VARS, were removed. These were used only in a single file, views.py, so were moved to there.
2. No database is used by this app, so references to it removed.
3. The base URI for the NDF-RT drug information database web service was commented out. It was left as a comment, as this may be useful in the future.
4. Added a directory name, STATICFILES_DIRS, that has the app?s /static directory
5. Added a new global name, settings.DRUGCLASSFILE, that contains the name of the file with drug class information.
6. Two variables were added: GOOD_MPR_THRESHOLD (=0.80) and GAP_THRESHOLD(= 30). These are used by the adherence tests. Since the values themselves are debated in the literature, they are placed here so that they might be changed in the future.	

readTable.py
1. Class renamed: readTable --> ReadTable
2. import string as str changed to import string. 

adherenceTests.py
This is a new file that contains a class AdherenceTests. This coordinates and simplifies all of the adherence tests that are applied to determine good or poor adherence.
This file replaces and makes obsolete adherence_check.py, adherence_predict.py and gap_check.py. These are no longer used or needed.

adherence_check.py
Obsolete and no longer needed.
adherence_predict.py
Obsolete and no longer needed.
gap_check.py
Obsolete and no longer needed.

index.html and risk.html
Both of these files display information about each medication that is prescribed for the patient and contained in their health record. Information received from the adherence test results are contained in a ?flag? variable. This variable has been simplified and uses text labels to make it easier to understand the meaning. The following flags are currently options assigned in AdherenceTests.py. Each of these has a unique display: 
* flag = "Good" (One can simply assume the mpr is above the set threshold, no gaps, no other tests failed.)           
* flag = "Poor_gaps"      		Poor adherence due to gaps > 30 days      
* flag = "Poor_lowMPR"            	Poor adherence due to low MPR after 1 year
* flag = "Good_predictedMPR"        Logistic reg prediction for 1 year is good  
* flag = "Warning_predictedMPR"     Logistic reg prediction for 1 year is poor         
* flag = "Warning_lowMPR"     		MPR is currently low, but not yet 1 year

The difference between ?poor? adherence and a ?warning? is somewhat arbitrary. The idea intended is that a warning is not quite as bad: the MPR at 1 year is either predicted to be poor or, if no prediction is available, the current MPR is low. In both these cases, the patient has been taking the medication for less than 1 year, and there is time to intervene and raise the MPR to an acceptable level before 1 year. 

When gaps > 30 days are encountered, there?s a problem, period, so it?s more than a warning and adherence is judged to be ?poor?. Similarly, if more than a year has passed and the MPR is < 0.80 (or whatever threshold is used), adherence is clearly ?poor?. 

about.html
Text has been cleaned up and shorted. It includes the abstract from 
Jonikas, M.A., and Mandl, K.D. (2011). Surveillance of medication use: early identification of poor adherence. J Am Med Inform Assoc.
A hypertext link to the full paper is included.


