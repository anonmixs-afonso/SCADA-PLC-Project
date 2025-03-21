from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, grafPopup, HistGraphPopup, MotorPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep 
from datetime import datetime
from client import Clientinit
import time
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from creategraph import TempGraphApp
from threading import Lock
import matplotlib.pyplot as plt

class MainWidget(BoxLayout):
    """
    Widget principal da aplicação
    """
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    button_on = BooleanProperty(False)
    _plot_timer = None  # Variable to keep track of the plot timer
    _time_window = 10  # We will display data for the last 10 seconds
    _temperature_data = []  # Stores the temperature data for the last 10 seconds
    _temperature_times = []  # Stores the timestamps for the last 10 seconds

    #def __init__(self, modbus_addrs=None, scan_time=5000, server_ip='10.15.30.183', server_port=502, **kwargs):
    def __init__(self, modbus_addrs=None, scan_time=5000, server_ip='127.0.0.1', server_port=1502,**kwargs):

        super().__init__(**kwargs)
        
        # Store the passed values as instance variables
        self._modbus_addrs = modbus_addrs or {        }
        self._scan_time = scan_time
        self._serverIP = server_ip
        self._serverPort = server_port
        self._lock = Lock()
        self._lock.acquire()
        self.modclient = ModbusClient(host='127.0.0.1', port=1502)
        #self.modclient = ModbusClient(host='10.15.30.183', port=502)

        self.data = Clientinit.ihmcli(self)
        self._lock.release()

        self._modbusPopup = ModbusPopup(self._serverIP, self._serverPort)
        self._motorPopup = MotorPopup(2,600,600,100,1)
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = Clientinit(host=self._serverIP, port=self._serverPort)
        self._grafPopup = grafPopup()
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        self._hgraph = HistGraphPopup(tags=self._tags)

        for key, value in self._modbus_addrs.items():
            self._tags[key] = {'addr': value}

    def startDataRead(self, ip, port):
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort

        try:
            Window.set_system_cursor("wait")
            modbusClient = Clientinit(self._serverIP, self._serverPort)
            data = modbusClient.ihmcli()
            Window.set_system_cursor("arrow")

            self._updateThread = Thread(target=self.updater)
            self._updateThread.start()

            #self._statusThread = Thread(target=self.update_data, args=(self.data, self.modclient), daemon=True)
            #self._statusThread.start()

            self.ids.img_con.source = 'imgs/conectado.png'
            self._modbusPopup.dismiss()

        except Exception as e:
            print("Erro:", e.args)

    def updater(self):
        try:
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                sleep(self._scan_time / 1000)
        except Exception as e:
            print("Erro:", e.args)

    def readData(self):
        '''
        Método para leitura dos dados pelo protocolo Modbus
        '''
        for key, value in self._tags.items():
            self._lock.acquire()
            self._meas['values'][key] = self._modbusClient.readindict()[key]
            self._lock.release()

    def update_data(self, data):
        while True:
            time.sleep(1)
           
            self.new_data = self._modbusClient.readindict()
            
            for key in self.new_data:
                self.data[key] = self.new_data[key]

    def updateGUI(self):
        '''
        Atualização dos labels
        '''
        self.ids.statuspid.text = str(self._meas['values'].get('statuspid', 'N/A'))
        for key, value in self._tags.items():
            self.ids[key].text = f"{self._meas['values'][key]:.2f}"
        
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0], self._meas['values']['temperaturasa'] / 100 * self.ids.termometro.size[1])

        self.ids.lb_temp1.size = (self.ids.lb_temp1.size[0], self._meas['values']['temperaturatit01'] / 100 * self.ids.termometro1.size[1])

    def plot_graph(self):
        '''
        Chama a função de atualização do gráfico quando o botão é clicado.
        Inicia a atualização periódica do gráfico.
        '''
        if self._plot_timer:  # If the plot is already updating, stop it
            self.stop_plot()  # Stop the current plot update
        else:
            self.start_plot()  # Otherwise, start updating the plot

    def start_plot(self):
        '''
        Inicia a atualização periódica do gráfico.
        '''
        self._plot_timer = Clock.schedule_interval(self.update_plot, 1)  # Update every 1 second

    def stop_plot(self):
        '''
        Para a atualização do gráfico.
        '''
        if self._plot_timer:
            self._plot_timer.cancel()  # Stop the periodic update
            self._plot_timer = None
        plt.close()

    def update_plot(self, dt=None):
        '''
        Atualiza o gráfico de temperatura com novos dados.
        Chamado periodicamente pelo Clock.
        '''
        #self.readData()  # Refresh data
        self.plot_temperature_data()  # Plot updated temperature data

    def plot_temperature_data(self):
        '''
        Filtra os dados de temperatura e exibe um gráfico com o valor de cada chave
        que começa com "temperatura".
        '''
        # Filter the keys that start with "temperatura"
        temperature_keys = [key for key in self._meas['values'].keys() if key.startswith('temperatura')]

        # Debugging: Print the filtered temperature keys
        print("Temperature keys:", temperature_keys)

        # If there are any temperature keys, plot the graph
        if temperature_keys:
            # Record the current time for plotting
            current_time = datetime.now()

            # Prepare data for the plot
            self._temperature_times.append(current_time)  # Append the current time
            
            # Initialize an empty list to hold temperature values for the current time
            current_temp_data = []
            
            for key in temperature_keys:
                # Append temperature value (default to 0 if missing)
                current_temp_data.append(self._meas['values'].get(key, 0))

            # Append the list of temperature values to the temperature data list
            self._temperature_data.append(current_temp_data)

            # Limit the data to the most recent 10 seconds (for rolling window)
            if len(self._temperature_times) > self._time_window:
                self._temperature_times.pop(0)  # Remove the oldest time point
                self._temperature_data.pop(0)  # Remove the oldest temperature data

            # Create the graph
            plt.clf()  # Clear the current plot to refresh with new data

            # Plot the data for each temperature key
            for i, temp_key in enumerate(temperature_keys):
                temp_values = [data[i] for data in self._temperature_data]
                plt.plot(self._temperature_times, temp_values, marker='o', label=f'{temp_key}')

            plt.title("Temperatura ao longo do tempo")
            plt.xlabel("Tempo")
            plt.ylabel("Valor da Temperatura (ºC)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()

            # Display the graph
            plt.draw()  # Redraw the plot with updated data
            plt.pause(0.1)  # Small pause to ensure the plot updates properly
        else:
            print("Nenhum dado de temperatura encontrado.")

    def ToggleButtonScroll(self, button):
        self._lock.acquire()
        currentvalue = Clientinit.readbitholding(self, addr=1328)
        self._lock.release()
        if(currentvalue[14] == 0): #scroll acionado
            button.background_color = 1, 1, 1, 1  # Cor branca quando "ligado"
            
        else:
            button.background_color = 0.3, 0.3, 0.3, 1  # Cor cinza escuro quando "desligado"
        self.button_on = not self.button_on  # Alterna o estado do botão

    
    def ToggleButtonHermetico(self, button):
        self._lock.acquire()
        currentvalue = Clientinit.readbitholding(self, addr=1328)
        self._lock.release()
        if(currentvalue[14] == 1): #hermetico adionado
            button.background_color = 1, 1, 1, 1  
        else:
            button.background_color = 0.3, 0.3, 0.3, 1 
        self.button_on = not self.button_on  # Alterna o estado do botão

    def AcionaMotor(self, inv, vel, rampaace, rampades, partida, **kwargs):
        '''
        Obter dados e acionar motor
        '''
        self.ids.inv = int(inv)
        self.ids.vel = int(vel)
        self.ids.rampaace = int(rampaace)
        self.ids.rampades = int(rampades)
        self.ids.partida = int(partida)
        
        Clientinit.writevalue(self, addr=int(1324), val=self.ids.inv)
        Clientinit.writevalue(self, addr=int(1313), val=self.ids.vel)
        Clientinit.writevalue(self, addr=int(1314), val=self.ids.rampaace)
        Clientinit.writevalue(self, addr=int(1315), val=self.ids.rampades)
        Clientinit.writevalue(self, addr=int(1312), val=self.ids.partida)

    def AcionaScroll(self, **kwargs):
        '''
        Obter dados e acionar motor
        '''
        self._lock.acquire()
        currentvalue = Clientinit.readbitholding(self, addr=1328)
        self._lock.release()
        currentvalue[14] = 0
        currentvalstr = ''.join(map(str, currentvalue))
        self._modbusClient.writebitholding(addr=1328, listbitrec=currentvalue)
    
    def AcionaHermetico(self, **kwargs):
        '''
        Obter dados e acionar motor
        '''
        self._lock.acquire()
        currentvalue = Clientinit.readbitholding(self, addr=1328)
        self._lock.release()
        currentvalue[14] = 1
        currentvalstr = ''.join(map(str, currentvalue))
        self._modbusClient.writebitholding(addr=1328, listbitrec=currentvalue)

    def graphrealtime(self):
        TempGraphApp(data=self.data).run()
    """
    def showHistGraph(self, init, final):
        self.ids.init = str(init)
        self.ids.final = str(final)
        print(init)
        print(final)"
        """
