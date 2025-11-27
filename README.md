# 大数据气象分析平台 - 项目答辩汇报

## 1. 项目背景与架构 (Overview)

**项目名称**：基于 Hadoop 的全国气象数据分析与可视化平台

**数据来源**：NCDC（美国国家气候数据中心）公开气象数据（1942年至今）。

**核心目标**：
- 搭建高可用的大数据集群环境。
- 清洗并处理海量非结构化气象数据。
- 多维度统计分析全国各省市气温、降水、风速等指标。
- 利用机器学习算法预测未来气温趋势。
- 通过 Web 大屏进行可视化展示。

**技术架构**：
- 基础设施：VMware + CentOS 7 (Master + 2 Slaves)
- 存储层：HDFS（分布式文件系统）、MySQL（结果存储/元数据）
- 计算层：YARN（资源调度）、MapReduce（离线计算）
- 数仓层：Hive（数据仓库/SQL 分析）
- 传输层：Sqoop（数据迁移）
- 挖掘层：Python（Pandas、Statsmodels、SQLAlchemy）
- 展示层：Django + ECharts + Bootstrap

---

## 2. 项目实施全流程 (Implementation)
（建议配合架构图讲解）

### 阶段一：基础设施搭建
- 搭建了 1 Master + 2 Slaves 的 Hadoop 完全分布式集群。
- 配置了 SSH 免密登录、JDK 环境、Hadoop 核心参数（如 `core-site.xml`, `yarn-site.xml` 等）。
- 亮点：成功解决了虚拟机网络配置（静态 IP + NAT）、防火墙策略配置等基础环境问题。

### 阶段二：数据采集与清洗 (ETL)
- 采集：将 NCDC 原始 `.gz` 压缩文件上传至 HDFS。
- 清洗（MapReduce）：
  - 编写 Java MapReduce 程序，从文件名中提取基站 ID。
  - 清洗原始文本数据，处理缺失值，转换为 CSV 格式。
- 技术挑战：处理了 22 年共 10,897 个小文件，解决了 MapReduce 本地模式内存溢出（OOM）问题。

### 阶段三：数据仓库建设与分析
- Hive 数仓分层设计：
  - ODS 层：加载清洗后的原始数据。
  - DIM 层：建立基站-城市映射表。
  - DWD 层：构建全量宽表，关联地理位置信息。
  - APP 层：统计各省月均气温、降水 Top10 城市、风速分布等指标。
- 数据迁移：使用 Sqoop 将 Hive 分析结果表批量导出至 MySQL，打通数据流。

### 阶段四：数据挖掘与预测
- 利用 Python 连接 MySQL 读取历史数据。
- 应用指数平滑法（Holt-Winters）和 ARIMA 模型对各省份气温进行时间序列预测。
- 创新点：实现了模型的批量训练与自动化入库，对比不同算法的 RMSE（均方根误差）并择优使用。

### 阶段五：可视化大屏开发
- 搭建 Django Web 后端，开发数据 API 接口。
- 前端集成 ECharts，实现：
  - 动态地图：展示各省气温颜色分级与风速散点。
  - 时间轴轮播：自动播放 1-12 月的数据变化。
  - 多图表联动：包含柱状图、词云图、折线图（含预测曲线）和矩形树图。

---

## 3. 核心技术难点与解决方案 (Challenges & Solutions)
（这是答辩加分项，证明你真的动手做了）

### 内存溢出（OOM）问题
- 现象：在运行 MapReduce 清洗 1 万个文件时，Master 节点报错 `GC overhead limit exceeded`。
- 解决：分析发现是 Local 模式导致单机负载过高。通过修改代码强制使用 YARN 集群模式（`mapreduce.framework.name=yarn`），并将 Master 内存升级至 16GB，成功利用集群算力解决问题。

### 集群节点通信故障
- 现象：YARN 任务卡在 `ACCEPTED` 状态，Active Nodes 为 0。
- 解决：排查发现 `yarn-site.xml` 缺少 `yarn.resourcemanager.hostname` 配置，导致 Slave 无法连接 Master 的 8031 端口。通过修正配置并同步分发解决问题。

### 数据类型兼容性
- 现象：Web 大屏不显示，前端报错 `Uncaught ReferenceError: np is not defined`。
- 解决：发现是 Pandas 读取的数据类型（`np.int64`）无法被 JS 识别。在 Django 后端增加了强制类型转换逻辑，将数据转为原生 Python 类型后再序列化为 JSON。

