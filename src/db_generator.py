import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class RiskPortfolioGenerator:
    """Generates a synthetic wholesale credit portfolio database for LOD2 monitoring."""
    
    def __init__(self, db_path: str = 'data/risk_portfolio.db', n_obligors: int = 500):
        self.db_path = db_path
        self.n_obligors = n_obligors
        self.sectors = ['Financials', 'Energy', 'Technology', 'Healthcare', 'Industrials', 'Real Estate']
        self.regions = ['EMEA', 'NAM', 'APAC', 'LATAM']
        self.ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D']
        self.high_yield = ['BB', 'B', 'CCC', 'D']
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def generate_data(self):
        np.random.seed(42)
        
        # 1. Obligors
        obligors = pd.DataFrame({
            'Obligor_ID': [f'OBL_{str(i).zfill(4)}' for i in range(1, self.n_obligors + 1)],
            'Name': [f'Corp_{i}' for i in range(1, self.n_obligors + 1)],
            'Sector': np.random.choice(self.sectors, self.n_obligors),
            'Region': np.random.choice(self.regions, self.n_obligors),
            'Internal_Rating': np.random.choice(self.ratings, self.n_obligors, p=[0.05, 0.1, 0.25, 0.35, 0.15, 0.07, 0.02, 0.01]),
            'Tier1_Capital_Allocated': np.random.uniform(1e6, 50e6, self.n_obligors)
        })
        
        # 2. Facilities
        fac_list = []
        fac_types = ['Revolving', 'Term Loan', 'ISDA/CSA']
        fac_counter = 1
        for obs in obligors['Obligor_ID']:
            num_facs = np.random.randint(1, 4)
            for _ in range(num_facs):
                limit = np.random.uniform(10e6, 500e6)
                fac_list.append({
                    'Facility_ID': f'FAC_{str(fac_counter).zfill(5)}',
                    'Obligor_ID': obs,
                    'Facility_Type': np.random.choice(fac_types),
                    'Approved_Limit': limit,
                    'Maturity_Date': datetime.today().date() + timedelta(days=np.random.randint(90, 1800))
                })
                fac_counter += 1
        facilities = pd.DataFrame(fac_list)
        
        # 3. Exposures (24 months history)
        dates = [datetime.today().date() - timedelta(days=30*i) for i in range(24)]
        exp_list = []
        exp_counter = 1
        for fac_id, limit in zip(facilities['Facility_ID'], facilities['Approved_Limit']):
            base_draw = np.random.uniform(0.1, 0.9)
            for d in dates:
                utilization = min(max(base_draw + np.random.normal(0, 0.05), 0), 1.1)
                drawn = limit * utilization
                undrawn = max(limit - drawn, 0)
                mtm = np.random.normal(0, limit * 0.05) if np.random.random() > 0.5 else 0
                pfe = limit * np.random.uniform(0.05, 0.2)
                
                exp_list.append({
                    'Exposure_ID': f'EXP_{str(exp_counter).zfill(6)}',
                    'Facility_ID': fac_id,
                    'Reporting_Date': d.strftime('%Y-%m-%d'),
                    'Drawn_Amount': drawn,
                    'Undrawn_Amount': undrawn,
                    'Trading_MtM': mtm,
                    'PFE': pfe
                })
                exp_counter += 1
        exposures = pd.DataFrame(exp_list)
        
        # 4. Rating Transitions
        transitions = []
        for obs in np.random.choice(obligors['Obligor_ID'], int(self.n_obligors * 0.1), replace=False):
            old_r = np.random.choice(self.ratings[:4])
            new_r = np.random.choice(self.high_yield)
            t_date = np.random.choice(dates).strftime('%Y-%m-%d')
            transitions.append({
                'Obligor_ID': obs,
                'Date': t_date,
                'Old_Rating': old_r,
                'New_Rating': new_r
            })
        rating_trans = pd.DataFrame(transitions)
        
        # Save to SQLite
        with sqlite3.connect(self.db_path) as conn:
            obligors.to_sql('Obligors', conn, if_exists='replace', index=False)
            facilities.to_sql('Facilities', conn, if_exists='replace', index=False)
            exposures.to_sql('Exposures', conn, if_exists='replace', index=False)
            rating_trans.to_sql('Rating_Transitions', conn, if_exists='replace', index=False)
        print("Database successfully generated.")

if __name__ == "__main__":
    generator = RiskPortfolioGenerator()
    generator.generate_data()
