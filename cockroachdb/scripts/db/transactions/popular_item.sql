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





# get items with max quantity in each order  # sample with d_id = 1, w_id = 1 and o_id = 3246
SELECT ol2.ol_w_id, ol2.ol_d_id, ol2.ol_o_id, ol2.ol_i_id, SUM(ol2.ol_quantity)
FROM order_line ol2
WHERE ol2.ol_w_id = 1 and ol2.ol_d_id = 1 and ol2.ol_o_id >= 3246 
GROUP BY ol2.ol_w_id, ol2.ol_d_id, ol2.ol_o_id, ol2.ol_i_id
HAVING (ol2.ol_w_id, ol2.ol_d_id, ol2.ol_o_id, SUM(ol2.ol_quantity)) IN
    (
    # get max quantity for each order
    SELECT ol1.w_id, ol1.d_id, ol1.o_id, MAX(ol1.sum_quantity) as "max_quantity"
    FROM
    (
        # group order by items and count sum of quantity for each item
        SELECT ol.ol_w_id as "w_id", ol.ol_d_id as "d_id", ol.ol_o_id as "o_id", ol.ol_i_id as "i_id", SUM(ol.ol_quantity) as "sum_quantity"
        FROM order_line ol
        WHERE ol.ol_w_id = 1 and ol.ol_d_id = 1 and ol.ol_o_id >= 3246
        GROUP BY ol.ol_w_id, ol.ol_d_id, ol.ol_o_id, ol.ol_i_id
    ) ol1
    GROUP BY ol1.w_id, ol1.d_id, ol1.o_id
    )