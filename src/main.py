"""
QtPaint, 2020-2022. Made by Pavel Savin A.K.A. "pashkev14".

Импортированные библиотеки. В основе всего приложения лежит фреймворк Qt, а конкретно его Python версия - PyQt5.
Сейчас эта библиотека неактуальна: Qt предоставляет для Python 2 решения - платный для коммерческих/закрытых проектов
PyQt6 и бесплатный для любого типа проектов PySide6. Этот проект сделан в некоммерческих целях, поэтому вопрос его
лицензии был предрешен еще в зачатке идеи. Библиотека sys открывает доступ к возможностям системы, здесь ее
функционал сведен до открытия приложения в потоке и работы с файлами.
"""

import sys
import os

from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

"""
Константы:
    MAINSIZE_KEYS - набор толщин объектов в приложении
    HELP_TEXT - текст раздела "Помощь". Открывает файл help.txt в папке приложения src и считывает все строки с него
    INFO_TEXT - текст раздела "О программе". Открывает файл about.txt в папке приложения src и считывает все строки
    с него
"""

MAINSIZE_KEYS = {'Маленькая': 2,
                 'Средняя': 3,
                 'Большая': 5,
                 'Очень большая': 8}
dir_help = os.path.join(os.path.dirname(__file__), 'help.txt')
dir_info = os.path.join(os.path.dirname(__file__), 'about.txt')
dir_ui = os.path.join(os.path.dirname(__file__), 'window.ui')
dir_icon = os.path.join(os.path.dirname(__file__), 'window_icon.ico')
HELP_TEXT = ''.join(open(dir_help, mode='r', encoding='utf-8').readlines())
INFO_TEXT = ''.join(open(dir_info, mode='r', encoding='utf-8').readlines())

"""
Функция setIcon. Задает иконку диалоговому окну. Функционал выведен в отдельный блок, потому что в приложении
присутствуют несколько диалоговых окон, которым каждый раз нужно задавать иконку.
"""


def setIcon(msgbox):
    global dir_icon
    msgbox.setWindowIcon(QIcon(dir_icon))


