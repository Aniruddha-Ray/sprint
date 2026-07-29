import yaml
import pandas as pd


class ScreenerEngine:

    def __init__(self, config_file="config/screener_config.yaml"):

        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

    def apply_filters(self, df, filters):

        out = df.copy()

        for key, value in filters.items():

            if key.endswith("_min"):

                col = key.replace("_min", "")

                if col in out.columns:
                    out = out[out[col] >= value]

            elif key.endswith("_max"):

                col = key.replace("_max", "")

                if col in out.columns:
                    out = out[out[col] <= value]

        if "composite_quality_score" in out.columns:

            out = out.sort_values(
                "composite_quality_score",
                ascending=False
            )

        return out

    def preset(self, df, name):

        preset = self.config["presets"][name]

        return self.apply_filters(df, preset)

    def export(self, df, output):

        df.to_excel(output, index=False)

