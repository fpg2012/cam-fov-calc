import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from typing import Tuple, Optional
import numpy as np

EPS = 1e-5

class Segment:

    def __init__(self, t_range: Tuple[float, float], k: Tuple[float, float], b: Tuple[float, float]):
        self.t_range = t_range
        self.k = k
        self.b = b

    def plot(self, ax: Axes, color=None, n_samples=100, t_range=None):
        if t_range is None:
            t_range = self.t_range
        t = np.linspace(t_range[0], t_range[1], n_samples)
        x = self.k[0] * t + self.b[0]
        y = self.k[1] * t + self.b[1]
        if color is not None:
            ax.plot(x, y, color=color)
        else:
            ax.plot(x, y)

    def __str__(self):
        return f'Segment(k={self.k}, b={self.b}, t_range={self.t_range})'

def p2s(start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> Segment:
    """convert points to segment"""
    t_range = (0, 1)
    b = start_pos
    k = (end_pos[0] - b[0], end_pos[1] - b[1])
    return Segment(t_range, k, b)

def x_p(seg1: Segment, seg2: Segment) -> Optional[Tuple[Tuple[float, float], float]]:
    """get the cross point of two segment"""
    k1, k2 = seg1.k
    h1, h2 = seg2.k
    b1, b2 = seg1.b
    c1, c2 = seg2.b

    delta = h2 * k1 - h1 * k2
    if np.abs(delta) < EPS:
        return None

    t = -((c2 - b2)*h1 - (c1 - b1)*h2) / delta

    x = k1 * t + b1
    y = k2 * t + b2
    return (x, y), t

class Lens:

    def __init__(self, position: float, height: float, focal: float):
        self.position = position # position on the axis of light
        self.height = height
        self.focal = focal

    @property
    def top(self) -> Tuple[float, float]:
        return (self.position, self.height/2)

    @property
    def bottom(self) -> Tuple[float, float]:
        return (self.position, -self.height/2)

    @property
    def center(self) -> Tuple[float, float]:
        return (self.position, 0)

    def plot(self, ax: Axes):
        seg = p2s(self.top, self.bottom)
        seg.plot(ax, color='gray')


def plot_ray(ax: Axes, source: Tuple[float, float], lens: Lens, image_plane: float, color='salmon'):
    segment_in_top = p2s(source, lens.top)
    segment_in_bottom = p2s(source, lens.bottom)
    segment_in_middle = p2s(source, lens.center)

    image_seg = p2s((image_plane, 0), (image_plane, 1))

    segment_out_parallel = p2s((lens.position, source[1]), (lens.focal, 0))

    image_pos = x_p(segment_out_parallel, segment_in_middle)
    if image_pos is None:
        return
    image_pos, t = image_pos


    segment_out_middle = p2s(lens.center, image_pos)
    segment_out_top = p2s(lens.top, image_pos)
    segment_out_bottom = p2s(lens.bottom, image_pos)

    pos_top, t_top = x_p(segment_out_top, image_seg)
    pos_bottom, t_bottom = x_p(segment_out_bottom, image_seg)
    _, t_middle = x_p(segment_out_middle, image_seg)
    _, t_parallel = x_p(segment_out_parallel, image_seg)

    print(f'source={source}, image_pos={tuple(round(x, 3) for x in image_pos)} t={t:.3f} h={pos_top[1] - pos_bottom[1]:.3f}')

    segment_in_top.plot(ax, color=color)
    segment_in_middle.plot(ax, color=color)
    segment_in_bottom.plot(ax, color=color)
    # segment_in_parallel.plot(ax, color=color)

    # segment_out_parallel.plot(ax, t_range=(0, t_parallel), color=color)
    segment_out_middle.plot(ax, t_range=(0, t_middle), color=color)
    segment_out_top.plot(ax, t_range=(0, t_top), color=color)
    segment_out_bottom.plot(ax, t_range=(0, t_bottom), color=color)

if __name__ == '__main__':
    image_plane_pos = -0.4

    lens = Lens(0, 0.5, -0.2)
    fig, ax = plt.subplots()
    sources = [(1.0, 0.1), (2.0, 0.1), (1.0, 1.0), (1.5, -0.5)]
    color = ['salmon', 'lightblue', 'orange', 'brown']
    for source, color in zip(sources, color):
        plot_ray(ax, source, lens, image_plane_pos, color=color)

    lens.plot(ax)
    ax.set_ylim(-1, 1)
    ax.set_xlim(image_plane_pos - 0.1, 2)
    image_plane = p2s((image_plane_pos, -1), (image_plane_pos, 1))
    image_plane.plot(ax, color='black')
    plt.gca().set_aspect('equal')
    plt.show()
