-- Popular items query using warehouse=1, district=1
SELECT *
FROM order_line ol1
JOIN (
    SELECT o_id, o_d_id, o_w_id, o_entry_d, o_c_id, c.c_first, c.c_middle, c.c_last
    FROM "order"
    JOIN customer c ON "order".o_w_id = c.c_w_id AND "order".o_d_id = c.c_d_id AND "order".o_c_id = c.c_id
    WHERE o_w_id = 1 AND o_d_id = 1
    ORDER BY o_entry_d DESC
    LIMIT 10
) o ON ol1.ol_w_id = o.o_w_id AND  ol1.ol_d_id = o.o_d_id AND o.o_id = ol1.ol_o_id
JOIN item i ON i.i_id = ol1.ol_i_id
WHERE ol1.ol_w_id = 1 AND ol1.ol_d_id = 1 AND ol1.ol_quantity IN (
    SELECT MAX(ol2.ol_quantity)
    FROM order_line ol2
    WHERE ol2.ol_w_id = ol1.ol_w_id AND ol2.ol_d_id = ol1.ol_d_id AND ol2.ol_o_id = ol1.ol_o_id
)
ORDER BY o.o_id;