### 软件版本冲突
- 现象：Django 连接 MySQL 5.7 报错。
- 解决：定位到新版 Django 不支持旧版 MySQL，通过降级 Django 到 3.2 LTS 版本解决兼容性问题。

---

## 4. 项目成果展示 (Project Demo)
（此时可以打开浏览器演示）

- 数据闭环：展示 MySQL 数据库中 `province_temp_all` 表，证明预测数据已成功回写。
- 可视化大屏：
  - 展示地图随时间轴自动轮播的效果。
  - 展示包含“历史数据”和“预测数据”的折线图，体现数据挖掘成果。
  - 展示交互功能（鼠标悬停显示具体数值）。

---

## 5. 总结与展望

**总结**：本项目打通了从数据采集、存储、计算、挖掘到展示的全链路，构建了一套完整的大数据处理系统。

**展望**：
- 引入 Spark 替代 MapReduce 提升计算速度。
- 引入 Kafka 实现实时气象数据处理。
- 优化前端界面，适配移动端展示。

---

## 6. 运维与常见故障排查 (Environment, Network, Cluster & Dev Troubleshooting)

下面将你提出的运维类问题按四类汇总，包含现象、原因与解决方案（都以实战经验为主）。

### 🛑 第一类：基础设施与网络配置 (Environment & Network)

1. 虚拟机网卡配置缺失  
- 现象：执行 `systemctl restart network` 失败，`ip addr` 只显示 `lo` 和 `ens33`，缺少外网网卡。  
- 原因：VMware 中未添加第二块 NAT 模式网卡（应为 `ens36`）。  
- 解决：关机 → 编辑虚拟机设置 → 添加网络适配器 → 选择 NAT 模式。

2. Windows 无法访问 Hadoop Web 页面  
- 现象：Windows 浏览器访问 `192.168.56.101:50070` 超时，但虚拟机内网互通。  
- 原因：Windows 的虚拟网卡 VMnet1 的 IP（如 `192.168.146.1`）与虚拟机集群（`192.168.56.x`）不在同一网段。  
- 解决：修改 Windows 网络适配器 VMnet1 的 IPv4 设置，固定为 `192.168.56.1`。

3. 集群内网通信失败（Hosts 配置错误）  
- 现象：Master ping Slave 失败，显示 100% packet loss。  
- 原因：`/etc/hosts` 中 Master 的 IP 写错（如 `192.168.15.101`，应为 `192.168.56.101`）。  
- 解决：修正 `hosts` 文件并重新分发到所有节点。

---

### 🛑 第二类：Hadoop 集群运维 (Cluster Operations)

4. Slave 节点缺少环境  
- 现象：在 Slave 执行 `java -version` 报 `command not found`。  
- 原因：只在 Master 解压 JDK/Hadoop，忘记分发到从节点。  
- 解决：使用 `scp` 或编写分发脚本将 `/home/java`、`/home/hadoop` 及环境配置（如 `/etc/profile`）同步到所有 Slave。

5. Hive 连接拒绝 (Connection Refused)  
- 现象：启动 Hive 报错 `java.net.ConnectException: Call From ... to master:9000 failed`。  
- 原因：Linux 重启后 HDFS/YARN 未自动启动，Hive 无法连接未启动的 HDFS。  
- 解决：重启机器后先执行 `start-all.sh` 启动 Hadoop 集群（或用 `sbin/start-dfs.sh`、`sbin/start-yarn.sh` 分步启动）。

6. HDFS 安全模式锁定 (Safe Mode)  
- 现象：执行 `hdfs dfs -rm` 报错 Name node is in safe mode。  
- 原因：HDFS 刚启动或数据块复制率不足时进入只读安全模式。  
- 解决：执行 `hdfs dfsadmin -safemode leave` 强制退出安全模式，或等待系统完成检查。

---

### 🛑 第三类：MapReduce 开发与性能调优 (Core Challenges)

7. 内存溢出 (OOM: GC overhead limit exceeded) 🔥（最核心难点）  
- 现象：运行 MapReduce 清洗 22 年气象数据（约 1.1 万个文件）时程序崩溃报错。  
- 原因：
  - 代码在 Local 模式下运行，Master 节点（仅 4GB）无法同时承受大量 Map 任务对象。
  - 小文件问题使切片数量极多。  
