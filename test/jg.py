from diagrams import Diagram, Cluster, Edge
from diagrams.generic.database import SQL
from diagrams.generic.place import Datacenter
from diagrams.onprem.analytics import Spark, Flink
from diagrams.custom import Custom

with Diagram("AI运维体系分层架构图", show=False, direction="TB"):
    # 基础层
    with Cluster("基础层"):
        data_lake = Custom("异构数据湖\n(15类数据接入)", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")
        spark = Spark("Spark离线计算")
        flink = Flink("Flink实时处理")
        k8s = Datacenter("Kubernetes容器化资源调度")

    # 能力层
    with Cluster("能力层"):
        algo_engine = Custom("智能标注核心引擎\n(23个算法模块)", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")
        kg_neo4j = SQL("Neo4j")
        kg_janus = Custom("JanusGraph", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")
        qc_system = Custom("质量控制系统\n(6σ质量管理模型)", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")

    # 应用层
    with Cluster("应用层"):
        app_monitor = Custom("智能监控标注系统", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")
        app_root_cause = Custom("根因分析标注平台", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")
        app_auto_repair = Custom("自动化修复配置中心", "/Users/leiyuxing/PycharmProjects/TestFramework/test/JANUSGRAPH.jpg")

    # 依赖关系
    data_lake >> Edge(color="darkgreen") << [spark, flink]
    [spark, flink] >> Edge(color="blue") << k8s
    k8s >> Edge(color="purple") >> algo_engine
    algo_engine >> Edge() << [kg_neo4j, kg_janus]
    [kg_neo4j, kg_janus] >> Edge() << qc_system
    qc_system >> Edge(color="red") >> [app_monitor, app_root_cause, app_auto_repair]