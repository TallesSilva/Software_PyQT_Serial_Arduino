import sys
import serial
import time
import threading
import serial.tools.list_ports as serial_tools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from scipy.ndimage import imread


import pista as base
from time import sleep

#---------------------------- VARIAVEIS GLOBAIS
global tempo_sensor
tempo_sensor = {
'contador_do_timer' : [0],
'A' : [0],
'B' : [0],
'C' : [0],
'D' : [0],
'E' : [0]
}
global tempo_sensor_backup
tempo_sensor_backup = tempo_sensor
# app = QtWidgets.QApplication(sys.argv)
#
# input_image = imread(pista.jpg)
# height, width, channels = input_image.shape
# bytesPerLine = channels * width
# qImg = QtGui.QImage(input_image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
# pixmap01 = QtGui.QPixmap.fromImage(qImg)
# pixmap_image = QtGui.QPixmap(pixmap01)
# label_imageDisplay = QtWidgets.QLabel()
# label_imageDisplay.setPixmap(pixmap_image)
# label_imageDisplay.setAlignment(QtCore.Qt.AlignCenter)
# label_imageDisplay.setScaledContents(True)
# label_imageDisplay.setMinimumSize(1,1)
# label_imageDisplay.show()
# sys.exit(app.exec_())

# referencia: https://nikolak.com/pyqt-threading-tutorial/
class ThreadLeitura(QThread):
    def __init__(self, conecao_com_a_porta):
        QThread.__init__(self)
        self.porta_serial = conecao_com_a_porta
        self.sensor = 0
        self.tempo_sensorA = 0
        self.tempo_sensorB = 0
        self.tempo_sensorC = 0
        self.tempo_sensorD = 0
        self.tempo_sensorE = 0

    def __del__(self):
        self.wait()

    def run(self):
        #tempo_sensor['contador_do_timer'][-1] = tempo_sensor['contador_do_timer'][0] + 0.100 # variave que aparece no lcd (sempre somar pois é o tempo pra ler todo mundo )''
        print("passou 100")

