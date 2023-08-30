#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NAME:
    emqx5-ee-dashboard.py

DESCRIPTION:
    This script creates Grafana dashboards using Grafanalib, and a static table
    which defines metrics/dashboards.

    The resulting dashboard can be easily uploaded to Grafana with associated script:

        upload_grafana_dashboard.sh

USAGE:
    Create and upload the dashboard:

    ./emqx5-ee-dashboard.py > dash.json
    ./upload_grafana_dashboard.sh dash.json

"""

import textwrap
import argparse
import sys
import io
import grafanalib.core as G
from grafanalib._gen import write_dashboard

DEFAULT_TITLE = "EMQX5 Enterprise"

# Simple example of table drive - good to enhance with Grid position, Legend etc.
metrics = [
    {

        'section': 'General'
    },
    {
        'title': 'Cluster Message Rate',
        'targets': [
            {
                'legendFormat': 'Msg Input Period Second',
                'exp': 'emqx_messages_input_period_second{cluster=\"$cluster\"}',
            },
            {
                'legendFormat': 'Msg Output Period Second',
                'exp': 'emqx_messages_output_period_second{cluster=\"$cluster\"}',
            },
        ],
    },
    {
        'title': 'Nodes Running',
        'targets': [
            {
                'legendFormat': 'Running',
                'exp': 'max(emqx_cluster_nodes_running{instance=~\".*\", cluster=\"$cluster\"})',


            },
            {
                'legendFormat': 'Stopped',
                'exp': 'max(emqx_cluster_nodes_stopped{instance=~\".*\", cluster=\"$cluster\"})',
            }
        ]
    },
]


class CreateDashboard():
    "See module doc string for details"

    def __init__(self, *args, **kwargs):
        self.parse_args(__doc__, args)

    def parse_args(self, doc, args):
        "Common parsing and setting up of args"
        desc = textwrap.dedent(doc)
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=desc)
        parser.add_argument('-t', '--title', default=DEFAULT_TITLE,
                            help="Dashboard title. Default: " + DEFAULT_TITLE)
        self.options = parser.parse_args(args=args)

    def run(self):
        templateList = [
            G.Template(
                name="datasource",
                label="datasource",
                query="prometheus",
                type="datasource",
                includeAll=False,
                multi=False,
                options=[],
                refresh=1,
                regex="",
                hide=0,
            ),
            G.Template(
                name="cluster",
                type="query",
                dataSource="$datasource",
                query="label_values(up, cluster)",
                includeAll=False,
                multi=False,
                options=[],
                refresh=1,
                regex="",
                hide=0,
            ),
        ]

        dashboard = G.Dashboard(title=self.options.title,
                                time=G.Time(start='now-5m', end='now'),
                                refresh='5s',
                                tags=['test'],
                                templating=G.Templating(list=templateList))

        # Simple table processing - could be enhanced to use GridPos etc.
        for metric in metrics:
            if 'section' in metric:
                dashboard.rows.append(G.Row(title=metric['section'], showTitle=True))
                continue
            ts = G.TimeSeries(
                title=metric['title'],
                dataSource='prometheus',
                scaleDistributionType='linear',
                legendDisplayMode='table',
                legendPlacement='bottom',
                tooltipMode='multi',
                lineInterpolation='smooth',
                showPoints='never',
                gradientMode='opacity',
                legendCalcs=[
                    "lastNotNull",
                    "min",
                    "max",
                    "mean",
                    "sum",
                ],
                unit='short',
                gridPos=G.GridPos(h=6, w=5, x=0, y=0),
            )
            ref_id = 'A'
            for target in metric['targets']:
                ts.targets.append(G.Target(
                    expr=target['exp'],
                    legendFormat=target['legendFormat'],
                    refId=ref_id))
                ref_id = chr(ord(ref_id) + 1)
            dashboard.rows[-1].panels.append(ts)

        # Auto-number panels - returns new dashboard
        dashboard = dashboard.auto_panel_ids()

        s = io.StringIO()
        write_dashboard(dashboard, s)
        print("""
        %s
        """ % s.getvalue())


if __name__ == '__main__':
    """ Main Program"""
    obj = CreateDashboard(*sys.argv[1:])
    obj.run()
