import abc
import os
import noise


class ScreenObject(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def getPixel(self, x, y):
        pass

    @abc.abstractmethod
    def getSpacedPixels(self):
        pass

class CLICore:
    def __init__(self, background: str = ' '):
        # TODO: проверка версии и открытой CLI для способа очистки консоли
        # TODO: добавить поддержку изменения размера консоли"
        self.background = background
        self.xMax = 80
        self.yMax = 25
        self.layerList = []
        self.outputMatrix = [[None for _ in range(self.xMax)] for _ in range(self.yMax)]
        self.layerMatrix: list[list[CLICore.Layer]] = [[None for _ in range(self.xMax)] for _ in range(self.yMax)]

    def updateScreen(self):
        self.clearScreen()

        # TODO: добавить поддержку динамического позиционирования

        # обновление матрицы layerMatrix
        for layer in self.layerList:
            for pixel in layer.getSpacedPixels():
                try:
                    xLocal, yLocal = layer.getPosition()
                    if self.layerMatrix[pixel[1] + yLocal][pixel[0] + xLocal] is None:
                        self.layerMatrix[pixel[1] + layer.yLocal][pixel[0] + layer.xLocal] = layer
                except IndexError:
                    pass

        for x in range(self.xMax):
            for y in range(self.yMax):
                if self.layerMatrix[y][x] is not None:
                    xLocal, yLocal = self.layerMatrix[y][x].getPosition()
                    self.outputMatrix[y][x] = self.layerMatrix[y][x].\
                        obj.getPixel(x - xLocal, y - yLocal)
                else:
                    self.outputMatrix[y][x] = self.background


        for y in range(self.yMax):
            for x in range(self.xMax):
                print(self.outputMatrix[y][x], end='')
            print()
    def clearScreen(self):
        os.system('cls')

    class Layer:
        def __init__(self, screenObject: ScreenObject, xLocal: int = 0, yLocal: int = 0):
            self.xLocal = xLocal
            self.yLocal = yLocal
            self.obj = screenObject

        def getSpacedPixels(self):
            return self.obj.getSpacedPixels()

        def getPosition(self):
            return self.xLocal, self.yLocal


    def addLayer(self, screen_object, x: int, y: int):
        if not isinstance(screen_object, ScreenObject):
            raise TypeError
        self.layerList.append(CLICore.Layer(screen_object, x, y))




class SelectedText(ScreenObject):
    def __init__(self, text, isSelected: bool = False, selectChar: str = '#', backgroundChar: str = ' '):
        if len(selectChar) != 1 or len(backgroundChar) != 1:
            raise ValueError
        self.selected = isSelected
        self.xSize = 10
        self.ySize = 1
        self.setText(text)
        self.selectChar = selectChar
        self.backgroundChar = backgroundChar

    def setText(self, text):
        self.text = text
        self.updateSpaceSize()

    def updateSpaceSize(self):
        self.xSize = len(max(self.text.split('\n'), key=len))
        #размер зависит от количества строчек в переменной text
        self.ySize = self.text.count('\n') + 1
        if self.selected:
            self.ySize += 2
            self.xSize += 2
    def setSelected(self, select: bool = True):
        self.selected = select
        self.updateSpaceSize()

    def getSelected(self):
        return self.selected

    def getPixel(self, x, y):
        # Возвращает символ в этой позиции
        if self.selected:
            if x == 0 or x == self.xSize-1 or y == 0 or y == self.ySize-1:
                return self.selectChar
            else:
                line = self.text.split('\n')[y-1]
                if len(line) <= x-1:
                    return self.backgroundChar
                return self.text.split('\n')[y-1][x-1]
        else:
            return self.text[x]

    def getSpacedPixels(self):
        return [(x, y) for x in range(self.xSize) for y in range(self.ySize)]

    def getSize(self):
        return self.xSize, self.ySize


# список для адаптивного отображения элементов последовательно
class ObjectList(ScreenObject):
    class ListElement:
        def __init__(self, obj):
            self.obj = obj
            self.xLocal = 0
            self.yLocal = 0
    def __init__(self, *objects, backgroundChar: str = ' '):
        self.xSize = 0
        self.ySize = 0
        self.elements = [] # список элементов
        for obj in objects:
            self.append(obj)
        self.backgroundChar = backgroundChar
    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, index):
        return self.elements[index]

    def __setitem__(self, index, value):
        self.elements[index] = value

    def __delitem__(self, index):
        del self.elements[index]

    def __iter__(self):
        return iter(self.elements)

    def append(self, other, index=None):
        if index is not None:
            self.elements.insert(index, ObjectList.ListElement(other))
        else:
            self.elements.append(ObjectList.ListElement(other))
        self.rebuild()
        return self.elements

    def rebuild(self): # пересборка списка объектов с указанием их новых позиций
        i = 0
        for elem in self.elements:
            elem.xLocal = 0
            elem.yLocal = i
            i += elem.obj.getSize()[1]
        self.updateSize()
    def updateSize(self):
        self.xSize = max([elem.obj.getSize()[0] for elem in self.elements])
        self.ySize = sum([elem.obj.getSize()[1] for elem in self.elements])

    def getSpacedPixels(self):
        return [(i[0] + elem.xLocal, i[1] + elem.yLocal) for elem in self.elements for i in elem.obj.getSpacedPixels()]

    def getPixel(self, x, y):
        for elem in self.elements:
            if x >= elem.xLocal and x < elem.xLocal + elem.obj.getSize()[0] and y >= elem.yLocal and y < elem.yLocal + elem.obj.getSize()[1]:
                return elem.obj.getPixel(x - elem.xLocal, y - elem.yLocal)
        return self.backgroundChar



