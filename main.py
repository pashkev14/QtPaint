"""
QtPaint, 2020-2022. Made by Pavel Savin A.K.A. "pashkev14".

Импортированные библиотеки. В основе всего приложения лежит фреймворк Qt, а конкретно его Python версия - PyQt5.
Сейчас эта библиотека неактуальна: Qt предоставляет для Python 2 решения - платный для коммерческих/закрытых проектов
PyQt6 и бесплатный для любого типа проектов PySide6. Этот проект сделан в некоммерческих целях, поэтому вопрос его
лицензии был предрешен еще в зачатке идеи. Библиотека sys открывает доступ к возможностям системы, здесь ее
функционал сведен до открытия приложения в потоке и работы с файлами.
"""
import sys

from PyQt5 import uic
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPolygon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMessageBox, QFileDialog, QColorDialog, QSizePolicy, \
    QLabel
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
HELP_TEXT = ''.join(open('src/help.txt', mode='r', encoding='utf-8').readlines())
INFO_TEXT = ''.join(open('src/about.txt', mode='r', encoding='utf-8').readlines())

"""
Класс Canvas, он же Холст. По сути является большим пустым виджетом, на котором будут отображаться заданные
пользователем рисунки. Базовый класс QWidget как раз обладает такой возможностью, поэтому реализация холста через
базовый виджет со своими параметрами имеет место быть.
"""