class Canvas(QWidget):

    """
    Класс Canvas, он же Холст. По сути является большим пустым виджетом, на котором будут отображаться заданные
    пользователем рисунки. Базовый класс QWidget как раз обладает такой возможностью, поэтому реализация холста через
    базовый виджет со своими параметрами имеет место быть.

    Параметры при инициализации экземпляра класса Canvas:
        objects - список рисуемых объектов
        instrument - выбранный инструмент (по умолчанию - кисть)
        default_color - активный цвет (по умолчанию - цвет 1)
        pen_color - текущий цвет 1 (по умолчанию - черный)
        brush_color - текущий цвет 2 (по умолчанию - белый)
        lineSize - текущая толщина рисуемой линии (по умолчанию - 3 пикселя)
        setCursor - унаследованный метод класса QWidget, задающий стиль курсора, когда он находится в области виджета
        Здесь - команда по смене обычного курсора на встроенный крест Qt.CrossCursor
        currentPoint - координаты текущей позиции курсора на холсте. Нужна для рисования, не отрывая руки
        fill - разрешение на заливку (по умолчанию - не заливать)
        saved - обновляемый "флажок" сохранения (по умолчанию холст сохранен, но стоит внести изменения в него, и холст
        перестает быть сохраненным)
        saved_objects - проверка на сохранение. При сохранении во время работы приложения записывает, сколько объектов
        было сохранено, и по этому числу проверяет изменения в холсте (по умолчанию - 1, заливка белым - тоже объект)
        color_pix1 - визуальное представление текущего цвета 1 (сразу же метод setStyleSheet задает цвет 1 по умолчанию)
        color_pix2 - визуальное представление текущего цвета 2 (сразу же метод setStyleSheet задает цвет 2 по умолчанию)
    """

    def __init__(self):
        super(Canvas, self).__init__()
        self.objects = []
        self.instrument = 'brush'
        self.default_color = 'color_1'
        self.pen_color = QColor(0, 0, 0)
        self.brush_color = QColor(255, 255, 255)
        self.lineSize = 3
        self.setCursor(Qt.CrossCursor)
        self.currentPoint = QPoint()
        self.fill = False
        self.saved = True
        self.saved_objects = 1
        self.color_pix1 = QLabel()
        self.color_pix2 = QLabel()
        self.color_pix1.setStyleSheet('background-color: rgb(0, 0, 0)')
        self.color_pix2.setStyleSheet('background-color: rgb(255, 255, 255)')

    """
    Встроенный метод класса QWidget. Срабатывает по отданной ядром библиотеки команде на рисование. Работает на
    специальном объекте класса QPainter, который как раз и отвечает за рисование. А в самом методе заводится цикл,
    в котором каждый рисуемый объект по очереди отдается соответствующему классу на 
    рисование (метод draw, в каждом классе-инструменте он есть). Так как метод срабатывает постоянно, здесь также 
    проверяется, соответствует ли кол-во отданных объектов кол-ву сохраненных или пуст ли холст вообще. Если нет, то 
    холст автоматически становится несохраненным.
    """

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        for obj in self.objects:
            obj.draw(painter)
        painter.end()
        if len(self.objects) > self.saved_objects or self.saved_objects > len(self.objects) > 1:
            self.saved = False

    """
    Встроенный метод класса QWidget. Срабатывает, если ядро библиотеки фиксирует нажатие мышью по области виджета.
    Метод проверяет, какой инструмент и какой цвет выбран на момент вызова себя, и дает команду добавить в список
    новый объект соответствующего инструмента с данными параметрами (координата, цвет, толщина). По окончании проверки
    метод обновляет текущую точку и сам холст.
    """

    def mousePressEvent(self, event):
        if self.instrument == 'brush':
            if self.default_color == 'color_1':
                self.objects.append(Brush(event.pos(), event.pos(), self.lineSize, self.pen_color))
            else:
                self.objects.append(Brush(event.pos(), event.pos(), self.lineSize, self.brush_color))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'pencil':
            if self.default_color == 'color_1':
                self.objects.append(Pencil(event.pos(), event.pos(), self.pen_color))
            else:
                self.objects.append(Pencil(event.pos(), event.pos(), self.brush_color))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'eraser':
            self.objects.append(Eraser(event.pos(), event.pos(), self.lineSize))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'fill':
            if self.default_color == 'color_1':
                self.objects.append(Fill(self.width(), self.height(), self.pen_color))
            else:
                self.objects.append(Fill(self.width(), self.height(), self.brush_color))
            self.update()
        elif self.instrument == 'line':
            if self.default_color == 'color_1':
                self.objects.append(Line(event.x(), event.y(), event.x(), event.y(), self.lineSize, self.pen_color))
            else:
                self.objects.append(Line(event.x(), event.y(), event.x(), event.y(), self.lineSize, self.brush_color))
            self.update()
        elif self.instrument == 'circle':
            if self.default_color == 'color_1':
                self.objects.append(
                    Circle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                           self.brush_color))
            else:
                self.objects.append(
                    Circle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                           self.pen_color))
            self.update()
        elif self.instrument == 'rectangle':
            if self.default_color == 'color_1':
                self.objects.append(
                    Rectangle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                              self.brush_color))
            else:
                self.objects.append(
                    Rectangle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                              self.pen_color))
            self.update()
        elif self.instrument == 'triangle':
            if self.default_color == 'color_1':
                self.objects.append(
                    Triangle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                             self.brush_color))
            else:
                self.objects.append(
                    Triangle(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                             self.pen_color))
            self.update()
        elif self.instrument == '5gon':
            if self.default_color == 'color_1':
                self.objects.append(
                    Pentagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                             self.brush_color))
            else:
                self.objects.append(
                    Pentagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                             self.pen_color))
            self.update()
        elif self.instrument == '6gon':
            if self.default_color == 'color_1':
                self.objects.append(
                    Hexagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                            self.brush_color))
            else:
                self.objects.append(
                    Hexagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                            self.pen_color))
            self.update()
        elif self.instrument == '8gon':
            if self.default_color == 'color_1':
                self.objects.append(
                    Octagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.pen_color,
                            self.brush_color))
            else:
                self.objects.append(
                    Octagon(event.x(), event.y(), event.x(), event.y(), self.fill, self.lineSize, self.brush_color,
                            self.pen_color))
            self.update()

    """
    Встроенный метод класса QWidget. Срабатывает, если ядро библиотеки фиксирует движение мыши с зажатой
    кнопкой в области виджета. Метод вновь проверяет, какой инструмент и какой цвет выбран, и дальше команды разнятся:
    "кистепроизводные" инструменты работают как обычно, а фигуры меняют координату конца, вследствие чего фигура меняет
    свои измерения. По окончании проверок метод обновляет текущую точку и сам холст.
    """

    def mouseMoveEvent(self, event):
        if self.instrument == 'brush':
            if self.default_color == 'color_1':
                self.objects.append(Brush(self.currentPoint, event.pos(), self.lineSize, self.pen_color))
            else:
                self.objects.append(Brush(self.currentPoint, event.pos(), self.lineSize, self.brush_color))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'pencil':
            if self.default_color == 'color_1':
                self.objects.append(Pencil(self.currentPoint, event.pos(), self.pen_color))
            else:
                self.objects.append(Pencil(self.currentPoint, event.pos(), self.brush_color))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'eraser':
            self.objects.append(Eraser(self.currentPoint, event.pos(), self.lineSize))
            self.currentPoint = event.pos()
            self.update()
        elif self.instrument == 'line':
            self.objects[-1].ex = event.x()
            self.objects[-1].ey = event.y()
            self.update()
        elif self.instrument == 'circle':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == 'rectangle':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == 'triangle':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == '5gon':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == '6gon':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()
        elif self.instrument == '8gon':
            self.objects[-1].x = event.x()
            self.objects[-1].y = event.y()
            self.update()

    """
    Методы-"настройщики". Сделаны специально, чтобы в ключевых моментах кода не было произвольных действий.
    Перечень методов и их функции:
        setDefaultColor - сделать цвет 1 или цвет 2 активным (в зависимости от того, что выбрал пользователь)
        setCustomColor - открыть диалоговое окно создания цвета и по закрытии окна задать созданный пользователем цвет
        в качестве активного
        setUpdateColor - обновить визуальное представление цвета
        setRed - поставить красный
        setOrange - поставить оранжевый
        setYellow - поставить желтый
        setGreen - поставить зеленый
        setLightBlue - поставить голубой
        setBlue - поставить синий
        setPurple - поставить фиолетовый
        setBlack - поставить черный
        setWhite - поставить белый
        setLightGrey - поставить светло-серый
        setDarkGrey - поставить темно-серый
        setBrown - поставить коричневый
        setDarkRed - поставить темно-красный
        setPink - поставить розовый
        setFigureFill - разрешить или запретить заливку
        setSize - установить толщину контура
        setBrush - сделать кисть активным инструментом
        setPencil - сделать карандаш активным инструментом
        setEraser - сделать ластик активным инструментом
        setFill - сделать заливку активным инструментом
        setLine - сделать линию активным инструментом
        setCircle - сделать эллипс активным инструментом
        setTriangle - сделать треугольник активным инструментом
        setRectangle - сделать прямоугольник активным инструментом
        setPentagon - сделать пятиугольник активным инструментом
        setHexagon - сделать шестиугольник активным инструментом
        setOctagon - сделать восьмиугольник активным инструментом
    Цвета были взяты из соответствующих запросов в поисковую строку Яндекса, их браузер позволяет сразу вывести
    визуальное представление искомого цвета и его код в разных кодировках.
    """

    def setDefaultColor(self):
        if self.sender().text() == 'Цвет 1':
            self.default_color = 'color_1'
        else:
            self.default_color = 'color_2'

    def setCustomColor(self):
        custom = QColorDialog()
        custom.exec()
        if self.default_color == 'color_1':
            self.pen_color = custom.selectedColor()
            self.updateColor(self.pen_color)
        else:
            self.brush_color = custom.selectedColor()
            self.updateColor(self.brush_color)

    def updateColor(self, color):
        fill_color = color.name()
        if self.default_color == 'color_1':
            self.color_pix1.setStyleSheet(f'background-color: {fill_color}')
        else:
            self.color_pix2.setStyleSheet(f'background-color: {fill_color}')

    def setRed(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 0, 0)
            self.updateColor(self.brush_color)

    def setOrange(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 165, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 165, 0)
            self.updateColor(self.brush_color)

    def setYellow(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 255, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 255, 0)
            self.updateColor(self.brush_color)

    def setGreen(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 128, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 128, 0)
            self.updateColor(self.brush_color)

    def setLightBlue(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(66, 170, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(66, 170, 255)
            self.updateColor(self.brush_color)

    def setBlue(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 0, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 0, 255)
            self.updateColor(self.brush_color)

    def setPurple(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(139, 0, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(139, 0, 255)
            self.updateColor(self.brush_color)

    def setBlack(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 0, 0)
            self.updateColor(self.brush_color)

    def setWhite(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 255, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 255, 255)
            self.updateColor(self.brush_color)

    def setLightGrey(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(187, 187, 187)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(187, 187, 187)
            self.updateColor(self.brush_color)

    def setDarkGrey(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(73, 66, 61)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(73, 66, 61)
            self.updateColor(self.brush_color)

    def setBrown(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(150, 75, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(150, 75, 0)
            self.updateColor(self.brush_color)

    def setDarkRed(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(139, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(139, 0, 0)
            self.updateColor(self.brush_color)

    def setPink(self):
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 192, 203)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 192, 203)
            self.updateColor(self.brush_color)

    def setFigureFill(self):
        if self.sender().isChecked():
            self.fill = True
        else:
            self.fill = False

    def setSize(self):
        self.lineSize = MAINSIZE_KEYS[self.sender().currentText()]

    def setBrush(self):
        self.instrument = 'brush'

    def setPencil(self):
        self.instrument = 'pencil'

    def setEraser(self):
        self.instrument = 'eraser'

    def setFill(self):
        self.instrument = 'fill'

    def setLine(self):
        self.instrument = 'line'

    def setCircle(self):
        self.instrument = 'circle'

    def setTriangle(self):
        self.instrument = 'triangle'

    def setRectangle(self):
        self.instrument = 'rectangle'

    def setPentagon(self):
        self.instrument = '5gon'

    def setHexagon(self):
        self.instrument = '6gon'

    def setOctagon(self):
        self.instrument = '8gon'


class Brush:

    """
    Класс Brush, он же Кисть. Самодельный класс инструмента, призванный отвечать за правильную отрисовку кисти.
    На деле - постоянно рисует линию, обновляя точки начала и конца, поэтому плавные мазки - не что иное, как одна
    большая ломанная, состоящая из огромного кол-ва маленьких линий. Плавность кисти особо не меняется, а вот
    скорость ее прорисовки уже зависит от толщины кисти и мощности компьютера.

    Параметры при инициализации экземпляра класса Brush:
        sp - координаты точки начала
        ep - координаты точки конца
        size - толщина
        color - цвет
    """

    def __init__(self, sp, ep, size, color):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.size = size
        self.color = color

    """
    Ранее упомянутый метод draw. Задает переданному "рисовальщику" ручку, которая будет рисовать сплошную линию 
    определенного цвета, определенной толщины, со скругленными краями, и дает ему команду рисовать по координатам
    начала и конца.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin))
        painter.drawLine(self.sp, self.ep)


class Pencil(Brush):

    """
    Класс Pencil, он же Карандаш. Самодельный класс инструмента, призванный отвечать за прорисовку карандаша.
    Принцип работы схож с кистью, поэтому и наследован от класса Brush, за исключением одного момента: у карандаша
    установлена стандартная ручка с неизменяемой толщиной в 1 пиксель.

    Параметры при инициализации экземпляра класса Pencil:
        sp - координаты точки начала
        ep - координаты точки конца
        color - цвет
    """

    def __init__(self, sp, ep, color):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.color = color

    """
    Ранее упомянутый метод draw. Работает как кисть, разве что параметров ручки всего два: цвет и толщина в 1 пиксель.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, 1))
        painter.drawLine(self.sp, self.ep)


class Eraser(Brush):

    """
    Class Eraser, он же Ластик. Самодельный класс инструмента, призванный отвечать за прорисовку ластика. Принцип
    работы схож с кистью, поэтому и наследован от класса Brush, за исключением одного момента: у ластика установлена
    стандартная ручка с постоянным белым цветом и толщиной больше, чем текущая, на 2 пикселя.

    Параметры при инициализации экземпляра класса Eraser:
        sp - координаты точки начала
        ep - координаты точки конца
        size - толщина
    """

    def __init__(self, sp, ep, size):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.size = size

    """
    Ранее упомянутый метод draw. Работает как кисть, разве что параметров ручки всего два: белый цвет 
    и толщина на 2 пикселя больше.
    """

    def draw(self, painter):
        painter.setPen(QPen(Qt.white, self.size + 2))
        painter.drawLine(self.sp, self.ep)


class Line:

    """
    Класс Line, он же Линия. Самодельный класс инструмента, призванный отвечать за прорисовку линии. Несмотря на то, что
    кистеподобные классы тоже рисуют линию, делают они это постоянно, в отличии от Line, который рисует одну и ту же
    линию, обновляя ее размер и координаты по мере перемещения пользователем мыши.

    Параметры при инициализации экземпляра класса Line:
        sx - x точки начала
        sy - y точки начала
        ex - x точки конца
        ey - y точки конца
        size - толщина
        color - цвет
    """

    def __init__(self, sx, sy, ex, ey, size, color):
        super(Line, self).__init__()
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.size = size
        self.color = color

    """
    Ранее упомянутый метод draw. Работает как кисть, но их конструктивные особенности прописаны не в классе, а в методе
    mouseMoveEvent, где кисть и ей подобные начинают рисовать новую линию, а линия просто обновляет конечную точку.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)


class Circle:

    """
    Класс Circle, он же Круг. Самодельный класс инструмента, призванный отвечать за прорисовку эллипса. Реализовано
    через прямоугольник, внутри которого встроенным методом drawEllipse рисуется эллипс

    Параметры при инициализации экземпляра класса Circle:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Circle, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует эллипс в прямоугольнике с точкой начала и длиной и шириной этого прямоугольника.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawEllipse(self.sx, self.sy, self.x - self.sx, self.y - self.sy)


class Triangle:

    """
    Класс Triangle, он же Треугольник. Самодельный класс инструмента, призванный отвечать за прорисовку треугольника.
    Реализовано через рисование многоугольника внутри области прямоугольника по следующему правилу: левый крайний,
    правый крайний и середина верхнего (или нижнего, в зависимости от того, куда смещена мышь по y относительно начала)
    основания.

    Параметры при инициализации экземпляра класса Triangle:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Triangle, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует многоугольник по точкам. Координаты точек задаются в соответствии с правилом построения
    треугольника внутри прямоугольника.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        dist = (self.x - self.sx) // 2
        triangle = QPolygon()
        triangle.append(QPoint(self.sx, self.sy))
        triangle.append(QPoint(self.sx + dist, self.y))
        triangle.append(QPoint(self.x, self.sy))
        painter.drawPolygon(triangle)


class Rectangle:

    """
    Класс Rectangle, он же Прямоугольник. Самодельный класс инструмента, призванный за прорисовку прямоугольника.
    Собственно, ничего тут не поменяешь - раз уж есть встроенный метод drawRect по рисованию прямоугольника, используй
    его.

    Параметры при инициализации экземпляра класса Rectangle:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Rectangle, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует прямоугольник встроенным методом drawRect.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(self.sx, self.sy, self.x - self.sx, self.y - self.sy)


class Pentagon:

    """
    Класс Pentagon, он же Пятиугольник. Самодельный класс инструмента, призванный отвечать за прорисовку пятиугольника.
    Реализовано через рисование многоугольника внутри области прямоугольника по следующему правилу
    (начиная с нижней левой точки, по часовой стрелке): 19% от длины нижнего основания, 61% от длины левого края,
    половина верхнего основания, 61% от длины правого края и 81% от длины нижнего основания. Это может показаться
    странным, но именно так рисуется пятиугольник в MS Paint, проверено лично.

    Параметры при инициализации экземпляра класса Pentagon:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Pentagon, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует многоугольник по точкам. Координаты точек задаются в соответствии с правилом построения
    пятиугольника внутри прямоугольника.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        pentagon = QPolygon()
        dist_x = self.x - self.sx
        dist_y = self.y - self.sy
        pentagon.append(QPoint(self.sx + int(dist_x * 0.19), self.sy))
        pentagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.61)))
        pentagon.append(QPoint(self.sx + dist_x // 2, self.y))
        pentagon.append(QPoint(self.x, self.sy + int(dist_y * 0.61)))
        pentagon.append(QPoint(self.sx + int(dist_x * 0.81), self.sy))
        painter.drawPolygon(pentagon)


class Hexagon:

    """
    Класс Hexagon, он же Шестиугольник. Самодельный класс инструмента, призванный отвечать за прорисовку шестиугольника.
    Реализовано через рисование многоугольника внутри области прямоугольника по следующему правилу
    (начиная с нижней точки, по часовой стрелке): середина нижнего основания, 25% от длины левого края,
    75% от длины левого края, середина верхнего основания, 75% от длины правого края и 25% от длины правого края.
    Это может показаться странным, но именно так рисуется шестиугольник в MS Paint, проверено лично.

    Параметры при инициализации экземпляра класса Hexagon:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Hexagon, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует многоугольник по точкам. Координаты точек задаются в соответствии с правилом построения
    шестиугольника внутри прямоугольника.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        hexagon = QPolygon()
        dist_x = self.x - self.sx
        dist_y = self.y - self.sy
        hexagon.append(QPoint(self.sx + dist_x // 2, self.sy))
        hexagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.25)))
        hexagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.75)))
        hexagon.append(QPoint(self.sx + dist_x // 2, self.y))
        hexagon.append(QPoint(self.x, self.sy + int(dist_y * 0.75)))
        hexagon.append(QPoint(self.x, self.sy + int(dist_y * 0.25)))
        painter.drawPolygon(hexagon)


class Octagon:

    """
    Класс Octagon, он же Восьмиугольник. Самодельный класс инструмента, призванный отвечать за прорисовку
    восьмиугольника. Реализовано через рисование многоугольника внутри области прямоугольника по следующему правилу
    (начиная с нижней левой точки, по часовой стрелке): 25% от длины нижнего основания, 25% от длины левого края,
    75% от длины левого края, 25% от длины верхнего основания, 75% от длины верхнего основания,
    75% от длины правого края, 25% от длины правого края и 75% от длины нижнего основания. Это может показаться
    странным, но именно так рисуется восьмиугольник в MS Paint, проверено лично.

    Параметры при инициализации экземпляра класса Octagon:
        sx - x точки начала
        sy - y точки начала
        x - x точки конца
        y - y точки конца
        to_fill - разрешение на заливку
        size - толщина контура
        color - цвет контура
        color_2 - цвет заливки
    """

    def __init__(self, sx, sy, x, y, fill, size, color, color_2):
        super(Octagon, self).__init__()
        self.sx = sx
        self.sy = sy
        self.x = x
        self.y = y
        self.to_fill = fill
        self.size = size
        self.color = color
        self.color_2 = color_2

    """
    Ранее упомянутый метод draw. Задает ручку, а если еще и заливка разрешена, задает кисть (в противном случае, кисть
    отменяется) и рисует многоугольник по точкам. Координаты точек задаются в соответствии с правилом построения
    восьмиугольника внутри прямоугольника.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        octagon = QPolygon()
        dist_x = self.x - self.sx
        dist_y = self.y - self.sy
        octagon.append(QPoint(self.sx + int(dist_x * 0.25), self.sy))
        octagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.25)))
        octagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.75)))
        octagon.append(QPoint(self.sx + int(dist_x * 0.25), self.y))
        octagon.append(QPoint(self.sx + int(dist_x * 0.75), self.y))
        octagon.append(QPoint(self.x, self.sy + int(dist_y * 0.75)))
        octagon.append(QPoint(self.x, self.sy + int(dist_y * 0.25)))
        octagon.append(QPoint(self.sx + int(dist_x * 0.75), self.sy))
        painter.drawPolygon(octagon)


class Fill:

    """
    Класс Fill, он же Заливка. Самодельный класс инструмента, призванный отвечать за заливку всего холста.
    По сути, рисует прямоугольник с заливкой во весь холст.

    Параметры при инициализации экземпляра класса Fill:
        w - ширина
        h - высота
        color - цвет заливки
    """

    def __init__(self, w, h, color):
        super(Fill, self).__init__()
        self.w = w
        self.h = h
        self.color = color

    """
    Ранее упомянутый метод draw. Задает ручку и кисть одного и того же цвета и рисует прямоугольник от начала холста
    до его конца.
    """

    def draw(self, painter):
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0, 0, self.w, self.h)


class Image:

    """
    Класс Image, он же Картинка. Самодельный класс инструмента, призванный отвечать за прорисовку загруженной
    пользователем картинки. Класс открывает картинку в виде объекта QImage и рисует ее на холст в исходном размере в
    верхний левый край.

    Параметры при инициализации экземпляра класса Image:
        file - файл с картинкой
    """

    def __init__(self, file):
        super(Image, self).__init__()
        self.file = file

    """
    Ранее упомянутый метод draw. Загружает выбранный файл в класс QImage и передает ее "рисовальшику".
    """

    def draw(self, painter):
        image = QImage()
        image.load(self.file)
        painter.drawImage(image.rect(), image)


class Save(Canvas):

    """
    Класс Save, он же Сохранение. Самодельный служебный класс, призванный отвечать за сохранение разрисованного холста.
    Зарисовывает весь холст на отдельную картинку и сохраняет ее. Класс наследован от Canvas из-за того, что
    возможностью открыть окно сохранения обладает только класс QWidget, от которого и наследован Canvas.

    Параметры при инициализации экземпляра класса Save:
        size - размер (на деле, просто переданный размер холста)
    """

    def __init__(self, size):
        super(Save, self).__init__()
        self.file = None
        self.image = QImage(size, QImage.Format_RGB16)
        self.image.fill(Qt.white)

    """
    Метод save. Рисует на созданной картинке все объекты по очереди и спрашивает у пользователя, куда сохранить
    картинку. Если пользователь дал файл, сохраняем, иначе игнорируем.
    """

    def save(self, objects):
        painter = QPainter(self.image)
        for obj in objects:
            obj.draw(painter)
        painter.end()
        self.file = QFileDialog.getSaveFileName(self, 'Сохранение', 'C:/', '(*.png);;(*.jpg);;(*.bmp)')[0]
        if self.file:
            self.image.save(self.file)


class Window(QMainWindow):

    """
    Класс Window, он же Окно. На ряду с Canvas, самый важный класс приложения, так как он создает окно и отвечает за
    все процессы внутри него. Параметров инициализации у класса нет, гораздо важнее рассказать про процесс
    инициализации:
        - Загружаем .ui файл с интерфейсом, созданном в Qt Designer
        - Отключаем окно, разрешаем пользователю использовать верхнее меню инструментов, а приложению - отслеживать мышь
        - Окно отключили, чтобы пользователь не успел наделать дел. Чтобы это не казалось странным, вызываем стартовое
        диалоговое окно и таким образом "задерживаем" пользователя на небольшое время
        - Создаем холст и вносим его в интерфейс, в том числе и его цвета
        - Добавляем в список толщин, непосредственно, толщины, подвязываем список к действию смены толщин и задаем
        значение по умолчанию
        - Подвязываем кнопки инструментов к действиям смены инструментов
        - Подвязываем кнопки переключения цветов и флажок заливки
        - Подтягиваем служебные команды из разделов "Файл" и "Инфо" к приложению
        - На конец, подключаем все кнопки цветов
    """

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi(dir_ui, self)

        self.main_widget.setEnabled(False)
        self.setMouseTracking(True)
        self.menubar.setEnabled(False)

        self.message = QMessageBox()
        setIcon(self.message)
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Перед запуском')
        self.message.setText('Чтобы начать работу, создайте новый холст или откройте существующую картинку.')
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()
        self.menubar.setEnabled(True)

        self.canvas = Canvas()
        self.canvas_layout.addWidget(self.canvas)
        self.color_layout.addWidget(self.canvas.color_pix1, 0, 0)
        self.color_layout.addWidget(self.canvas.color_pix2, 0, 1)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.size_box.addItems(MAINSIZE_KEYS.keys())
        self.size_box.activated.connect(self.canvas.setSize)
        self.size_box.setCurrentIndex(1)

        self.brush_button.setDefaultAction(self.action_brush)
        self.pencil_button.setDefaultAction(self.action_pencil)
        self.fill_button.setDefaultAction(self.action_fill)
        self.eraser_button.setDefaultAction(self.action_eraser)
        self.line_button.setDefaultAction(self.action_line)
        self.circle_button.setDefaultAction(self.action_circle)
        self.triangle_button.setDefaultAction(self.action_triangle)
        self.rectangle_button.setDefaultAction(self.action_rectangle)
        self.pentagon_button.setDefaultAction(self.action_pentagon)
        self.hexagon_button.setDefaultAction(self.action_hexagon)
        self.octagon_button.setDefaultAction(self.action_octagon)
        self.action_brush.triggered.connect(self.canvas.setBrush)
        self.action_pencil.triggered.connect(self.canvas.setPencil)
        self.action_fill.triggered.connect(self.canvas.setFill)
        self.action_eraser.triggered.connect(self.canvas.setEraser)
        self.action_line.triggered.connect(self.canvas.setLine)
        self.action_circle.triggered.connect(self.canvas.setCircle)
        self.action_triangle.triggered.connect(self.canvas.setTriangle)
        self.action_rectangle.triggered.connect(self.canvas.setRectangle)
        self.action_pentagon.triggered.connect(self.canvas.setPentagon)
        self.action_hexagon.triggered.connect(self.canvas.setHexagon)
        self.action_octagon.triggered.connect(self.canvas.setOctagon)

        self.fill_check.toggled.connect(self.canvas.setFigureFill)
        self.maincolor_button.toggled.connect(self.canvas.setDefaultColor)
        self.secondcolor_button.toggled.connect(self.canvas.setDefaultColor)
        self.maincolor_button.setChecked(True)

        self.action_open.triggered.connect(self.openFile)
        self.action_save.triggered.connect(self.saveFile)
        self.action_create.triggered.connect(self.newCanvas)
        self.action_clear.triggered.connect(self.clearCanvas)
        self.action_aboutme.triggered.connect(self.aboutProgram)
        self.action_help.triggered.connect(self.helpMe)

        self.red_button.setDefaultAction(self.action_red)
        self.red_button.setText('')
        self.orange_button.setDefaultAction(self.action_orange)
        self.orange_button.setText('')
        self.yellow_button.setDefaultAction(self.action_yellow)
        self.yellow_button.setText('')
        self.green_button.setDefaultAction(self.action_green)
        self.green_button.setText('')
        self.lightblue_button.setDefaultAction(self.action_lightblue)
        self.lightblue_button.setText('')
        self.blue_button.setDefaultAction(self.action_blue)
        self.blue_button.setText('')
        self.purple_button.setDefaultAction(self.action_purple)
        self.purple_button.setText('')
        self.black_button.setDefaultAction(self.action_black)
        self.black_button.setText('')
        self.white_button.setDefaultAction(self.action_white)
        self.white_button.setText('')
        self.lightgrey_button.setDefaultAction(self.action_lightgrey)
        self.lightgrey_button.setText('')
        self.darkgrey_button.setDefaultAction(self.action_darkgrey)
        self.darkgrey_button.setText('')
        self.brown_button.setDefaultAction(self.action_brown)
        self.brown_button.setText('')
        self.darkred_button.setDefaultAction(self.action_darkred)
        self.darkred_button.setText('')
        self.pink_button.setDefaultAction(self.action_pink)
        self.pink_button.setText('')
        self.customcolor_button.clicked.connect(self.canvas.setCustomColor)
        self.action_red.triggered.connect(self.canvas.setRed)
        self.action_orange.triggered.connect(self.canvas.setOrange)
        self.action_yellow.triggered.connect(self.canvas.setYellow)
        self.action_green.triggered.connect(self.canvas.setGreen)
        self.action_lightblue.triggered.connect(self.canvas.setLightBlue)
        self.action_blue.triggered.connect(self.canvas.setBlue)
        self.action_purple.triggered.connect(self.canvas.setPurple)
        self.action_black.triggered.connect(self.canvas.setBlack)
        self.action_white.triggered.connect(self.canvas.setWhite)
        self.action_lightgrey.triggered.connect(self.canvas.setLightGrey)
        self.action_darkgrey.triggered.connect(self.canvas.setDarkGrey)
        self.action_brown.triggered.connect(self.canvas.setBrown)
        self.action_darkred.triggered.connect(self.canvas.setDarkRed)
        self.action_pink.triggered.connect(self.canvas.setPink)

    """
    Метод openFile. Работает с пользователем по открытию файла. Также привязан к окну, потому что при запуске окно
    отключено, а чтобы его "разблокировать", нужно создать новый холст или открыть картинку.
    """

    def openFile(self):
        file = QFileDialog.getOpenFileName(self, 'Открытие', 'C:/', '(*.png);;(*.jpg);;(*.bmp)')[0]
        if file:
            self.canvas.objects.clear()
            self.canvas.objects.append(Image(file))
            if not self.main_widget.isEnabled():
                self.main_widget.setEnabled(True)

    """
    Метод saveFile. Работает над сохранением разрисованного холста. Если сохранение состоялось, кол-во сохраненных
    объектов холста обновляется, а холст становится сохраненным
    """

    def saveFile(self):
        saver = Save(self.canvas.size())
        saver.save(self.canvas.objects)
        if saver.file:
            self.canvas.saved_objects = len(self.canvas.objects)
            self.canvas.saved = True

    """
    Метод newCanvas. Создает "новый" холст. Первостепенная задача этого метода - дать пользователю начать рисование,
    далее - стирать холст и обновлять его. При этом пользователь имеет выбор между опциями "Создать холст" и "Очистить
    холст". Функционально "создание холста" и является "очисткой холста", только "создание холста" предупреждает
    пользователя о возможных потерях и предлагает сохраниться, в отличии от "очистки холста".
    """

    def newCanvas(self):
        if not self.main_widget.isEnabled():
            self.main_widget.setEnabled(True)
            self.clearCanvas()
        else:
            if not self.canvas.saved:
                self.message = QMessageBox()
                setIcon(self.message)
                self.message.setIcon(QMessageBox.Warning)
                self.message.setWindowTitle('Предупреждение')
                self.message.setText('Создание нового холста приведет к потери текущего.\nСохраниться?\n')
                self.message.setStandardButtons(QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel)
                btnsave = self.message.button(QMessageBox.Save)
                btnsave.setText('Да')
                btnclose = self.message.button(QMessageBox.Close)
                btnclose.setText('Нет')
                btncancel = self.message.button(QMessageBox.Cancel)
                btncancel.setText('Отмена')
                self.message.exec()
                if self.message.clickedButton() == btnclose:
                    self.clearCanvas()
                elif self.message.clickedButton() == btnsave:
                    self.saveFile()
                    if not self.canvas.saved:
                        pass
                    else:
                        self.clearCanvas()
                else:
                    pass
            else:
                self.clearCanvas()

    """
    Метод clearCanvas. Очищает холст, то есть, удаляет все объекты и заливает чистым белым. Разница между "очисткой"
    и "созданием" объяснена выше.
    """

    def clearCanvas(self):
        self.canvas.objects.clear()
        self.canvas.objects.append(Fill(self.canvas.width(), self.canvas.height(), Qt.white))
        self.update()

    """
    Метод aboutProgram. Создает информационное диалоговое окно и выводит информацию о программе с заготовленного текста.
    """

    def aboutProgram(self):
        self.message = QMessageBox()
        setIcon(self.message)
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Информация о проекте')
        self.message.setText(INFO_TEXT)
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()

    """
    Метод helpMe. Создает информационное диалоговое окно и выводит заготовленный текст-подсказку.
    """

    def helpMe(self):
        self.message = QMessageBox()
        setIcon(self.message)
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Помощь')
        self.message.setText(HELP_TEXT)
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()

    """
    Встроенный метод класса QMainWindow, от которого унаследован Окно. Срабатывает, если ядро библиотеки 
    фиксирует закрытие приложения. Если окно так и не было "разблокировано", все в порядке. А если нет, проверяем, 
    сохранен ли холст, если нет, то предлагаем сохраниться. "Да" - сохраняем и выходим. "Нет" - сразу выходим.
    "Отмена" - откладываем закрытие приложения, пока пользователь не решит.
    """

    def closeEvent(self, event):
        if self.main_widget.isEnabled():
            if not self.canvas.saved:
                self.message = QMessageBox()
                setIcon(self.message)
                self.message.setIcon(QMessageBox.Warning)
                self.message.setWindowTitle('Предупреждение')
                self.message.setText('Вы собираетесь завершить работу с несохраненным файлом.\nСохраниться?\n')
                self.message.setStandardButtons(QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel)
                btnsave = self.message.button(QMessageBox.Save)
                btnsave.setText('Да')
                btnclose = self.message.button(QMessageBox.Close)
                btnclose.setText('Нет')
                btncancel = self.message.button(QMessageBox.Cancel)
                btncancel.setText('Отмена')
                self.message.exec()
                if self.message.clickedButton() == btnclose:
                    event.accept()
                elif self.message.clickedButton() == btnsave:
                    self.saveFile()
                    if not self.canvas.saved:
                        event.ignore()
                else:
                    event.ignore()


"""
Стандартная проверка самостоятельного запуска кода. Для зеленых в Python - эта часть кода запустится, только если
файл был запущен самостоятельно, а не как часть другой программы (например, при импортировании). Ну а поскольку в этой
части находится инициализация приложения и отслеживание его работы в системе, ВСЁ приложение не заработает как
импортированная библиотека.
"""


def main():
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
