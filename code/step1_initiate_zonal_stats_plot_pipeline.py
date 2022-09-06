"""

Author: Rob McGregor
email: Robert.Mcgregor@nt.gov.au
Date: 27/10/2020
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
"""

# Import modules
from __future__ import print_function, division
import os
from datetime import datetime
import argparse
import shutil
import sys
import pandas as pd
from glob import glob
import warnings

warnings.filterwarnings("ignore")


def get_cmd_args_fn():
    p = argparse.ArgumentParser(description='Produce zonal plots (.jpg) and interactive .html files.')

    p.add_argument('-d', '--directory_zonal', help='The directory containing the zonal stats csv files (default)',
                   default=r'E:\DENR\code\rangeland_monitoring\rmb_zonal_plots_ploting_pipeline\data\zonalStats')

    p.add_argument('-x', '--export_dir', help='Enter the export directory for all outputs (default)',
                   default=r'Z:\Scratch\Rob\outputs\zonal_plots')

    p.add_argument('-r', '--rainfall_dir', help='The directory containing the rainfall zonal stats csv files (default)',
                   default=r'E:\DENR\code\rangeland_monitoring\rmb_zonal_plots_ploting_pipeline\data\rainfall')

    p.add_argument('-e', '--end_date', help='Final date for the rainfall data (i.e.2020-05-01) (default).',
                   default='2021-06-01')

    p.add_argument('-i', '--rainfall_raster_dir', help='Directory containing the rainfall raster images (default)',
                   default=r'Z:\Scratch\Zonal_Stats_Pipeline\rainfall')

    p.add_argument('-v', '--visits', help='Path to the latest integrated site shapefile containing previous '
                                          'visit information (default).',
                   default=r"E:\DENR\code\rangeland_monitoring\rmb_zonal_plots_ploting_pipeline\assets\shapefiles\NT_StarTransect_20200713.shp")

    p.add_argument('-p', '--pastoral_estate', help='File path to the pastoral estate shapefile.',
                   default=r"E:\DENR\code\rangeland_monitoring\rmb_zonal_plots_ploting_pipeline\assets\shapefiles\pastoral_estate.shp")

    cmdargs = p.parse_args()

    if cmdargs.directory_zonal is None:
        p.print_help()

        sys.exit()

    return (cmdargs)


def export_dir_fn(export_dir):
    """Create an export directory 'YYYMMDD_HHMM' at the location specified in command argument exportDir.

    :param export_dir: string object containing the path to the export directory.
    :return export_dir_path: string object containing the path to a newly created folder within the
            export_dir. """

    # create file name based on date and time.
    date_time_replace = str(datetime.now()).replace('-', '')
    date_time_list = date_time_replace.split(' ')
    date_time_list_split = date_time_list[1].split(':')
    export_dir_path = export_dir + '\\' + str(date_time_list[0]) + '_' + str(date_time_list_split[0]) + str(
        date_time_list_split[1])

    # check if the folder already exists - if False = create directory, if True = return error message.
    try:
        shutil.rmtree(export_dir_path)

    except:
        print('The following directory did not exist: ', export_dir_path)

    # create folder titled 'tempFolder'
    os.makedirs(export_dir_path)

    return export_dir_path


def create_export_dir_fn(export_dir_path):
    """ Create export directory folder structure.

    :param export_dir_path: string object containing the path to a newly created folder within the
            export_dir.
    :return plot_dir: string object containing the path to a newly created plot folder within the
            export_dir. """
    # Create folders within the tempDir directory.

    plot_dir = export_dir_path + '\\plots'
    os.mkdir(plot_dir)

    interactive_dir = plot_dir + '\\interactive'
    os.mkdir(interactive_dir)

    final_plot_dir = export_dir_path + '\\finalPlots'
    os.mkdir(final_plot_dir)

    final_inter_dir = export_dir_path + '\\finalInteractive'
    os.mkdir(final_inter_dir)

    return plot_dir


def glob_create_df(directory, search_criteria):
    """ Search for files with the matching search criteria passed through the function, open as pandas data frames and
    store in a list.

    :param directory:
    :param search_criteria: string object passed into the function used to match files.
    :return df: pandas data frame.
    :return file_list: list objet containing open data frames. """

    # create a df from all csv files in a directory.
    list_df = []
    file_list = []
    # search through the directory
    for file in glob(directory + search_criteria):
        file_list.append(file)
        df = pd.read_csv(file)
        list_df.append(df)

    df = pd.concat(list_df)

    return df, file_list


