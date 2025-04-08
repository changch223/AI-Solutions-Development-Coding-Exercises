DROP TABLE IF EXISTS report_current_month;
CREATE TABLE report_current_month
SELECT r.region_name,
	   s.state_name,
	   SUM(i.quantity) AS monthly_quantity_sold,
	   SUM(i.amount) - SUM(i.unit_cost * i.quantity) AS monthly_profit,
	   SUM(i.amount) AS monthly_revenue
FROM orders o
	 JOIN order_items i ON o.order_id = i.order_id
	 JOIN stores ON o.postal_code = stores.postal_code
	 JOIN cities c ON stores.city_id = c.city_id
	 JOIN states s ON c.state_code = s.state_code
	 JOIN regions r ON s.region_code = r.region_code
WHERE o.order_date >= '2021-11-01' AND o.order_date < '2021-12-01'
GROUP BY YEAR(o.order_date),
	  	 MONTH(o.order_date),
	   	 r.region_name,
		 s.state_name;

DROP TABLE IF EXISTS report_prev_month;
CREATE TABLE report_prev_month
SELECT r.region_name,
	   s.state_name,
	   SUM(i.quantity) AS monthly_quantity_sold,
	   SUM(i.amount) - SUM(i.unit_cost * i.quantity) AS monthly_profit,
	   SUM(i.amount) AS monthly_revenue
FROM orders o
	 JOIN order_items i ON o.order_id = i.order_id
	 JOIN stores ON o.postal_code = stores.postal_code
	 JOIN cities c ON stores.city_id = c.city_id
	 JOIN states s ON c.state_code = s.state_code
	 JOIN regions r ON s.region_code = r.region_code
WHERE o.order_date >= '2021-10-01' AND o.order_date < '2021-11-01'
GROUP BY r.region_name,
		 s.state_name;

DROP TABLE IF EXISTS report_prev_year;
CREATE TABLE report_prev_year
SELECT r.region_name,
	   s.state_name,
	   SUM(i.quantity) AS monthly_quantity_sold,
	   SUM(i.amount) - SUM(i.unit_cost * i.quantity) AS monthly_profit,
	   SUM(i.amount) AS monthly_revenue
FROM orders o
	 JOIN order_items i ON o.order_id = i.order_id
	 JOIN stores ON o.postal_code = stores.postal_code
	 JOIN cities c ON stores.city_id = c.city_id
	 JOIN states s ON c.state_code = s.state_code
	 JOIN regions r ON s.region_code = r.region_code
WHERE o.order_date >= '2020-11-01' AND o.order_date < '2020-12-01'
GROUP BY r.region_name,
		 s.state_name;


SELECT c.region_name, c.state_name,
	   c.monthly_quantity_sold, c.monthly_profit, c.monthly_revenue,
	   m.monthly_revenue AS prev_monthly_revenue,
	   c.monthly_revenue - m.monthly_revenue AS monthly_revenue_growth,
	   (c.monthly_revenue - m.monthly_revenue) / m.monthly_revenue AS monthly_revenue_growth_rate,
	   y.monthly_revenue AS prev_year_monthly_revenue,
	   c.monthly_revenue - y.monthly_revenue AS year_over_year_monthy_revenue_growth,
	   (c.monthly_revenue - y.monthly_revenue) / y.monthly_revenue AS year_over_year_monthy_revenue_growth_rate
FROM report_current_month c
LEFT JOIN report_prev_month m ON c.region_name=m.region_name AND c.state_name=m.state_name
LEFT JOIN report_prev_year y on c.region_name=y.region_name AND c.state_name=y.state_name
ORDER BY region_name, state_name;

