INSERT INTO warehouse
VALUES (1, 'WH 1', '10 WH St.', null, 'New Brunswick', 'NJ', '10000', '0.2042'),
       (2, 'WH 2', '10 WH St.', null, 'New Brunswick', 'NJ', '10000', '0.3401'),
       (3, 'WH 3', '10 WH St.', null, 'New Brunswick', 'NJ', '10000', '0.1940')
ON CONFLICT DO NOTHING;

INSERT INTO district
VALUES (1, 1, 'District 1', '10 D St.', null, 'New Brunswick', 'NJ', '10000', '0.2020'),
       (2, 1, 'District 2', '10 D St.', null, 'New Brunswick', 'NJ', '10000', '0.2020'),
       (3, 1, 'District 3', '10 D St.', null, 'New Brunswick', 'NJ', '10000', '0.2020')
ON CONFLICT DO NOTHING;

INSERT INTO customer
VALUES (1, 1, 1, 'Terry', null, 'Lu', '10 Dover St.', null, 'New Brunswick', 'NJ', '10039', null)
ON CONFLICT DO NOTHING;

INSERT INTO item
VALUES (1, 'Item 1', 32.42),
       (2, 'Item 2', 92.38),
       (3, 'Item 3', 25.31)
ON CONFLICT DO NOTHING;

INSERT INTO stock
VALUES (1, 1, 100),
       (1, 2, 10),
       (1, 3, 0)
ON CONFLICT DO NOTHING;
