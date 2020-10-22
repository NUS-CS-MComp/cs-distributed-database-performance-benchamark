-- Related customer query using warehouse=1, district=1, customer=1
WITH customer_order_lines AS (
    SELECT DISTINCT ol_i_id, ol_w_id, ol_d_id, ol_o_id
    FROM order_line
    JOIN (
        SELECT *
        FROM "order"
        WHERE o_w_id = 1
          AND o_d_id = 1
          AND o_c_id = 1
    ) o ON o.o_w_id = order_line.ol_w_id AND o.o_d_id = order_line.ol_d_id AND o.o_id = order_line.ol_o_id
), other_order_lines AS (
    SELECT DISTINCT ol_i_id, ol_w_id, ol_d_id, ol_o_id, o2.c_id
    FROM order_line
    JOIN (
        SELECT *
        FROM "order" other_order
        JOIN (
            SELECT *
            FROM customer
            WHERE c_w_id != 1
        ) c2 ON other_order.o_w_id = c2.c_w_id AND other_order.o_d_id = c2.c_d_id AND other_order.o_c_id = c2.c_id
     ) o2 ON o2.o_w_id = order_line.ol_w_id AND o2.o_d_id = order_line.ol_d_id AND o2.o_id = order_line.ol_o_id
)
SELECT DISTINCT ool.ol_w_id, ool.ol_d_id, ool.c_id
FROM (
    SELECT
        col1.ol_i_id AS col1_i_id,
        col2.ol_i_id AS col2_i_id,
        col1.ol_w_id,
        col1.ol_d_id,
        col1.ol_o_id
    FROM customer_order_lines col1
    JOIN customer_order_lines col2
        ON col1.ol_w_id = col2.ol_w_id AND col1.ol_d_id = col2.ol_d_id AND col1.ol_o_id = col2.ol_o_id
    WHERE col1.ol_i_id < col2.ol_i_id
) col
JOIN (
    SELECT
        ool1.ol_i_id AS ool1_i_id,
        ool2.ol_i_id AS ool2_i_id,
        ool1.ol_w_id,
        ool1.ol_d_id,
        ool1.ol_o_id,
        ool1.c_id
    FROM other_order_lines ool1
    JOIN other_order_lines ool2
        ON ool1.ol_w_id = ool2.ol_w_id AND ool1.ol_d_id = ool2.ol_d_id AND ool1.ol_o_id = ool2.ol_o_id
    WHERE ool1.ol_i_id < ool2.ol_i_id
) ool ON ool.ool1_i_id = col.col1_i_id AND ool.ool2_i_id = col.col2_i_id;
