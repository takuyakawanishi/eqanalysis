## データ準備の詳細
### 準備
#### 1. Download and unzip

* We downloaded the data from
  * https://www.data.jma.go.jp/eqev/data/bulletin/shindo.html
* The snippet and the data directory:
  * eqanalysis/src/eqa_takuyakawanishi/utilities_preparation/download_data.py
  * eqanalysis/data_2024/data_downloaded
* Extracted the downloaded zip files and saved to
  * eqanalysis/data_2024/data_unzip


#### 2. Create code_p DataFrame file

* From the same site as above, we downloaded the meta file of the stations
  * code_p.dat
  * eqanalysis/data_2024/code_p.dat
* eqanalysis/src/eqa_takuyakawanishi/utilities_preparation/decode_code_p.py
  * The content of code_p.dat is saved to the following Pandas' DataFrame
  * eqanalysis/data_2024/code_p_YYYYmmdd_df.csv
  * Current file is 
  * eqanalysis/data_2024/code_p_20231205_df.csv
  * The column index names are set to
    * ["code", "address", "lat", "lon", "from", "to"].

#### 3. Organize the data into station by station files

* eqanalysis/src/eqa_takuyakawanishi/utilities_preparation/create_stationwise_dataframe.py
* Original data: 
  * eqanalysis/data_2024/data_unzip/ 
    * From i1919.dat to i2121.dat
* Convert them to station by station files
  * Names are st_(station code).txt
  * csv files with extension ".txt"
* st_stationnumber.txt contains the following data
  * station,intensity,year,month,day,hour,minute,second,intensity_equip,acceleration_max_comb

#### 4. code_p.dat

* adderess + parentheses
* The variations of the comments in the parenthesis are one of the following
  * {"(旧)", "（旧）", "（旧２）", "（旧３）", "（旧４）", "（臨）",
     "（臨時）", "（測候所）}

##### 4.1 Combine only （旧）, （旧２）, （旧３）, （旧４）

* Combine if the names of the station contains the same address followed by one of （旧）

##### 4.2 Measurement Periods, gaps and overlaps

* If the beginning year is marked as "9999":, we assume the beginning date was January 1st of the year in which first earthquake was recored.
* If the ending year is marked as "9999", we assume the ending data was December 31 of the year in which the last earthquake was recorded.
* 