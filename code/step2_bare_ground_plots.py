#!/usr/bin/env python

"""
MIT License

Copyright (c) 2020 Rob McGregor, script modified from zzzz Grant Staben 2019

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
"""

# import modules.
from __future__ import print_function, division
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
import warnings

warnings.filterwarnings("ignore")
mpl.rcParams['figure.figsize'] = (30, 8.0)


def previous_visits_fn(previous_visits):
    """ Read in and clean the integrated site shapefile for previous site visit information.

    :param previous_visits: latest shapefile containing previous visits to the site.
    :return integrated: open geo-dataframe. """

    # Import the integrated site shapefile for previous visit dates to the site.
    integrated = gpd.read_file(previous_visits)
    # convert site name to capital letters
    integrated['siteTitle'] = integrated.site.str.upper()
    # add a datTime feature from the obs_time variables.
    integrated['dateTime'] = integrated.obs_time.apply(pd.to_datetime)

    return integrated


def import_rainfall_data(output_rainfall):
    """ Import rainfall zonal stats csv and produce three columns from the im_date column, year, month and date

    :param output_rainfall:
    :return output_rainfall:    """
    # create the date time field and sort the values
    output_rainfall['year'] = output_rainfall['im_date'].map(lambda x: str(x)[:4])
    output_rainfall['month'] = output_rainfall['im_date'].map(lambda x: str(x)[4:6])
    output_rainfall['Date'] = output_rainfall['year'] + '/' + output_rainfall['month'] + '/' + '15'
    output_rainfall.sort_values(['Date'])

    # convert site_date feature from object to datetime
    output_rainfall['site_date'] = pd.to_datetime(output_rainfall['site_date'])
    #todo remove
    output_rainfall.to_csv(r"Z:\Scratch\Zonal_Stats_Pipeline\rmb_fractonal_cover_zonal_stats\outputs\new_plotsrainfall_sort.csv")
    return output_rainfall


def import_zonal_stats(output_zonal_stats):
    output_zonal_stats['site_date'] = pd.to_datetime(output_zonal_stats['site_date'])
    # remove all data points which do not have at least 3 valid pixels to produce the average bare ground for a site
    output_zonal_stats = output_zonal_stats.loc[(output_zonal_stats['b1_count'] > 3)]
    # create the date time field and sort the values
    output_zonal_stats['dateTime'] = output_zonal_stats['year'].apply(str) + "/" + output_zonal_stats['month'].apply(
        str) + "/" + output_zonal_stats['day'].apply(str)
    output_zonal_stats['dateTime'] = output_zonal_stats.dateTime.apply(pd.to_datetime)
    # sort values by dateTime.
    output_zonal_stats.sort_values(['dateTime'])

    return output_zonal_stats


def rainfall_data_amend_fn(output_rainfall, i):
    # select the site to plot
    site_s = output_rainfall.loc[(output_rainfall.site == i)]
    print('rainfall site: ', site_s)

    site_label = str(i)

    property_name = output_rainfall.prop_name.unique()
    prop = property_name[0]

    site_date = output_rainfall.site_date.unique()
    s_date = site_date[0]

    # read in the rainfall stats and covert them to total mm
    site_sort = site_s.sort_values(['Date'])
    date = pd.Series(site_sort['Date']).apply(pd.to_datetime)
    rain = site_sort['mean'] / 10

    return rain, date, site_label


def b1(output_zonal_stats_fn, i):
    """ Calculate rolling average for band 1.
    :param output_zonal_stats_fn:
    :param i:
    :return:
    """

    # use all predicted bare frac cover values to produce the fitted line 
    lsat_bg = output_zonal_stats_fn.loc[(output_zonal_stats_fn['site'] == i)]
    date_bg = lsat_bg.sort_values(['dateTime'])
    # ('date_bg: ', type(date_bg))
    date_fit_bg = pd.Series(date_bg['dateTime']).apply(pd.to_datetime)
    # print('date_fit_bg line 213: ', date_fit_bg)
    mean_bg = date_bg['b1_mean']

    # currently set to calculate the rolling mean for five points
    mean_b_gfl = mean_bg.rolling(5, center=True).mean()

    # interpolate the missing values to enable it to be plotted
    interp_bg = mean_b_gfl.interpolate(method='linear', limit_direction='both')

    vals_bg = interp_bg.values
    # print('values_bg: ', values_bg)

    return vals_bg, date_fit_bg


def b2(output_zonal_stats, i):
    """ Calculate rolling average for band 2.
    :param output_zonal_stats:
    :param i:
    :return:
    """
    # use all predicted green fraction cover values to produce the fitted line
    lsat_pv = output_zonal_stats.loc[(output_zonal_stats['site'] == i)]
    date_pv = lsat_pv.sort_values(['dateTime'])
    date_fit_pv = pd.Series(date_pv['dateTime']).apply(pd.to_datetime)
    mean_pv = date_pv['b2_mean']

    # currently set to calculate the rolling mean for four points
    mean_p_vfl = mean_pv.rolling(5, center=True).mean()  # changed from 5

    # interpolate the missing values to enable it to be plotted
    interp_pv = mean_p_vfl.interpolate(method='linear', limit_direction='both')
    vals_pv = interp_pv.values

    return vals_pv, date_fit_pv


