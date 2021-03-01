from util.location_util import Clouds


def burridge_gadd_parameterization(clouds=Clouds(0, 0, 0)):
    return -100 * (1 - 0.1*clouds.high - 0.3*clouds.medium - 0.6*clouds.low) #W/m^2