// 1. 获取可用月份逻辑
// 优先使用后端传入的 months，次之使用 map_data1 的 key，最后 fallback 到 1-12
var month_keys = [];
if (typeof months !== 'undefined' && months && months.length) {
    month_keys = months.slice();
} else if (typeof map_data1 !== 'undefined') {
    month_keys = Object.keys(map_data1).map(function(key){ return parseInt(key); });
}
if (!month_keys.length) {
    month_keys = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
}
// 确保月份按顺序排列
month_keys.sort(function(a, b){ return a - b; });

// 2. 初始化 month_index
if (typeof month_index === 'undefined' || month_keys.indexOf(month_index) === -1) {
    month_index = month_keys[0];
}

// 3. 初始化指针
var month_pointer = month_keys.indexOf(month_index);
if (month_pointer < 0) {
    month_pointer = 0;
    month_index = month_keys[0];
}

// 4. 渲染所有动态图表 (随时间变化的图表)
function render_all() {
    // 使用 typeof 检查，防止因为还没写某个图表的 js 文件导致全屏报错
    if (typeof map_chart === 'function') map_chart();
    if (typeof tree_chart === 'function') tree_chart();
    if (typeof word_chart === 'function') word_chart();
    if (typeof bar_chart === 'function') bar_chart();

    // 如果你希望时间轴的高亮块也跟随这个定时器跳动，可以取消下面这行的注释
    // if (typeof timeline === 'function') timeline();
}

// 5. 全局时间控制器
function month_index_charge() {
    // 指针循环 +1
    month_pointer = (month_pointer + 1) % month_keys.length;
    // 更新全局月份变量
    month_index = month_keys[month_pointer];
    // 重绘所有图表
    render_all();
}

// 6. 页面加载时的初始渲染
render_all();

// 渲染时间轴 (静态组件，通常只初始化一次)
if (typeof timeline === 'function') timeline();

// 渲染折线图 (静态组件，显示全年趋势，通常只初始化一次)
if (typeof line_chart === 'function') line_chart();

// 7. 启动定时器
setInterval(month_index_charge, time_interval);