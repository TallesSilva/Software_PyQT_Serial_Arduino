'''
UNIVERSIDADE FEDERAL DE UBERLÂNDIA
PET Eng. Elétrica - PROGRAMA DE EDUCAÇÃO TUTORIAL
autores: Ítalo G S Fernandes
        github.com/italogsfernandes
        Talles Silva Rodrigues
        github.com/TallesSilva

Este código esta disponpivel no repositório do PET Eng. Elética: github.com/pet-eletrica/tur
Ele está diponivel para consulta e uso segundo a licensa MIT.

Descrição: Interface para controle e visualização do sistema de detecção de
passagem dos robôs seguidores de linha no Torneiro Universitário de Robôtica.

Abaixo explicações sobre o seu funcionamento:
'''
# primeira opção de software : chamar função e contabilizar tempos no fim da Corrida ( timer do python rodando e não deixar informações ate o fim da corrda)
# segunda opção : chamar e contabilizar a medida ( tempo quase real a medida que chega um valor )
# esse tempo_sensor é um dicionario com 5 chaves sendo elas A, B, C, D e E
# em cada chave do dicionario tem um vetor
# Onde vai ter as leituras brutas...
# por exemplo
# Se o arduino enviar:
# A10
# B11
# C11
# D12
# A10
# B15
# C14
# D13
# A11
# B17
# Os vetores vao ficar:
'''
self.tempo_sensor = {
'A' : [10, 10, 11],
'B' : [11, 15, 17],
'C' : [11, 14],
'D' : [12, 13],
'E' : []
}
'''
# Deu pra pegar a ideia?
# Isso so vai acumular enquanto estiver numa partida e depois vc reseta pra proxima,
# antes de resetar vc salvar num txt
# Seu PC tem no minumo uns 2GB de mémoria ram, nsao sei se da pra perceber mas é mta memoria
# cada variavel dessa devo ocupar no maximo uns 4 byte, vamo chutar 10
# Se for por 5 minutos a corrida, considerando 10ms de intervalo
# 5 sensores * 5 min * 60 s/min * 10 intervalos/s * 100 bytes = 1500 Kbytes
# E quando apertar o botão de finalizar, vc já salva tudo num txt
# E deixa preparado pra se alguem quiser falar que o software roubou
# Você fala: pega esse txt e faz as contas na mão. Pode conferir.

##### exemplo no final de um dado tempo:
'''
self.tempo_sensor = {
'A' : [0, 0, 0 , 1, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
'B' : [0, 0, 0 , 0, 0, 0, 0, 0, 0, 13, 14, 15, 16, 16, 16, 16, 16, 16],
'C' : [0, 0, 0 , 0, 0, 0, 0, 0, 0,  ],
'D' : [0, 0, 0 , 0, 0, 0, 0, 0, 0, ],
'E' : [0, 0, 0 , 0, 0, 0, 0, 0, 0, ]
}
'''

