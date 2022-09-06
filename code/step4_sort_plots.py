#!/usr/bin/env python

'''
step2_sort_plots.py
============

Description: This script determines which Landsat tile had the most non null zonal statistics records per site and files those plots (bare ground, all bands and interattive) into final output folders.


Author: Rob McGregor
email: Robert.Mcgregor@nt.gov.au
Date: 30/11/2020
Version: 1.0

###############################################################################################

MIT License

Copyright (c) 2020 Rob McGregor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.


THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

##################################################################################################

Input requirements:
-------------------

1.	ODK output directory in .xlsx format
2.	Singlepart polygon shapefile or shapefiles with the following attributes “LAISKEY”, “PROP_NAME”, “WGS52_ha” and “WGS53_ha”. The shapefiles with correct attributes can be derived from: select_and_project_property_shapefiles_calc_area.py (McGregor, 2020).
3.	A final classification must been applied to the MODIS derived NAFI fire scars file names include (i.e. MTHS.tif or MTH.tif). However, if you wish to include the current year (not complete) you will need to pre-process that raster. Pre-processing can be derived from: modis_raster_12_month_classification.py (McGregor, 2020).

===================================================================================================

Command arguments:
------------------

None


======================================================================================================

Parameters:
-----------

df: DataFrame
DataFrame object to open and temporarily house each zonalStats csv located in the 'zonalStats' folder.

listDF: list
list Object to store all zonalStats.csv records as open DataFrames for concatenation.

dfConcat: DataFrame
DataFrame object that stores all zonalStats observations, excluding all null values. 

seriesVC: Series
Series object that stores site, tile and value count information.

dfVC : DataFrame
DataFrame object created from the seriesVC, index has been reset and the value count feature has been renamed to 'count'.

listDfVC: list
list object to house the open Dataframes 'topUniqueDfVC'.

uniqueSite: list
list object to house unique site names derived from the dfVC DataFrame.
       
uniqueDfVC: DataFrame
DataFrame object to temporarily store a subset of the dfVC DataFrame based on the unique identifier (site).

topUniqueDfVC: DataFrame
DataFrame object to temporarily store the tope observation within the subset DataFrame uniqueDfVC.

listDfVC: listlist object to house all of the open topUniqueDfVC DataFrames.

outputTopZonalStatsTiles: DataFrame
DataFrame object housing the complete list of site, tile and count information for the tiles which had the most non null zonalStats observations.

uniqueSiteTopZonal: list
list object to store unique site names from the outputTopZonalStatsTiles DataFrame.

uniqueTileTopZonal: list
list object to store unique tile names from the outputTopZonalStatsTiles DataFrame

========================================================================================================
'''



from __future__ import print_function, division
import pandas as pd
import glob
import os 
import shutil
import warnings
warnings.filterwarnings("ignore")


def globDir(zonal_dir):
    '''
    Search a specified Directory (zonalStats) and concatenate all records to a DataFrame.
    '''

    # create an empty list
    listDF = []

    for file in glob.glob (zonal_dir + '\\*'):
        print(zonal_dir)
        # read in all zonal stats csv
        #print(file)
        df = pd.read_csv(file)
        # append all zonalStatstat DataFrames to a list.
        listDF.append(df)

    dfConcat = pd.concat(listDF)
    dfConcat.dropna(axis=0, inplace=True)
    return dfConcat

    
"""def createTileLabel(dfConcat, export_dir_path):
    '''
    Add a feature (tile) to the DataFrame, feature variables are extracted  from the image feature variable.
    '''
    listTile = []
    
    for image in dfConcat.image:
        tile = str(image[-35:-32]) + str(image[-31:-28])
        print('tile: ', tile)
        listTile.append(tile)
      
    # create a feature called 'tile' and fill with listTile values.
    dfConcat['tile'] = listTile 
    dfConcat.to_csv(export_dir_path + '\\allSitesZonalStats.csv')    
    return dfConcat"""


def add_tile_column(dfConcat):
    # add a tile column to the dataframe.
    
    image_list = dfConcat['image'].tolist()
    for i in image_list:
        begining = i[8:11]
        end = i[12:15]
        tile = begining + end
        # print(tile)

    dfConcat['tile'] = tile
    
    return dfConcat
 
