<%page args = "highest_score, your_score, lowest_score, mean_score, graph_div_id, **kwargs"/>
<%!
    from openedx.core.djangolib.js_utils import(
        dump_js_escaped_json, js_escaped_string
    )
%>

        $(function () {
            function showTooltip(x, y, contents) {
                $("#tooltip").remove();
                var $tooltip_div = $('<div id="tooltip"></div>').css({
                    position: 'absolute',
                    display: 'none',
                    top: y + 5,
                    left: x + 15,
                    border: '1px solid #000',
                    padding: '4px 6px',
                    color: '#fff',
                    'background-color': '#222',
                    opacity: 0.90
                });

                edx.HtmlUtils.setHtml(
                    $tooltip_div,
                    edx.HtmlUtils.HTML(contents)
                );

                edx.HtmlUtils.append(
                    $('body'),
                    edx.HtmlUtils.HTML($tooltip_div)
                );

                $('#tooltip').fadeIn(200);
            }
            var mean_index;
            var your_index;
            if(${ your_score } >= ${ mean_score }){
                your_index = 3;
                mean_index = 4.5;
            } else {
                mean_index = 3;
                your_index = 4.5;
            }
            var series = [
                {
                    'color': '#b72121',
                    'data': [
                        [1.5, ${ highest_score }]
                    ],
                    'label': "highest"
                },
                {
                    'color': '#b72121',
                    'data': [
                        [mean_index, ${ mean_score }]
                    ],
                    'label': "mean"
                },
                {
                    'color': '#13ca09',
                    'data': [
                        [your_index, ${ your_score }]
                    ],
                    'label': "score"
                },
                {
                    'color': '#b72121',
                    'data': [
                        [6, ${ lowest_score }]
                    ],
                    'label': "lowest"
                }
            ]
            var ticks = [
                [
                    1.5, "Highest Score"
                ],
                [
                    your_index, "Your Score"
                ],
                [
                    mean_index, "Mean Score"
                ],
                [
                    6, "Lowest Score"
                ]
            ]
            var detail_tooltips = {
                'highest': [
                    'Hightest score is ' + ${ highest_score } * 100 + '%'
                ],
                'mean': [
                    'Mean Score is ' + ${ mean_score } * 100 + '%'
                ],
                'score': [
                    'Your score is ' + ${ your_score } * 100 + '%'
                ],
                'lowest': [
                    'Lowest score is ' + ${ lowest_score } * 100 + '%'
                ]
            }
            var grade_cutoff_ticks = [
                [
                    0, "0%"
                ],
                [
                    0.2, "20%"
                ],
                [
                    0.4, "40%"
                ],
                [
                    0.6, "60%"
                ],
                [
                    0.8, "80%"
                ],
                [
                    1, "100%"
                ]
            ]

            // if(${ your_score } > ${ mean_score }){
            //     series[1].data.push([3, ${ your_score }]);
            //     series[1].data.push([4.5, ${ mean_score }]);
            //     detail_tooltips.score = [
            //         'Your score is ' + ${ your_score } * 100 + '%',
            //         'Mean Score is ' + ${ mean_score } * 100 + '%'
            //     ]
            //     ticks = [
            //         [
            //             1.5, "Highest Score"
            //         ],
            //         [
            //             3, "Your Score"
            //         ],
            //         [
            //             4.5, "Mean Score"
            //         ],
            //         [
            //             6, "Lowest Score"
            //         ]
            //     ]
            // } else {
            //     series[1].data.push([3, ${ mean_score }]);
            //     series[1].data.push([4.5, ${ your_score }]);
            //     detail_tooltips = [
            //         'Mean Score is ' + ${ mean_score } * 100 + '%',
            //         'Your score is ' + ${ your_score } * 100 + '%'
            //     ]
            //     ticks = [
            //         [
            //             1.5, "Highest Score"
            //         ],
            //         [
            //             3, "Mean Score"
            //         ],
            //         [
            //             4.5, "Your Score"
            //         ],
            //         [
            //             6, "Lowest Score"
            //         ]
            //     ]
            // }

            var yAxisTooltips = {};

            var ascending_grades = grade_cutoff_ticks.map(function (el) { return el[0]; }); // Percentage point (in decimal) of each grade cutoff
            ascending_grades.sort();

            var colors = ['#f3f3f3', '#e9e9e9', '#ddd', '#c9c9c9'];
            var markings = [];
            for (var i = 1; i < ascending_grades.length - 1; i++) // Skip the i=0 marking, which starts from 0%
                markings.push({ yaxis: { from: ascending_grades[i], to: ascending_grades[i + 1] }, color: colors[(i - 1) % colors.length] });

            var options = {
                series: {
                    stack: true,
                    lines: {
                        show: false,
                        steps: false
                    },
                    bars: {
                        show: true,
                        barWidth: 0.8,
                        align: 'center',
                        lineWidth: 0,
                        fill: .8
                    }
                },
                xaxis: {
                    tickLength: 0,
                    min: 0.0,
                    max: 8,
                    ticks: ticks,
                    labelAngle: 90
                },
                yaxis: {
                    ticks: grade_cutoff_ticks,
                    min: 0.0,
                    max: 1.0,
                    labelWidth: 100
                },
                grid: {
                    hoverable: true,
                    clickable: true,
                    borderWidth: 1,
                    markings: markings
                },
                legend: {
                    show: false
                }
            };

            var $grade_detail_graph = $("#${graph_div_id | n, js_escaped_string}");
            if ($grade_detail_graph.length > 0) {
                var plot = $.plot($grade_detail_graph, series, options);



                $grade_detail_graph.find('.xAxis .tickLabel').attr('tabindex', '0').focus(function (event) {
                    var $target = $(event.target), srElements = $target.find('.sr'), srText = "", i;
                    if (srElements.length > 0) {
                        for (i = 0; i < srElements.length; i++) {
                            srText += srElements[i].innerHTML;
                        }
                        // Position the tooltip slightly above the tick label.
                        showTooltip($target.offset().left - 70, $target.offset().top - 120, srText);
                    }
                });

                $grade_detail_graph.focusout(function () {
                    $("#tooltip").remove();
                });
            }


            var previousPoint = null;
            $grade_detail_graph.bind("plothover", function (event, pos, item) {
                if (item) {
                    if (previousPoint != (item.dataIndex, item.seriesIndex)) {
                        previousPoint = (item.dataIndex, item.seriesIndex);

                        if (item.series.label in detail_tooltips) {
                            var series_tooltips = detail_tooltips[item.series.label];
                            if (item.dataIndex < series_tooltips.length) {
                                showTooltip(item.pageX, item.pageY, series_tooltips[item.dataIndex]);
                            }
                        }

                    }
                } else {
                    $("#tooltip").remove();
                    previousPoint = null;
                }
            });
        });
