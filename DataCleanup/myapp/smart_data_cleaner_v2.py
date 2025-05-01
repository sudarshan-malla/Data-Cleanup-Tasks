import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import os

class SmartDataCleanerV2:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
        self.cleaned_df = self.df.copy()

    def assess_data(self):
        assessment = [
            "--- Data Assessment ---",
            f"Shape: {self.df.shape}",
            "\nMissing values:\n" + str(self.df.isnull().sum()),
            "\nData types:\n" + str(self.df.dtypes),
            "\nDuplicates: " + str(self.df.duplicated().sum())
        ]
        return "\n".join(assessment)

    def identify_outliers(self):
        numeric_cols = self.df.select_dtypes(include=[np.number])
        outlier_report = ["--- Outlier Detection ---"]
        for col in numeric_cols.columns:
            Q1 = numeric_cols[col].quantile(0.25)
            Q3 = numeric_cols[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            count = ((numeric_cols[col] < lower) | (numeric_cols[col] > upper)).sum()
            outlier_report.append(f"{col}: {count} outliers")
        return "\n".join(outlier_report)

    def correlation_analysis(self):
        corr_matrix = self.cleaned_df.select_dtypes(include=[np.number]).corr()
        return f"--- Correlation Matrix ---\n{corr_matrix.to_string()}"

    def feature_extraction(self):
        report = [
            "--- Feature Extraction ---",
            f"Original Columns: {list(self.df.columns)}",
            f"Cleaned Columns: {list(self.cleaned_df.columns)}",
            f"Numeric Features: {list(self.cleaned_df.select_dtypes(include=[np.number]).columns)}",
            f"Categorical Features: {list(self.cleaned_df.select_dtypes(include=['object']).columns)}"
        ]
        return "\n".join(report)

    def summary_statistics(self):
        try:
            stats = self.cleaned_df.describe(include='all')
            return f"--- Summary Statistics ---\n{stats.to_string()}"
        except Exception as e:
            return f"Error in summary statistics: {str(e)}"

    def clean(self, normalize=True, standardize=False):
        imputer = SimpleImputer(strategy='most_frequent')
        for col in self.cleaned_df.columns:
            if self.cleaned_df[col].isnull().any():
                try:
                    self.cleaned_df[col] = imputer.fit_transform(self.cleaned_df[[col]]).ravel()
                except:
                    self.cleaned_df[col] = self.cleaned_df[col].fillna(method='ffill')

        if normalize:
            self._apply_scaler(MinMaxScaler())
        if standardize:
            self._apply_scaler(StandardScaler())

    def _apply_scaler(self, scaler):
        numeric_cols = self.cleaned_df.select_dtypes(include=[np.number]).columns
        self.cleaned_df[numeric_cols] = scaler.fit_transform(self.cleaned_df[numeric_cols])

    def export(self):
        output_path = self.filepath.replace('.', '_cleaned.', 1)
        if output_path.endswith('.csv'):
            self.cleaned_df.to_csv(output_path, index=False)
        else:
            self.cleaned_df.to_excel(output_path, index=False)
        return output_path
