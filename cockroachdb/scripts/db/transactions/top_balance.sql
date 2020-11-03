-- Top customer balance query
SELECT c_first, c_middle, c_last, c_balance, w.w_name, d.d_name
FROM customer
JOIN district d on d.d_w_id = customer.c_w_id and d.d_id = customer.c_d_id
JOIN warehouse w on w.w_id = d.d_w_id
ORDER BY customer.c_balance DESC
LIMIT 10;
