# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: 开发绩效明细.py
@time: 2025/8/29 19:38
"""
import pymysql
import pandas as pd
from datetime import datetime

# 数据库连接配置
db_config = {
    'host': '192.168.30.34',
    'port': 3306,
    'user': 'leiyx',
    'password': 'Leiyx#2022',
    'database': 'zentao',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def query_timeout_bugs(developer_name, product_id, start_date, end_date):
    """
    查询指定开发人员在指定产品和时间范围内的超时Bug

    Parameters:
    developer_name: 开发人员姓名
    product_id: 产品ID
    start_date: 开始时间 (格式: 'YYYY-MM-DD HH:MM:SS')
    end_date: 结束时间 (格式: 'YYYY-MM-DD HH:MM:SS')
    """

    # SQL查询语句（使用参数化查询）
    sql_query = """
    SELECT
        u.realname AS 开发人员,
        b.id AS BugID,
        b.title AS Bug标题,
        b.severity AS 严重程度,
        b.pri AS 优先级,
        CASE
            WHEN (b.severity = 1 OR b.pri = 1) THEN '一级超时'
            ELSE '普通超时'
        END AS 超时类型,
        b.openedDate AS 创建时间,
        b.resolvedDate AS 解决时间,
        TIMESTAMPDIFF(HOUR, b.openedDate, COALESCE(b.resolvedDate, NOW())) AS 处理时长_小时,
        CASE
            WHEN (b.severity = 1 OR b.pri = 1) THEN
                CASE
                    WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN 72  -- 一级优先级周末顺延
                    ELSE 24  -- 一级优先级正常
                END
            ELSE
                CASE
                    WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN 120  -- 普通优先级周末顺延
                    ELSE 72  -- 普通优先级正常
                END
        END AS 超时阈值_小时,
        CASE
            WHEN b.resolvedDate IS NOT NULL THEN '已解决'
            WHEN b.status = 'active' THEN '未解决'
            ELSE b.status
        END AS 状态,
        b.type AS Bug类型
    FROM
        zt_user u
    JOIN
        zt_bug b ON (u.account = b.resolvedBy OR u.account = b.assignedTo)
    WHERE
        u.realname = %s
        AND b.product = %s
        AND b.openedDate BETWEEN %s AND %s
        AND b.deleted = '0'
        AND (
            -- 一级优先级超时条件
            ((b.severity = 1 OR b.pri = 1) AND
                (
                    -- 已解决的一级超时bug
                    (b.resolvedDate IS NOT NULL AND
                     TIMESTAMPDIFF(HOUR, b.openedDate, b.resolvedDate) >
                        CASE
                            WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN 72
                            ELSE 24
                        END)
                    OR
                    -- 未解决的一级超时bug
                    (b.status = 'active' AND
                     NOW() >
                        CASE
                            WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN DATE_ADD(b.openedDate, INTERVAL 72 HOUR)
                            ELSE DATE_ADD(b.openedDate, INTERVAL 24 HOUR)
                        END)
                ))
            OR
            -- 普通优先级超时条件
            ((b.severity != 1 AND b.pri != 1) AND
                (
                    -- 已解决的普通超时bug
                    (b.resolvedDate IS NOT NULL AND
                     TIMESTAMPDIFF(HOUR, b.openedDate, b.resolvedDate) >
                        CASE
                            WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN 120
                            ELSE 72
                        END)
                    OR
                    -- 未解决的普通超时bug
                    (b.status = 'active' AND
                     NOW() >
                        CASE
                            WHEN DAYOFWEEK(b.openedDate) IN (1, 6, 7) THEN DATE_ADD(b.openedDate, INTERVAL 120 HOUR)
                            ELSE DATE_ADD(b.openedDate, INTERVAL 72 HOUR)
                        END)
                ))
        )
    ORDER BY
        CASE WHEN (b.severity = 1 OR b.pri = 1) THEN 1 ELSE 2 END,  -- 先显示一级超时
        b.openedDate DESC;
    """

    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)

        print("数据库连接成功！")
        print(f"开始查询：{developer_name}在产品ID:{product_id}的超时Bug")
        print(f"时间范围：{start_date} 至 {end_date}")
        print("-" * 80)

        # 执行查询（使用参数化查询防止SQL注入）
        with connection.cursor() as cursor:
            cursor.execute(sql_query, (developer_name, product_id, start_date, end_date))
            results = cursor.fetchall()

            # 将结果转换为DataFrame以便更好的显示
            df = pd.DataFrame(results)

            if len(df) > 0:
                print(f"找到 {len(df)} 条超时Bug记录：")
                print("-" * 80)

                # 显示结果
                for index, row in df.iterrows():
                    print(f"BugID: {row['BugID']}")
                    print(f"标题: {row['Bug标题']}")
                    print(f"严重程度: {row['严重程度']}, 优先级: {row['优先级']}")
                    print(f"超时类型: {row['超时类型']}")
                    print(f"创建时间: {row['创建时间']}")
                    print(f"解决时间: {row['解决时间']}")
                    print(f"处理时长: {row['处理时长_小时']} 小时")
                    print(f"超时阈值: {row['超时阈值_小时']} 小时")
                    print(f"状态: {row['状态']}")
                    print(f"Bug类型: {row['Bug类型']}")
                    print("-" * 50)

                # 统计信息
                print("\n统计信息：")
                print(f"总超时Bug数: {len(df)}")
                print(f"一级超时: {len(df[df['超时类型'] == '一级超时'])}")
                print(f"普通超时: {len(df[df['超时类型'] == '普通超时'])}")
                print(f"已解决: {len(df[df['状态'] == '已解决'])}")
                print(f"未解决: {len(df[df['状态'] == '未解决'])}")

                return df
            else:
                print("未找到符合条件的超时Bug记录。")
                return pd.DataFrame()

    except pymysql.Error as e:
        print(f"数据库连接或查询错误: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.open:
            connection.close()
            print("\n数据库连接已关闭。")


# 使用示例
if __name__ == "__main__":
    # 参数配置
    developer_name = '陈伟南'
    product_id = 51
    start_date = '2025-07-30 00:00:00'
    end_date = '2025-08-28 23:59:59'

    # 执行查询
    result_df = query_timeout_bugs(developer_name, product_id, start_date, end_date)

    # # 查询不同人员和时间范围
    # result1 = query_timeout_bugs('陈伟南', 51, '2025-07-30 00:00:00', '2025-08-28 23:59:59')
    # result2 = query_timeout_bugs('张三', 52, '2025-08-01 00:00:00', '2025-08-31 23:59:59')

    # 如果需要保存结果到文件
    if result_df is not None and not result_df.empty:
        result_df.to_csv('timeout_bugs_report.csv', index=False, encoding='utf-8-sig')
        print("结果已保存到 timeout_bugs_report.csv")
