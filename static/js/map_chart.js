function map_chart(){
    var container = document.getElementById('id3');
    if (!container) {
        return;
    }

    var myChart = echarts.init(container);
    var mapName = 'china';
    var geoCoordMap = {};

    myChart.showLoading();
    var mapFeatures = echarts.getMap(mapName).geoJson.features;
    myChart.hideLoading();

    mapFeatures.forEach(function(v) {
        geoCoordMap[v.properties.name] = v.properties.cp;
    });

    function convertData(data) {
        if (!data || !data.length) {
            return [];
        }
        var res = [];
        for (var i = 0; i < data.length; i++) {
            var geoCoord = geoCoordMap[data[i].name];
            if (geoCoord) {
                res.push({
                    name: data[i].name,
                    value: geoCoord.concat(data[i].value)
                });
            }
        }
        return res;
    }

    var option = {
        title: {
            text: "2022年各省份" + month_index + "月份平均温度和风速情况",
            textStyle: text_style,
            top: '5%',
            left: 'center'
        },
        tooltip:{
            show:true,
            valueFormatter:(value) => value + '°C'
        },
        visualMap: {
            show: true,
            left: '8%',
            top: 'bottom',
            seriesIndex: [1],
            pieces:[
                {gt:25,label:'25°C以上',color:'#FF3300'},
                {gt:20,lte:25,label:'20°C-25°C',color:'#FF9966'},
                {gt:10,lte:20,label:'10°C-20°C',color:'#66FF33'},
                {gt:0,lte:10,label:'0°C-10°C',color:'#66CCFF'},
                {gt:-10,lte:0,label:'-10°C-0°C',color:'#0066FF'},
                {lte:-10,label:'-10°C以下',color:'#000099'}
            ],
            textStyle:{
                color:'white'
            }
        },
        geo: {
            show: true,
            map: mapName,
            roam: false
        },
        series: [{
                name: '散点',
                type: 'scatter',
                coordinateSystem: 'geo',
            data: convertData(map_data2[month_index]),
                label: {
                    normal: {
                        formatter: '{b}',
                        position: 'right',
                        show: true,
                        fontSize:8
                    },
                    emphasis: {
                        show: true
                    }
                }
            },
            {
                name:'本月温度',
                type: 'map',
                map: mapName,
                geoIndex: 0,
                aspectScale: 0.5,
                showLegendSymbol: false,
                label: {
                    normal: {
                        show: true
                    },
                    emphasis: {
                        show: false,
                        textStyle: {
                            color: '#fff'
                        }
                    }
                },
                roam: true,
                animation: false,
                data: map_data1[month_index] || []
            },
            {
                name: '散点',
                type: 'effectScatter',
                coordinateSystem: 'geo',
                data: convertData(map_data2[month_index]),
                symbolSize: function(val) {
                    return val[2]*5;
                },
                showEffectOn: 'render',
                rippleEffect: {
                    period: 4,
                    brushType: 'stroke',
                    scale: 4
                },
                hoverAnimation: true,
                label: {
                    normal: {
                        formatter: '{b}',
                        position: 'left',
                        show: false
                    }
                },
                itemStyle: {
                    normal: {
                        color: 'yellow',
                        shadowBlur: 10,
                        shadowColor: 'yellow'
                    }
                },
                zlevel: 1
            }

        ]
    };
    myChart.setOption(option);
    window.addEventListener("resize", function() {
        myChart.resize();
    });
}
