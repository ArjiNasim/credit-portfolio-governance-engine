import sqlite3
import pandas as pd

class PortfolioLimitsMonitor:
    """Monitors credit portfolio limits and regulatory thresholds."""
    
    def __init__(self, db_path: str = 'data/risk_portfolio.db', bank_tier1_capital: float = 10e9):
        self.db_path = db_path
        self.bank_tier1_capital = bank_tier1_capital
        
    def get_latest_exposures(self) -> pd.DataFrame:
        query = """
        SELECT e.*, f.Obligor_ID, f.Approved_Limit, o.Name, o.Sector, o.Region, o.Internal_Rating
        FROM Exposures e
        JOIN Facilities f ON e.Facility_ID = f.Facility_ID
        JOIN Obligors o ON f.Obligor_ID = o.Obligor_ID
        WHERE e.Reporting_Date = (SELECT MAX(Reporting_Date) FROM Exposures)
        """
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn)
            
    def get_lll_breaches(self) -> pd.DataFrame:
        df = self.get_latest_exposures()
        df['Total_Exposure'] = df['Drawn_Amount'] + df['Trading_MtM'].clip(lower=0) + df['PFE']
        breaches = df[df['Total_Exposure'] > df['Approved_Limit']].copy()
        breaches['Breach_Amount'] = breaches['Total_Exposure'] - breaches['Approved_Limit']
        return breaches.sort_values(by='Breach_Amount', ascending=False)
        
    def get_large_exposures(self) -> pd.DataFrame:
        df = self.get_latest_exposures()
        df['Total_Exposure'] = df['Drawn_Amount'] + df['Trading_MtM'].clip(lower=0) + df['PFE']
        agg_exp = df.groupby(['Obligor_ID', 'Name', 'Sector', 'Internal_Rating'])['Total_Exposure'].sum().reset_index()
        agg_exp['Pct_Tier1'] = agg_exp['Total_Exposure'] / self.bank_tier1_capital
        large_exposures = agg_exp[agg_exp['Pct_Tier1'] >= 0.10].copy()
        return large_exposures.sort_values(by='Pct_Tier1', ascending=False)