def valueCounts(dfConcat):
    '''
    Preform value counts function on the DataFrame and rename the new feature(0) to 'count'.
    '''
    # calculate value counts of features site and tile.



    seriesVC = dfConcat[['site', 'tile']].value_counts()
    dfVC = pd.DataFrame(seriesVC)
    
    # reset index
    dfVC.reset_index(inplace=True)
    
    # change column header
    dfVC.rename(columns={0:'count'}, inplace=True)
   
    return dfVC


def selectTopRow(dfVC):
    '''
    Subset the DataFrame based on site names and select the top observation (highest count value), and concatenated to a new DataFrame (outputTopZonalStatsTiles).
    '''
    # create an empty list
    listDfVC = []
    
    # create a list of unique site names.
    uniqueSite = dfVC.site.unique().tolist()
    
    # loop through the list of unique sites
    for i in uniqueSite:
        # subsect DataFrame based on unique site names.
        uniqueDfVC = dfVC[dfVC['site'] == i]
        #subsect the first row of the DataFrame (highest count value) 
        topUniqueDfVC = uniqueDfVC.head(1)
        # append subset DataFrame to list
        listDfVC.append(topUniqueDfVC)
    # concatenate dfList to a DataFrame.
    outputTopZonalStatsTiles = pd.concat(listDfVC)
    
    # outputTopZonalStatsTiles.to_csv(export_dir_path + '\\testoutputTopZonalStatsTilesdropna.csv')
    return outputTopZonalStatsTiles
    

def sortPlots(zonal_dir, exportDirPath, finalPlotOutputs, finalInteractiveOutputs, outputTopZonalStatsTiles):
    '''
    Using the outputTopZonalStatsTiles DataFrame, copy all plots (bare ground, all bands and interactive) to new folders titled finalPlot and finalInteractive.
    '''
    # create a list of unique site names.
    uniqueSiteTopZonal = outputTopZonalStatsTiles.site.unique().tolist()
    uniqueTileTopZonal = outputTopZonalStatsTiles.tile.unique().tolist()
    print('zonal_dir line 200: ', zonal_dir)
    for i in uniqueSiteTopZonal:
        print(i)
        tile = outputTopZonalStatsTiles.loc[outputTopZonalStatsTiles['site'] == i, 'tile'].item()

        for barePlot in glob.glob(exportDirPath + '\\plots\\bareGroundPlot_' + tile + '_' + i + '*.png'):
            print('bare plot copied: ', exportDirPath + '\\plots\\bareGroundPlot_' + tile + '_' + i + '*.png')
            shutil.copy(barePlot, finalPlotOutputs)

        for interPlot in glob.glob(exportDirPath + '\\plots\\all_bands_for_interpretation_' + tile + '_' + i + '*.png'):
            print('Inter plot copied: ', exportDirPath + '\\plots\\all_bands_for_interpretation_' + tile + '_' + i + '*.png')
            shutil.copy(interPlot, finalPlotOutputs)

        for interactivePlot in glob.glob(exportDirPath + '\\plots\\interactive' + '\\' + i + '_'+ tile + '_' + '*layout.html'): # + i + '_'+ tile + '_' + 
            print('interactivePlot: ', exportDirPath + '\\plots\\interactive' + '*layout.html')
            shutil.copy(interactivePlot, finalInteractiveOutputs)


    return()
   
def mainRoutine(zonal_dir, exportDirPath):
 
    # output folder paths
    finalPlotOutputs = exportDirPath + '\\finalPlots'

    finalInteractiveOutputs = exportDirPath + '\\finalInteractive'
    
    # call the globDir function.
    print('call the globDir function')
    dfConcat = globDir(zonal_dir)
    # dfConcat.to_csv(export_dir_path + '\\dfConcat.csv')
    # call the createTileLabel
    # dfConcat = createTileLabel(dfConcat, export_dir_path)

    dfConcat = add_tile_column(dfConcat)

    # call the value_counts function
    dfVC = valueCounts(dfConcat)
    # call the selectTopRow function
    outputTopZonalStatsTiles = selectTopRow(dfVC)
    # call the sortPlots function.
    sortPlots(zonal_dir, exportDirPath, finalPlotOutputs, finalInteractiveOutputs, outputTopZonalStatsTiles)
    
    
    print('step2_sort_plots.py COMPLETE.')
    
     
if __name__ == "__main__":
    mainRoutine()   