# ------------------------------------------------------------------------------
# Libraries
import sys
import serial
import time
import serial.tools.list_ports as serial_tools #list ade porta seriais
# ------------------------------------------------------------------------------
# PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pista as base
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
class ExampleApp(QMainWindow, base.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        # iniciando variaveis (propriedades)
        ##### Timers: #####
        self.meu_timer = QTimer()
        self.contador_do_timer = 0
        self.t = 0
        ##### Porta Serial #####
        self.port_name = None
        if self.port_name is None:
            self.port_name = ExampleApp.get_arduino_serial_port()
        self.baudrate = 115200
        ##### Leituras dos Sensores #####
        # Dicionario que armazenará os vetores de tempo de passagem em cada checkpoint
        self.tempo_sensor = {'A' : [0], 'B' : [0], 'C' : [0], 'D' : [0], 'E' : [0]}
        # indica qual sensor atualmente esta enviando dados para a interface
        self.ql_sensor_enviando = None
        # indica o tempo lido pelo sensor cidado a cima
        self.tempo_lido = ""
        ##### Valores referêntes aos tempos de passagem na pista do tur 2018 #####
        self.tempo_de_saida_do_sensor = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'Final': 0}
        self.tempo_A_B = 0
        self.tempo_B_C = 0
        self.tempo_C_D = 0
        self.tempo_D_A = 0
        self.etapas_da_pista = [
        "Aguardando passagem por A.",
        "Percorrendo trecho AB.",
        "Percorrendo trecho BC.",
        "Percorrendo trecho CD.",
        "Percorrendo trecho DA.",
        "Corrida finalizada."
        ]
        self.etapa_atual = self.etapas_da_pista[0]
        ##### Inicialização do PyQt #####
        #configuracoes do pyqt
        self.setupUi(self)
        self.setup_signals_connections()
        ##### configuracao adicional #####
        print("Codigo comecou a rodar")

    def setup_signals_connections(self):
        """Faz a conexão entre os elementos da interface e os metódos presentes
        nesta classe.
        """
        self.Iniciar.clicked.connect(self.btn_clicado)
        self.meu_timer.timeout.connect(self.tarefa_do_timer)
        self.Finalizar.clicked.connect(self.btn_desclicado)

    def btn_clicado(self):
        print("começou a contar")
        self.resetar_variaveis_de_leitura()
        self.conectar()
        self.meu_timer.start(10)

    def btn_desclicado(self):
        print("Parou de Contar")
        self.meu_timer.stop()
        self.conexao.close()
        #implementar criar txt
        self.resetar_variaveis_de_leitura() # posso ?

    def resetar_variaveis_de_leitura(self):
        # Dicionario que armazenará os vetores de tempo de passagem em cada checkpoint
        self.tempo_sensor = {'A' : [0], 'B' : [0], 'C' : [0], 'D' : [0], 'E' : [0]}
        # indica qual sensor atualmente esta enviando dados para a interface
        self.ql_sensor_enviando = None
        # indica o tempo lido pelo sensor cidado a cima
        self.tempo_lido = ""

    def tarefa_do_timer(self):
         self.enviar()
         # Como os dados chegam:
         # A11\nB23423\n

    def timer_do_lcd(self):
        """ Incrementa o tempo nos LCDs disponíveis na interface.
        """
        self.contador_do_timer = self.contador_do_timer + 1 # variave que aparece no lcd
        self.t = self.t + 1 # variavel auxiliar para fazer funcionar o if ali embaixo
        if (self.t > 10):
            self.receber()
            self.lineEdit_A.setText(self.tempo_A_B)
            self.lineEdit_B.setText(self.sensor_B_C)
            self.lineEdit_C.setText(self.sensor_C_D)
            self.lineEdit_D.setText(self.sensor_D_A)
            self.lineEdit_E.setText("sensor desabilitado")
            self.lcdNumber.display(self.contador_do_timer)

    def conectar(self):
        """Caso não esteja conectado, abre uma nova conexão.
        """
        if not self.conexao.isOpen():
            self.conexao = serial.Serial(self.port_name, self.baudrate, timeout=0.5)
            self.conexao.flushInput()
            self.conexao.flushOutput()

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

    def receber(self):
        """Chama um loop a cada novo pacote de dados disponível na porta serial.
        """
        if self.conexao.isOpen():
            if self.conexao.inWaiting() >= 3: # No minimo 3
                for n in range(self.conexao.inWaiting()):
                     #sempre que tiver no minimo 1 byte pra ler é chamado o loop de leitura
                    self.loop_de_leitura()

    def loop_de_leitura(self):
        """Este método é chamado sempre que existir no mínimo 1 valor para ser lido na porta serial
        O pacote está na seguinte forma: [Sensor][Multiplicador como string de um inteiro][Quebra de Linha]
        Exemplo: A11\n
                Sensor: 'A'
                Multiplicador: '11'
                Quebra de linha: '\n'
        Para a leitura primeiro se verifica se já é conhecido o sensor, caso não seja ele é lido.
        Após a leitura do sensor cada novo caracter é concatenado em uma string,
        esta string conterá o multiplicador que indica o tempo.
        Caso uma leitura seja igual a '\n' ou '\t' (quebra de linha) é reconhecido
        o final de um pacote.
        O tempo é convertido para inteiro e salvo em um vetor para aquele sensor.
        E a string de tempo e variavel q indica ql sensor são resetadas para
        possibilitar a leitura de um novo pacote.
        """
        valor_lido = self.conexao.read()
         # Os pacotes podem começar com A, B, C, D e E
        if self.ql_sensor_enviando is not None:
            if valor_lido == 'A' or valor_lido == 'B' or valor_lido == 'C' or valor_lido == 'D' or valor_lido == 'E':
                self.ql_sensor_enviando = valor_lido
        elif valor_lido != '\n' and valor_lido != '\t': # se não for o \n então vai acumulando numa string
            self.tempo_lido = self.tempo_lido + valor_lido
        else: # Se chegou o \n, converte a string pra inteiro e salva num dict
            self.tempo_sensor[self.ql_sensor_enviando].append(int(self.tempo_lido))
            self.verifica_se_eh_necessario_calcular_algo_nessa_nova_leitura_xablaus()
            self.tempo_lido = ""
            self.ql_sensor_enviando = None

    def verifica_se_eh_necessario_calcular_algo_nessa_nova_leitura_xablaus(self):
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
        if self.tempo_sensor['A'][-1] > 0:
            if self.tempo_sensor['B'][- 1] == 0 and self.tempo_sensor['C'][-1] == 0  and self.tempo_sensor['D'][-1] == 0:
                """O robô passou no 1º checkpoint (A) está percorrendo o trecho AB."""
                #O robô está na frente do caminho do sensor infravermelho em A
                print("Tempo de saida do sensor A: %f" %(self.tempo_sensor['A'][-1]))
                self.tempo_de_saida_do_sensor['A'] = self.tempo_sensor['A'][-1]
                self.etapa_atual = self.etapas_da_pista[1] # "Percorrendo trecho AB."

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


    def finalizar_corrida(self):
        print("A Corrida terminou, mostrar na interface fazer altas coisas, parar o timer...")

    def enviar(self):
        self.conexao.write("I")

def main():
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    sys.exit(app.exec_())