def list_dir(rainfall_raster_dir, search_criteria):
    """ Return a list of the rainfall raster images in a directory for the given file extension.
    :param rainfall_raster_dir: string object containing the rainfall directory path (command argument)
    :param search_criteria: string object passed into the function used to match files.
    :return list_image: list object containing the path to all files that matched the search criteria. """

    list_image = []

    for root, dirs, files in os.walk(rainfall_raster_dir):

        for file in files:
            print(files)
            if file.endswith(search_criteria):
                img = (os.path.join(root, file))
                # print(img)
                list_image.append(img)
    # print(list_image)
    return list_image


def rainfall_start_fin_dates(list_image):
    """ extract the first and last dates for available rainfall images.
    :param list_image: list object containing the path to all files that matched the search criteria.
    :return rain_start_date: string object containing the first image date.
    :return rain_finish_date: string object containing the last image date. """

    # sort the list image
    list_image.sort()
    # print('sorted image list: ', list_image)

    path_s = list_image[0]
    # print('path_s: ', path_s)
    head_s, tail_s = os.path.split(path_s)

    year_s = tail_s[:4]
    month_s = tail_s[4:-4]
    rain_start_date = (str(year_s) + '-' + str(month_s) + '-01')
    # print('rain_start_date: ', rain_start_date)

    path_f = list_image[-1]
    head_f, tail_f = os.path.split(path_f)
    year_f = tail_f[:4]
    month_f = tail_f[4:-4]

    rain_finish_date = (str(year_f) + '-' + str(month_f) + '-30')
    # print('rain_finish_date: ', rain_finish_date)

    return rain_start_date, rain_finish_date


'''def get_completeTile():
    listZonalTile = []
    for file in glob.glob(tileForProcessingDir + '\\*.csv'):
        # append tile paths to list.
        listZonalTile.append(file)
    return listZonalTile'''


def main_routine():
    """ Created time series plots using matplotlib one per site per tile and interactive time series plots using Boken.
    Plots are sorted based on which tile registered the most amount of zonal stats hits (i.e. limited cloud masking).
    :param directory_zonal: string object containing the directory path to the processed zonal stats csv files.
        (command argument).
    :param export_dir: string object containing the export directory path for all outputs (command argument).
    :param rainfall_dir: string object containing the directory path to the rainfall zonal stat csv files.
        (command argument).
    :param finish_date: string object containing the date you wish the plots to end (y axis).
    :param rainfall_raster_dir: string object containing the directory path to the rainfall raster files.
        (command argument).
    :param pastoral_estate: string object containing the file path to the pastoral estate shapefile. """

    print('step1_initiate_zonal_plot_pipeline.py INITIATED.')
    # read in the command arguments
    cmdargs = get_cmd_args_fn()
    zonal_dir = cmdargs.directory_zonal
    export_dir = cmdargs.export_dir
    rainfall_dir = cmdargs.rainfall_dir
    finish_date = cmdargs.end_date
    rainfall_raster_dir = cmdargs.rainfall_raster_dir
    previous_visits = cmdargs.visits
    pastoral_estate = cmdargs.pastoral_estate

    # complete_tile = '104072'  # TODO create a complete_tile variable from file name

    # call the export_dir function.
    export_dir_path = export_dir_fn(export_dir)
    # call the create_export_dir_fn function.
    plot_dir = create_export_dir_fn(export_dir_path)
    output_zonal_stats, zonal_file_list = glob_create_df(zonal_dir, '//*.csv')
    output_rainfall, rainfall_file_list = glob_create_df(rainfall_dir, '//*.csv')
    list_image = list_dir(rainfall_raster_dir, 'img')

    rain_start_date, rain_finish_date = rainfall_start_fin_dates(list_image)

    for tile in zonal_file_list:
        # strip Landsat tile label from csv file name.
        _, tile_name = tile.rsplit('_', 1)
        complete_tile = tile_name[:-4]
        output_zonal_stats = pd.read_csv(tile)

        print('step2_bare_ground_plots.py initiating..........')
        # call the step2_bare_ground_plots.py script.
        import step2_bare_ground_plots
        step2_bare_ground_plots.main_routine(export_dir_path, output_zonal_stats, output_rainfall, complete_tile,
                                             rain_finish_date, rainfall_raster_dir, previous_visits, plot_dir)

        print('step3_interactive_plots.py initiating..........')
        import step3_interactive_plots
        step3_interactive_plots.main_routine(export_dir_path, output_zonal_stats, complete_tile,
                                             plot_dir, pastoral_estate)

    print('step4_sort_plots.py initiating..........')
    print('zonal_dir: ', zonal_dir)
    # call the step2_sort_plots.py script.
    import step4_sort_plots
    step4_sort_plots.mainRoutine(zonal_dir, export_dir_path)

    # delete the TempDir Path and its contents.
    # shutil.rmtree(tempDirPath)

    # print('Temporary directory and its contents has been deleted from your working drive.')
    print('fcZonalStatsPipeline.py COMPLETE.')


if __name__ == '__main__':
    main_routine()
