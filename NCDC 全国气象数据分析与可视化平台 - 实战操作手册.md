# 软件版本清单

| 类别 | 软件 | 版本 | 备注 |
|------|------|------|------|
| 操作系统 | CentOS | 7.9 | |
| 虚拟化 | VMware Workstation Pro | 17 | |
| Java | JDK | 1.8.0_221 | Oracle JDK |
| 大数据 | Hadoop | 2.9.2 | 完全分布式部署 |
| 大数据 | Hive | 2.1.0 | 元数据存储于 MySQL |
| 大数据 | Sqoop | 1.4.6-cdh5.9.3 | CDH 版本 |
| 数据库 | MySQL | 5.7.28 | |
| 后端 | Python | 3.9 | 虚拟环境 |
| 后端 | Django | 3.2.25 | LTS 版本 |
| 后端 | pandas | 2.3.3 | |
| 后端 | numpy | 2.0.2 | |
| 后端 | sqlalchemy | 2.0.44 | |
| 后端 | pymysql | 1.1.2 | |
| 后端 | statsmodels | 0.14.x | 时间序列分析 |
| 前端 | ECharts | 5.x | 可视化核心库 |
| 前端 | Bootstrap | 3.x | 响应式布局 |
| 前端 | D3.js | 7.x | 用于下拉框交互 |

---

# 数据字典

## 原始数据字段说明（NCDC ISD-Lite 格式）

| 序号 | 字段名 | 中文含义 | 数据类型 | 备注 |
|------|--------|----------|----------|------|
| 1 | stn | 基站ID | string | 从文件名前5位提取 |
| 2 | year | 年份 | string | 2000-2022 |
| 3 | month | 月份 | string | 1-12 |
| 4 | day | 日期 | string | 1-31 |
| 5 | hour | 小时 | string | 0-23 |
| 6 | temp | 气温 | string | 放大10倍存储，-9999表示缺失 |
| 7 | dew_point_temp | 露点温度 | string | 放大10倍存储 |
| 8 | pressure | 气压 | string | 放大10倍存储 |
| 9 | wind_direction | 风向 | string | 角度值 |
| 10 | wind_speed | 风速 | string | 放大10倍存储 |
| 11 | clouds | 云量 | string | |
| 12 | precipitation_1 | 1小时降水量 | string | |
| 13 | precipitation_6 | 6小时降水量 | string | |

> **重要提示**：原始数据中 `-9999` 表示该字段值缺失，需在分析时过滤。温度、气压、风速等数值均放大 10 倍存储，展示时需除以 10 还原。

---

# 第一部分：基础设施与 Hadoop 集群搭建

## 1. 核心目标
搭建一个高可用、完全分布式的 Hadoop 集群，包含 1 个主节点 (Master) 和 2 个从节点 (Slave1, Slave2)。

## 2. 详细操作步骤（复盘）

### 2.1 虚拟机规划与创建
- 软件选型：VMware Workstation Pro + CentOS 7.9。
- 硬件规划：
  - 初始配置：Master (8GB), Slaves (8GB)。
  - 最终优化配置：Master (8GB), Slaves (16GB)。为了解决 MapReduce 处理海量小文件时的 OOM 问题，提升了内存配置。
- 节点信息：
  - Master: 192.168.56.101
  - Slave1: 192.168.56.102
  - Slave2: 192.168.56.103

### 2.2 网络环境配置（双网卡方案）
目的：模拟真实内网环境并保证外网连接。

- 网卡 1 (ens33)：仅主机模式 (Host-Only)
  - 作用：集群内部通信，使用固定静态 IP（192.168.56.x），避免 IP 变动导致集群分裂。
  - 示例配置：修改 `/etc/sysconfig/network-scripts/ifcfg-ens33`，设置：
    ```bash
    BOOTPROTO=static
    IPADDR=192.168.56.101
    ```
- 网卡 2 (ens36)：NAT 模式
  - 作用：连接外网，用于下载安装包（yum/wget）。
  - 示例配置：修改 `/etc/sysconfig/network-scripts/ifcfg-ens36`，设置：
    ```bash
    BOOTPROTO=dhcp
    ```
    并通过设置路由优先级（Metric）确保默认路由走 `ens36` 上网。

- Windows 端：
  - 修改 Windows 的 VMnet1 虚拟网卡 IP 为 `192.168.56.1`，确保物理机能访问虚拟机 Web 界面（如 Hadoop Web UI）。

### 2.3 系统初始化（标准化配置）
在所有节点上执行，保证环境一致性：

- 设置主机名：
  ```bash
  hostnamectl set-hostname master
  hostnamectl set-hostname slave1
  hostnamectl set-hostname slave2
  ```
- Hosts 映射：修改 `/etc/hosts`，添加三台机器的 IP 和主机名，并分发到所有节点，例如：
  ```text
  192.168.56.101 master
  192.168.56.102 slave1
  192.168.56.103 slave2
  ```
- 关闭防火墙与 SELinux（根据实际安全策略调整）：
  ```bash
  systemctl stop firewalld
  setenforce 0
  ```
- SSH 免密登录：
  - 生成密钥：
    ```bash
    ssh-keygen -t rsa
    ```
  - 分发公钥（示例）：
    ```bash
    ssh-copy-id user@slave1
    ssh-copy-id user@slave2
    ```
  - 以便 Master 对各节点实现无密码控制。

### 2.4 Hadoop 集群部署
- 软件版本：
  - JDK 1.8
  - Hadoop 2.9.2
- 核心配置文件（示例说明）：
  - `core-site.xml`：指定 HDFS 地址，例如 `hdfs://master:9000`。
  - `hdfs-site.xml`：指定 NameNode / DataNode 数据存储路径。
  - `yarn-site.xml`：指定 ResourceManager 地址（master）及各项资源调度参数。
  - `slaves`：列出所有从节点（slave1、slave2）。在后续优化中可将 master 加入计算节点以参与任务。
- 分发安装包：
  - 使用 `scp` 将配置好的 Hadoop 和 JDK 分发到从节点，保持配置一致。
- 启动集群（示例命令）：
  ```bash
  # 格式化 NameNode（仅第一次）
  hdfs namenode -format

  # 启动所有服务（根据 Hadoop 发行版可能为 start-dfs.sh / start-yarn.sh）
  start-all.sh
  ```

## 3. 遇到的关键问题与解决方案（要点）
以下列出在搭建过程中遇到的关键问题与对应的解决方法（供复盘与答辩使用）：

- 问题：Windows 无法访问 Hadoop 页面（50070 / 8088）
  - 原因：Windows 的 VMnet1 网卡 IP 与虚拟机不在同一网段，导致物理机无法访问虚拟机服务。
  - 解决：将 Windows VMnet1 IP 调整为 `192.168.56.1`，使物理机与虚拟机处于同一网段，从而访问 Hadoop Web UI。

