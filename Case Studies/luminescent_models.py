import numpy as np

def general_order(temperature:list, activation_energy,kinectic_order, iMax,Tmax): #pg82
    """Describes the general order TL Kinectics Model"""
    k = 0.00008617
    return (iMax*(kinectic_order**(kinectic_order/(kinectic_order-1)))*
            np.exp(((activation_energy)/(k*temperature))*((temperature-Tmax)/Tmax)) * 
            (1+(kinectic_order-1)*((2*k*Tmax)/activation_energy)+(kinectic_order-1)*(1-((2*k*Tmax)/activation_energy))*
            ((temperature**2/Tmax**2)*np.exp((activation_energy/k*temperature)*((temperature-Tmax)/Tmax)))**(-kinectic_order/(kinectic_order-1))))
#Escape factor is calculated
#Heating rate is given
#The solution of the integrals discribed in time resulted on on a single value of temperature in the scale of time. Can the scale of time be 