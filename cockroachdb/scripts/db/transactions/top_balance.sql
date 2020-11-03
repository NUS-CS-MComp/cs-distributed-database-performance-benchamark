-- Top customer balance query
WITH top_customer AS (
    SELECT c_first, c_middle, c_last, c_balance, c_d_id, c_w_id
    FROM customer
    ORDER BY customer.c_balance DESC
    LIMIT 10
)
SELECT top_customer.*, d_name, w_name
FROM top_customer
JOIN district ON d_id = top_customer.c_d_id AND d_w_id = top_customer.c_w_id
JOIN warehouse w on top_customer.c_w_id = w.w_id
ORDER BY top_customer.c_balance DESC;