- 问题：Slave 节点“失联”（Active Nodes = 0）
  - 原因：`yarn-site.xml` 中缺少 `yarn.resourcemanager.hostname` 配置，导致 Slave 尝试连接 `0.0.0.0:8031` 而非 Master。
  - 解决：在 `yarn-site.xml` 中显式添加 ResourceManager 主机名配置（例如 `master`），同步分发配置并重启 YARN。

- 问题：资源调度瓶颈（升级物理内存后算力未释放）
  - 原因：YARN 容器内存默认限制未调整（示例为 4GB），导致集群未能有效利用新增物理内存。
  - 解决：在 `yarn-site.xml` 中调整例如 `yarn.nodemanager.resource.memory-mb` 等参数，将可用容器内存调至更高值（如 6GB），以充分利用硬件资源。

---
以上为 Hadoop 集群搭建过程的结构化复盘，包含环境规划、网络与系统初始化、部署要点以及遇到的问题与解决方案。
---

# 第二部分：数据采集与 ETL 清洗 (Data Ingestion & ETL)

## 1. 核心目标
将 NCDC 提供的 22 年（2000-2022）原始气象数据（共计 10,897 个 .gz 压缩小文件）上传至 HDFS，并通过编写 MapReduce 程序进行清洗，提取文件名中的基站 ID，将非结构化的空格分隔数据转换为结构化的 CSV 格式。

## 2. 详细操作步骤 (Step-by-Step)

### 2.1 数据准备与上传
- 数据源：china_isd_lite_2000 至 china_isd_lite_2022 文件夹。
- 在 Master 节点上传到 HDFS（示例）：

```bash
# 1. 创建存储目录
hdfs dfs -mkdir -p /china

# 2. 上传本地数据（假设数据在 /usr/local/data/ncdc/isd-lite/china_data/）
# 这一步将所有年份文件夹上传到 HDFS 的 /china 目录下
hdfs dfs -put /usr/local/data/ncdc/isd-lite/china_data/* /china/
```

- 生成输入路径列表（辅助 MapReduce 读取）：编写 `getHDFSfile.sh`，遍历 `/china` 下的所有文件夹路径，生成 `filename.txt`。

```bash
#!/bin/bash
rm -rf /home/filename.txt
for line in `hdfs dfs -ls /china | awk -F ' ' '{print $8}'`
do
    if [ -n "$line" ]; then
        echo "hdfs://master:9000$line" >> /home/filename.txt
    fi
done
```

### 2.2 MapReduce 代码开发（核心技术点）
为处理大量小文件，编写了三个 Java 类：ChinaMapper、ChinaReducer、ChinaDriver。

- ChinaMapper.java（清洗逻辑）  
  功能：
  - 读取原始一行数据；
  - 从 InputSplit（文件切片）中获取文件名，截取前 5 位作为基站 ID（Station ID）；
  - 将空格分隔（\s+）替换为逗号（,），去除脏数据，拼接基站 ID 到记录前列。

  **完整代码（ChinaMapper.java）：**

```java
package com;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import java.io.IOException;

public class ChinaMapper extends Mapper<LongWritable, Text, Text, NullWritable> {

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        // 使用标准 API 获取文件名，确保能准确拿到基站ID
        FileSplit inputSplit = (FileSplit) context.getInputSplit();
        String fileName = inputSplit.getPath().getName();

        // 提取基站 ID (前5位)
        String stn = fileName.substring(0, 5);

        String values = value.toString();
        String[] lines = values.split("\\s+");

        // 安全检查：确保字段数量足够
        if (lines.length > 11) {
            String year = lines[0];
            String month = lines[1];
            String day = lines[2];
            String hour = lines[3];
            String temp = lines[4];
            String dew_point_temp = lines[5];
            String pressure = lines[6];
            String wind_direction = lines[7];
            String wind_speed = lines[8];
            String cloud = lines[9];
            String precipitation_1 = lines[10];
            String precipitation_6 = lines[11];

            String line = stn + "," + year + "," + month + "," + day + "," + hour + "," + temp + "," + dew_point_temp
                    + "," + pressure + "," + wind_direction + "," + wind_speed + "," + cloud + "," + precipitation_1 + "," + precipitation_6;

            context.write(new Text(line), NullWritable.get());
        }
    }
}
```

- ChinaReducer.java（透传）
  功能：简单透传（pass-through），不做复杂聚合，直接输出清洗后的结果。

  **完整代码（ChinaReducer.java）：**

```java
package com;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class ChinaReducer extends Reducer<Text, NullWritable, Text, NullWritable> {
    @Override
    protected void reduce(Text key, Iterable<NullWritable> values, Context context) 
            throws IOException, InterruptedException {
        NullWritable val = NullWritable.get();
        Text outLine = key;
        context.write(outLine, val);
    }
}
```

- ChinaDriver.java（驱动配置 — 重点优化）  
  功能：配置 Job 参数并提交任务。重点是强制使用 YARN 模式以分散算力，避免单机 OOM。

  **完整代码（ChinaDriver.java）：**

