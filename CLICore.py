import abc


class ScreenObject(abc.ABC):
    def __init__(self):
        pass
    @abc.abstractmethod
    def getPixel(self, x, y):
        pass

class CLICore:
    def __init__(self, defalt: str = ' '):
        # TODO: проверка версии и открытой CLI для способа очистки консоли
        # TODO: добавить поддержку изменения размера консоли"
        self.defalt = defalt
        self.xMax = 80
        self.yMax = 25
        self.layerList = []
        self.outputMatrix = [[None for _ in range(self.xMax)] for _ in range(self.yMax)]
        self.layerMatrix = [[None for _ in range(self.xMax)] for _ in range(self.yMax)]

    def updateScreen(self):
        self.clearScreen()

        for layer in self.layerList:
            for pixel in layer.getSpacedPixels():
                try:
                    if self.layerMatrix[pixel[1] + layer.yLocal][pixel[0] + layer.xLocal] is None:
                        self.layerMatrix[pixel[1] + layer.yLocal][pixel[0] + layer.xLocal] = layer
                except IndexError:
                    pass


        for x in range(self.xMax):
            for y in range(self.yMax):
                if self.layerMatrix[y][x] is not None:
                    xLocal, yLocal = self.layerMatrix[y][x].getPosition()
                    self.outputMatrix[y][x] = self.layerMatrix[y][x].\
                        screenObject.getPixel(x - xLocal, y - yLocal)
                else:
                    self.outputMatrix[y][x] = self.defalt

        for y in range(self.yMax):
            for x in range(self.xMax):
                print(self.outputMatrix[y][x], end='')
            print()
    def clearScreen(self):
        pass

    class Layer:
        def __init__(self, screenObject: ScreenObject, xLocal: int = 0, yLocal: int = 0):
            self.xLocal = xLocal
            self.yLocal = yLocal
            self.screenObject = screenObject

        def getSpacedPixels(self):
            return self.screenObject.getSpacedPixels()

        def getPosition(self):
            return self.xLocal, self.yLocal

    def addLayer(self, *screen_objects, x, y):
        for screenObject in screen_objects:
            if not isinstance(screenObject, ScreenObject):
                raise TypeError
            self.layerList.append(CLICore.Layer(screenObject, x, y))


class SelectedText(ScreenObject):
    def __init__(self, text, isSelected: bool = False, selectChar: str = '#'):
        self.selected = isSelected
        self.xSize = 10
        self.ySize = 1
        self.setText(text)
        self.selectChar = selectChar

    def setText(self, text):
        self.text = text
        self.updateSpaceSize()

    def updateSpaceSize(self):
        self.xSize = len(self.text)
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
                return self.text[x-1]
        else:
            return self.text[x]

    def getSpacedPixels(self):
        return [(x, y) for x in range(self.xSize) for y in range(self.ySize)]


if __name__ == '__main__':
    UI = CLICore()
    UI.addLayer(SelectedText("Hello1", isSelected=False), x=10, y=11)
    UI.addLayer(SelectedText("Hello2", isSelected=True), x=13, y=11)
    UI.addLayer(SelectedText("Hello3", isSelected=False), x=17, y=13)
    UI.addLayer(SelectedText("Hello4", isSelected=True), x=19, y=13)
    UI.updateScreen()


