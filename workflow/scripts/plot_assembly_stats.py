#!/usr/bin/env python

import argparse
from pathlib import Path
import datetime

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool
from bokeh.resources import CDN
from bokeh.embed import file_html

def parse_arguments():
    parser = argparse.ArgumentParser(
            description="Plot runtime stats for assemblers"
            )

    optionalArgs = parser._action_groups.pop()

    requiredArgs = parser.add_argument_group("Required arguments")

    requiredArgs.add_argument(
            '-d',
            '--data-dir',
            type=lambda p: Path(p).resolve(strict=True), 
            dest='data_dir',
            required=True,
            help="Directory containing [assembler].[mem|time].txt files"
            )

    requiredArgs.add_argument(
            "-o",
            "--output-html",
            type=lambda p: Path(p).resolve(),
            required=True,
            dest='out_html',
            help="Save html in this file"
            )

    parser._action_groups.append(optionalArgs)

    return parser.parse_args()

colors={
        'metaspades' : {
                'line': 'royalblue',
                'circle' : 'darkblue'
                },
            'megahit' : {
                'line': 'indianred',
                'circle' : 'darkred'
                }
        }
        

def get_sample_id(data_dir):
    sample_id = data_dir.parent.parent.name
    return sample_id


def parse_time_info(time_txt):
    '''
    Get maximum mem and duration from the time file
    '''
    with open(time_txt, 'r') as fin:
        fields = fin.readline().split()
    # Convert to a datetime object
    runtime =  datetime.datetime.strptime(fields[0], "%H:%M:%S") 
    # Convert to a timedelta
    duration = datetime.timedelta(hours = runtime.hour,
                        minutes= runtime.minute,
                        seconds = runtime.second
                        )
    # Conver memory to Gbs
    max_mem = int(fields[1]) / 1024**2
    
    return duration, max_mem


def is_core_cmd(command_string):
    cmd_binary = command_string.split('/')[-1]
    
    if cmd_binary in ['spades-core', 'megahit_core']:
        return True
    else:
        return False


def parse_mem_txt(mem_txt):
    
    dic = {
            'timepoints': [],
            'tstamps': [],
            'mem': []
          }


    with open(mem_txt, 'r') as fin:
        # using proper datetime objects for easier plotting
        # Start is arbitrary
        start = datetime.datetime(
                year=2021, month=5, day=1, hour=0, minute=0, second = 0)
        timepoint = 0
        seconds = 0.0
        for line in fin:
            fields = line.split()
            if len(fields) == 1:
                # Time 0 - the core job hasn't been submitted yet
                if len(dic['timepoints']) == 0:
                    dic['timepoints'].append(timepoint)
                    dic['tstamps'].append(start)
                    dic['mem'].append(0.)
            # The actual command is this
            elif is_core_cmd(fields[3]) is True:
                # Increment the seconds
                seconds += 60.
                run_minute = start + datetime.timedelta(seconds=seconds)
                dic['tstamps'].append(run_minute)

                # Increment the index
                timepoint += 1
                dic['timepoints'].append(timepoint)

                # Calculate Memory in GB
                rss = int(fields[2]) / 1024**2                
                dic['mem'].append(rss)
            else:
                #print(fields)
                pass

    return dic


def runstats_plot(plot_data):

    sample_id = plot_data['sample_id']
    metaspades_data = plot_data['metaspades']
    metaspades_source = ColumnDataSource(
            data={
                'tstamps': metaspades_data['tstamps'],
                'mem' :  metaspades_data['mem']
                }
            )

    megahit_data=plot_data['megahit']
    megahit_source = ColumnDataSource(
            data={
                'tstamps': megahit_data['tstamps'],
                'mem' : megahit_data['mem']
                }
            )


    p = figure(title="Sample: {}".format(sample_id),
        x_axis_type="datetime",
        x_axis_label="Runtime (hours)",
        y_axis_label="Memory Usage (GB)",
        sizing_mode="stretch_width",
        toolbar_location="below",
        tools=["pan,wheel_zoom,box_zoom,hover,reset,save,help"],
        tooltips= [
            ("Time", "@x{%H:%M:%S}"),
            ("Memory", "@y")
            ]
        )

    p.circle(x=metaspades_data['tstamps'],
            y=metaspades_data['mem'],
            line_color=colors['metaspades']['circle'],
            fill_color=colors['metaspades']['circle'],
            name='metaspades_circles'
            )

    p.line(x='tstamps',
            y='mem',
            source = metaspades_source,
            legend_label='metaspades',
            line_width=2,
            line_color=colors['metaspades']['line'],
            line_alpha=0.8
            )

    p.circle(x=megahit_data['tstamps'],
            y=megahit_data['mem'],
            line_color=colors['megahit']['circle'],
            fill_color=colors['megahit']['circle'],
            name='megahit_circles'
            )

    p.line(x='tstamps',
            y='mem',
            source = megahit_source,
            legend_label='megahit',
            line_width=2,
            line_color=colors['megahit']['line'],
            line_alpha=0.8
            )

    p.xaxis[0].formatter = DatetimeTickFormatter(
        minutes="%M:%S",
        hours="%Hh",
        days="%Hh"
        )


    p.add_layout(p.legend[0],'right')
    hover_tool = p.select(type=HoverTool)
    hover_tool.names = [
            "metaspades_circles",
            "megahit_circles"
            ]
    hover_tool.formatters= { "@x" : "datetime"}

    return p

if __name__ == '__main__':
    args = parse_arguments()
    
    sample_id = get_sample_id(args.data_dir)

    metaspades_mem_txt = args.data_dir / Path("metaspades.mem.txt")
    metaspades_time_txt = args.data_dir / Path("metaspades.time.txt")
    metaspades_duration, metaspades_max_mem = parse_time_info(metaspades_time_txt)

    megahit_mem_txt = args.data_dir / Path("megahit.mem.txt")
    megahit_time_txt=args.data_dir / Path("megahit.time.txt")
    megahit_duration, megahit_max_mem = parse_time_info(megahit_time_txt)

    metaspades_data = parse_mem_txt(metaspades_mem_txt)
    megahit_data = parse_mem_txt(megahit_mem_txt)

    metaspades_data['duration'] = metaspades_duration
    metaspades_data['max_mem'] = metaspades_max_mem

    megahit_data['duration'] = megahit_duration
    megahit_data['max_mem'] = megahit_max_mem

    plot_data = {
            'sample_id': sample_id,
            'megahit': megahit_data,
            'metaspades': metaspades_data
            }
    
    runstats_plot = runstats_plot(plot_data)
    runstats_html = file_html(runstats_plot, CDN, '{}_runstats'.format(sample_id))
    args.out_html.write_text(runstats_html)



