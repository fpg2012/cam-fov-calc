import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches

CMOS = {
    'aps-c': {
        'h': 0.0158,  # 15.8 mm -> m
        'w': 0.0238,  # 23.8 mm -> m
    },
    'full': {
        'h': 0.0240,
        'w': 0.0360,
    },
    'm43': {
        'h': 0.0130,
        'w': 0.0173,
    }
}

def calc_h_o(f, u, h_prop):
    # 使用米为单位的计算
    H = h_prop * (u - f) / f
    return H

def calc_h_i(f, u, h_o):
    h_prop = h_o * f / (u - f)
    return h_prop

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', required=True, type=float)  # 焦距(mm)
    parser.add_argument('-u', required=True, type=float)  # 物距(m)
    parser.add_argument('-cmos', default='aps-c', type=str)
    parser.add_argument('-h_prop', default=None, type=float)  # 像高占传感器比例
    parser.add_argument('-h_o', type=float)
    parser.add_argument('-vis', default=True, type=bool)
    args = parser.parse_args()

    mode = None
    if args.h_prop is None and args.h_o is None:
        exit(-1)
    elif args.h_prop is None and args.h_o is not None:
        mode = "calc h_prop"
    elif args.h_prop is not None and args.h_o is None:
        mode = "calc h_o"

    f = args.f / 1000
    u = args.u
    w_cmos = CMOS[args.cmos]['w']  # 使用长边（米）

    h_prop = 1
    h_i = 1
    h_o = 1
    if mode == "calc h_prop":
        h_o = args.h_o
        h_i = calc_h_i(f, u, h_o)
        h_prop = h_i / w_cmos
    elif mode == "calc h_o":
        h_i = args.h_prop * w_cmos  # 成像高度 = 比例 * 长边（单位：米）
        h_o = calc_h_o(f, u, h_i)
        h_prop = args.h_prop

    print(f'h_prop={h_prop}, u={u}, f={f*100:.0f}, h_i={h_i}, h_o={h_o}')

    if args.vis:
        pad = 0.1

        fig, ax = plt.subplots()
        rect = patches.Rectangle((0, 0), 1, 2/3, linewidth=2, facecolor='none', edgecolor='b')
        rect_2 = patches.Rectangle((0.5 - h_prop/2, 1/3 - h_prop/2), h_prop, h_prop, linewidth=1, facecolor='none', edgecolor='r')
        ax.add_patch(rect)
        ax.add_patch(rect_2)
        ax.set_xlim(-pad, 1 + pad)
        ax.set_ylim(-pad, 2/3 + pad)
        plt.gca().set_aspect('equal')
        plt.show()
