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
    u.realname = '陈伟南'
    AND b.product = 51
    AND b.openedDate BETWEEN '2025-07-30 00:00:00' AND '2025-08-28 23:59:59'
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