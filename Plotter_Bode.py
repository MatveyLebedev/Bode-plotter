import matplotlib.pyplot as plt
import numpy as np
import sympy
import tkinter
import math
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk )
import sys

root = tkinter.Tk()
root.wm_title("MY_LAFCHA")

W_min = float('inf')
W_max = float('-inf')

LEGENDS_lax = []
LEGENDS_fase = []

figsize = (10, 8)
if sys.platform == 'darwin':
    figsize = (10, 7)
    root.wm_attributes('-fullscreen','true')


def bild_lax(nom, den): # nom and den are strings
    global Ws, Wf, S_den, S_num, naclon_0, W_min, W_max
    S_den = 1
    S_num = 1
    s = sympy.symbols('s')

    nom = nom.split(', ')
    den = den.split(', ')

    def find_w(nom):
        nom = nom.split(' ')
        Tn = []
        for t in nom:
            Tn.append(eval(t))
        eq_n = ''
        s_m = len(Tn) - 1
        for t in Tn:
            if eq_n != '':
                eq_n += '+'
            eq_n += f'{t}*s**{s_m}'
            s_m -= 1
        eq_n = sympy.parse_expr(eq_n)
        S_nom = sympy.solve(eq_n)
        for i in range(len(S_nom)):
            S_nom[i] = S_nom[i].as_real_imag()[0]
        W_n = []
        for i in range(len(S_nom)):
            W_n.append(abs(S_nom[i]))
        return W_n, eq_n

    eq_n = sympy.parse_expr('1')
    eq_d = sympy.parse_expr('1')
    W_n = []
    W_d = []

    for e in nom:
        W, eq = find_w(e)
        W_n.extend(W)
        if eq.subs(s, 0) != 0:
            eq_n *= eq

    for e in den:
        W, eq = find_w(e)
        W_d.extend(W)
        if eq.subs(s, 0) != 0:
            eq_d *= eq


    naklon = 0
    naklons = []

# TODO: [::-1]
    for i in range(len(W_d))[::-1]:
        if W_d[i] == 0:
            W_d.pop(i)
            naklon += -1
            S_den *= s


    for i in range(len(W_n))[::-1]:
        if W_n[i] == 0:
            W_n.pop(i)
            naklon += 1
            S_num *= s

    K = eq_n.subs(s, 0) / eq_d.subs(s, 0) * float(eval(inp_ku.get()))

    if len(W_n) == 0:
        n_min = float('inf')
    else:
        n_min = min(W_n)
    if len(W_d) == 0:
        d_min = float('inf')
    else:
        d_min = min(W_d)
    if d_min and n_min == float('inf'):
        d_min = 10
    Ws = min(n_min, d_min) / 10
    if Ws >= W_min:
        Ws = W_min
    else:
        W_min = Ws

    if len(W_n) == 0:
        n_min = float('-inf')
    else:
        n_min = max(W_n)
    if len(W_d) == 0:
        d_min = float('-inf')
    else:
        d_min = max(W_d)
    if d_min == float('-inf') and n_min == float('-inf'):
        d_min = 1
    Wf = max(n_min, d_min) * 10

    if Wf == Ws:
        Wf = 10

    if Wf <= W_max:
        Wf = W_max
    else:
        W_max = Wf

    # enable manual scale
    if inp_X_min.get() != 'auto':
        Ws = float(inp_X_min.get())
    if inp_X_max.get() != 'auto':
        Wf = float(inp_X_max.get())

    Y1 = 20 * np.log10(float(K)) + (np.log10(float(Ws)) - np.log10(1)) * 20 * naklon
    X = [Ws]
    Y = [Y1]

    naklons.append(naklon)


    for i in range(len(W_n) + len(W_d)):
        if len(W_n) == 0:
            n_min = float('inf')
        else:
            n_min = min(W_n)
        if len(W_d) == 0:
            d_min = float('inf')
        else:
            d_min = min(W_d)
        if n_min < d_min:
            X.append(W_n.pop(W_n.index(n_min)))
            if X[-1] / X[-2] == 1: # for case with 2 same roots
                Y.append(Y[-1])
            else:
                Y.append(abs(np.log10(float(X[-2])) - np.log10(float(X[-1]))) * 20 * naklon + Y[-1])
                if type(Y[-1]) is sympy.core.numbers.NaN:
                    Y[-1] = 0
            naklon += 1
        elif n_min > d_min:
            X.append(W_d.pop(W_d.index(d_min)))
            if X[-1] / X[-2] == 1:
                Y.append(Y[-1])
            else:
                Y.append(abs(np.log10(float(X[-2])) - np.log10(float(X[-1]))) * 20 * naklon + Y[-1])
                if type(Y[-1]) is sympy.core.numbers.NaN:
                    Y[-1] = 0
            naklon += -1
        elif n_min == d_min:
            X.append(W_d.pop(W_d.index(d_min)))
            if X[-1] / X[-2] == 1:
                Y.append(Y[-1])
            else:
                Y.append(abs(np.log10(float(X[-2])) - np.log10(float(X[-1]))) * 20 * naklon + Y[-1])
                if type(Y[-1]) is sympy.core.numbers.NaN:
                    Y[-1] = 0
        naklons.append(naklon)



    for i in range(len(X)):
        if X[i] >= Wf:
            X = X[0: i]
            Y = Y[0: i]
            naklon = naklons[i - 1]
            break
        if X[i] < Ws:
            X = [X[0]].append(X[i::])
            Y = [Y[0]].append(Y[i::])

    X.append(Wf)
    Y.append(abs(np.log10(float(X[-2])) - np.log10(float(X[-1]))) * 20 * naklon + Y[-1])

    if type(Y[-1]) is sympy.core.numbers.NaN:
        Y[-1] = 0

    naclon_0 = naklons[0]
    return X, Y

