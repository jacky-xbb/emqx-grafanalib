#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NAME:
    table-example-dashboard.py

DESCRIPTION:
    This script creates Grafana dashboards using Grafanalib, and a static table
    which defines metrics/dashboards.

    The resulting dashboard can be easily uploaded to Grafana with associated script:

        upload_grafana_dashboard.sh

USAGE:
    Create and upload the dashboard:

    ./table-example-dashboard.py --title "My python dashboard" > dash.json
    ./upload_grafana_dashboard.sh dash.json

"""

import textwrap
import argparse
import sys
import io
import grafanalib.core as G
from grafanalib._gen import write_dashboard

DEFAULT_TITLE = "EMQX Message"

# Simple example of table drive - good to enhance with Grid position, Legend etc.
metrics = [
    {
        'section': 'EMQX Message'
    },
    {
        'title': 'Message Sent Rate',
        'expr': ['sum by(instance) (irate(emqx_messages_sent{cluster="$cluster", instance=~"$node"}[$__rate_interval]))'],
    },
    {
        'title': 'Message Received Rate',
        'expr': ['sum by(instance) (irate(emqx_messages_received{cluster=\"$cluster\", instance=~\"$node\"}[$__rate_interval]))'],
    },
    {
        'title': 'Message Dropped Rate',
        'expr': ['sum by(instance) (irate(emqx_messages_dropped{cluster=\"$cluster\", instance=~\"$node\"}[$__rate_interval]))'],
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
            G.Template(
                name="node",
                type="query",
                dataSource="$datasource",
                query="label_values(up{from=\"emqx\",cluster=\"$cluster\"}, instance)",
                includeAll=True,
                multi=True,
                options=[],
                refresh=1,
                regex="",
                hide=0,
            ),
        ]

        dashboard = G.Dashboard(title=self.options.title,
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
                fillOpacity=18,
                gradientMode='opacity',
                legendCalcs=[
                    "lastNotNull",
                    "min",
                    "max",
                    "mean",
                    "sum",
                ],
                unit='short',
                gridPos=G.GridPos(h=8, w=8, x=0, y=0),
            )
            ref_id = 'A'
            for texp in metric['expr']:
                ts.targets.append(G.Target(
                    expr=texp,
                    legendFormat="{{ instance }}",
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
