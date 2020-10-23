-- Order status query using warehouse=1, district=1, customer=1
SELECT o.*
FROM "order" o
WHERE o_d_id = 1 AND o_w_id = 1 AND o_c_id = 1
ORDER BY o.o_entry_d DESC
LIMIT 1;