def find_lafch_not_asimpt(den, nom):
    global S_den, S_num, naclon_0, Ws, Wf
    K = float(eval(inp_ku.get()))
    s = sympy.symbols('s')

    nom = nom.split(', ')
    den = den.split(', ')

    def find_w(nom):
        nom = nom.split(' ')
        Tn = []
        for t in nom:
            Tn.append(eval(t))
        eq_n = ''
        s_m = len(Tn) - 1
        for t in Tn:
            if eq_n != '':
                eq_n += '+'
            eq_n += f'{t}*s**{s_m}'
            s_m -= 1
        eq_n = sympy.parse_expr(eq_n)
        S_nom = sympy.solve(eq_n)
        for i in range(len(S_nom)):
            S_nom[i] = S_nom[i].as_real_imag()[0]
        W_n = []
        for i in range(len(S_nom)):
            W_n.append(abs(S_nom[i]))
        return W_n, eq_n

    eq_n = sympy.parse_expr('1')
    eq_d = sympy.parse_expr('1')
    W_n = []
    W_d = []

    for e in nom:
        W, eq = find_w(e)
        W_n.extend(W)
        if eq.subs(s, 0) != 0:
            eq_n *= eq

    for e in den:
        W, eq = find_w(e)
        W_d.extend(W)
        if eq.subs(s, 0) != 0:
            eq_d *= eq

    tf = (K * eq_d / eq_n) * S_num / S_den
    # manual scale
    if inp_X_min.get() != 'auto':
        Ws = float(inp_X_min.get())
    if inp_X_max.get() != 'auto':
        Wf = float(inp_X_max.get())

    W_to_compute = np.geomspace(float(Ws), float(Wf), 100)
    X = W_to_compute

    Y_LAX = []
    Y_FASE = []

    flag = True
    fase_0 = 0
    fase_dif = 0
    for w in W_to_compute:
        PQ = tf.subs(s, np.complex(0, w)).evalf()
        P, Q = PQ.as_real_imag()
        AMP = (P**2 + Q**2)**(1/2)
        FASE = 180 * naclon_0 + math.degrees(math.atan(Q/P))
        Y_LAX.append(20 * math.log10(AMP))

        if flag:
            fase_0 = FASE
            flag = False
        if abs(FASE - fase_0) > 100:
            fase_dif = fase_0 - FASE
        fase_0 = FASE
        Y_FASE.append(FASE + fase_dif)

    return X, Y_LAX, Y_FASE


