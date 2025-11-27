function bar_chart(){
    var myChart = echarts.init(document.getElementById('id5'));
    option = {
      title:{
            text:'2022年各城市'+month_index+'月份降水量TOP10',
            textStyle:text_style,
            left: 'center',
          },
      grid:{
        bottom:'8%',
        top:'10%',
        left:'10%'
      },
      yAxis: {
        type: 'category',
        inverse:true,
        boundaryGap:true,
        axisLabel:{
            color: 'white',
            fontSize: 8,
        },
        data: (bar_data[month_index] ? bar_data[month_index].city : [])
      },
      xAxis: {
        type: 'value',
        splitLine:false,
        axisLabel:{
            color: 'white',
            fontSize: 8,
        },
      axisLine:{
            show:true,
            lineStyle:{
                color:"#FFF",
                width:0.5,
            },
        },
      axisTick:{
            show:true,
        }
      },

      series: [
        {
          data: (bar_data[month_index] ? bar_data[month_index].precipitation : []),
          type: 'bar',
          showBackground: true,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
      },
        }
      ]
    };
    myChart.setOption(option);
}