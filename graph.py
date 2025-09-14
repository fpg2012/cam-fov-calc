import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from cam2 import calc_h_i, CMOS

cmos_picked = 'aps-c'
# cmos_picked = 'full'

def plot_graph_u_h_prop(h_o, f = 50, cmos: str = 'aps-c'):
    w_c = CMOS[cmos]['w']
    f = f / 1000

    u = np.linspace(5, 60, 100)
    h_props = calc_h_i(f, u, h_o) / w_c
    plt.plot(u, h_props, label=f'f = {f*1000:.0f}mm, $h_o$ = {h_o}m')

def plot_graph_f_h_prop(h_o, u = 50, cmos: str = 'aps-c'):
    w_c = CMOS[cmos]['w']

    f = np.linspace(0.024, 0.5, 100)
    plt.plot(f * 1000, calc_h_i(f, u, h_o) / w_c, label=f'u = {u}m, $h_o$ = {h_o}m')
    plt.ylim((0, 1))

def plot_h_prop(h_props, labels=None, ratio_o=1):
    pad = 0.1

    fig, ax = plt.subplots()

    rect = patches.Rectangle((0, 0), 1, 2/3, linewidth=2, facecolor='none', edgecolor='black')
    ax.add_patch(rect)
    color_list = [(0.3 + 0.05*i, 0.5 + 0.06*i, 0, 1.0-0.1 * i) for i in range(10)]

    handles = []
    for i, h_prop in enumerate(h_props):
        rect_2 = patches.Rectangle(
            (0.5 - (h_prop/ratio_o)/2, 1/3 - h_prop/2),
            h_prop/ratio_o, h_prop,
            linewidth=1, edgecolor=color_list[i], facecolor='none',
            label=f'{labels[i]} {h_prop*100:.1f}%' if isinstance(labels, list) else f'{h_prop*100:.1f}%'
        )

        ax.add_patch(rect_2)
        handles.append(rect_2)

    ax.set_xlim(-pad, 1 + pad)
    ax.set_ylim(-pad, 2/3 + pad)
    plt.gca().set_aspect('equal')
    plt.legend(handles=handles)

if __name__ == '__main__':
    h_o = 10
    f_arr = [24, 50, 75, 140, 200, 250, 300, 350, 400]
    u_arr = [1, 5, 10, 20, 30, 40, 75, 100, 200]
    for f in f_arr:
        plot_graph_u_h_prop(h_o, f, cmos=cmos_picked)
    plt.xlabel('u')
    plt.ylabel('$h_{prop}$')
    plt.title(f'$h_o$={h_o}m')
    plt.legend()
    plt.show()
    for u in u_arr:
        plot_graph_f_h_prop(h_o, u, cmos=cmos_picked)
    plt.xlabel('f')
    plt.ylabel('$h_{prop}$')
    plt.title(f'$h_o$={h_o}m')
    plt.legend()
    plt.show()

    f = 300
    w_c = CMOS[cmos_picked]['w']
    h_props = [calc_h_i(f=f/1000, u=u, h_o=h_o) / w_c for u in u_arr]
    plot_h_prop(h_props, labels=[f'u={u}m' for u in u_arr])
    plt.title(f'f={f}mm $h_o$={h_o}m')
    plt.show()

    h_o = 1.74 * 1e6
    u = 3.84 * 1e8
    h_props = [calc_h_i(f=f/1000, u=u, h_o=h_o) / w_c for f in f_arr[::-1]]
    plot_h_prop(h_props, labels=[f'f={f}mm' for f in f_arr[::-1]])
    plt.title(f'u={u}m $h_o$={h_o}m')
    plt.show()
