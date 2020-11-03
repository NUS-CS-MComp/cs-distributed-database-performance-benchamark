-- Related customer query using warehouse=1, district=1, customer=1
WITH customer_order_lines AS (
    SELECT DISTINCT ol_i_id, ol_w_id, ol_d_id, ol_o_id
    FROM order_line
    JOIN (
        SELECT o_w_id, o_d_id, o_id
        FROM "order"
        WHERE o_w_id = 1
          AND o_d_id = 1
          AND o_c_id = 1
    ) o ON o.o_w_id = order_line.ol_w_id AND o.o_d_id = order_line.ol_d_id AND o.o_id = order_line.ol_o_id
), customer_order_line_item_pairs AS (
    SELECT col1.ol_i_id AS col1_i_id,
           col2.ol_i_id AS col2_i_id
    FROM customer_order_lines col1
    JOIN customer_order_lines col2
    ON col1.ol_w_id = col2.ol_w_id AND col1.ol_d_id = col2.ol_d_id AND col1.ol_o_id = col2.ol_o_id AND col1.ol_i_id < col2.ol_i_id
), other_customer_order_lines_containing_same_item AS (
    SELECT DISTINCT ol_i_id, ol_w_id, ol_d_id, ol_o_id
    FROM order_line
    WHERE ol_w_id != 1
      AND ol_i_id IN (
        SELECT DISTINCT customer_order_lines.ol_i_id
        FROM customer_order_lines
    )
)
SELECT DISTINCT ool1.ol_w_id, ool1.ol_d_id, o.o_c_id
FROM other_customer_order_lines_containing_same_item ool1
JOIN other_customer_order_lines_containing_same_item ool2
ON ool1.ol_w_id = ool2.ol_w_id AND ool1.ol_d_id = ool2.ol_d_id AND ool1.ol_o_id = ool2.ol_o_id AND ool1.ol_i_id < ool2.ol_i_id
JOIN "order" o ON ool1.ol_o_id = o.o_id
WHERE (ool1.ol_i_id, ool2.ol_i_id) IN (
    SELECT col1_i_id, col2_i_id
    FROM customer_order_line_item_pairs
)
ORDER BY ool1.ol_w_id, ool1.ol_d_id, o.o_c_id;

