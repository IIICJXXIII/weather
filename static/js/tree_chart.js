function tree_chart(){
    var myChart = echarts.init(document.getElementById('id2'));
    option = {
      title:{
            text:'2022年各省份'+month_index+'月份气压情况',
            textStyle:text_style,
            left: 'center',
          },
      series: [
        {
            type: 'treemap',
            roam:false,
            nodeClick:false,
            breadcrumb:false,
            left:0,
            right:0,
            top:30,
            bottom:0,
            data: tree_data[month_index] || [],
        },
      ]
    };
    myChart.setOption(option);
}