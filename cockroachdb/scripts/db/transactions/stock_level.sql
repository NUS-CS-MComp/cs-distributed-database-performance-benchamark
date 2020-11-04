-- Stock level query using warehouse=1, district=1, last_order=10, threshold=100
SELECT COUNT((s_w_id, s_i_id))
FROM stock
JOIN (
    SELECT DISTINCT ol_w_id, ol_i_id
    FROM order_line
    JOIN (
        SELECT o_w_id, o_d_id, o_id
        FROM "order"
        JOIN district d on d.d_w_id = o_w_id and d.d_id = o_d_id
        WHERE o_w_id = 1
          AND o_d_id = 1
          AND o_id >= d.d_next_o_id - 10
    ) o ON ol_w_id = o_w_id AND ol_d_id = o_d_id AND ol_o_id = o_id
    WHERE ol_w_id = 1 AND ol_d_id = 1
) ol ON s_w_id = ol.ol_w_id AND s_i_id = ol.ol_i_id
WHERE s_quantity < 1000;


SELECT COUNT((s_w_id, s_i_id))
FROM stock
JOIN (
    SELECT DISTINCT ol_w_id, ol_i_id
    FROM order_line
    WHERE ol_w_id = 1 AND ol_d_id = 1 AND ol_o_id >= d.d_next_o_id - 10
) ol ON s_w_id = ol.ol_w_id AND s_i_id = ol.ol_i_id
WHERE s_quantity < 1000;



