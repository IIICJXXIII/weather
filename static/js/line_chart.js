var data_index=0;
//console.log(line_data[provinces[data_index]]);
var myselect=d3.select('.listbox')
    .append('select')
    .attr('id','test')
    .attr('height',16)
    .style('font-size',6)
    .on('change',select_list);
//列表框中添加选项
var myoption=myselect.selectAll('.option')
    .data(provinces)
    .enter()
    .append('option')
    .attr('value',function(d,i){return i;})
    .text(function(d){return d;});

//自定义选项改变的事件，当选项改变时，删除掉svg所有元素，同时获取选项的索引值，并重新绘制图形
function select_list(){
    data_index=this.selectedIndex;
    console.log(data_index);
    line_chart();
};

function line_chart(){
    var myChart = echarts.init(document.getElementById('id1'));
    var option = {
      title: {
        text: '2022年'+provinces[data_index]+'平均气温和预测情况',
        textStyle:text_style,
        left:'center',
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        bottom:'5%',
        textStyle:{
            color:"#FFF",
            fontSize: 10,
        },
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        axisLabel:{
            color: 'white',
            fontSize: 6,
            formatter: '{value} 月'
        },
        axisLine:{
            lineStyle:{
                color:"#FFF",
                width:0.5,
            },
        },
        data: line_data[provinces[data_index]].month
      },
      yAxis: {
        type: 'value',
        splitLine:false,
        axisLabel:{
            color: 'white',
            fontSize: 6,
            formatter: '{value} °C'
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
          name: '实际气温',
          type: 'line',
          data: line_data[provinces[data_index]].temp,
          markPoint: {
            symbolSize:30,
            label:{
                fontSize:8,
            },
            data: [
              { type: 'max', name: 'Max' },
              { type: 'min', name: 'Min' }
            ]
          },
        },
        {
          name: '预测气温',
          type: 'line',
          data: line_data[provinces[data_index]].temp_forecast,
        }
      ]
    };
    myChart.setOption(option)
}

