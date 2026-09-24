SELECT 
    Customer_ID,
    Location,
    Income_Level,
    Total_Spent,
    Customer_Segment,
    AVG(Total_Spent) OVER(PARTITION BY Location) AS Avg_Spent_In_Location,
    ROUND(
        Total_Spent - AVG(Total_Spent) OVER(PARTITION BY Location), 2
    ) AS Diff_From_Location_Avg,
    DENSE_RANK() OVER(PARTITION BY Location ORDER BY Total_Spent DESC) AS Rank_In_Location
FROM dim_customers_ltv
ORDER BY Location, Rank_In_Location ASC
LIMIT 20;