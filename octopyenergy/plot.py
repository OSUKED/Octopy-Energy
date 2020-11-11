from __future__ import absolute_import

"""
Imports
"""
import matplotlib.pyplot as plt


"""
General Helpers
"""
def hide_spines(ax, positions=["top", "right"]):
    """
    Pass a matplotlib axis and list of positions with spines to be removed
    
    args:
        ax:          Matplotlib axis object
        positions:   Python list e.g. ['top', 'bottom']
    """
    assert isinstance(positions, list), "Position must be passed as a list "

    for position in positions:
        ax.spines[position].set_visible(False)
        
def simple_plot(s, ylabel='', ax=None):
    if ax is None:
        fig, ax = plt.subplots(dpi=150)

    s.plot(ax=ax)

    ax.legend(frameon=False)
    hide_spines(ax)
    ax.set_xlabel('')
    ax.set_ylabel(ylabel)
    
    return plt.gcf(), ax
        
"""
Specific Plots
"""
def plot_consumption_production(s_elec_consumption, s_elec_production, ax=None, units='kWh'):
    if ax is None:
        fig, ax = plt.subplots(dpi=150)

    s_elec_consumption.plot(ax=ax, label='Consumption')
    s_elec_production.plot(ax=ax, label='Production')

    ax.legend(frameon=False)
    hide_spines(ax)
    ax.set_xlabel('')
    ax.set_ylabel(f'Power ({units})')
    
    return plt.gcf(), ax