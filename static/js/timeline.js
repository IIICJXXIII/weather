function timeline() {
    // 1. 获取容器
    var chartDom = document.getElementById('time_line');
    if (!chartDom) {
        console.error("找不到时间线容器 time_line");
        return;
    }
    var myChart = echarts.init(chartDom);

    // 2. 定义月份
    var months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

    // 3. 配置项
    var option = {
        timeline: {
            axisType: 'category',
            autoPlay: true,           // 默认开启自动播放
            playInterval: time_interval, // 使用全局变量定义的间隔 (5000ms)
            data: months,
            currentIndex: month_index - 1, // 同步当前月份

            // 样式调整
            left: '5%',
            right: '5%',
            bottom: 0,
            height: 40,

            // 隐藏控制按钮 (如果你想让用户能暂停，可以设为 true)
            controlStyle: {
                show: false
            },

            // 文字样式
            label: {
                color: '#fff',
                interval: 0
            },
            // 线条样式
            lineStyle: {
                color: '#00C6FB'
            },
            itemStyle: {
                color: '#00C6FB'
            },
            checkpointStyle: {
                color: '#00C6FB',
                borderColor: '#fff'
            }
        }
    };

    // 4. 渲染图表
    myChart.setOption(option);

    // 5. 【关键新增】监听时间轴切换事件
    myChart.on('timelinechanged', function (params) {
        // params.currentIndex 是用户点击的索引 (0-11)
        // 将其转换为对应的月份 (1-12)
        var clickMonth = params.currentIndex + 1;

        // 如果点击的月份和当前显示的月份不一致，说明是用户手动切换的
        if (clickMonth !== month_index) {
            console.log("用户切换到了: " + clickMonth + "月");

            // 更新全局变量
            month_index = clickMonth;

            // 更新全局指针 (配合 total_control.js 的逻辑)
            if (typeof month_keys !== 'undefined') {
                month_pointer = month_keys.indexOf(month_index);
            }

            // 立即刷新所有图表
            if (typeof render_all === 'function') {
                render_all();
            }
        }
    });

    // 6. 响应窗口大小变化
    window.addEventListener("resize", function() {
        myChart.resize();
    });
}