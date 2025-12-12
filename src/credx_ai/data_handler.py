# file: data_handler.py

import pandas as pd
import json

class DataHandler:
    def __init__(self, file_path):
        try:
            self.jobs_df = pd.read_csv(file_path)
            self._preprocess_data()
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            self.jobs_df = pd.DataFrame()

    def _preprocess_data(self):
        for col in ['required_skills', 'values_promoted']:
            self.jobs_df[col] = self.jobs_df[col].apply(
                lambda x: [skill.strip() for skill in x.split(';')] if isinstance(x, str) else []
            )
        
        self.jobs_df['salary_range'] = self.jobs_df['salary_range'].apply(
            lambda x: json.loads(x) if isinstance(x, str) and x.startswith('[') else [0, 0]
        )

    def get_jobs(self):
        return self.jobs_df
