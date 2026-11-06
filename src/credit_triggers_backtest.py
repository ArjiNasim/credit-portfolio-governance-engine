import sqlite3
import pandas as pd

class CreditTriggersBacktester:
    """Simulates time-series backtesting of credit risk early warning triggers."""
    
    def __init__(self, db_path: str = 'data/risk_portfolio.db'):
        self.db_path = db_path
        self.output_path = 'data/trigger_alerts_log.csv'
        
    def run_backtest(self) -> pd.DataFrame:
        query_trans = "SELECT * FROM Rating_Transitions"
        query_exp = """
        SELECT e.Reporting_Date, f.Obligor_ID, f.Facility_ID, e.Drawn_Amount, f.Approved_Limit, e.PFE
        FROM Exposures e
        JOIN Facilities f ON e.Facility_ID = f.Facility_ID
        """
        with sqlite3.connect(self.db_path) as conn:
            transitions = pd.read_sql_query(query_trans, conn)
            exposures = pd.read_sql_query(query_exp, conn)
            
        exposures['Utilization'] = exposures['Drawn_Amount'] / exposures['Approved_Limit']
        transitions['Month'] = transitions['Date'].str[:7]
        exposures['Month'] = exposures['Reporting_Date'].str[:7]
        
        merged = pd.merge(transitions, exposures, on=['Obligor_ID', 'Month'], how='inner')
        hy_ratings = ['BB', 'B', 'CCC', 'D']
        trigger_mask = (merged['New_Rating'].isin(hy_ratings)) & (merged['Utilization'] > 0.85)
        
        alerts = merged[trigger_mask].copy()
        alerts['Alert_Type'] = 'Downgrade + High Utilization (>85%)'
        alerts.to_csv(self.output_path, index=False)
        return alerts

if __name__ == "__main__":
    backtester = CreditTriggersBacktester()
    backtester.run_backtest()
