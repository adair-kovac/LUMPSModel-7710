import model.penman_monteith.moisture_variables as moisture_vars


def sensible_and_latent_heat(config, net_radiation, heat_storage, temp, pressure):
    params = config.penman_monteith_params
    alpha = params["alpha"]
    beta = params["beta"]
    return calc_sensible_and_latent_heat(alpha, beta, net_radiation, heat_storage, temp, pressure)


def calc_sensible_and_latent_heat(alpha, beta, net_radiation, heat_storage, temp, pressure):
    gamma = moisture_vars.get_psychrometric_constant(pressure)
    delta = moisture_vars.slope_e_s(temp)

    available_heat = net_radiation - heat_storage # Q* - delta_Q_s term

    Q_H = calc_sensible_heat(alpha, beta, available_heat, gamma, delta)
    Q_E = calc_latent_heat(alpha, beta, available_heat, gamma, delta)

    return Q_H, Q_E


def calc_sensible_heat(alpha, beta, available_heat, gamma, delta):
    temp = (1 - alpha) + gamma/delta
    temp = temp/(1 + gamma/delta)
    temp = temp * available_heat
    temp = temp - beta
    return temp


def calc_latent_heat(alpha, beta, available_heat, gamma, delta):
    temp = alpha/(1 + gamma/delta)
    temp = temp * available_heat
    temp = temp + beta
    return temp