def b3(output_zonal_stats_fn, i):
    """ Calculate rolling average for band 3.
    :param output_zonal_stats_fn:
    :param i:
    :return:
    """

    # use all predicted NPV fractional cover values to produce the fitted line
    lsat_npv = output_zonal_stats_fn[(output_zonal_stats_fn['site'] == i)]
    date_npv = lsat_npv.sort_values(['dateTime'])
    date_fit_npv = pd.Series(date_npv['dateTime']).apply(pd.to_datetime)
    mean_npv = date_npv['b3_mean']

    # Calculate the rolling mean for four points
    mean_np_vfl = mean_npv.rolling(5, center=True).mean()  # changed from 5

    # interpolate the missing values to enable it to be plotted
    interp_npv = mean_np_vfl.interpolate(method='linear', limit_direction='both')
    vals_npv = interp_npv.values

    return vals_npv, lsat_npv, date_fit_npv


def plot_bare_ground_fn(lsat_npv, vals, date, rain, integrated, completeTile, siteLabel, startDate, finishDate,
                        dateFitBG,
                        sDate, i, plotOutputs):
    # --------------------------------------- BARE GROUND PLOT ---------------------------------------------------

    # get the site name for the plot title
    s_name = str(lsat_npv.site.unique())
    site_name = s_name.strip("['']")

    # set up the format for the plot 
    fig, ax = plt.subplots()

    ax.set_ylim(0, 100)
    print('start_date: ', startDate)
    print('finish_date: ', finishDate)
    # set up the x axis limits using pandas 
    ax.set_xlim(pd.Timestamp(startDate), pd.Timestamp(finishDate))
    ax.set_xlim(startDate, finishDate)

    barax = ax.twinx()
    print('Rain: ', rain)
    barax.bar(date, rain, width=20, color="b", label='Rainfall')  # , alpha=0.15, '#00539C'

    ###################################################################################

    """# add bare ground data to the plot
    ax.plot(dateFitBG, vals, linestyle='-', linewidth=2, color='#E13B18', label='Bare ground')

    # add av line representing previous visits to the site.
    plt.axvline(x = sDate, color ='r') #, linestyle = '--', linewidth = 1)"""

    ##################################################################
    years = mdates.YearLocator(1)  # 2 plots up every second year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')

    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)  # Tick every year on Jan 1st

    ##################################################################

    # add legend in the fixed position and use numpoints=1 to only show one point
    # otherwise it will show two points
    # ax.tick_params(axis='both', which='major', labelsize=20)
    ax.legend(loc=2, numpoints=1, prop={'size': 20})
    ax.set_title("Time Trace - site " + site_name, fontsize=25)
    ax.set_xlabel('Year', fontsize=25)

    ######################### Select a y axis label #############################
    ax.set_ylabel('Bare Ground (%)', fontsize=20)
    barax.set_ylabel('Monthly Rainfall mm)', fontsize=20)
    barax.tick_params(axis='both', which='major', labelsize=20)
    barax.legend(loc=1, numpoints=1, prop={'size': 20})

    fig.autofmt_xdate()

    # Add the current years inspection date.

    """plt.axvline(x=pd.Timestamp(sDate), color='dimgrey', linestyle='--')

    # Add previous dates from the star transect shapefile.
    integratedSite = integrated.loc[integrated['siteTitle'] == i]
    listDate = integratedSite.dateTime.unique().tolist()

    listLength = len(listDate)

    if listLength >= 1:

        for i in listDate:
            plt.axvline(x=pd.Timestamp(i), color='dimgrey', linestyle='--')"""

    fig.savefig(
        plotOutputs + '\\bareGroundPlot_' + str(completeTile) + '_' + siteLabel + '_' + str(startDate) + '_' + str(
            finishDate) + '_150.png', dpi=150, bbox_inches='tight')  # bbox_inches removes the white space

    plt.close(fig)

    return (fig)


