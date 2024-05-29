#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

import flet as ft
from flet_core import ControlEvent, DataColumnSortEvent

from service.common import S_Text, build_tab_container, human_size
from service.es_service import es_service


class Broker(object):
    """
    Cluster页的组件
    kafka版本、操作系统、集群信息等等
    """

    def __init__(self):
        # page
        self.nodes_tmp = []
        self.page_num = 1
        self.page_size = 10
        self.page_label = None
        # order
        self.reverse = None
        self.cluster_table_rows = None
        self.stats = None
        self.nodes = None
        self.cluster_table = None


        # 先加载框架
        self.stats_tab = ft.Tab(
            text="基础信息", content=ft.Column(), icon=ft.icons.INFO_OUTLINE
        )

        self.node_tab = ft.Tab(
            text='集群节点列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.config_tab = ft.Tab(
            text='Broker配置', content=ft.Container(content=ft.Text("请从broker的配置按钮进入", size=20)),
            icon=ft.icons.CONSTRUCTION_OUTLINED,
        )

        self.tab = ft.Tabs(
            tabs=[
                self.node_tab,
                self.stats_tab,
                # self.config_tab,
            ],
            expand=True,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page=None):
        self.init_data()
        self.init_rows()
        self.init_table()

    def init_data(self):
        self.nodes = es_service.get_nodes()
        self.stats = es_service.get_stats()
        # page
        self.nodes_tmp = self.nodes[:self.page_size]

    def init_rows(self):
        # page
        offset = (self.page_num - 1) * self.page_size
        self.cluster_table_rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(offset + i + 1)),
                    ft.DataCell(S_Text(f"{_node['ip']}")),
                    ft.DataCell(S_Text(f"{_node['name']}")),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['heap.current']}/{_node['heap.max']}={_node['heap.percent']}%",
                                    size=12),
                            ft.ProgressBar(value=float(_node['heap.percent']) / 100.0,
                                           color="green" if float(_node['heap.percent']) < 70 else "amber" if float(
                                               _node['heap.percent']) < 80 else "red")
                        ], alignment=ft.MainAxisAlignment.CENTER), data=float(_node['heap.percent'])),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['ram.current']}/{_node['ram.max']}={_node['ram.percent']}%", size=12),
                            ft.ProgressBar(value=float(_node['ram.percent']) / 100.0,
                                           color="green" if float(_node['ram.percent']) < 70 else "amber" if float(
                                               _node['ram.percent']) < 80 else "red", )
                        ], alignment=ft.MainAxisAlignment.CENTER), data=float(_node['ram.percent'])),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['disk.used']}/{_node['disk.total']}={_node['disk.used_percent']}%",
                                    size=12),
                            ft.ProgressBar(value=float(_node['disk.used_percent']) / 100.0, color="green" if float(
                                _node['disk.used_percent']) < 70 else "amber" if float(
                                _node['disk.used_percent']) < 80 else "red", )
                        ], alignment=ft.MainAxisAlignment.CENTER), data=float(_node['disk.used_percent'])),
                    ft.DataCell(S_Text(f"{_node['node.role']}")),
                    ft.DataCell(S_Text(f"{_node['master']}")),
                    ft.DataCell(S_Text(f"{_node['cpu']}")),
                    ft.DataCell(S_Text(f"{_node['load_5m']}")),
                ]
            ) for i, _node in enumerate(self.nodes_tmp)  # page
        ]

    def init_table(self):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available kafka connection first!"

        # 节点列表表格
        self.cluster_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("序号")),
                ft.DataColumn(S_Text("ip")),
                ft.DataColumn(S_Text("name")),
                ft.DataColumn(S_Text("堆使用率(点右侧排序)"), on_sort=self.on_sort),
                ft.DataColumn(S_Text("内存使用率(点右侧排序)"), on_sort=self.on_sort),
                ft.DataColumn(S_Text("磁盘使用率(点右侧排序)"), on_sort=self.on_sort),
                ft.DataColumn(S_Text("角色")),
                ft.DataColumn(S_Text("是否为master")),
                ft.DataColumn(S_Text("cpu")),
                ft.DataColumn(S_Text("5分钟负载")),

            ],
            rows=self.cluster_table_rows,
            column_spacing=20,
            expand=True
        )
        stats_nodes = self.stats['nodes']
        self.node_tab.content = build_tab_container(
            col_controls=[

                ft.Row([S_Text(
                    f"节点总数：{stats_nodes['count']['total']}  协调节点数：{stats_nodes['count']['coordinating_only']}  "
                    f"存储节点数：{stats_nodes['count']['data']}  可写节点数：{stats_nodes['count']['ingest']}  "
                    f"允许主节点数：{stats_nodes['count']['master']}  仅投票节点数：{stats_nodes['count']['voting_only']}"
                    , weight=ft.FontWeight.BOLD)]),
                ft.Row([
                    self.cluster_table,
                ]),
                # page
                ft.Row(
                    [
                        # 翻页图标和当前页显示
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_size=20,
                            on_click=self.page_prev,
                            tooltip="上一页",
                        ),
                        ft.Text(f"{self.page_num}/{int(len(self.nodes) / self.page_size) + 1}"),
                        ft.IconButton(
                            icon=ft.icons.ARROW_FORWARD,
                            icon_size=20,
                            on_click=self.page_next,
                            tooltip="下一页",
                        ),
                        ft.Text(f"每页{self.page_size}条"),
                        ft.Slider(min=5, max=55, divisions=10, round=1,value=self.page_size, label="{value}", on_change_end=self.page_size_change),

                    ]
                )
            ]
        )

        # card集群基本信息
        stats_indices = self.stats['indices']
        self.stats_tab.content = build_tab_container(
            col_controls=[
                ft.Row(
                    [
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("分片", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[ft.DataCell(S_Text("分片总数")),
                                       ft.DataCell(S_Text(f"{stats_indices['count']}")),
                                       ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("主分片数")),
                                              ft.DataCell(
                                                  S_Text(f"{stats_indices['shards']['primaries']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("副本分片数")),
                                              ft.DataCell(
                                                  S_Text(f"{stats_indices['shards']['replication']}")), ]),
                            # ft.DataRow(cells=[ft.DataCell(S_Text("最少索引分片数")),
                            #                   ft.DataCell(
                            #                       S_Text(
                            #                           f"{stats_indices['shards']['index']['shards']['min']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("最大索引分片数")),
                                              ft.DataCell(
                                                  S_Text(
                                                      f"{stats_indices['shards']['index']['shards']['max']}")), ]),
                            # ft.DataRow(cells=[ft.DataCell(S_Text("平均索引分片数")),
                            #                   ft.DataCell(
                            #                       S_Text(
                            #                           f"{stats_indices['shards']['index']['shards']['avg']}")), ]),
                        ])),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("文档、存储、缓存", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(S_Text("文档总数")),
                                    ft.DataCell(S_Text(f"{stats_indices['docs']['count']}")),

                                ]),
                            ft.DataRow(
                                cells=[ft.DataCell(S_Text("已删除文档数")),
                                       ft.DataCell(S_Text(f"{stats_indices['docs']['deleted']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("存储大小")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['store']['size_in_bytes'])}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("字段缓存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['fielddata']['memory_size_in_bytes'])}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("查询缓存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['query_cache']['memory_size_in_bytes'])}")), ])
                        ])),

                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("段", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(S_Text("段总数")),
                                    ft.DataCell(S_Text(f"{stats_indices['segments']['count']}")),

                                ]),
                            ft.DataRow([ft.DataCell(S_Text("段总占用内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['segments']['memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("terms词项内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['terms_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("字段内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['stored_fields_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("向量内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['term_vectors_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("norms归一化因子内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['term_vectors_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("数值型和地理坐标等点类型内存")), ft.DataCell(
                                S_Text(
                                    f"{human_size(stats_indices['segments']['points_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("Doc Values内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['doc_values_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("索引写入占用内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['index_writer_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("固定位集合内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['fixed_bit_set_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("ID唯一性的最大安全时间戳")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['max_unsafe_auto_id_timestamp'])}"))]),
                        ])),
                    ], vertical_alignment=ft.CrossAxisAlignment.START
                ),
            ]
        )

    def page_prev(self, e):
        # page
        if self.page_num == 1:
            return
        self.page_num -= 1

        offset = (self.page_num - 1) * self.page_size
        self.nodes_tmp = self.nodes[offset:offset + self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def page_next(self, e):
        # page
        # 最后一页则return
        if self.page_num * self.page_size >= len(self.nodes):
            return
        self.page_num += 1
        offset = (self.page_num - 1) * self.page_size
        self.nodes_tmp = self.nodes[offset:offset + self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def page_size_change(self, e):
        # page
        self.page_size = int(e.control.value)
        self.nodes_tmp = self.nodes[:self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def on_sort(self, e: DataColumnSortEvent):
        """
        排序
        """
        # order
        # 反转true false
        self.reverse = not self.reverse
        self.cluster_table_rows = sorted(self.cluster_table_rows, key=lambda x: x.cells[e.column_index].data, reverse=self.reverse)
        self.init_table()
        e.page.update()

    def show_config_tab(self, e: ControlEvent):
        """
        打开侧边栏
        """
        e.control.disabled = True
        broker_id = e.control.data
        configs = es_service.get_configs(res_type='broker', name=broker_id)

        _col = ft.ListView(expand=True, spacing=10, padding=10)

        for config in configs:
            config_names = f"{config['config_names']}"
            config_value = f"{config['config_value']}" if config['config_value'] is not None else ""
            _col.controls.append(ft.Row([
                ft.Text(f" • {config_names}", style=ft.TextStyle(weight=ft.FontWeight.BOLD), ),
                ft.Text(f"    值：{config_value}"),
            ]))
        self.config_tab.content = _col

        self.tab.selected_index = 2
        e.control.disabled = False
        e.page.update()