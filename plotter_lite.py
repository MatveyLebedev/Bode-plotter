import matplotlib.pyplot as plt
import numpy as np
import sympy
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tkinter.Tk()
root.wm_title("MY_LAFCHA")

W_min = float('inf')
W_max = float('-inf')


def bild_lax(nom, den): # nom and den are strings
    global W_max, W_min
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
            if eq_n is not '':
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

    for i in range(len(W_d)):
        if W_d[i] == 0:
            W_d.pop(i)
            naklon += -1

    for i in range(len(W_n)):
        if W_n[i] == 0:
            W_d.pop(i)
            naklon += 1

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

    Y1 = 20 * np.log10(float(K)) + (np.log10(float(Ws)) - np.log10(1)) * 20 * naklon
    X = [Ws]
    Y = [Y1]


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

    X.append(Wf)
    Y.append(abs(np.log10(float(X[-2])) - np.log10(float(X[-1]))) * 20 * naklon + Y[-1])
    if type(Y[-1]) is sympy.core.numbers.NaN:
        Y[-1] = 0

    for i in range(len(X)):
        X[i] = X[i]

    return X, Y



fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xscale('log')
ax.set_xlabel('Omega [rad / s]')
ax.set_ylabel('Magnitude [db]')
ax.grid()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, columnspan=4)

def plot():
    nom = inp_num.get()
    den = inp_den.get()
    X, Y = bild_lax(nom, den)
    ax.set_xscale('log')
    ax.plot(X, Y)
    canvas.draw_idle()

def clear():
    ax.clear()
    ax.grid()
    canvas.draw_idle()

nom_text = tkinter.StringVar()
nom_text.set('0.0292 1')
den_text = tkinter.StringVar()
den_text.set('0.447 1, 0.0014 1, 1 0')
ku_text = tkinter.StringVar()
ku_text.set('2409')
inp_ku = tkinter.Entry(master=root, width=10, textvariable=ku_text, justify='center')
inp_ku.grid(row=1, column=1, rowspan=2)
tkinter.Label(master=root, text="W(S)=").grid(row=1, column=0, rowspan=2)
inp_num = tkinter.Entry(master=root, width=80, textvariable=nom_text, justify='center')
inp_num.grid(row=1, column=2, pady=10)
inp_den = tkinter.Entry(master=root, width=80, textvariable=den_text, justify='center')
inp_den.grid(row=2, column=2, pady=10)

tkinter.Button(master=root, text="Clear", command=clear, width=10).grid(row=1, column=3)
tkinter.Button(master=root, text="Plot", command=plot, width=10).grid(row=2, column=3)

tkinter.mainloop()