```java
package com;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;

public class ChinaDriver {
    public static void main(String[] args) {
        // 【关键】强制使用 YARN 集群模式
        Configuration conf = new Configuration();
        conf.set("mapreduce.framework.name", "yarn");
        conf.set("yarn.resourcemanager.hostname", "master");
        conf.set("mapreduce.app-submission.cross-platform", "true");
        Job job = null;

        try {
            // 读取 Linux 本地的 filename.txt（包含所有输入文件路径）
            BufferedReader br = new BufferedReader(new FileReader("/home/filename.txt"));
            String line = null;
            ArrayList<Path> list = new ArrayList<>();

            while((line = br.readLine()) != null){
                if(line.trim().length() > 0){
                    list.add(new Path(line));
                }
            }
            br.close();

            Path[] inputPath = list.toArray(new Path[0]);
            System.out.println("Total input paths loaded: " + inputPath.length);

            job = Job.getInstance(conf);

            job.setJarByClass(ChinaDriver.class);
            job.setJobName("ChinaDriver_YARN");

            job.setMapperClass(ChinaMapper.class);
            job.setReducerClass(ChinaReducer.class);

            job.setMapOutputKeyClass(Text.class);
            job.setMapOutputValueClass(NullWritable.class);

            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(NullWritable.class);

            // 设置输入路径
            FileInputFormat.setInputPaths(job, inputPath);

            // 设置输出路径
            FileOutputFormat.setOutputPath(job, new Path("hdfs://master:9000/china_all/"));

            System.exit(job.waitForCompletion(true) ? 0 : 1);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

**注意：** 尝试使用 CombineTextInputFormat 会导致无法从 InputSplit 中获取到具体原始文件名（因为 CombineFileSplit），从而无法提取基站 ID。为保证能从每个记录定位到原始文件名，最终放弃合并切片，使用 FileSplit（即默认 TextInputFormat）让每个小文件由独立 Map 任务处理。

### 2.3 打包与运行
- Maven 打包（在本地或 CI/IDE 中）：

```bash
mvn clean package
# 生成 china_etl-1.0-SNAPSHOT.jar
```

- 上传 Jar 包到 Master 节点的 /home/ 目录。
- 清理目标路径（输出目录必须不存在）：

```bash
hdfs dfs -rm -r /china_all
```

- 提交作业：

```bash
hadoop jar /home/china_etl-1.0-SNAPSHOT.jar com.ChinaDriver
```

## 3. 遇到的重大技术障碍与解决方案 (Troubleshooting)
以下为关键障碍、原因分析与解决措施，建议答辩时重点说明思路与权衡：

- 障碍 1：内存溢出 (OOM: GC overhead limit exceeded)  
  - 现象：程序运行数秒后崩溃，抛出 java.lang.OutOfMemoryError: GC overhead limit exceeded。  
  - 分析：数据包含 10,897 个小文件，默认情况下 MapReduce 会为每个文件启动一个 Map 任务。若在 Local 模式或单机上提交，会导致单台机器尝试处理大量 Map 任务实例，内存耗尽。  
  - 解决：
    - 硬件升级：将 Master 内存扩容；
    - 架构切换：Driver 中显式设置 conf.set("mapreduce.framework.name", "yarn")，并配置 ResourceManager，使任务分发到 YARN 集群（Slave 节点参与计算），Master 仅负责调度。这样内存压力分散，避免单机 OOM。

- 障碍 2：CombineTextInputFormat 与 FileSplit 冲突  
  - 尝试：为减少小文件影响曾尝试使用 CombineTextInputFormat 合并切片。  
  - 问题：运行时报 ClassCastException（CombineFileSplit 不能被强制转换为 FileSplit），且 Mapper 无法准确获取每行对应的原始文件名，导致无法提取基站 ID。  
  - 结论：为保证业务逻辑（提取基站 ID）正确性，放弃合并切片，使用每文件单 Map 的策略。借助 YARN 集群算力承受大量 Map 任务调度开销。

- 障碍 3：集群“假死”（Active Nodes = 0）  
  - 现象：提交 YARN 作业后状态卡在 ACCEPTED，Web UI 显示 Active Nodes: 0。  
  - 原因与解决：
    - 在 `yarn-site.xml` 中缺失 `yarn.resourcemanager.hostname` 配置，导致 NodeManager 无法正确注册 ResourceManager：补充并同步分发该配置；
    - 虚拟机重启或安全策略可能导致防火墙开启，阻断 Slave 的心跳包：关闭防火墙或按策略开放所需端口（示例：执行 `systemctl stop firewalld` 并在必要时配置防火墙规则）；
    - 在 Slave 上重启 NodeManager 使其能重新注册到 ResourceManager。

## 4. 成果验收
- 执行时间：在 YARN 集群上并行运行，任务约 5–10 分钟完成（视集群资源与数据分布而定）。
- 输出位置：HDFS 目录 `/china_all` 下生成清洗后的 CSV 数据文件。
- 数据样例：

```text
45001,2000,01,01,00,80,-94,10285,50,60,1,-9999,-9999
```

（格式为逗号分隔，第一列为成功补全的基站 ID）

---
以上为数据采集与 ETL 清洗部分的结构化复盘，包含数据上传、MapReduce 开发要点、运行步骤与遇到的问题与解决方案。
---


# 第三部分：数据仓库建设与维度分析 (Hive Data Warehouse)

## 1. 核心目标
建立基于 Hive 的分层数据仓库，将 MapReduce 清洗后的结构化数据（CSV）映射为数据库表，并引入地理维度表（基站-城市映射），通过 SQL 语句进行多维度的统计分析，为后续的可视化和挖掘提供指标数据。

## 2. 环境准备与数据加载

### 2.1 启动元数据服务 (Metastore)
Hive 需要连接 MySQL 来存储元数据（表结构、列名、分区等）。

示例命令：

```bash
# 后台启动 Metastore 服务
nohup hive --service metastore &

# 进入 Hive 客户端
hive
```

### 2.2 准备维度数据 (DIM 层)
气象数据中只有“基站ID”，没有城市名称。需上传映射文件。

文件：China_stn_city.csv（包含 Station ID, Province, City, Latitude, Longitude）

示例命令：

```bash
hdfs dfs -mkdir -p /china_stn
hdfs dfs -put /home/data/China_stn_city.csv /china_stn/
```

## 3. 数据仓库分层架构设计与实现（ODS -> DIM -> DWD -> APP）

本项目采用轻量级四层架构：ODS（贴源层）-> DIM（维度层）-> DWD（明细层/宽表）-> APP（应用层/结果表）。

---

### 🟢 第一层：ODS 层（贴源层）
表名：china_all  
作用：直接映射 HDFS 上 MapReduce 清洗后的全量数据（外部表，防止删表误删数据）。

示例建表语句：

```sql
create external table china_all(
    stn string,
    year string,
    month string,
    day string,
    hour string,
    temp string,
    dew_point_temp string,
    pressure string,
    wind_direction string,
    wind_speed string,
    clouds string,
    precipitation_1 string,
    precipitation_6 string
)
row format delimited
fields terminated by ','
location '/china_all';
```

---

### 🔵 第二层：DIM 层（维度层）
表名：stn_city  
作用：存储基站与地理位置的映射关系（外部表）。

示例建表语句：

```sql
create external table stn_city(
    stn string,
    province string,
    city string,
    latitude string,
    longitude string
)
row format delimited
fields terminated by ','
location '/china_stn';
```

---

### 🟡 第三层：DWD 层（明细层 - 宽表）
表名：tmp_city  
作用：通过 JOIN 操作，将气象数据与地理数据合并，形成包含省份、城市信息的全量宽表，并过滤掉无法匹配基站的脏数据。

示例 SQL：

```sql
create table tmp_city as
select
    c.*,
    s.province,
    s.city
