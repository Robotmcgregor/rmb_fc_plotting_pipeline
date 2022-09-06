#!/usr/bin/env python

"""

bareGroundPlot.py
=================

Description: This reads in the fractonal cover zonal stats and the rainfall zonal stats csv file and produces two time series plots per site.
Plot 1: bare ground
plot 2: all bands for interpretation.

This script also reads in the star transect shapefile for historic site visists and plots this information on each plot using the axvline function.

Author Grant Staben
email grant.staben@nt.gov.au
Date: 21/09/2020
Version: 1.0

Modified: Rob McGregor
email: Robert.Mcgregor@nt.gov.au
Date: 27/10/2020
Version: 2.0

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


===================================================================================================

Command arguments:
------------------

None


======================================================================================================

Input requirements (used in script):
------------------------------------

--output_zonal_stats: DataFrame
open DataFrame containing the fractonal cover zonal stats derived from fcZonalStats.py.
    - this DataFrame will be subset based on: 
            - b1, b2 and b3 count feature greater than 3, and
            - year feature greater than 1987.
    
--complete_tile: str
string object contining the Landsat tile name created by fcZonalStats.py

--rainFinishDate: str
string object containing the year month and day of the last image available (YYYY + '-' + MM + '-30').

--plot_outputs: str
string object contining the path to the plots folder within the export directory 'YYYYMMDD_HHMM'.

output_zonal_stats: DataFrame
DataFrame object zzzz

propName: str
string object to house the property name for each plot, derived from the pastoral estate shapefile. zzzz

siteDF: DataFrame
DataFrame object - subset of DataFrame 'output_zonal_stats', based on unique identifier 'site'.

dateSortDF: DataFrame
DataFrame object siteDF that has been sorted in assending order by the dateTime feature.

# use all predicted frac cover values to produce the fitted line
sortSiteDF: DataFrame
DataFrame object - subset of the sorted DataFrame 'dateSortDF', based on unique identifier 'site'.

variables:
-----------

--interactiveOutputs: str
string object containing the path to the interactive folder within the plot_outputs folder.

--unique_site: list
list object containing the unique identifier 'SITE' from the output_zonal_stats DataFrame.

--propName: str
string object containing the property name derived from the pastoral estate shapefile.

--siteID: str
string object containing the variable 'i' derived from zzzz

--i: zzzz
zzzz
 
siteDF: GeoDataFrame
geoDataFrame object - a subset of the output_zonal_stats geoDataFrame based on the unique identifier 'site'.

--dateSortDF: DataFrame
DataFrame object sorted in ascending order based on the dateTime feature - For the hover tool.

--sortSiteDF: geoDataFrame
geoDataFrame - subset of the a subset of the output_zonal_stats geoDataFrame based on the unique identifier 'site'.

--dateF: DataFrame
DataFrame object in ascending order base on the feature dateTime.
              
--dateFit: series
series object contining the dateTime feature from the datef DataFrame.
        
--meanBGfit: series
series object contining the b1_mean feature from the datef DataFrame.

--meanBGrolling: series
series object containing the rolling mean of the feature datef from the bg_mean_f series - perameters:(3,center=True)

s1, s2, s3: plots       

"""

# import modules
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.plotting import figure
import geopandas as gpd
import warnings

warnings.filterwarnings("ignore")


def string_clean_upper_fn(dirty_string):
    """ Remove whitespaces and clean strings.

            :param dirty_string: string object.
            :return clean_string: processed string object."""

    str1 = dirty_string.replace('_', ' ')
    str2 = str1.replace('-', ' ')
    str3 = str2.upper()
    clean_string = str3.strip()
    return clean_string


def prop_name_extraction_fn(estate_series, site_code):
    """ Extract the common name from the botanical_common_series excel document.

            :param estate_series: geopandas series object containing properties and properties code variables.
            :param site_code: string object containing the properties three letter code - read into the function.
            :return prop_label: string object containing the property name and code. """

    property_code_list = estate_series.PROPERTY.tolist()
    prop_code_upper = string_clean_upper_fn(str(site_code))
    if prop_code_upper in property_code_list:
        prop_name = estate_series.loc[estate_series['PROPERTY'] == prop_code_upper, 'PROP_TAG'].iloc[0]
    else:
        prop_name = prop_code_upper

    properties = string_clean_upper_fn(str(prop_name))
    prop_label = properties + "_" + prop_code_upper

    return prop_label