def plot():
    nom = inp_num.get()
    den = inp_den.get()
    X, Y = bild_lax(nom, den)
    ax.set_xscale('log')
    if inp_legend.get() != 'auto':
        name = inp_legend.get().split(', ')[0]
        col = inp_legend.get().split(', ')[1]
        LEGENDS_lax.append(name)
        ax.plot(X, Y, color=col)
    else:
        ax.plot(X, Y, color='b')
    ax.legend(LEGENDS_lax)
    canvas.draw_idle()

def plot_real():
    nom = inp_num.get()
    den = inp_den.get()
    bild_lax(nom, den)
    X, Y, Y_f = find_lafch_not_asimpt(nom, den)
    ax.set_xscale('log')
    if inp_legend.get() != 'auto':
        name = inp_legend.get().split(', ')[0]
        col = inp_legend.get().split(', ')[1]
        LEGENDS_lax.append(name)
        ax.plot(X, Y, color=col)
    else:
        ax.plot(X, Y, color='r')
    ax.legend(LEGENDS_lax)
    canvas.draw_idle()

def plot_fase():
    nom = inp_num.get()
    den = inp_den.get()
    bild_lax(nom, den)
    X, Y, Y_f = find_lafch_not_asimpt(nom, den)
    ax_f.set_xscale('log')
    if inp_legend.get() != 'auto':
        name = inp_legend.get().split(', ')[0]
        col = inp_legend.get().split(', ')[1]
        LEGENDS_fase.append(name)
        ax_f.plot(X, Y_f, color=col)
    else:
        ax_f.plot(X, Y_f, color='r')
    ax_f.legend(LEGENDS_fase)
    canvas.draw_idle()

def plot_point_lax():
    points_X = list(map(float, inp_X.get().split(', ')))
    points_Y = list(map(float, inp_Y_lax.get().split(', ')))
    ax.set_xscale('log')
    if inp_legend.get() != 'auto':
        name = inp_legend.get().split(', ')[0]
        col = inp_legend.get().split(', ')[1]
        LEGENDS_lax.append(name)
        ax.plot(points_X, points_Y, color=col)
    else:
        ax.plot(points_X, points_Y, color='g')
    ax.legend(LEGENDS_lax)
    canvas.draw_idle()

def plot_point_fase():
    points_X = list(map(float, inp_X.get().split(', ')))
    points_Y = list(map(float, inp_Y_fase.get().split(', ')))
    ax_f.set_xscale('log')
    if inp_legend.get() != 'auto':
        name = inp_legend.get().split(', ')[0]
        col = inp_legend.get().split(', ')[1]
        LEGENDS_fase.append(name)
        ax_f.plot(points_X, points_Y, color=col)
    else:
        ax_f.plot(points_X, points_Y, color='g')
    ax_f.legend(LEGENDS_fase)
    canvas.draw_idle()

def clear():
    global LEGENDS_lax, LEGENDS_fase
    ax.clear()
    ax.grid()
    ax_f.clear()
    ax_f.grid()
    LEGENDS_lax = []
    LEGENDS_fase = []
    canvas.draw_idle()

def save():
    plt.savefig('MY_LAFCH', dpi=300)

fig, (ax, ax_f) = plt.subplots(nrows=2, ncols=1, figsize=figsize)
fig.subplots_adjust(bottom=0.04, top=0.99)
ax.set_xscale('log')
ax.set_xlabel('Omega [rad / s]')
ax.set_ylabel('Magnitude [db]')
ax_f.set_ylabel('Fase [grad]')
ax.grid()
ax_f.grid()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, columnspan=6)
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

