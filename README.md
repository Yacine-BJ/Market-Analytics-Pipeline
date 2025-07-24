# Market-Analytics-Pipeline
This project creates a real-time stock market data pipeline. It captures live stock prices, processes them, and displays them on a dashboard.

## Architecture and Data Flow
The project follows a classic, scalable pipeline architecture for handling streaming data.

## Data Ingestion:
A script connects to the Polygon.io API to get real-time stock data. This data is immediately sent as messages to an Apache Kafka topic, which acts as a high-throughput, real-time data buffer.

## Stream Processing: 
Apache Spark continuously reads the data stream from the Kafka topic. It performs calculations and transformations, such as calculating 1-minute moving averages for open, high, low, and close prices for each stock symbol.

## Data Storage: 
The processed and aggregated data from Spark is then written into a MySQL database table. This table stores the calculated moving averages and is optimized for querying by the visualization tool.

## Data Visualization: 
Grafana connects directly to the MySQL database. It queries the processed data to create real-time dashboards and graphs, allowing users to visualize the stock price trends and the calculated moving averages.

## Core Components
Data Source (Polygon.io): Provides the live, raw financial market data.

Messaging Queue (Apache Kafka): Serves as the durable, real-time pipeline backbone that decouples the data source from the processing engine.

Processing Engine (Apache Spark): Performs the heavy lifting of stateful computations (like windowed averages) on the live data stream.

Database (MySQL): Acts as the structured data warehouse for the final, aggregated results.

Dashboard (Grafana): Provides the user-facing interface for monitoring and analyzing the data visually.
<img width="1898" height="927" alt="Spark jobs" src="https://github.com/user-attachments/assets/0bc060a0-3867-4cae-b992-440787893fed" />
<img width="1907" height="932" alt="Kafka" src="https://github.com/user-attachments/assets/4dbb37a4-f603-4fcd-a074-83e7c9263c4f" />
<img width="1122" height="381" alt="Mysql" src="https://github.com/user-attachments/assets/583a4aac-fcde-481a-b8e0-c0c4f4422741" />
<img width="1914" height="1005" alt="mini projet grafana" src="https://github.com/user-attachments/assets/a43c59c4-3e71-4c27-946b-1145c7ac9aba" />