class ExampleApp(QMainWindow, base.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        # TIMER
        self.meu_timer = QTimer()
        # CONEXAO SERIAL
        self.port = None
        if self.port is None:
            self.port = ExampleApp.get_arduino_serial_port()
        self.baudrate = 115200
        self.conexao = serial.Serial(self.port, self.baudrate)
        self.conexao.write(b'I')
        print("conectado\n")
        # CHAMADAS DE SETUP
        self.setupUi(self)
        self.setup_signals_connections()
        # VARIAVEIS DE INICIALIZAÇÃO
        self.sensor_A_B = 0
        self.sensor_B_C = 0
        self.sensor_C_D = 0
        self.sensor_D_A = 0
        print("Codigo comecou a rodar")

    @staticmethod
    def get_arduino_serial_port():
        """
        Tries to found a serial port compatible.
        If there is only one serial port available, return this one.
        Otherwise it will verify the manufacturer of all serial ports
        and compares with the manufacturer defined in the ArduinoConstants.
        This method will return the first match.
        If no one has found, it will return a empty string.
        :return: Serial Port String
        """
        serial_ports = serial_tools.comports()
        if len(serial_ports) == 0:
            return ""
        if len(serial_ports) == 1:
            return serial_ports[0].device
        for serial_port_found in serial_ports:
            if serial_port_found.manufacturer == 'Arduino (www.arduino.cc)':
                return serial_port_found.device
        return ""

    def setup_signals_connections(self):
        self.Iniciar.clicked.connect(self.btn_clicado)
        self.Finalizar.clicked.connect(self.btn_desclicado)
        self.meu_timer.timeout.connect(self.Loop)
        self.myThread = ThreadLeitura(self.conexao)

    def btn_clicado(self):
        self.reset()
        self.conectar()
        self.myThread.start()
        self.meu_timer.start(100)


    def Loop(self):
        print("oi")
        self.Requisitar_Ler()
        print("aqui5")
        self.valida_percurso()
        print("aqui6")
        self.Printar_display()
        print("aqui7")

    def btn_desclicado(self):
        self.conexao.write(b'A')
        self.meu_timer.stop()
        # self.salvar_arquivo_txt()
        self.reset()

    def reset(self):
        global tempo_sensor, tempo_sensor_backup
        self.sensor = 0
        self.tempo_sensorA = 0
        self.tempo_sensorB = 0
        self.tempo_sensorC = 0
        self.tempo_sensorD = 0
        self.tempo_sensorE = 0
        self.sensor_A_B = 0
        self.sensor_B_C = 0
        self.sensor_C_D = 0
        self.sensor_D_A = 0
        tempo_sensor['contador_do_timer'][-1] = 0
        tempo_sensor['A'][-1] = 0
        tempo_sensor['B'][-1] = 0
        tempo_sensor['C'][-1] = 0
        tempo_sensor['D'][-1] = 0

    def conectar(self):
        """Caso não esteja conectado, abre uma nova conexão.
        """
        if not self.conexao.is_open:
            self.conexao = serial.Serial(self.port_name, self.baudrate, timeout=0.5)
            self.conexao.flushInput()
            self.conexao.flushOutput()

    def Requisitar_Ler(self):
        self.conexao.write(b'R')
        aux1 =self.conexao.inWaiting() #serve pra ver quantos bytes tem na fila
        if aux1 != None :
            print("aqui1") #se tiver byte pra ler
            self.sensor = ord(self.conexao.read(1)) #Lê qual sensor é
            if self.sensor == 49: #se for sensor 1 ( 1 = 49 em ascii)
                self.tempo_sensorA = ord(self.conexao.read(1)) # lê primeiro valor, High valor
                self.tempo_sensorA = (ord(self.tempo_sensorA) * 256) + ord(self.conexao.read(1)) # lê segundo valor (low) e transforma para o numero real que foi enviado antes de ser convertido
                tempo_sensor['A'][-1] = self.tempo_sensorA * 0.005; # calcula o tempo
                print("sensorA")
                print(tempo_sensor['A'][-1])
            # if self.sensor == 50:
            #     self.tempo_sensorB = ord(self.conexao.read(1)) # lê primeiro valor, High valor
            #     self.tempo_sensorB = (ord(self.tempo_sensorB) * 256) + ord(self.conexao.read(1)) # lê segundo valor (low) e transforma para o numero real que foi enviado antes de ser convertido
            #     tempo_sensor['B'][-1] = self.tempo_sensorB * 0.005; # calcula o tempo
            #     print("sensorB")
            #     print(tempo_sensor['B'][-1])
            # if self.sensor == 51:
            #     self.tempo_sensorC = self.porta_serial.read(1)
            #     self.tempo_sensorC = (ord(self.tempo_sensorC) * 256) + ord(self.porta_serial.read(1))
            #     tempo_sensor['C'][-1] = self.tempo_sensorC * 0.005; # calcula o tempo
            #     print("sensorC")
            #     print(tempo_sensor['C'][-1])
            # if self.sensor == 52:
            #     self.tempo_sensorD = self.porta_serial.read(1)
            #     self.tempo_sensorD = (ord(self.tempo_sensorD) * 256) + ord(self.porta_serial.read(1))
            #     tempo_sensor['D'][-1] = self.tempo_sensorD * 0.005; # calcula o tempo
            #     print("sensorD")
            #     print(tempo_sensor['D'][-1])
            # if self.sensor == 53:
            #     self.tempo_sensorE = self.porta_serial.read(1)
            #     self.tempo_sensorE = (ord(self.tempo_sensorE) * 256) + ord(self.porta_serial.read(1))
            #     tempo_sensor['E'][-1] = self.tempo_sensorE * 0.005; # calcula o tempo
            #     print(tempo_sensor['E'][-1])
            #     print("sensorE")

    def valida_percurso(self):
        """Verifica o novo valor lido e compara para saber se houve ou está
        ocorrendo a passagem por um checkpoint.
        Defeitos Conhecidos: O valor oscila enquanto o robô esta passando ( a leitura é feita em 0,5s, não da pra perceber)
                            e se estabiliza robô o carrinho terminar de passar.
        Ele está implementado através de uma serie de condicionais que são
        especificas para a pista do TUR 2018 e o modo como os sensores estão
        dispostos.
        Esta não é a melhor implementação, existem melhores. Mas através de todos
        esses 'if' e 'else' é possível determinar onde o robô está.
        """
        if tempo_sensor['A'][-1] > 0:
            if tempo_sensor['B'][-1]>tempo_sensor['A'][-1] and tempo_sensor['C'][-1] == 0 and tempo_sensor['D'][-1] == 0:
                self.sensor_A_B = tempo_sensor['B'][-1] - tempo_sensor['A'][-1]
            if tempo_sensor['A'][-1] < tempo_sensor['B'][-1] and tempo_sensor['C'][-1] > tempo_sensor['B'][-1] and tempo_sensor['D'][-1] == 0:
                self.sensor_B_C = tempo_sensor['C'][-1] - tempo_sensor['B'][-1]
            if tempo_sensor['A'][-1] < tempo_sensor['D'][-1] and tempo_sensor['B'][-1] < tempo_sensor['C'][-1] and tempo_sensor['D'][-1] > tempo_sensor['C'][-1]:
                self.sensor_C_D = tempo_sensor['D'][-1] - tempo_sensor['C'][-1]
            if tempo_sensor['A'][-1] > tempo_sensor['D'][-1] and tempo_sensor['B'][-1] < tempo_sensor['C'][-1] and tempo_sensor['A'][-1] > tempo_sensor['B'][-1]:
                self.sensor_D_A = tempo_sensor['A'][-1] - tempo_sensor['D'][-1]

    def Printar_display(self):
        """ Incrementa o tempo nos LCDs disponíveis na interface.
        """
        self.lcdNumber.display(int(tempo_sensor['contador_do_timer'][-1]))
        self.lcdNumber_2.display(self.sensor_A_B)
        self.lcdNumber_3.display(self.sensor_B_C)
        self.lcdNumber_4.display(self.sensor_C_D)
        self.lcdNumber_5.display(self.sensor_D_A)
        self.lcdNumber_6.display(0)

def main():
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    sys.exit(app.exec_())
