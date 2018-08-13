import sys
import serial
import time
import threading
import serial.tools.list_ports as serial_tools
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pista as base
from time import sleep

#---------------------------- VARIAVEIS GLOBAIS
tempo_sensor = {
'contador_do_timer' : [0],
'A' : [0],
'B' : [0],
'C' : [0],
'D' : [0],
'E' : [0]
}
etapas_da_pista = [
"Aguardando passagem por A.",
"Percorrendo trecho AB.",
"Percorrendo trecho BC.",
"Percorrendo trecho CD.",
"Percorrendo trecho DA.",
"Corrida finalizada."
]


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
        self.Ler()
        #print(aux1)
        #print("sensor")
        #print(self.sensor)
        #print("cronometro")
        #print(contador_do_timer)

    def Ler(self):
        tempo_sensor['contador_do_timer'][-1] = tempo_sensor['contador_do_timer'][0] + 0.133 # variave que aparece no lcd (sempre somar pois é o tempo pra ler todo mundo )
        aux1 =self.porta_serial.inWaiting() #serve pra ver quantos bytes tem na fila
        if aux1 != None : #se tiver byte pra ler
            self.sensor = ord(self.porta_serial.read(1)) #Lê qual sensor é
            if self.sensor == 49: #se for sensor 1 ( 1 = 49 em ascii)
                self.tempo_sensorA = self.porta_serial.read(1) # lê primeiro valor, High valor
                self.tempo_sensorA = (ord(self.tempo_sensorA) * 256) + ord(self.porta_serial.read(1)) # lê segundo valor (low) e transforma para o numero real que foi enviado antes de ser convertido
                tempo_sensor['A'][-1] = self.tempo_sensorA * 0.005; # calcula o tempo
                print("sensorA")
                print(tempo_sensor['A'][-1])
            if self.sensor == 50: # o ciclo se repete para outros sensores ( 2,3,4 e 5)
                self.tempo_sensorB = self.porta_serial.read(1)
                self.tempo_sensorB = (ord(self.tempo_sensorB) * 256) + ord(self.porta_serial.read(1))
                tempo_sensor['B'][-1] = self.tempo_sensorB * 0.005; # calcula o tempo
                print("sensorB")
                print(tempo_sensor['B'][-1])
            if self.sensor == 51:
                self.tempo_sensorC = self.porta_serial.read(1)
                self.tempo_sensorC = (ord(self.tempo_sensorC) * 256) + ord(self.porta_serial.read(1))
                tempo_sensor['C'][-1] = self.tempo_sensorC * 0.005; # calcula o tempo
                print("sensorC")
                print(tempo_sensor['C'][-1])
            if self.sensor == 52:
                self.tempo_sensorD = self.porta_serial.read(1)
                self.tempo_sensorD = (ord(self.tempo_sensorD) * 256) + ord(self.porta_serial.read(1))
                tempo_sensor['D'][-1] = self.tempo_sensorD * 0.005; # calcula o tempo
                print("sensorD")
                print(tempo_sensor['D'][-1])
            if self.sensor == 53:
                self.tempo_sensorE = self.porta_serial.read(1)
                self.tempo_sensorE = (ord(self.tempo_sensorE) * 256) + ord(self.porta_serial.read(1))
                tempo_sensor['E'][-1] = self.tempo_sensorE * 0.005; # calcula o tempo
                print(tempo_sensor['E'][-1])
                print("sensorE")

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
        print("conectado\n")
        # CHAMADAS DE SETUP
        self.setupUi(self)
        self.setup_signals_connections()
        # VARIAVEIS DE INICIALIZAÇÃO
        self.sensor_A_B = 0
        self.sensor_B_C = 0
        self.sensor_C_D = 0
        self.sensor_D_A = 0
        tempo_sensor = {
        'A' : [0],
        'B' : [0],
        'C' : [0],
        'D' : [0],
        'E' : [0]
        }
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
        self.meu_timer.timeout.connect(self.loop_thread)
        self.myThread = ThreadLeitura(self.conexao)

    def btn_clicado(self):
        self.reset()
        print("COMEÇOU")
        self.conectar()
        self.conexao.write(b'I')


        self.meu_timer.start(0.01)
        self.loop_thread()

    def btn_desclicado(self):
        self.myThread.close()
        self.conexao.close()
        self.meu_timer.stop()
        #self.salvar_arquivo_txt()
        self.reset()


    def reset(self):
        tempo_sensor = {
        'contador_do_timer' : [0],
        'A' : [0],
        'B' : [0],
        'C' : [0],
        'D' : [0],
        'E' : [0]
        }
        etapas_da_pista = [
        "Aguardando passagem por A.",
        "Percorrendo trecho AB.",
        "Percorrendo trecho BC.",
        "Percorrendo trecho CD.",
        "Percorrendo trecho DA.",
        "Corrida finalizada."
        ]

    def conectar(self):
        """Caso não esteja conectado, abre uma nova conexão.
        """
        print("esse é o certo, tira o parenteses do is_open")
        if not self.conexao.is_open:
            self.conexao = serial.Serial(self.port_name, self.baudrate, timeout=0.5)
            self.conexao.flushInput()
            self.conexao.flushOutput()

    def loop_thread(self):
        """ Incrementa o tempo nos LCDs disponíveis na interface.
        """
        self.myThread.start()
        self.valida_percurso()
        self.lcdNumber.display(int(tempo_sensor['contador_do_timer'][-1]))
        self.lcdNumber_2.display(self.sensor_A_B)
        self.lcdNumber_3.display(self.sensor_B_C)
        self.lcdNumber_4.display(self.sensor_C_D)
        self.lcdNumber_5.display(self.sensor_D_A)
        self.lcdNumber_6.display(0)


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
        # Exemplo de uso de indexação nos vetores em python
        # a = [0 1 2 3 4 5]
        # a[0] vale 0
        # a[-6] vale 0
        # a[1] vale 0
        # a[-1] vale 5
        # a[-2] vale 4
        # self.tempo_sensor['A'] = [0 0 0 0 0 12 13 14 15 15 15 15]
        # Se esta passando pelo sensor A e os outros ngm passou ainda
        # o programa desconsidera B se caso A estiver 0
        #  A    B    C   D
        #  0    0    0   0
        #  0    0    0   0
        #  15   20   0   0
        #  15   20   25  40
        if tempo_sensor['A'][-1] > 0:
            if tempo_sensor['B'][-1]>tempo_sensor['A'][-1] and tempo_sensor['C'][-1] == 0 and tempo_sensor['D'][-1] == 0:
                self.sensor_A_B = tempo_sensor['B'][-1] - tempo_sensor['A'][-1]
            if tempo_sensor['A'][-1] < tempo_sensor['B'][-1] and tempo_sensor['C'][-1] > tempo_sensor['B'][-1] and tempo_sensor['D'][-1] == 0:
                self.sensor_B_C = tempo_sensor['C'][-1] - tempo_sensor['B'][-1]
            if tempo_sensor['A'][-1] < tempo_sensor['D'][-1] and tempo_sensor['B'][-1] < tempo_sensor['C'][-1] and tempo_sensor['D'][-1] > tempo_sensor['C'][-1]:
                self.sensor_C_D = tempo_sensor['D'][-1] - tempo_sensor['C'][-1]
            if tempo_sensor['A'][-1] > tempo_sensor['D'][-1] and tempo_sensor['B'][-1] < tempo_sensor['C'][-1] and tempo_sensor['A'][-1] > tempo_sensor['B'][-1]:
                self.sensor_D_A = tempo_sensor['A'][-1] - tempo_sensor['D'][-1]

def main():
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    sys.exit(app.exec_())