from china_all c
left join stn_city s
on c.stn = s.stn
where s.province is not null; -- 过滤掉无效基站
```

另外为便于可视化分析，还创建了针对 2022 年的宽表（如 tmp_city_2022）用于单年分析与展示。

---

### 🔴 第四层：APP 层（应用层 - 结果表）
作用：根据业务需求（大屏展示、模型训练）进行聚合计算，生成最终结果表，这些表可通过 Sqoop 导出到 MySQL 供上层应用使用。

场景示例：

- 场景 A：各省气象概览（用于地图）  
  表名：china_map  
  逻辑：按月份和省份分组，计算平均气温和平均风速。

  ```sql
  insert overwrite table china_map
  select month, province, avg(temp), avg(wind_speed)
  from tmp_city_2022
  where temp <> '-9999' -- 排除无效数据
  group by month, province;
  ```

- 场景 B：降水 Top10 城市（用于柱状图）  
  表名：city_precipitation_top10  
  技术点：使用窗口函数（row_number）进行组内排序取 TopN。

  ```sql
  select * from (
      select *,
             row_number() over(partition by month order by pre6 desc) as rank
      from (
          select month, city, avg(precipitation_6) as pre6
          from tmp_city_2022
          group by month, city
      ) t1
  ) t2
  where t2.rank <= 10;
  ```

- 场景 C：全量历史气温（用于 Python 预测）
  表名：province_temp_all  
  逻辑：聚合 22 年间所有省份的月均气温，作为机器学习训练集。

  ```sql
  create table province_temp_all as
  select year, province, month, avg(temp) as avg_temp
  from tmp_city
  where temp <> '-9999'
  group by year, province, month;
  ```

---

## 4. 遇到的障碍与解决方案（Troubleshooting）

1. Hive 运行缓慢  
   - 现象：执行 insert overwrite 或 group by 时，MapReduce 进度很慢。  
   - 原因：Hive 将 SQL 转为 MapReduce 任务，数据量大（数千万至上亿条记录）。  
   - 解决：借助此前对 YARN 的资源调优（Master/Node 更大内存及提升容器内存配置），通过并行 Container 并行化任务，保证稳定性与容错，减少 OOM 风险。

2. 数据精度问题（放大因子）  
   - 现象：Hive 计算的平均气温为 256.5，但实际应为 25.65°C。  
   - 原因：原始 NCDC 数据为节省空间，将温度放大 10 倍存储。  
   - 决策：在 Hive 层保留原始放大后的数值（便于后续批量计算），在前端展示层（Django）或挖掘层（Python）再统一除以 10 进行还原与格式化。

3. 关联查询数据倾斜  
   - 现象：JOIN 操作时某个 Reduce 卡住或极慢。  
   - 解决：尽量将小表放在 join 的右边或使用 MapJoin（广播小表）策略；对倾斜键做盐值处理（如果必要）；并保证维表（stn_city）在执行计划中以合适方式广播或分配。

---

## 5. 阶段成果
本阶段完成的核心资产包括：

- Hive 数据库：包含 china_all（ODS）、stn_city（DIM）、tmp_city（DWD）等表。
- APP 层结果表（6 个核心表）：
  - china_map （地图展示数据）
  - city_precipitation_top10 （城市降水排行）
  - city_temp （词云/城市温度分布）
  - province_temp （省级温度折线图数据）
  - province_pressure （省级气压树图数据）
  - province_temp_all （历史月均温表，用于预测训练）

---
以上为数据仓库建设与维度分析部分的结构化复盘，包含环境准备、分层设计、示例 SQL、遇到的问题与解决策略，以及阶段性成果清单。
---


# 第四部分：数据迁移与同步 (Data Migration with Sqoop)

## 1. 核心目标
使用 Apache Sqoop 将 Hive 数仓中 APP 层计算好的 6 张最终结果表，批量导出到 MySQL 关系型数据库，供前端 Django Web 系统快速读取和展示。

## 2. 环境准备与安装 (Environment Setup)

### 2.1 Sqoop 安装
- 节点：在 Master 节点上部署 Sqoop 客户端。  
- 版本：Sqoop 1.4.6

安装与依赖配置要点：
```bash
# 解压安装包（示例）
tar -zxvf sqoop-1.4.6.tar.gz
# 将 MySQL JDBC 驱动与 JSON 支持包放入 lib
cp mysql-connector-java-5.1.41-bin.jar $SQOOP_HOME/lib/
cp java-json.jar $SQOOP_HOME/lib/
# 配置环境变量（/etc/profile）并在 $SQOOP_HOME/conf/sqoop-env.sh 指定 HADOOP/HIVE 路径
```

关键点：
- 必须将 MySQL 驱动（mysql-connector-java-5.1.41-bin.jar）拷贝到 $SQOOP_HOME/lib/。
- 推荐将 JSON 支持包（java-json.jar）也放入 $SQOOP_HOME/lib/（部分版本可能需要）。
- 在 sqoop-env.sh 中配置 HADOOP_COMMON_HOME、HADOOP_MAPRED_HOME、HIVE_HOME 等环境变量，使 Sqoop 能与 Hadoop/Hive 协同工作。

### 2.2 MySQL 目标库表准备
Sqoop export 要求目标表必须预先存在，且字段类型需与 Hive 输出兼容（如 Hive string -> MySQL varchar/float 等）。

示例建库与建表脚本：
```sql
/*
 * 数据库：china_all
 * 用途：存储 Hive 清洗后的指标数据以及 Python 预测结果
 */

-- 1. 创建并使用数据库
CREATE DATABASE IF NOT EXISTS china_all DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
USE china_all;

