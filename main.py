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
        self.meu_timer = QTimer()
        self.port = None
        if self.port is None:
            self.port = ExampleApp.get_arduino_serial_port()
        self.baudrate = 115200
        self.conexao = serial.Serial(self.port, self.baudrate)
        print("conectado\n")
        self.setupUi(self)
        self.setup_signals_connections()
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
        self.lcdNumber.display(int(tempo_sensor['contador_do_timer'][-1]))
        self.lcdNumber_2.display(tempo_sensor['A'][-1])
        self.lcdNumber_3.display(tempo_sensor['B'][-1])
        self.lcdNumber_4.display(tempo_sensor['C'][-1])
        self.lcdNumber_5.display(tempo_sensor['D'][-1])
        self.lcdNumber_6.display(tempo_sensor['E'][-1])

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
            if tempo_sensor['B'][- 1] == 0 and tempo_sensor['C'][-1] == 0  and tempo_sensor['D'][-1] == 0:
                """O robô passou no 1º checkpoint (A) está percorrendo o trecho AB."""
                #O robô está na frente do caminho do sensor infravermelho em A
                print("Tempo de saida do sensor A: %f" %(tempo_sensor['A'][-1]))
                self.tempo_de_saida_do_sensor['A'] = stempo_sensor['A'][-1]
                self.etapa_atual = etapas_da_pista[1] # "Percorrendo trecho AB."


            elif self.tempo_sensor['B'][-1] >= self.tempo_de_saida_do_sensor['A']:
                if self.tempo_sensor['C'][-1] == 0  and self.tempo_sensor['D'][-1] == 0:
                    """O robô passou no 2º checkpoint (B) está percorrendo o trecho BC."""
                    #O robô está na frente do caminho do sensor infravermelho em B
                    print("Tempo de saida do sensor B: %f" %(self.tempo_sensor['B'][-1]))
                    self.tempo_de_saida_do_sensor['B'] = self.tempo_sensor['B'][-1]
                    self.tempo_A_B = self.tempo_de_saida_do_sensor['B'] - self.tempo_de_saida_do_sensor['A']
                    self.etapa_atual = self.etapas_da_pista[2] # "Percorrendo trecho BC."

                elif self.tempo_sensor['C'][-1] >= self.tempo_de_saida_do_sensor['B']:
                    if self.tempo_sensor['D'][-1] == 0:
                        """O robô passou no 3º checkpoint (C) está percorrendo o trecho CD."""
                        #O robô está na frente do caminho do sensor infravermelho em C
                        print("Tempo de saida do sensor C: %f" %(self.tempo_sensor['C'][-1]))
                        self.tempo_de_saida_do_sensor['C'] = self.tempo_sensor['C'][-1]
                        self.tempo_B_C = self.tempo_de_saida_do_sensor['C'] - self.tempo_de_saida_do_sensor['B']
                        self.etapa_atual = self.etapas_da_pista[3] # "Percorrendo trecho CD."

                    elif self.tempo_sensor['D'][-1] >= self.tempo_de_saida_do_sensor['C']:
                        #  A    B    C   D
                        #  0    0    0   0 (0,5s)
                        #  0    0    0   0 (1,0s)
                        #  15   20   0   0 (1,5s)
                        #  15   20   25  0 (2,0s)
                        #  50   20   25  40 (2,5s)
                        # para evitar problema trocou o self.tempo_sensor['A'][-1] por  self.tempo_sensor['A'][-2]
                        if self.tempo_sensor['A'][-2] == self.tempo_de_saida_do_sensor['A']:
                            """O robô passou no 4º checkpoint (D) está percorrendo o trecho DA."""
                            #O robô está na frente do caminho do sensor infravermelho em D
                            print("Tempo de saida do sensor D: %f" %(self.tempo_sensor['D'][-1]))
                            self.tempo_de_saida_do_sensor['D'] = self.tempo_sensor['D'][-1]
                            self.tempo_C_D = self.tempo_de_saida_do_sensor['D'] - self.tempo_de_saida_do_sensor['C']
                            self.etapa_atual = self.etapas_da_pista[4] # "Percorrendo trecho DA."
                        # Se caso a pista tiver sensor E, implementar mais um if do sensor E
                        elif self.tempo_sensor['A'][-1] >= self.tempo_de_saida_do_sensor['D']:
                            """O robô passou no 5º checkpoint (A) está finalizando a corrida."""
                            #O robô está na frente do caminho do sensor infravermelho em A
                            print("Tempo de finalizacao: %f" %(self.tempo_sensor['A'][-1]))
                            self.tempo_de_saida_do_sensor['Final'] = self.tempo_sensor['A'][-1]
                            self.tempo_D_A = self.tempo_de_saida_do_sensor['Final'] - self.tempo_de_saida_do_sensor['D']
                            self.etapa_atual = self.etapas_da_pista[5] # "Corrida finalizada."
                            print("""ACABOU!!
                            É TETRA!!
                            É TETRA!!
                            ACABOU!!""")
                            #NOTE: Tem um potencial problema aqui...
                            #NOTE: Esse 'if' detecta qnd o "bico" do carro obstrui o sensor
                            #NOTE: Ele não espera a leitura se acomodar...
                            #NOTE: Com isso carrinhos mais compridos tem vantagem
                            #NOTE: Pois o tempo de inicio se dará ao carrinho passar a
                            #NOTE: bunda pelo sensor na largada e o tempo de fim
                            #NOTE: vai ser dado quando ele encostar o bico...
                            #NOTE: Uma solução é finalizar a corrida com um botão e recalcular o tempo de chegada para ser o tempo da bunda tbm
                            #NOTE:
                            #NOTE: Outra solicação é detectar a passagem somente do bico do carrinho.
                            #NOTE:      A segunda solução tem o problema de depender do tempo de comunicação RF (500ms)
                            #NOTE:      Mas seria necessario alterar no código do RF  para q ele avise assim que ocorrer o primeiro toque e trave nesta leitura.
                            #NOTE:      Ou seja ele leria 0,0,0,15,15,15,15 ao inves de ler 0,0,0,15,16,17,17,17,17....
                            #NOTE: posso alterar a leitura, pra que ela aconteça quando o sinal mudar de 1 -> 0 e assim salvar o tempo só uma vez e envia só um valor
                            #NOTE:      Faz isso, fica melhor.
                            #NOTE:      E coloca uma comando que o arduino pode enviar pro sensor, pra desbloquear essa leitura.
                            #NOTE:      COMANDO: INICIAR
                            #NOTE:      LEITURAS: 0, 0, 0, 0, 0, 15, 15, 15, 15, 15.
                            #NOTE:      COMANDO: DESBLOQUEAR SENSOR A
                            #NOTE:      LEITURAS: 0,0 ,0 ,0 ,0, 15, 15, 15, 15, 15, 67, 67, 67 ,67
                            #NOTE:      Entendeu a necessidade?
                            #NOTE:      essa parte do desbloquear nao, se eu alterar a forma de leitura já consigo resolver isso, não ?
                            #NOTE:      é pq o sensor A precisa ler 2 vezes
                            #NOTE:      Atende minha ligação desgraça
                            #NOTE:      Se ele não desbloquear a leitura, ele vai ficar travado na primeira vez.
                            #NOTE: também podemos so deixar como esta e colocar no edital que vai ser desse jeito.
                            #NOTE: O problema é se não colocar pode vir alguem falando dps que a detecção favorecia
                            #NOTE:     os carrinhos mais compridos e que nao foi justo...
                            #self.finalizar_corrida()
                        else:
                            print("""ERRO!!
                            Opções:
                            1. O tempo de passagem em A foi alterado antes do robô passar em D.
                            2.
                            Ocorreu uma segunda passagem pelo sensor A em um tempo menor do que a passagem pelo sensor D.
                            Por favor verifique.""")
                    else:
                        print("""ERRO!!
                        Opções:
                        1. O tempo em D não valeu 0 durante a passagem por C.
                        2. Ocorreu uma passagem pelo sensor D em um tempo menor do que a passagem pelo sensor C.
                        Por favor verifique.""")
                else:
                    print("""ERRO!!
                    Opções:
                    1. O tempo em C ou D não valeu 0 durante a passagem por B.
                    2. Ocorreu uma passagem pelo sensor C em um tempo menor do que a passagem pelo sensor B.
                    Por favor verifique.""")
            else:
                print("""ERRO!!
                Opções:
                1. O tempo em B, C ou D não valeu 0 durante a passagem por A.
                2. Ocorreu uma passagem pelo sensor B em um tempo menor do que a passagem pelo sensor A.
                Por favor verifique.""")
        else:
            print("Ainda não ocorreu a passagem pelo sensor A... Tempo lido em A = 0")


def main():
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    sys.exit(app.exec_())
