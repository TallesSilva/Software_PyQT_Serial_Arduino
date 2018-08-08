import sys
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
        self.meu_timer = QTimer()
        self.contador_do_timer = 0
        #configuracoes do pyqt
        self.setupUi(self)
        self.setup_signals_connections()
        #configuracao adicional
        print("Codigo comecou a rodar")

    def setup_signals_connections(self):
        self.Iniciar.clicked.connect(self.btn_clicado)
        self.meu_timer.timeout.connect(self.tarefa_do_timer)
        self.Finalizar.clicked.connect(self.btn_desclicado)

    def btn_clicado(self):
        print("começou a contar")
        self.meu_timer.start(10)

    def btn_desclicado(self):
        print("Parou de Contar")
        self.meu_timer.stop()


    def tarefa_do_timer(self):
         self.contador_do_timer = self.contador_do_timer + 1
         self.lineEdit_A.setText("Aqui")
         self.lineEdit_B.setText("eu")
         self.lineEdit_C.setText("mostro")
         self.lineEdit_D.setText("as")
         self.lineEdit_E.setText("Variaveis")
         self.lcdNumber.display(self.contador_do_timer)

def main():
    app = QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
    sys.exit(app.exec_())
