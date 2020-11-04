-- Popular items query using warehouse=1, district=1
SELECT ol1.ol_o_id, o.o_entry_d, CONCAT(o.c_first, o.c_middle, o.c_last), SUM(ol1.ol_quantity) AS qty, i.i_id, i.i_name
FROM order_line ol1
JOIN (
    SELECT o_id, o_d_id, o_w_id, o_entry_d, o_c_id, c.c_first, c.c_middle, c.c_last
    FROM "order"
    JOIN customer c ON "order".o_w_id = c.c_w_id AND "order".o_d_id = c.c_d_id AND "order".o_c_id = c.c_id
    WHERE o_w_id = 1 AND o_d_id = 1
    ORDER BY o_entry_d DESC
    LIMIT 10
) o ON ol1.ol_w_id = o.o_w_id AND ol1.ol_d_id = o.o_d_id AND o.o_id = ol1.ol_o_id
JOIN item i ON i.i_id = ol1.ol_i_id
GROUP BY ol1.ol_o_id, o.o_entry_d, CONCAT(o.c_first, o.c_middle, o.c_last), i.i_id, i.i_name
HAVING (ol1.ol_o_id, SUM(ol1.ol_quantity)) IN (
    SELECT sum_ol.ol_o_id, MAX(sum_ol.qty)
    FROM(
        SELECT ol2.ol_w_id, ol2.ol_d_id, ol2.ol_o_id, SUM(ol2.ol_quantity) AS qty
        FROM order_line ol2
        WHERE ol2.ol_w_id = 1 AND ol2.ol_d_id = 1
        GROUP BY ol2.ol_w_id, ol2.ol_d_id, ol2.ol_o_id, ol2.ol_i_id
    ) sum_ol
    GROUP BY sum_ol.ol_w_id, sum_ol.ol_d_id, sum_ol.ol_o_id
)
ORDER BY ol1.ol_o_id DESC, i.i_id, qty DESC;
