from grafanalib.core import (
    Dashboard, Template, Templating, TimeSeries,
    GaugePanel, Target, GridPos,
    OPS_FORMAT
)

dashboard = Dashboard(
    title="EMQX-Enterprise 5 message dashboard",
    description="EMQX-Enterprise 5 message dashboard",
    tags=["emqx"],
    timezone="browser",
    templating=Templating(list=[
        Template(
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
        Template(
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
        Template(
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
    ]),
    panels=[
        TimeSeries(
            title="Messge Sent Rate",
            dataSource='prometheus',
            targets=[
                Target(
                    expr='sum by(instance) (irate(emqx_messages_sent{cluster="$cluster", instance=~"$node"}[$__rate_interval]))',
                    legendFormat="{{ instance }}",
                    refId='A',
                ),
            ],
            legendDisplayMode="table",
            legendPlacement="bottom",
            legendCalcs=[
                "lastNotNull",
                "min",
                "max",
                "mean",
                "sum",
            ],
            unit=OPS_FORMAT,
            gridPos=GridPos(h=8, w=8, x=0, y=0),
        ),
        TimeSeries(
            title="Messge Received Rate",
            dataSource='prometheus',
            targets=[
                Target(
                    expr='sum by(instance) (irate(emqx_messages_received{cluster=\"$cluster\", instance=~\"$node\"}[$__rate_interval]))',
                    legendFormat="{{ instance }}",
                    refId='B',
                ),
            ],
            legendDisplayMode="table",
            legendPlacement="bottom",
            legendCalcs=[
                "lastNotNull",
                "min",
                "max",
                "mean",
                "sum",
            ],
            unit=OPS_FORMAT,
            gridPos=GridPos(h=8, w=8, x=0, y=0),
        ),
        TimeSeries(
            title="Messge Dropped Rate",
            dataSource='prometheus',
            targets=[
                Target(
                    expr='sum by(instance) (irate(emqx_messages_dropped{cluster=\"$cluster\", instance=~\"$node\"}[$__rate_interval]))',
                    legendFormat="{{ instance }}",
                    refId='C',
                ),
            ],
            legendDisplayMode="table",
            legendPlacement="bottom",
            legendCalcs=[
                "lastNotNull",
                "min",
                "max",
                "mean",
                "sum",
            ],
            unit=OPS_FORMAT,
            gridPos=GridPos(h=8, w=8, x=0, y=0),
        ),
    ],
).auto_panel_ids()
