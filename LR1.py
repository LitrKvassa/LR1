from copy import deepcopy
from itertools import product
import numpy as np
import random as rnd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker
import click

#Начальные параметры по умолчанию
data = {
    'N': 100, 'M': 100, 'f': .01, 'p': .01, 
    'tti': 2, 't': 110, 'inter': 400, 'areatype': 0
}
#tti ~ trees-to-ignite
#функции для проверки значений
def validate_positive(value):
        val = int(value)
        if val <= 0:
            raise click.UsageError("Значение должно быть больше 0")
        return val

def validate_threshold(value):
        val = int(value)
        if val <= 1:
            raise click.UsageError("Значение должно быть больше 1")
        return val

def validate_frames(value):
        val = int(value)
        if val < 1:
            raise click.UsageError("Значение должно быть не менее 1")
        return val

def validate_probability(value):
    val = float(value)
    if not (0.0 <= val <= 1.0):
        raise click.UsageError("Вероятность должна быть в диапазоне от 0 до 1")
    return val

def validate_bool(value):
    val = float(value)
    if val not in (0,1):
        raise click.UsageError("Значение есть 0 или 1")
    return val

def show_menu():
    #Отображение меню
    click.clear()
    click.secho("=== КА лесного пожара ===", bold=True)
    click.echo("1. Текущие параметры")
    click.echo("2. Ввод параметров")
    click.echo("3. Расчёт КА")
    click.echo("4. Выход")
    click.echo("=======================")

def show_data():
    #Отображение текущих значений переменных
    click.clear()
    click.secho("--- ТЕКУЩИЕ ПАРАМЕТРЫ ---", bold=True)
    for key, value in data.items():
        click.echo(f" {key} = {value}")
        
    click.echo("-------------------------")
    input("<ENTER для возврата в меню>")

def input_data():
    #Последовательный ввод значений параметров
    click.clear()
    click.secho("--- ВВОД ДАННЫХ ---", bold=True)
    click.echo("Числовые значения для переменных:")

    data['N'] = click.prompt(" N (число строк, int)", type=int, value_proc=validate_threshold)
    data['M'] = click.prompt(" M (число столбцов, int)", type=int, value_proc=validate_threshold)
    data['f'] = click.prompt(" f (вероятность случайного возгорания, float)", type=float, value_proc=validate_probability)
    data['p'] = click.prompt(" p (вероятность роста дерева, float)", type=float, value_proc=validate_probability)
    data['tti'] = click.prompt(" tti (минимальное число горящих деревьев для возгорания, int)", type=int, value_proc=validate_positive)
    data['t'] = click.prompt(" t (число итераций, int)", type=int, value_proc=validate_frames)
    data['inter'] = click.prompt(" inter (задержка между кадрами анимации, мс)", type=int, value_proc=validate_positive)
    data['areatype'] = click.prompt(" areatype (тип окрестности, 0 - Неймана, 1 - Мура)", type=int, value_proc=validate_bool)
    
    click.secho("\n<Данные обновлены>")
    input("<ENTER для возврата в меню>")


#Рабочие функции
def calc4(ca, cell):
    #Функция расчёта состояния соседей - 4 соседа
    #Возвращает число S горящих деревьев в окрестности
    i, j = cell
    s = 0
    
    if 0 < i < len(ca) - 1:
        if ca[i-1][j] == 2:
            s += 1
        if ca[i+1][j] == 2:
            s += 1
    elif i == 0:
        if ca[i+1][j] == 2:
            s += 1
    else:
        if ca[i-1][j] == 2:
            s += 1

    if 0 < j < len(ca[0]) - 1:
        if ca[i][j-1] == 2:
            s += 1
        if ca[i][j+1] == 2:
            s += 1
    elif j == 0:
        if ca[i][j+1] == 2:
            s += 1
    else:
        if ca[i][j-1] == 2:
            s += 1
    return s

def calc8(ca, cell):
    #Функция расчёта состояния соседей - 8 соседей
    #Возвращает число S горящих деревьев в окрестности
    i, j = cell
    #i ~ y, j ~ x
    s = 0
    #print(ca[0][1])
    c1 = (i == 0)
    c3 = (0 < i < len(ca) - 1)
    c5 = (i == len(ca) - 1)
    
    c2 = (j == 0)
    c4 = (0 < j < len(ca[0]) - 1)
    c6 = (j == len(ca[0]) - 1)
    
    if c1 and c2:
        s += [ca[i][j+1], ca[i+1][j+1], ca[i+1][j]].count(2)
    elif c1 and c4:
        s += [ca[i][j-1], ca[i+1][j-1], ca[i+1][j], ca[i+1][j+1], ca[i][j+1]].count(2)
    elif c1 and c6:
        s += [ca[i][j-1], ca[i+1][j-1], ca[i+1][j]].count(2)
    
    elif c3 and c2:
        s += [ca[i-1][j], ca[i-1][j+1], ca[i][j+1], ca[i+1][j+1], ca[i+1][j]].count(2)
    elif c3 and c4:
        s += [ca[i-1][j-1], ca[i-1][j], ca[i-1][j+1], ca[i][j-1], ca[i][j+1], ca[i+1][j-1], ca[i+1][j], ca[i+1][j+1]].count(2)
    elif c3 and c6:
        s += [ca[i-1][j], ca[i-1][j-1], ca[i][j-1], ca[i+1][j-1], ca[i+1][j]].count(2)
        
    elif c5 and c2:
        s += [ca[i][j+1], ca[i-1][j+1], ca[i-1][j]].count(2)
    elif c5 and c4:   
        s += [ca[i-1][j-1], ca[i-1][j], ca[i-1][j+1], ca[i][j-1], ca[i][j+1]].count(2) 
    elif c5 and c6:
        s += [ca[i][j-1], ca[i-1][j-1], ca[i-1][j]].count(2)
    return s

