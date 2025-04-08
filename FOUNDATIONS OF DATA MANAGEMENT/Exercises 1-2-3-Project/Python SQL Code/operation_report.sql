SELECT 
    r.region_name AS Region,
    s.state_name AS State,
    c.city_name AS City,
    p.product_name AS Item_name,
    oi.unit_price AS Unit_Price,
    
    SUM(oi.quantity) AS Weekly_Quantity_Sold,
    SUM(oi.amount) AS Weekly_Revenue_Sales,
    SUM(oi.amount) - SUM(oi.unit_cost * oi.quantity) AS Weekly_Profit,
    1 - (SUM(oi.amount) / SUM(oi.unit_price * oi.quantity)) AS Weekly_Discount_Applied

FROM 
    orders o 
JOIN 
    stores st ON o.postal_code = st.postal_code 
JOIN 
    cities c ON st.city_id = c.city_id 
JOIN 
    states s ON c.state_code = s.state_code 
JOIN 
    regions r ON s.region_code = r.region_code 
JOIN 
    order_items oi ON o.order_id = oi.order_id 
JOIN 
    products p ON oi.product_id = p.product_id

WHERE 
    o.order_date >= '2021-12-19' 
    AND o.order_date < '2021-12-26'
    
GROUP BY 
    r.region_name, s.state_name, c.city_name, p.product_name, oi.unit_price
    
ORDER BY 
    r.region_name, s.state_name, c.city_name, p.product_name

