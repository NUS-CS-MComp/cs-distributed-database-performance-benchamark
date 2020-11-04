-- Stock level query using warehouse=1, district=1, last_order=10, threshold=1000
SELECT COUNT((s_w_id, s_i_id))
FROM stock
JOIN (
    SELECT DISTINCT ol_w_id, ol_i_id
    FROM order_line
    JOIN district d ON d.d_w_id = ol_w_id AND d.d_id = ol_d_id
    WHERE ol_w_id = 1 AND ol_d_id = 1 AND ol_o_id >= d.d_next_o_id - 10
) ol ON s_w_id = ol.ol_w_id AND s_i_id = ol.ol_i_id
WHERE s_quantity < 1000;