def upd4(ca, tti, f, p):
    #Функция обновления сетки
    new_ca = deepcopy(ca)
    rows, columns = range(len(ca)), range(len(ca[0]))
    
    for i, j in product(rows, columns):
        s = calc4(ca, (i, j))
        rdf = rnd.random()
        rdt = rnd.random()
        
        if new_ca[i][j] == 2:
            new_ca[i][j] = 0
        elif new_ca[i][j] == 1:
            if s >= tti:
                new_ca[i][j] = 2
            elif rdf <= f:
                new_ca[i][j] = 2
        elif s == 0 and rdt <= p:
            new_ca[i][j] = 1
    return new_ca

def upd8(ca, tti, f, p):
    #Функция обновления сетки
    new_ca = deepcopy(ca)
    rows, columns = range(len(ca)), range(len(ca[0]))
    
    for i, j in product(rows, columns):
        s = calc8(ca, (i, j))
        rdf = rnd.random()
        rdt = rnd.random()

        if new_ca[i][j] == 2:
            new_ca[i][j] = 0
        elif new_ca[i][j] == 1:
            if s >= tti:
                new_ca[i][j] = 2
            elif rdf <= f:
                new_ca[i][j] = 2
        elif s == 0 and rdt <= p:
            new_ca[i][j] = 1
    return new_ca

def upd0(ca, rng):
    #Задание начальной сетки со случайной генерацией
    new_ca = deepcopy(ca)
    rows, columns = range(len(ca)), range(len(ca[0]))
    for i, j in product(rows, columns):
        new_ca[i][j] = rng.integers(0, 2)
    return new_ca

def run_calculation():
    #Блок расчётного кода и построения анимации
    click.clear()
    click.secho(">")
    
    N = data['N']
    M = data['M']
    f = data['f']
    p = data['p']
    tti = data['tti']
    t = data['t']
    inter = data['inter']
    areatype = data['areatype']
    
    F = np.zeros((N, M)) #нулевая сетка
    rng = np.random.default_rng() #генератор случ чисел
    
    plt.close('all')
    F = upd0(F, rng) #задание начальной сетки
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    colors_list = ['tan', 'green', 'orange'] #цветовая схема
    bounds = [-0.5, 0.5, 1.5, 2.5] #пороги цветов
    cmap = mcolors.ListedColormap(colors_list)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    im = ax.imshow(F, cmap=cmap, norm=norm, aspect='auto', 
                   extent=[0, M, 0, N], origin='upper')
    
    ax.set_xticks(np.arange(0, M + 1, 1))
    ax.set_yticks(np.arange(0, N + 1, 1))
    stepx = 5
    stepy = 5
    ax.set_xticklabels([str(x) if x % stepx == 0 else "" for x in np.arange(0, M + 1, 1)])
    ax.set_yticklabels([str(y) if y % stepy == 0 else "" for y in np.arange(0, N + 1, 1)][::-1])

    ax.set_axisbelow(False)
    ax.grid(visible=True, which='major', color='black', linestyle='-', linewidth=.25)

    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(['0 Пустая клетка', '1 Дерево', '2 Горящее дерево'])

    plt.xlabel("Столбцы")
    plt.ylabel("Строки")
    plt.title("Модель лесного пожара")
    #plt.show(fig)
    #Функция обновления кадров для анимации
    def update_frame(frame):
        nonlocal F
        if areatype == 0:
            F = upd4(F, tti, f, p)
        else:
            F = upd8(F, tti, f, p)
        im.set_data(F)
        return [im]
    ani = FuncAnimation(fig, update_frame, frames=t, interval=inter, blit=True)
    ani.save('animation.gif', writer='pillow')
    k = [i for row in F for i in row]
    zeros = k.count(0)
    ones = k.count(1)
    doubles = len(k)-ones-zeros
    print(zeros, ones, doubles)
    click.secho("Файл 'animation.gif' сохранён", fg="green")
    plt.show(fig)
    plt.close(fig)
    input("<ENTER для возврата в меню>")

@click.command()
def main():
    #Основной цикл управления интерфейсом
    while True:
        show_menu()
        choice = click.prompt(">Ввод", type=click.Choice(['1', '2', '3', '4']), show_choices=False)
        
        if choice == '1':
            show_data()
        elif choice == '2':
            input_data()
        elif choice == '3':
            run_calculation()
        elif choice == '4':
            click.secho("\nРабота программы завершена")
            break

if __name__ == '__main__':
    main()
