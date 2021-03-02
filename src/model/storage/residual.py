def set_residual(data):
    data["residual"] = data["net_radiation"] - data["sensible_heat"] - data["latent_heat"]