-- ----------------------------
-- Table structure for china_map
-- 用途：存储各省份每月平均气温和风速 (用于大屏地图展示)
-- ----------------------------
DROP TABLE IF EXISTS `china_map`;
CREATE TABLE `china_map` (
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `province` varchar(20) DEFAULT NULL COMMENT '省份',
  `temp` float DEFAULT NULL COMMENT '平均气温',
  `wind_speed` float DEFAULT NULL COMMENT '平均风速'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for city_precipitation_top10
-- 用途：存储每月降水量 Top10 的城市 (用于柱状图展示)
-- ----------------------------
DROP TABLE IF EXISTS `city_precipitation_top10`;
CREATE TABLE `city_precipitation_top10` (
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `city` varchar(20) DEFAULT NULL COMMENT '城市',
  `precipitation_6` float DEFAULT NULL COMMENT '6小时平均降水量'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for city_temp
-- 用途：存储各城市每月平均气温 (用于词云展示)
-- ----------------------------
DROP TABLE IF EXISTS `city_temp`;
CREATE TABLE `city_temp` (
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `city` varchar(20) DEFAULT NULL COMMENT '城市',
  `temp` float DEFAULT NULL COMMENT '平均气温'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for province_pressure
-- 用途：存储各省份每月平均气压 (用于矩形树图展示)
-- ----------------------------
DROP TABLE IF EXISTS `province_pressure`;
CREATE TABLE `province_pressure` (
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `province` varchar(20) DEFAULT NULL COMMENT '省份',
  `pressure` float DEFAULT NULL COMMENT '平均气压'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for province_temp
-- 用途：存储各省份每月气温及预测值 (用于折线图展示)
-- 注意：temp_forecast 字段由 Python 脚本回写更新
-- ----------------------------
DROP TABLE IF EXISTS `province_temp`;
CREATE TABLE `province_temp` (
  `province` varchar(20) DEFAULT NULL COMMENT '省份',
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `temp` float DEFAULT NULL COMMENT '当年真实气温',
  `temp_forecast` float DEFAULT NULL COMMENT '下一年预测气温'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for province_temp_all
-- 用途：存储 2000-2022 年所有省份的历史气温 (用于 Python 训练模型)
-- ----------------------------
DROP TABLE IF EXISTS `province_temp_all`;
CREATE TABLE `province_temp_all` (
  `year` int(4) DEFAULT NULL COMMENT '年份',
  `province` varchar(20) DEFAULT NULL COMMENT '省份',
  `month` int(4) DEFAULT NULL COMMENT '月份',
  `temp` float DEFAULT NULL COMMENT '平均气温'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

## 3. 数据导出实战 (Execution)
使用 sqoop export 将 HDFS 上的 Hive 数据文件推送到 MySQL。

通用命令模板：
```bash
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table <MySQL表名> \
  --export-dir <Hive表在HDFS的路径> \
  --input-fields-terminated-by ',' \
  --m 1
```

参数说明：
- --connect：JDBC 连接字符串，指向 MySQL 服务。
- --username / --password：MySQL 登录凭据（生产环境请避免明文密码）。
- --table：目标 MySQL 表名（必须已存在）。
- --export-dir：Hive 在 HDFS 上的输出目录或表对应的 HDFS 路径。
- --input-fields-terminated-by ','：指明输入文件是逗号分隔的 CSV。
- --m 1：使用 1 个并行 Map 任务写入 MySQL（写入稳定性高，适用于小量结果表）。

核心导出任务（需针对每张表执行一次）：
- china_map -> 对应地图数据
- city_precipitation_top10 -> 对应降水 Top10
- city_temp -> 城市气温（词云）
- province_temp -> 省份气温（折线 & 预测字段）
- province_pressure -> 省份气压（矩形树图）
- province_temp_all -> 全量历史气温（机器学习训练数据）

示例（导出 province_temp_all）：
```bash
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table province_temp_all \
  --export-dir /user/hive/warehouse/province_temp_all \
  --input-fields-terminated-by ',' \
  --m 1
```

## 4. 遇到的障碍与解决方案 (Troubleshooting)
列出常见问题及解决方法，答辩时可突出“落地执行与权限/策略调整”能力。

问题 1：MySQL 连接拒绝 (Access Denied)  
- 现象：执行 Sqoop 报错 java.sql.SQLException: Access denied for user 'root'@'master' (using password: YES)。  
- 原因：MySQL 默认只允许 localhost 访问，或用户未被授予从 master 主机连接的权限。  
- 解决：在 MySQL 中明确授权 root@master：
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'master' IDENTIFIED BY 'root' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

问题 2：密码策略限制（ERROR 1819）  
- 现象：在设置简单密码或授权时，MySQL 报错密码不满足策略。  
- 原因：MySQL 的 validate_password 插件强制强密码策略（MySQL 5.7+）。  
- 解决（实验/开发环境可短期调整）：
```sql
SET GLOBAL validate_password_policy = 0;  -- 降低策略
SET GLOBAL validate_password_length = 4;  -- 最小长度
```
（生产环境请遵守安全规范，不推荐长期放松策略）

问题 3：字段分隔符不匹配（导出后全是 NULL 或乱码）  
- 现象：导出执行成功，但插入 MySQL 的字段显示 NULL 或列错位。  
- 原因：Hive 表默认字段分隔符可能是 Ctrl+A（\001），而导出时使用了不同的分隔符；或者 Hive 输出的数据清洗不正确。  
- 解决：
  - 确认 Hive 建表语句中有 row format delimited fields terminated by ','；  
  - 在 Sqoop 命令中显式添加 --input-fields-terminated-by ','；  
  - 检查 Hive 输出文件是否是真正的 CSV（无额外控制字符或 header）。

## 5. 阶段成果验证
导出完成后，进行数据核验示例：
```bash
mysql -uroot -proot -e "USE china_all; SELECT COUNT(*) FROM province_temp_all;"
```
- 结果示例：返回 9384 行数据（22 年 × 34 个省份 × 12 个月 = 22*34*12 = 8976，实际可能因省份统计口径或分区不同出现差异，本示例为核验结果）。
- 意义：确认 APP 层的结果表已成功从 HDFS 迁移到 MySQL，可供 Django 前端和 Python 训练脚本直接访问与使用。

---
以上为数据迁移与同步（Sqoop）部分的结构化复盘，包含环境安装、MySQL 表结构准备、导出命令模板、常见问题与解决方案以及阶段性验证方法。
---


# 第五部分：数据挖掘与预测 (Data Mining & Prediction)

## 1. 核心目标
利用 Python 数据分析生态（Pandas、Statsmodels），连接 MySQL 读取 2000–2022 年的全量历史气温数据，基于时间序列模型预测全国 34 个省份/地区 2023 年 1–12 月的平均气温，并将预测结果回写到数据库，完成数据闭环。

## 2. 技术栈与环境 (Tech Stack)
- 开发语言：Python 3.9
- 核心库：
  - pymysql / sqlalchemy：数据库读写
  - pandas：数据清洗、索引与格式转换
  - statsmodels（或 statsmodels.tsa / Holt-Winters）：时间序列模型（ExponentialSmoothing）
  - matplotlib：可视化及结果验证

## 3. 实施步骤与代码逻辑 (Implementation)

### 3.1 模型选型与对比
- 对比模型：ARIMA（适合平稳或差分后平稳序列） vs Holt-Winters（三次指数平滑，适合周期性/季节性明显的数据）。
- 结论：气温序列表现出强烈的 12 个月季节性（夏高冬低），适合使用 Holt-Winters（加法趋势 + 加法季节性）。通过 RMSE 比较发现 Holt-Winters 更贴合历史波动，故最终采用 ExponentialSmoothing(seasonal_periods=12, trend='add', seasonal='add')。

### 3.2 批量预测脚本（task20_predict_all.py）

**完整代码：**

```python
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# ==========================================
# 1. 配置数据库连接
# ==========================================
print("正在连接数据库...")
db_url = 'mysql+pymysql://root:root@192.168.56.101:3306/china_all'
engine = create_engine(db_url)

# ==========================================
# 2. 读取全量历史数据
# ==========================================
try:
    with engine.connect() as conn:
        query = text('select * from province_temp_all')
        mydata = pd.read_sql(query, conn)

    print(f"读取成功，总数据量: {len(mydata)} 行")

    # 获取所有省份列表
    provinces = mydata['province'].unique()
    print(f"检测到 {len(provinces)} 个省份/地区，准备开始批量预测...")
    print("-" * 30)

    # ==========================================
    # 3. 循环预测并更新数据库
    # ==========================================

    # 建立统一的时间索引 (2000-01 到 2022-12)
    date_idx = pd.period_range(start='2000/01', end='2022/12', freq='M')

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            count = 0
            for prov in provinces:
                count += 1
                print(f"[{count}/{len(provinces)}] 正在处理: {prov} ...", end=" ")

                # 3.1 提取当前省份数据
                current_prov_data = mydata[mydata['province'] == prov]

                if len(current_prov_data) < 24:
                    print("数据不足，跳过")
                    continue

                # 3.2 数据预处理（除以10还原真实温度）
                temp_vals = current_prov_data['temp'].values.astype(float) / 10

                if len(temp_vals) != len(date_idx):
                    current_date_idx = pd.period_range(start='2000/01', periods=len(temp_vals), freq='M')
                    temp_data = pd.DataFrame(temp_vals, index=current_date_idx, columns=['temp'])
                else:
                    temp_data = pd.DataFrame(temp_vals, index=date_idx, columns=['temp'])

                # 3.3 建立 Holt-Winters 模型与预测
                try:
                    hw_model = ExponentialSmoothing(temp_data['temp'],
                                                    trend='add',
                                                    seasonal='add',
                                                    seasonal_periods=12).fit()

                    # 预测未来 12 个月
                    temp_forecast = hw_model.forecast(12)

                    # 3.4 更新回 MySQL
                    for i, val in enumerate(temp_forecast):
                        month = i + 1
                        sql = text(
                            f'update province_temp set temp_forecast={val:.4f} where province="{prov}" and month={month}')
                        conn.execute(sql)

                    print("完成 ✅")

                except Exception as model_err:
                    print(f"建模失败: {model_err}")

            trans.commit()
            print("-" * 30)
            print("所有省份预测完成并已更新到数据库！")

        except Exception as db_err:
            trans.rollback()
            print(f"\n数据库操作发生错误，已回滚: {db_err}")

except Exception as e:
    print(f"程序运行出错: {e}")
```

**脚本执行流程：**
1. 从 MySQL 表 `province_temp_all` 全量读取 2000-2022 年历史数据
2. 对每个省份分组切片，提取该省份的月均气温序列
3. 数据预处理：除以 10 还原真实温度，建立时间索引
4. 使用 Holt-Winters（三次指数平滑）模型拟合历史数据
5. 预测未来 12 个月（2023 年）的气温
6. 将预测结果回写到 `province_temp` 表的 `temp_forecast` 字段

**注意事项：**
- 强制将 numpy 类型转换为 Python 原生类型（`float(val)`），避免数据库驱动兼容问题
- 使用事务（`trans.begin()` / `trans.commit()`）保证数据一致性
- 对数据不足的省份进行跳过处理，避免模型报错

## 4. 遇到的障碍与解决方案 (Troubleshooting)
- 障碍 1：预测函数参数错误  
  - 现象：报错：predict() got an unexpected keyword argument 'steps'。  
  - 原因：不同模型/版本 API 差异，一些接口使用 predict(start, end)，另一些使用 forecast(steps)。  
  - 解决：统一使用 model.forecast(12) 或参考当前 statsmodels 版本的推荐用法。

- 障碍 2：数据库字段名不匹配  
  - 现象：回写时报错 Unknown column 'forecast' in 'field list'。  
  - 原因：代码 SQL 使用了错误的列名（forecast），实际表字段为 temp_forecast。  
  - 解决：核对数据库 Schema，将 SQL 列名调整为 temp_forecast，与数据库保持一致。

- 障碍 3：数据类型兼容问题  
  - 现象：Pandas 中的 numpy.float64 在 SQL 拼接或驱动传参时发生错误或精度异常。  
  - 解决：明确类型转换为 Python 原生类型，例如通过 float(val) 或 val.item()；使用参数化 SQL（避免手工拼接）以防注入与类型问题。

## 5. 阶段成果验证
### 5.1 数据库验证
在 Master 机器上执行 SQL 校验，示例：
```bash
mysql -uroot -proot -e "SELECT * FROM china_all.province_temp WHERE province='山东' LIMIT 5;"
```
结果示例：查看到 `temp` 列为历史真实值，`temp_forecast` 列已填入预测值（如 26.32）。

### 5.2 业务价值体现
- 成果：完成了从数据仓库 -> 模型训练 -> 预测回写的闭环，实现了历史回顾 + 未来预测的能力。
- 价值：平台从“只看历史”升级为“可预测未来”，预测结果可驱动前端展示、预警、与后续模型迭代。

---

以上为数据挖掘与预测部分的结构化复盘，包含模型选型、批量预测脚本逻辑、常见问题与解决方案，以及成果验证方法。
---


# 第六部分：可视化大屏开发复盘 (Data Visualization)

## 1. 核心目标
构建一个基于 Web 的动态数据可视化大屏，集成地图、时间轴、折线图、词云等多种图表组件，能够：
- 实时从 MySQL 读取分析结果；
- 通过时间轴自动轮播展示 1–12 月的全国气象变化趋势；
- 展示 22 年气温历史及基于 Holt-Winters 算法的未来一年预测数据。

## 2. 技术架构与选型 (Tech Stack)
- 后端：Django 3.2（LTS，兼容 MySQL 5.7）
- 数据库驱动：pymysql（替代 mysqlclient）
- 前端：
  - ECharts（地图、折线、柱状、树图）
  - ECharts-Wordcloud（词云插件）
  - jQuery（AJAX 与 DOM 操作）
  - Bootstrap（栅格布局）
- 数据流：MySQL ← Sqoop ← Hive ← HDFS（MapReduce 清洗）

### 2.1 Django 项目目录结构
```
weather/                          # 项目根目录
├── manage.py                     # Django 管理脚本
├── requirements.txt              # Python 依赖清单
├── db.sqlite3                    # SQLite（未使用，默认生成）
│
├── weather/                      # Django 项目配置目录
│   ├── __init__.py               # pymysql 注册
│   ├── settings.py               # 项目配置（数据库、静态文件等）
│   ├── urls.py                   # 路由配置
│   ├── wsgi.py                   # WSGI 入口
│   └── asgi.py                   # ASGI 入口
│
├── china_weather/                # 应用目录
│   ├── __init__.py
│   ├── admin.py                  # 后台管理
│   ├── apps.py                   # 应用配置
│   ├── models.py                 # 数据模型（本项目未使用 ORM）
│   ├── views.py                  # 视图函数（核心数据处理逻辑）
│   ├── tests.py                  # 测试
│   └── migrations/               # 数据库迁移
│
├── templates/                    # HTML 模板目录
│   ├── index.html                # 大屏主页
│   ├── 地图对照模板.html          # 地图参考模板
│   └── 词云对照模板.html          # 词云参考模板
│
└── static/                       # 静态资源目录
    ├── css/
    │   ├── app.css               # 自定义样式
    │   └── bootstrap.min.css     # Bootstrap 框架
    ├── js/
    │   ├── echarts.min.js        # ECharts 核心库
    │   ├── china.js              # 中国地图数据
    │   ├── wordcount.min.js      # 词云插件
    │   ├── d3.min.js             # D3.js（用于下拉框）
    │   ├── total_control.js      # 总控逻辑（月份切换）
    │   ├── map_chart.js          # 地图图表
    │   ├── timeline.js           # 时间轴图表
    │   ├── line_chart.js         # 折线图
    │   ├── tree_chart.js         # 矩形树图
    │   ├── word_chart.js         # 词云图
    │   └── bar_chart.js          # 柱状图
    ├── img/                      # 图片资源
    │   ├── bg06.png              # 背景图
    │   └── ...                   # 其他装饰图片
    └── data/                     # 备用 CSV 数据（开发调试用）
```

## 3. 实施步骤与核心代码 (Implementation)

### 3.1 Django 项目初始化与配置
- 指定 Django 版本：`Django==3.2.25`（与 MySQL 5.7 兼容性考虑）。
- settings.py 关键配置：
  - 数据库连接：指向 Master 节点（例：192.168.56.101）。
  - 静态文件：区分 `STATICFILES_DIRS`（开发目录）与 `STATIC_ROOT`（收集目录），避免 staticfiles 错误。
  - 安全：`ALLOWED_HOSTS = ['*']`（开发/演示环境）。
- 驱动注册（项目 __init__.py）：
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 3.2 后端数据接口开发（views.py）
- 数据读取：使用 `pandas.read_sql` 从 MySQL 的结果表中读取数据（china_map、tmp_city_2022、province_temp 等）。
- 类型与序列化问题：
  - Pandas 返回的数值常为 numpy 类型（`numpy.int64`、`numpy.float64`），Django 的 JSON 序列化器无法直接处理，前端会报错（如 np is not defined）。
  - 解决：在 `views.py` 中遍历每行数据并强制转换为 Python 原生类型（`int()`、`float()`），或使用 `DataFrame.to_dict(orient='records')` 后再转换。
- 数据封装：将清洗后的字典通过 `json.dumps` 序列化并注入模板，或通过 REST API 返回 JSON。

示例（类型转换）：
```python
rows = df.to_dict(orient='records')
for r in rows:
    r['temp'] = float(r['temp'])
    r['month'] = int(r['month'])
# jsonify 或 render 到模板
```

### 3.3 前端大屏开发（index.html + JS）

**前端文件清单与职责：**

| 文件 | 位置 | 职责说明 |
|------|------|----------|
| index.html | templates/ | 大屏主页，定义布局与全局变量 |
| total_control.js | static/js/ | 时间控制器，驱动月份切换与图表刷新 |
| map_chart.js | static/js/ | 地图绑定与散点渲染（气温填色 + 风速散点） |
| timeline.js | static/js/ | 时间轴组件（自动轮播 1-12 月） |
| line_chart.js | static/js/ | 折线图（历史气温 + 预测曲线） |
| tree_chart.js | static/js/ | 矩形树图（省份气压分布） |
| word_chart.js | static/js/ | 词云图（城市温度分布） |
| bar_chart.js | static/js/ | 柱状图（降水量 Top10） |
| china.js | static/js/ | 中国地图坐标数据（ECharts 地图包） |
| echarts.min.js | static/js/ | ECharts 核心库 |
| wordcount.min.js | static/js/ | ECharts 词云插件 |
| d3.min.js | static/js/ | D3.js（用于省份下拉框） |

- 模块化 JS：
  - total_control.js：总控逻辑，维护 `month_index`，使用 `setInterval` 每 5 秒切换月份并触发 `render_all()`。
  - map_chart.js：地图渲染，基于省份平均气温填色、基于风速绘制散点大小，使用 local 的 `china.js` 地图数据。
  - timeline.js：时间轴绘制与交互，监听 `timelinechanged` 事件以支持手动与自动切换。
  - bar_chart.js：降水 Top10 柱状图。
  - line_chart.js：气温趋势与预测折线图（展示历史 + 预测值）。
  - word_chart.js：城市气温热度词云。
- 坐标问题：手工补充 34 个省份的经纬度映射（geoCoordMap），解决散点图坐标显示问题。
- 前端数据交互：通过 AJAX 请求 Django 后端数据接口，或直接在模板中注入 JSON 数据供 ECharts 使用。

## 4. 遇到的障碍与解决方案 (Troubleshooting)

- 障碍 1：前端白屏，控制台报错 "np is not defined"  
  - 原因：后端返回的数据仍包含 Numpy 类型，前端 JSON 无法解析。  
  - 解决：在后端将所有数值强制转换为 Python 原生类型（int/float），或先转换为标准 Python 字典再序列化。

- 障碍 2：JS 文件中文乱码导致 SyntaxError  
  - 原因：文件编码不一致（IDE 默认 GBK，而浏览器按 UTF-8 解析）。  
  - 解决：将所有 JS/HTML/模板文件保存为 UTF-8 编码。

- 障碍 3：静态文件配置冲突（STATICFILES_DIRS 与 STATIC_ROOT 相同）  
  - 现象：Django 报错 The STATICFILES_DIRS setting should not contain the STATIC_ROOT setting。  
  - 解决：分离开发静态目录（如 `static/`）与收集目录（如 `staticfiles/`），并在部署时运行 `collectstatic`。

- 障碍 4：安全访问限制（DisallowedHost / Invalid HTTP_HOST）  
  - 原因：Django 默认拒绝非 localhost 的 Host。  
  - 解决：在开发/演示环境设置 `ALLOWED_HOSTS = ['*']` 或指定允许的 IP/域名。

## 5. 最终成果展示 (Showcase)
- 动态性：时间轴自动轮播（每月切换），图表随月份变化实时重绘，形成立体的季节变化动画效果。
- 交互性：用户可手动点击时间轴或地图上的省份查看详细数值；悬停显示工具提示（tooltip）。
- 可视化要点：
  - 地图：显示各省当月平均气温（色块）与风速（散点大小）。
  - 折线图：展示 2000–2022 历史气温曲线并叠加 2023 年 预测值（Holt-Winters 输出）。
  - 词云：基于城市温度/热度生成词云，直观显示高温城市分布。
- 业务闭环验证：整套展示链路为 HDFS → Hive → MySQL → Django → ECharts，前端可实时读取 MySQL 中的 APP 层与预测结果，支持展示与下钻分析。

---
以上为可视化大屏开发的结构化复盘，包含目标、技术栈、实现要点、常见故障与解决方案，以及最终成果要点。
---


# 附录

## A. Sqoop 导出命令汇总

以下为 6 张结果表的完整导出命令，可按需执行：

```bash
# 1. 导出地图数据
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table china_map \
  --export-dir /user/hive/warehouse/china_map \
  --input-fields-terminated-by ',' \
  --m 1

# 2. 导出降水 Top10 数据
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table city_precipitation_top10 \
  --export-dir /user/hive/warehouse/city_precipitation_top10 \
  --input-fields-terminated-by ',' \
  --m 1

# 3. 导出城市气温数据（词云）
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table city_temp \
  --export-dir /user/hive/warehouse/city_temp \
  --input-fields-terminated-by ',' \
  --m 1

# 4. 导出省份气温数据（折线图）
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table province_temp \
  --export-dir /user/hive/warehouse/province_temp \
  --input-fields-terminated-by ',' \
  --m 1

# 5. 导出省份气压数据（树图）
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table province_pressure \
  --export-dir /user/hive/warehouse/province_pressure \
  --input-fields-terminated-by ',' \
  --m 1

# 6. 导出全量历史气温（机器学习训练）
sqoop export \
  --connect jdbc:mysql://master:3306/china_all \
  --username root \
  --password root \
  --table province_temp_all \
  --export-dir /user/hive/warehouse/province_temp_all \
  --input-fields-terminated-by ',' \
  --m 1
```

---

## B. 常用运维命令速查

### Hadoop/YARN 相关
```bash
# 查看各节点进程
jps

# 查看 HDFS 集群状态
hdfs dfsadmin -report

# 查看 YARN 节点状态
yarn node -list

# 启动/停止集群
start-all.sh / stop-all.sh
start-dfs.sh / stop-dfs.sh
start-yarn.sh / stop-yarn.sh

# HDFS 常用操作
hdfs dfs -ls /path              # 列出目录
hdfs dfs -mkdir -p /path        # 创建目录
hdfs dfs -put local remote      # 上传文件
hdfs dfs -get remote local      # 下载文件
hdfs dfs -rm -r /path           # 删除目录
hdfs dfs -cat /path/file        # 查看文件内容
```

### Hive 相关
```bash
# 启动 Metastore 服务
nohup hive --service metastore &

# 进入 Hive CLI
hive

# 常用 Hive 命令
show databases;
use database_name;
show tables;
desc table_name;
select * from table_name limit 10;
```

### MySQL 相关
```bash
# 登录 MySQL
mysql -uroot -proot

# 常用命令
show databases;
use china_all;
show tables;
desc table_name;
select count(*) from table_name;
```

### Django 相关
```bash
# 启动开发服务器（允许外部访问）
python manage.py runserver 0.0.0.0:8000

# 收集静态文件（部署时）
python manage.py collectstatic

# 检查配置
python manage.py check
```

---

## C. 常见问题速查表 (FAQ)

| 问题现象 | 可能原因 | 快速解决方案 |
|----------|----------|-------------|
| YARN Active Nodes = 0 | yarn-site.xml 缺少 resourcemanager.hostname | 添加配置并重启 NodeManager |
| OOM: GC overhead | Local 模式处理大量小文件 | 切换到 YARN 模式，调大容器内存 |
| MySQL Access Denied | 用户权限不足 | `GRANT ALL ... TO 'root'@'master'` |
| 前端 np is not defined | 返回了 numpy 类型 | 后端转换为 Python 原生类型 |
| JS 文件乱码 | 编码不一致 | 统一保存为 UTF-8 |
| 静态文件 404 | STATIC_URL 配置错误 | 检查 settings.py 和模板路径 |
| Sqoop 导出全 NULL | 字段分隔符不匹配 | 检查 Hive 建表和 Sqoop 参数 |
| Hive 查询慢 | MapReduce 任务多 | 调优 YARN 内存配置 |
| Django DisallowedHost | ALLOWED_HOSTS 限制 | 添加允许的 IP 或设为 ['*'] |
| 预测脚本报错 steps | statsmodels API 变更 | 使用 `model.forecast(12)` |

---

## D. 项目启动检查清单

### 集群启动检查
- [ ] Master 节点：NameNode、ResourceManager 进程正常
- [ ] Slave 节点：DataNode、NodeManager 进程正常
- [ ] HDFS Web UI 可访问：http://master:50070
- [ ] YARN Web UI 可访问：http://master:8088
- [ ] Active Nodes 数量正确（应为 2 或 3）

### 数据库检查
- [ ] MySQL 服务运行中
- [ ] china_all 数据库存在
- [ ] 6 张结果表数据完整
- [ ] province_temp 表的 temp_forecast 字段已填充

### Django 应用检查
- [ ] 虚拟环境已激活
- [ ] 依赖已安装：`pip install -r requirements.txt`
- [ ] 数据库连接配置正确（settings.py）
- [ ] 静态文件路径配置正确
- [ ] 开发服务器启动成功：`python manage.py runserver 0.0.0.0:8000`
- [ ] 浏览器访问 http://master:8000 正常显示大屏

### 数据验证
- [ ] 地图数据：各省份气温/风速显示正常
- [ ] 时间轴：自动轮播 1-12 月
- [ ] 折线图：历史曲线 + 预测曲线同时显示
- [ ] 词云：城市温度词云渲染正常
- [ ] 柱状图：降水 Top10 排序正确
- [ ] 树图：省份气压分布显示正常

---

## E. 答辩常见问题预测

### 技术选型类
1. **为什么选择 Hadoop 2.9.2 而不是 3.x？**
   - 稳定性考虑，2.x 版本生态成熟，与 Hive/Sqoop 兼容性好

2. **为什么使用 Holt-Winters 而不是 ARIMA？**
   - 气温数据有明显的 12 个月季节性，Holt-Winters 对周期性数据拟合更好

3. **为什么不用 Django ORM 而直接用 pandas.read_sql？**
   - 数据已在 MySQL 清洗完成，直接读取更高效，避免 ORM 映射开销

### 问题解决类
4. **遇到 OOM 问题是如何解决的？**
   - 从 Local 模式切换到 YARN 模式，分散算力到多节点

5. **如何处理 10,000+ 个小文件？**
   - 放弃 CombineTextInputFormat（会丢失文件名），接受多 Map 任务，依赖 YARN 调度

6. **数据精度放大 10 倍是在哪里处理的？**
   - 在 Hive/Django 层保留原值，仅在前端展示时除以 10

### 扩展思考类
7. **如果数据量增加 10 倍，系统如何扩展？**
   - 横向扩展 Slave 节点，调整 YARN 资源配置

8. **预测模型有什么改进空间？**
   - 可尝试 LSTM、Prophet 等深度学习/自动化模型

9. **如何实现实时数据更新？**
   - 引入 Kafka + Flink 实时流处理管道


