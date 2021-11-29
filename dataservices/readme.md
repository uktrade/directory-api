# Updating data sources

Instructions on how to get updates for the data in dataservices.

## 1) Ease of doing business

Go to https://databank.worldbank.org/reports.aspx?dsid=1&series=IC.BUS.EASE.XQ# 

The data available appear as a table with the year in columns. 
Although several year columns are present, only the last appears to be populated.

It's best to select the right download options to deliver the data as a list. There will be lots of unpopulated rows (for the non-populated years) but that doesn't matter.

**To downoad:**


 * Open 'Advanced options' from the download button on the top-right.
 * Under 'download format, tab -> csv' choose:
       * variable format: 'codes only',
       * data format : 'List',
       * NA preference: 'Blank'
 * Download the data in that format.
 * Save the csv into the resources folder with the appropriate year in the filename. e.g. **EaseOfDoingBusiness_2020.csv**
The loader will skip all blank rows so you don't need to tidy the file in any way.


