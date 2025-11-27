function word_chart(){
    var myChart = echarts.init(document.getElementById('id4'));
    var option = {
        title: {
            text: '2022年各城市'+month_index+'月份气温词云',
            x: 'center',
            textStyle:text_style,

        },
        tooltip: {},
        series: [{
            type: 'wordCloud',
            gridSize: 1,//字符间距
            sizeRange: [2, 20],  //字体大小
            shape: 'pentagon', //形状
            width: 320,
            height: 250,
            grid: {
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: '#fff',
                width: "auto", //图例宽度
                height: "100%", //图例高度
            },

            drawOutOfBound: false,
            textStyle: {

                color: function() {
                    return 'rgb(' + [Math.round(Math.random() * 160),
                            Math.round(Math.random() * 160),
                            Math.round(Math.random() * 160)
                        ]
                        .join(',') + ')';
                },
                emphasis: {
                    shadowBlur: 10,
                    shadowColor: '#333'
                }
            },
            data: word_data[month_index] || []
        }]
    };
    myChart.setOption(option);
}