def main_routine(export_dir, output_zonal_stats, complete_tile, plot_outputs, pastoral_estate):
    print('interactivePlot.py INITIATED.')
    interactive_outputs = plot_outputs + '\\interactive'

    # read in the estate shapefile and create series
    estate = gpd.read_file(pastoral_estate)
    estate_series = estate[['PROPERTY', 'PROP_TAG']]
    prop_name = 'Unknown property' # todo  get pastoral name from estate shapefiles.

    #prop_code = prop_code_extraction_fn(estate_series, property_name)

    # read in the new csv file and create an index using the date_time column

    # subset DataFrame - drop all values less than 3 to reduce noise
    output_zonal_stats = output_zonal_stats[(output_zonal_stats['b1_count'] > 3)]

    # subset DataFrame - drop all values less than 1987
    output_zonal_stats = output_zonal_stats.loc[
        (output_zonal_stats['year'] >= 1987)]  # TODO converted from a string to int '1987'
    # output_zonal_stats.to_csv(export_dir_path + '\\outputZonal_greater1987.csv')

    for site in output_zonal_stats.site.unique():

        print('Interactive site: ', site)
        # convert all site names variables to a string.

        output_zonal_stats['dateTime'] = pd.to_datetime(output_zonal_stats[['year', 'month', 'day']])

        site_code = str(site[:3])
        print(site_code)
        # select out only the landsat derived fractional cover values.
        prop_label = prop_name_extraction_fn(estate_series, site_code)
        print('prop_label ', prop_label)

        # subset DataFrame by the unique identifier 'site'.  
        site_df = output_zonal_stats.loc[(output_zonal_stats.site == site)]  # comment

        date_sort_df = site_df.sort_values(['dateTime'])  # comment

        # format the image date for the hover tool
        date_sort_df['DateTime'] = date_sort_df['dateTime'].dt.strftime('%Y/%m/%d')

        # date_sort_df['DateTime'] = date_sort_df['site_date'].dt.strftime('%Y/%m/%d')

        # -----------------------------------------------Bare ground - band 1 ------------------------------------------

        # use all predicted fractional cover values to produce the fitted line
        sort_site_df = output_zonal_stats.loc[(output_zonal_stats.site == site)]
        sort_site_df.to_csv(export_dir + '\\sort_site_df_' + str(site) + '.csv')
        date_f = sort_site_df.sort_values(['dateTime'])
        print('date_f: ', date_f)
        date_fit = date_f['dateTime']
        print('date_fit: ', date_fit)
        mean_bg_fit = date_f['b1_mean']
        print('mean_bg_fit: ', mean_bg_fit)
        mean_bg_rolling = mean_bg_fit.rolling(5, center=True).mean()
        print('mean_bg_rolling: ', mean_bg_rolling)
        # set up the hover tool
        source2 = ColumnDataSource(date_sort_df)
        print('source2: ', source2)
        TOOLS = "pan,wheel_zoom,box_zoom,reset,save,".split(',')
        hover = HoverTool(tooltips=[('image date', '@DateTime'), ('Bare fraction', '@b1_mean{int}%')], names=["lsat"])
        TOOLS.append(hover)

        # set up the plots parameters
        s1 = figure(title='Fractional Cover Time Trace - Bare ground: ' + prop_name + ' site (%s)' % (str(site)),
                    x_axis_label='time',
                    y_axis_label='Bare Ground fraction %', x_axis_type='datetime', y_range=(0, 105),
                    plot_width=900, plot_height=250, tools=TOOLS)
        # plot the time series data
        s1.line(date_fit, mean_bg_rolling, color='red', line_width=3)
        s1.circle("dateTime", "b1_mean", source=source2, name="lsat", size=5, color='red', alpha=0.6, line_alpha=0.6,
                  line_color='black')
        print('s1:', type(s1))

        # ----------------------------------- Photosynthetic vegetation band 2 -----------------------------------------

        output_zonal_stats = output_zonal_stats.loc[(output_zonal_stats['b2_count'] > 3)]
        output_zonal_stats.sort_values(['dateTime'])
        output_zonal_stats = output_zonal_stats.loc[(output_zonal_stats['year'] >= 1987)]

        pv_mean_f = date_f['b2_mean']
        pv_mean_fpd4 = pv_mean_f.rolling(5, center=True).mean()

        # set up the hover tool
        source2 = ColumnDataSource(date_sort_df)

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save,".split(',')

        hover = HoverTool(tooltips=[('image date', '@DateTime'), ('pv fraction', '@b2_mean{int}%')], names=["lsat"])

        TOOLS.append(hover)

        # set up the plots parameters
        s2 = figure(
            title='Fractional Cover Time Trace - Photosynthetic vegetation: ' + prop_name + ' site (%s)' % (str(site)),
            x_axis_label='time',
            y_axis_label='PV fraction %', x_axis_type='datetime', y_range=(0, 105),
            plot_width=900, plot_height=250, tools=TOOLS)
        # plot the time series data
        s2.line(date_fit, pv_mean_fpd4, color='green', line_width=3)
        s2.circle("dateTime", "b2_mean", source=source2, name="lsat", size=5, color='green', alpha=0.6, line_alpha=0.6,
                  line_color='black')

        # ------------------------------- Non - photosynthetic vegetation band 3 ---------------------------------------

        output_zonal_stats = output_zonal_stats[(output_zonal_stats['b3_count'] > 3)]
        output_zonal_stats.sort_values(['dateTime'])
        output_zonal_stats = output_zonal_stats[(output_zonal_stats['year'] >= 1987)]

        npv_mean_f = date_f['b3_mean']
        npv_mean_fpd4 = npv_mean_f.rolling(5, center=True).mean()

        # set up the hover tool
        source2 = ColumnDataSource(date_sort_df)

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save,".split(',')

        hover = HoverTool(tooltips=[('image date', '@DateTime'), ('npv fraction', '@b3_mean{int}%')], names=["lsat"])

        TOOLS.append(hover)

        # set up the plots parameters
        s3 = figure(
            title='Fractional Cover Time Trace - Non-photosynthetic vegetation: ' + prop_name + ' site (%s)' % str(site),
            x_axis_label='time',
            y_axis_label='NPV fraction %', x_axis_type='datetime', y_range=(0, 105),
            plot_width=900, plot_height=250, tools=TOOLS)
        # plot the time series data
        s3.line(date_fit, npv_mean_fpd4, color='blue', line_width=3)
        s3.circle("dateTime", "b3_mean", source=source2, name="lsat", size=5, color='blue', alpha=0.6, line_alpha=0.6,
                  line_color='black')

        # complete_tile = str(106071)
        output_file(interactive_outputs + '\\' + str(prop_label) + '_' + site + '_' + complete_tile + '_layout.html')

        save(column(s1, s2, s3))

    print('step3_interactive plots.py COMPLETE.')


if __name__ == "__main__":
    main_routine()