nom_text = tkinter.StringVar()                                                                                 #data
nom_text.set('8.79e-11 0.0088')
den_text = tkinter.StringVar()
den_text.set('4.7e-4 0, 7.67e-14 7.67e-06 0.0032 0.0859 1')
ku_text = tkinter.StringVar()
ku_text.set('25')

inp_ku = tkinter.Entry(master=root, width=10, textvariable=ku_text, justify='center')
inp_ku.grid(row=1, column=1, rowspan=2)
tkinter.Label(master=root, text="W(S)=").grid(row=1, column=0, rowspan=2)
inp_num = tkinter.Entry(master=root, width=60, textvariable=nom_text, justify='center')
inp_num.grid(row=1, column=2, pady=1)
inp_den = tkinter.Entry(master=root, width=60, textvariable=den_text, justify='center')
inp_den.grid(row=2, column=2, pady=1)

tkinter.Button(master=root, text="Clear", command=clear, width=10).grid(row=2, column=3)
tkinter.Button(master=root, text="Plot", command=plot, width=10).grid(row=1, column=3)
tkinter.Button(master=root, text="Plot_real", command=plot_real, width=10).grid(row=1, column=4)
tkinter.Button(master=root, text="Plot_fase", command=plot_fase, width=10).grid(row=2, column=4)

tkinter.Label(master=root, text="Plot by points:").grid(row=3, column=0)
tkinter.Label(master=root, text=" X :").grid(row=3, column=1)
X_points_text = tkinter.StringVar()
X_points_text.set('1, 10, 100, 1000')
Y_lax_points = tkinter.StringVar()
Y_lax_points.set('1, -20, -50, -100')
Y_fase_points = tkinter.StringVar()
Y_fase_points.set('0, -65, -90, -180')
inp_X = tkinter.Entry(master=root, width=60, textvariable=X_points_text, justify='center')
inp_X.grid(row=3, column=2)
tkinter.Label(master=root, text=" Y LAX :").grid(row=4, column=1)
inp_Y_lax = tkinter.Entry(master=root, width=60,  textvariable=Y_lax_points, justify='center')
inp_Y_lax.grid(row=4, column=2)
tkinter.Label(master=root, text=" Y FASE :").grid(row=5, column=1)
inp_Y_fase = tkinter.Entry(master=root, width=60, textvariable=Y_fase_points, justify='center')
inp_Y_fase.grid(row=5, column=2)
tkinter.Button(master=root, text="Points_lax", command=plot_point_lax, width=10).grid(row=4, column=3)
tkinter.Button(master=root, text="Points_fase", command=plot_point_fase, width=10).grid(row=5, column=3)

X_min_text = tkinter.StringVar()
X_min_text.set('auto')
X_max_text = tkinter.StringVar()
X_max_text.set('auto')
tkinter.Label(master=root, text="X_min[rad/s]:").grid(row=4, column=4)
tkinter.Label(master=root, text="X_max[rad/s]:").grid(row=5, column=4)
inp_X_min = tkinter.Entry(master=root, width=10, textvariable=X_min_text, justify='center')
inp_X_min.grid(row=4, column=5)
inp_X_max = tkinter.Entry(master=root, width=10, textvariable=X_max_text, justify='center')
inp_X_max.grid(row=5, column=5)

toolbar.grid(row=6, column=0, columnspan=3)

tkinter.Label(master=root, text="Legend and color \nname, r or auto").grid(row=1, column=5)
Legend_and_color = tkinter.StringVar()
Legend_and_color.set('auto')
inp_legend = tkinter.Entry(master=root, width=10, textvariable=Legend_and_color, justify='center')
inp_legend.grid(row=2, column=5)

tkinter.mainloop()