class Canvas(QWidget):
    """
    Параметры при инициализации экземпляра класса:
        objects - список рисуемых объектов
        instrument - выбранный инструмент (по умолчанию - кисть)
        default_color - активный цвет (по умолчанию - цвет 1)
        pen_color - текущий цвет 1 (по умолчанию - черный)
        brush_color - текущий цвет 2 (по умолчанию - белый)
        lineSize - текущая толщина рисуемой линии (по умолчанию - 3 пикселя)
        setCursor - унаследованный метод класса QWidget, задающий стиль курсора, когда он находится в области виджета.
        Здесь - команда по смене обычного курсора на встроенный крест Qt.CrossCursor
        currentPoint - координаты текущей позиции курсора на холсте. Нужна для рисования, не отрывая руки
        fill - разрешение на заливку (по умолчанию - не заливать)
        saved - обновляемый "флажок" сохранения (по умолчанию холст сохранен, но стоит отклониться от )
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

    def paintEvent(self, event):  # непосредственно процесс отрисовки объектов на холст
        painter = QPainter()
        painter.begin(self)
        for obj in self.objects:
            obj.draw(painter)
        painter.end()
        if len(self.objects) > self.saved_objects or self.saved_objects > len(self.objects) > 1:
            self.saved = False

    def mousePressEvent(self, event):  # обработка клика по мыши; о хитросплетениях параметров в описании классов
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

    def mouseMoveEvent(self, event):  # обработка движения мыши; о хитросплетениях параметров в описании классов
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

    def setDefaultColor(self):  # установка ведущего цвета
        if self.sender().text() == 'Цвет 1':
            self.default_color = 'color_1'
        else:
            self.default_color = 'color_2'

    def setCustomColor(self):  # дадим пользователю расширить палитру
        custom = QColorDialog()
        custom.exec()
        if self.default_color == 'color_1':
            self.pen_color = custom.selectedColor()
            self.updateColor(self.pen_color)
        else:
            self.brush_color = custom.selectedColor()
            self.updateColor(self.brush_color)

    def updateColor(self, color):  # обновление отображаемых цветов
        fill_color = color.name()
        if self.default_color == 'color_1':
            self.color_pix1.setStyleSheet(f'background-color: {fill_color}')
        else:
            self.color_pix2.setStyleSheet(f'background-color: {fill_color}')

    # спасибо Яндексу за предоставленную инфу
    def setRed(self):  # поставить красный
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 0, 0)
            self.updateColor(self.brush_color)

    def setOrange(self):  # поставить оранжевый
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 165, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 165, 0)
            self.updateColor(self.brush_color)

    def setYellow(self):  # поставить желтый
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 255, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 255, 0)
            self.updateColor(self.brush_color)

    def setGreen(self):  # поставить зеленый
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 128, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 128, 0)
            self.updateColor(self.brush_color)

    def setLightBlue(self):  # поставить голубой
        if self.default_color == 'color_1':
            self.pen_color = QColor(66, 170, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(66, 170, 255)
            self.updateColor(self.brush_color)

    def setBlue(self):  # поставить синий
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 0, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 0, 255)
            self.updateColor(self.brush_color)

    def setPurple(self):  # поставить фиолетовый
        if self.default_color == 'color_1':
            self.pen_color = QColor(139, 0, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(139, 0, 255)
            self.updateColor(self.brush_color)

    def setBlack(self):  # поставить черный
        if self.default_color == 'color_1':
            self.pen_color = QColor(0, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(0, 0, 0)
            self.updateColor(self.brush_color)

    def setWhite(self):  # поставить белый
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 255, 255)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 255, 255)
            self.updateColor(self.brush_color)

    def setLightGrey(self):  # поставить светло-серый
        if self.default_color == 'color_1':
            self.pen_color = QColor(187, 187, 187)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(187, 187, 187)
            self.updateColor(self.brush_color)

    def setDarkGrey(self):  # поставить темно-серый
        if self.default_color == 'color_1':
            self.pen_color = QColor(73, 66, 61)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(73, 66, 61)
            self.updateColor(self.brush_color)

    def setBrown(self):  # поставить коричневый
        if self.default_color == 'color_1':
            self.pen_color = QColor(150, 75, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(150, 75, 0)
            self.updateColor(self.brush_color)

    def setDarkRed(self):  # поставить темно-красный(а не бордовый)
        if self.default_color == 'color_1':
            self.pen_color = QColor(139, 0, 0)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(139, 0, 0)
            self.updateColor(self.brush_color)

    def setPink(self):  # поставить розовый
        if self.default_color == 'color_1':
            self.pen_color = QColor(255, 192, 203)
            self.updateColor(self.pen_color)
        else:
            self.brush_color = QColor(255, 192, 203)
            self.updateColor(self.brush_color)

    def setFigureFill(self):  # разрешить заливать площадь фигуры
        if self.sender().isChecked():
            self.fill = True
        else:
            self.fill = False

    def setSize(self):  # установить текущую толщину кисти на основе переданного значения
        self.lineSize = MAINSIZE_KEYS[self.sender().currentText()]

    def setBrush(self):  # установить кисть
        self.instrument = 'brush'

    def setPencil(self):  # установить карандаш
        self.instrument = 'pencil'

    def setEraser(self):  # установить ластик
        self.instrument = 'eraser'

    def setFill(self):  # установить заливку
        self.instrument = 'fill'

    def setLine(self):  # установить линию
        self.instrument = 'line'

    def setCircle(self):  # установить эллипс
        self.instrument = 'circle'

    def setTriangle(self):  # установить треугольник
        self.instrument = 'triangle'

    def setRectangle(self):  # установить прямоугольник
        self.instrument = 'rectangle'

    def setPentagon(self):  # установить пятиугольник
        self.instrument = '5gon'

    def setHexagon(self):  # установить шестиугольник
        self.instrument = '6gon'

    def setOctagon(self):  # установить восьмиугольник
        self.instrument = '8gon'


class Brush(Canvas):  # класс кисти, принимает начальную и конечную точки, толщину и цвет кисти
    def __init__(self, sp, ep, size, color):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.size = size
        self.color = color

    def draw(self, painter):  # отрисовка построена на рисовании линии с постоянным обновлением обеих точек
        painter.setPen(QPen(self.color, self.size, Qt.SolidLine, Qt.RoundCap, Qt.BevelJoin))
        painter.drawLine(self.sp, self.ep)


class Pencil(Brush):  # класс карандаш, для удобства наследован от кисти, только толщина всегда 1 пикс
    def __init__(self, sp, ep, color):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.color = color

    def draw(self, painter):  # отрисовка карандаша схожа с кистью
        painter.setPen(QPen(self.color, 1))
        painter.drawLine(self.sp, self.ep)


class Eraser(Brush):  # класс ластика, также наследован от кисти, только цвет всегда белый и толщина на 2 пикс больше
    # заданной
    def __init__(self, sp, ep, size):
        super(Brush, self).__init__()
        self.sp = sp
        self.ep = ep
        self.size = size

    def draw(self, painter):  # отрисовка ластика схожа с кистью
        painter.setPen(QPen(Qt.white, self.size + 2))
        painter.drawLine(self.sp, self.ep)


class Line(Canvas):  # класс линии, принимает координаты начальной и конечной точек, толщину и цвет кисти
    def __init__(self, sx, sy, ex, ey, size, color):
        super(Line, self).__init__()
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.size = size
        self.color = color

    def draw(self, painter):  # отличие от кисти в том, что линия обновляет только конечную точку
        painter.setPen(QPen(self.color, self.size))
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)


# пошли многоугольники в бой
# их отрисовка подвязана на прямоугольнике с определенными точками внутри него
class Circle(Canvas):  # класс эллипса, принимает координаты начальной и конечной точек, разрешение на заливку,
    # толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # для отрисовки уже есть метод drawEllipse, реализованный здесь через прямоугольник
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawEllipse(self.sx, self.sy, self.x - self.sx, self.y - self.sy)


class Triangle(Canvas):  # класс треугольника, принимает координаты начальной и конечной точек, разрешение на заливку,
    # толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # отрисовка построена на рисовании многоугольника внутри прямоугольника по правилу
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        dist = (self.x - self.sx) // 2  # само правило
        triangle = QPolygon()
        triangle.append(QPoint(self.sx, self.sy))
        triangle.append(QPoint(self.sx + dist, self.y))
        triangle.append(QPoint(self.x, self.sy))
        painter.drawPolygon(triangle)


class Rectangle(Canvas):  # класс прямоугольника, принимает координаты начальной и конечной точек, разрешение на
    # заливку, толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # метод drawRect никто не забывал
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(self.sx, self.sy, self.x - self.sx, self.y - self.sy)


class Pentagon(Canvas):  # класс пятиугольника, принимает координаты начальной и конечной точек, разрешение на заливку,
    # толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # отрисовка построена на рисовании многоугольника внутри прямоугольника по правилу
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        pentagon = QPolygon()
        dist_x = self.x - self.sx
        dist_y = self.y - self.sy
        # для такого шаманства обратился к нарисованному в MS Paint пятиугольнику
        # и самостоятельно просчитывал координаты
        pentagon.append(QPoint(self.sx + int(dist_x * 0.19), self.sy))
        pentagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.61)))
        pentagon.append(QPoint(self.sx + dist_x // 2, self.y))
        pentagon.append(QPoint(self.x, self.sy + int(dist_y * 0.61)))
        pentagon.append(QPoint(self.sx + int(dist_x * 0.81), self.sy))
        painter.drawPolygon(pentagon)


class Hexagon(Canvas):  # класс шестиугольника, принимает координаты начальной и конечной точек, разрешение на заливку,
    # толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # отрисовка построена на рисовании многоугольника внутри прямоугольника по правилу
        painter.setPen(QPen(self.color, self.size))
        if self.to_fill:
            painter.setBrush(QBrush(self.color_2))
        else:
            painter.setBrush(QBrush(Qt.NoBrush))
        hexagon = QPolygon()
        dist_x = self.x - self.sx
        dist_y = self.y - self.sy
        # для такого шаманства обратился к нарисованному в MS Paint шестиугольнику
        # и самостоятельно просчитывал координаты
        hexagon.append(QPoint(self.sx + dist_x // 2, self.sy))
        hexagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.25)))
        hexagon.append(QPoint(self.sx, self.sy + int(dist_y * 0.75)))
        hexagon.append(QPoint(self.sx + dist_x // 2, self.y))
        hexagon.append(QPoint(self.x, self.sy + int(dist_y * 0.75)))
        hexagon.append(QPoint(self.x, self.sy + int(dist_y * 0.25)))
        painter.drawPolygon(hexagon)


class Octagon(Canvas):  # класс восьмиугольника, принимает координаты начальной и конечной точек, разрешение на заливку,
    # толщину и цвет контура, а также цвет заливки
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

    def draw(self, painter):  # отрисовка построена на рисовании многоугольника внутри прямоугольника по правилу
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


class Fill(Canvas):  # класс заливки
    def __init__(self, w, h, color):
        super(Fill, self).__init__()
        self.w = w
        self.h = h
        self.color = color

    def draw(self, painter):  # заливка построена на прямоугольнике во весь холст заданного цвета
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0, 0, self.w, self.h)


class Image(Canvas):  # класс картинки
    def __init__(self, w, h, file):
        super(Image, self).__init__()
        self.rect = QRect(0, 0, w, h)
        self.file = file

    def draw(self, painter):  # создаем картинку, загружаем файл и ставим ее на весь холст
        image = QImage()
        image.load(self.file)
        painter.drawImage(self.rect, image)


class Save(QWidget):  # класс сохранения, создает картинку для сохранения
    def __init__(self, size):
        super(Save, self).__init__()
        self.file = None
        self.image = QImage(size, QImage.Format_RGB16)
        self.image.fill(Qt.white)

    def save(self, objects):  # нарисуем все объекты холста на картинке и сохраним эту картинку
        painter = QPainter(self.image)
        for obj in objects:
            obj.draw(painter)
        painter.end()
        self.file = QFileDialog.getSaveFileName(self, 'Сохранение', 'C:/', '(*.png);;(*.jpg);;(*.bmp)')[0]
        if self.file:
            self.image.save(self.file)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())


class Window(QMainWindow):  # класс окна
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('src/window.ui', self)

        self.main_widget.setEnabled(False)
        self.setMouseTracking(True)
        self.menubar.setEnabled(False)
        # это чтобы юзер мог получать по шапке вовремя, но для начала выведем стартовое сообщение
        self.message = QMessageBox()
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Перед запуском')
        self.message.setText('Чтобы начать работу, создайте новый холст или откройте существующую картинку.')
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()
        self.menubar.setEnabled(True)
        # создаем холст
        self.canvas = Canvas()
        self.canvas_layout.addWidget(self.canvas)
        self.color_layout.addWidget(self.canvas.color_pix1, 0, 0)
        self.color_layout.addWidget(self.canvas.color_pix2, 0, 1)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # настраиваем список толщин
        self.size_box.addItems(MAINSIZE_KEYS.keys())
        self.size_box.activated.connect(self.canvas.setSize)
        self.size_box.setCurrentIndex(1)
        # подключение кнопок к инструментам
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
        # подключение инструментов
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
        # подключение переключателей
        self.fill_check.toggled.connect(self.canvas.setFigureFill)
        self.maincolor_button.toggled.connect(self.canvas.setDefaultColor)
        self.secondcolor_button.toggled.connect(self.canvas.setDefaultColor)
        self.maincolor_button.setChecked(True)
        # настройки файла
        self.action_open.triggered.connect(self.openFile)
        self.action_save.triggered.connect(self.saveFile)
        self.action_create.triggered.connect(self.newCanvas)
        self.action_clear.triggered.connect(self.clearCanvas)
        # подключение кнопок цветов к действиям
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
        # подключение стандартных цветов
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
        # особые кнопочки
        self.action_aboutme.triggered.connect(self.aboutProgram)
        self.action_help.triggered.connect(self.helpMe)

    def openFile(self):  # открываем файл
        file = QFileDialog.getOpenFileName(self, 'Открытие', 'C:/', '(*.png);;(*.jpg);;(*.bmp)')[0]
        if file:
            self.canvas.objects.clear()
            self.canvas.objects.append(Image(self.canvas.width(), self.canvas.height(), file))  # просто рисуем объект
            # класса картинка
            if not self.main_widget.isEnabled():
                self.main_widget.setEnabled(True)

    def saveFile(self):  # сохраняем файл, то есть, выполняем метод сохранения из класса сохранения
        saver = Save(self.canvas.size())
        saver.save(self.canvas.objects)
        if saver.file:
            self.canvas.saved_objects = len(self.canvas.objects)
            self.canvas.saved = True

    def newCanvas(self):  # создаем файл
        if not self.main_widget.isEnabled():  # при запуске окно отключено, чтобы юзер не намутил лишнего
            self.main_widget.setEnabled(True)
            self.clearCanvas()
        else:
            if not self.canvas.saved:
                message = QMessageBox()
                message.setIcon(QMessageBox.Warning)
                message.setWindowTitle('Предупреждение')
                message.setText('Создание нового холста приведет к потери текущего.\n'
                                'Сохраниться?\n')
                message.setStandardButtons(QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel)
                btnsave = message.button(QMessageBox.Save)
                btnsave.setText('Да')
                btnclose = message.button(QMessageBox.Close)
                btnclose.setText('Нет')
                btncancel = message.button(QMessageBox.Cancel)
                btncancel.setText('Отмена')
                message.exec()
                if message.clickedButton() == btnclose:
                    self.clearCanvas()
                elif message.clickedButton() == btnsave:
                    self.saveFile()
                    if not self.canvas.saved:
                        pass
                    else:
                        self.clearCanvas()
                else:
                    pass
            else:
                self.clearCanvas()

    def clearCanvas(self):  # рисует объект класса заливки белого цвета
        self.canvas.objects.clear()
        self.canvas.objects.append(Fill(self.canvas.width(), self.canvas.height(), Qt.white))
        self.update()

    def aboutProgram(self):  # не бейте за такое кощунство, но лучше уж написать инфо, пока не поздно
        self.message = QMessageBox()
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Информация о проекте')
        self.message.setText(INFO_TEXT)
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()

    def helpMe(self):  # самый крутой и важный метод
        self.message = QMessageBox()
        self.message.setIcon(QMessageBox.Information)
        self.message.setWindowTitle('Помощь')
        self.message.setText(HELP_TEXT)
        self.message.addButton('ОК', QMessageBox.YesRole)
        self.message.exec()

    def closeEvent(self, event):  # перед закрытием ОБЯЗАТЕЛЬНО предупредить о сохранениях
        if self.main_widget.isEnabled():
            if not self.canvas.saved:
                message = QMessageBox()
                message.setIcon(QMessageBox.Warning)
                message.setWindowTitle('Предупреждение')
                message.setText('Вы собираетесь завершить работу с несохраненным файлом.\n'
                                'Сохраниться?\n')
                message.setStandardButtons(QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel)
                btnsave = message.button(QMessageBox.Save)
                btnsave.setText('Да')
                btnclose = message.button(QMessageBox.Close)
                btnclose.setText('Нет')
                btncancel = message.button(QMessageBox.Cancel)
                btncancel.setText('Отмена')
                message.exec()
                if message.clickedButton() == btnclose:
                    event.accept()
                elif message.clickedButton() == btnsave:
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
if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window()
    wnd.showMaximized()
    sys.exit(app.exec())