def plot_all_bands_fn(lsat_npv, date, rain, values_bg, values_pv, values_npv, integrated, complete_tile, site_label,
                      start_date, finish_date, date_fit_bg, date_fit_pv, date_fit_npv, s_date, i, plot_outputs):
    s_name = str(lsat_npv.site.unique())
    site_name = s_name.strip("['']")

    # set up the format for the plot 
    fig, ax = plt.subplots()

    ax.set_ylim(0, 100)

    # set up the x axis limits using pandas 
    ax.set_xlim(pd.Timestamp(start_date), pd.Timestamp(finish_date))
    # ax.set_xlim(start_date, finish_date)

    bar_ax = ax.twinx()
    bar_ax.bar(date, rain, width=20, color='#00539C', label='Rainfall', alpha=0.15)  # , alpha=0.15

    # ------------------------------------------------------------------------------------------------------------------

    # plot all three data fields (bare ground, npv and pv)
    ax.plot(date_fit_bg, values_bg, linestyle='-', linewidth=2, color='#E13B18', label='Bare ground')
    ax.plot(date_fit_pv, values_pv, linestyle='-', linewidth=2, color='green', label='PV')
    ax.plot(date_fit_npv, values_npv, linestyle='-', linewidth=2, color='#1873E1', label='NPV')

    # plt.axvline(x = s_date, color ='r') #, linestyle = '--', linewidth = 1)

    # ------------------------------------------------------------------------------------------------------------------
    years = mdates.YearLocator(1)  # 2 plots up every second year
    months = mdates.MonthLocator()  # every month
    years_fmt = mdates.DateFormatter('%Y')

    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)  # Tick every year on Jan 1st

    # ------------------------------------------------------------------------------------------------------------------

    # add legend in the fixed position and use numpoints=1 to only show one point otherwise
    # it will show two points which is annoying
    # ax.tick_params(axis='both', which='major', labelsize=20)
    ax.legend(loc=2, numpoints=1, prop={'size': 20})
    ax.set_title("Time Trace - site " + site_name, fontsize=25)
    ax.set_xlabel('Year', fontsize=25)

    # ------------------------------------------- Select a y axis label ------------------------------------------------

    ax.set_ylabel('Bare Ground (%)', fontsize=20)
    ax.set_ylabel('Photosynthetic Vegetation (%)', fontsize=20)
    ax.set_ylabel('Non-photosynthetic Vegetation (%)', fontsize=20)
    ax.set_ylabel('Fractional Cover (%)', fontsize=20)

    bar_ax.set_ylabel('Monthly Rainfall mm)', fontsize=20)
    bar_ax.tick_params(axis='both', which='major', labelsize=20)
    bar_ax.legend(loc=1, numpoints=1, prop={'size': 20})

    fig.autofmt_xdate()

    plt.axvline(x=pd.Timestamp(s_date), color='dimgrey', linestyle='--')

    # Add previous dates from the star transect shapefile.
    integrated_site = integrated.loc[integrated['siteTitle'] == i]
    list_date = integrated_site.dateTime.unique().tolist()

    list_length = len(list_date)

    if list_length >= 1:

        for i in list_date:
            plt.axvline(x=pd.Timestamp(i), color='dimgrey', linestyle='--')

    fig.savefig(plot_outputs + '\\all_bands_for_interpretation_' + str(complete_tile) + '_' + site_label + '_' + str(
        start_date) + '_' + str(finish_date) + '_150.png', dpi=150,
                bbox_inches='tight')  # bbox_inches removes the white space

    plt.close(fig)

    return fig


def main_routine(export_dir_path, output_zonal_stats, output_rainfall, complete_tile,
                 rain_finish_date, rainfall_raster_dir, previous_visits, plot_dir):
    """ Produce static time series plot from the matplotlib module from fractional cover and rainfall zonal stat
    information.

    :param export_dir_path:
    :param output_zonal_stats:
    :param output_rainfall:
    :param complete_tile:
    :param rain_finish_date:
    :param rainfall_raster_dir:
    :param previous_visits:
    :return:
    """
    print('step2_bare_ground_plots.py INITIATED.')

    # define the start and finish dates fro the plots
    start_date = '1988-05-01'
    finish_date = '2020-08-31'  # rain_finish_date

    # call previous visits function.
    integrated = previous_visits_fn(previous_visits)

    output_rainfall = import_rainfall_data(output_rainfall)
    # output_rainfall.to_csv(export_dir_path + '\\output_rainfall.csv')

    output_zonal_stats = import_zonal_stats(output_zonal_stats)
    # output_zonal_stats.to_csv(export_dir_path + '\\output_zonal_stats.csv')

    for i in output_rainfall.site.unique():
        rain, date, site_label = rainfall_data_amend_fn(output_rainfall, i)

        # select the site to plot
        site_s = output_rainfall.loc[(output_rainfall.site == i)]

        site_label = str(i)

        property_name = output_rainfall.prop_name.unique()
        prop = property_name[0]

        site_date = output_rainfall.site_date.unique()
        s_date = site_date[0]

        site_date = output_rainfall.site_date.unique()
        s_date = site_date[0]

        # read in the rainfall stats and covert them to total mm
        site_sort = site_s.sort_values(['Date'])
        date = pd.Series(site_sort['Date']).apply(pd.to_datetime)
        rain = site_sort['mean'] / 10

        values_bg, date_fit_bg = b1(output_zonal_stats, i)
        values_pv, date_fit_pv = b2(output_zonal_stats, i)
        values_npv, lsat_npv, date_fit_npv = b3(output_zonal_stats, i)

        fig = plot_bare_ground_fn(lsat_npv, values_bg, date, rain, integrated, complete_tile, site_label, start_date,
                                  finish_date,
                                  date_fit_bg, s_date, i, plot_dir)

        fig = plot_all_bands_fn(lsat_npv, date, rain, values_bg, values_pv, values_npv, integrated, complete_tile, site_label,
                                start_date, finish_date, date_fit_bg, date_fit_pv, date_fit_npv, s_date, i, plot_dir)

    print('step2_bare_ground_plot.py COMPLETED')


if __name__ == "__main__":
    main_routine()
