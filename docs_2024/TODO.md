#### As of Feb. 8, 2024
* find_intensity_frequency_regression_summarize_ts
  * ending date in summary should be corrected (to actual.)
  * summary should contain latitude and longitude


* eqanalysis/src/eqa_takuyakawanishi/utilities_preparation/organize_stations_2024_03_manage_overlaps.py
  * the resulting .csv file has incorrect "gaps" values.
  
  * for this, separate calc_gaps snippet from organize_stations_2024_02
  * organize_stations_2024_02 contains add beginninga datetimes and ending datetimes, then add calc_gaps.
  * organize_stations_2024_03 contains adjust_overlap and calc_gaps

* consider bringing organize_stations_2024 files into one file.
  * Also automate creating document for the organization of the data.


* As of Feb 8, 2024, organize_stations_2024.py now calculate gaps.
  * We have to add the content of organize_stations_2024_03.py to above.

* MAKE DATETIME_E_S, final be "2022-01-01 00:00:00"
  * This should be automatic, refer to stationwise_20aa 

* MOST IMPORTANTLY
* we have to check the following.
* The frequency of intensity 7 earthquake increased one year after the euqke from one day after the quake. This is impossible.
* No, station 7413931 experienced TWO quakes in two days.


  