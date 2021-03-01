from experiments.config.config import Config
from model import lumps


def main():
    config = Config().load()
    data = lumps.get_model_output(config)
    data.to_csv(config.output_dir / "model_output.csv")
    lumps.make_hysteresis_charts(config, data)
    lumps.make_lumps_chart(config, data)


if __name__ == "__main__":
    main()