- 解决（组合拳）：
  - 升级硬件：Master 内存从 4GB 扩容到 16GB。
  - 切换架构：在代码中 `conf.set("mapreduce.framework.name", "yarn")` 强制使用 YARN 集群模式。
  - 资源调优：调整 `yarn-site.xml` 中 `yarn.nodemanager.resource.memory-mb`（示例从默认 4096 提高到 6144），并合理设置 Map/Reduce 内存参数。

8. 集群节点“失联” (Active Nodes = 0)  
- 现象：YARN 任务提交后卡在 `ACCEPTED`，Web 界面 Active Nodes = 0，日志显示 Slave 连接 `0.0.0.0:8031` 失败。  
- 原因：`yarn-site.xml` 缺少 `yarn.resourcemanager.hostname` 配置，且防火墙/iptables 未关闭。  
- 解决：补充 `yarn.resourcemanager.hostname`（如 `master`），同步分发到所有节点，关闭防火墙并重启 YARN 服务。

9. 代码逻辑冲突 (ClassCastException)  
- 现象：使用 `CombineTextInputFormat` 优化小文件时报 `ClassCastException`。  
- 原因：CombineTextInputFormat 生成的切片类型与 Mapper 中强制将 InputSplit 转为 `FileSplit` 不兼容，导致无法获取文件名。  
- 解决：放弃合并切片策略，利用 YARN 集群算力承受大量切片；同时修正 Mapper 获取文件名的 API（使用通用的 `InputSplit` 判断和适配逻辑）。

10. Windows 本地开发环境缺失  
- 现象：在 Windows IDEA 运行时报 `HADOOP_HOME and hadoop.home.dir are unset`。  
- 原因：Windows 本地运行 Hadoop 需要 `winutils.exe` 等，本地环境配置复杂。  
- 解决：将项目打包为 JAR，上传至 Linux Master 节点并直接 `hadoop jar ...` 提交运行，放弃在 Windows 上直接运行集群相关作业。

---

### 🛑 第四类：Web 可视化与全链路 (Visualization & Integration)

11. 前端数据类型报错 (np is not defined)  
- 现象：大屏页面白屏，控制台报 `Uncaught ReferenceError: np is not defined`。  
- 原因：Pandas 使用 `numpy` 类型（如 `np.int64`、`np.float64`），前端 JS 无法识别。  
- 解决：在 Django 后端（views.py）遍历数据并强制将数值类型转换为 Python 原生 `int()` 或 `float()`，然后再序列化为 JSON。

12. JS 文件中文乱码  
- 现象：时间轴组件不显示，JS 文件中中文注释或变量出现乱码。  
- 原因：Windows 编辑时使用 GBK 编码，浏览器默认 UTF-8 导致乱码。  
- 解决：在 IDE 中将文件编码转换为 UTF-8 并保存，或在 HTTP header 指定 `Content-Type: text/javascript; charset=utf-8`。

13. MySQL 权限拒绝 (Access Denied)  
- 现象：Sqoop 导出时报 `Access denied for user 'root'@'master'`。  
- 原因：MySQL 用户权限未明确授予来自 master 的访问，或密码策略/主机解析导致授权失败。  
- 解决：在 MySQL 中显式授予 `root@'master'` 权限，或使用 `%` 并确保主机名解析一致；必要时调整 MySQL 密码策略。

14. Django 版本不兼容  
- 现象：启动 Django 报 `MySQL 8.0 or later is required`。  
- 原因：安装了 Django 新版本（4.x/5.x），与 CentOS7 上的 MySQL 5.7 不兼容。  
- 解决：降级 Django 至 3.2 LTS（与 MySQL 5.7 兼容），或升级数据库到受支持的版本。

---

（附）常用命令速查：
- 启动 HDFS/YARN：`sbin/start-dfs.sh`、`sbin/start-yarn.sh` 或 `sbin/start-all.sh`
- 退出 HDFS 安全模式：`hdfs dfsadmin -safemode leave`
- 查看节点状态：HDFS Web UI（NameNode:50070/9870）、YARN ResourceManager（8088）
- 分发文件：`scp -r /path/to/hadoop slave:/path/to/` 或用 `rsync`/配置管理工具

---