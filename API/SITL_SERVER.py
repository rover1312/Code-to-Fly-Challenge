import socket
from dronekit import connect
import json
import dronekit_sitl
import select
from math import degrees


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


'''
@brief:
This class deals with Networking and uses TCP/IP Protocols (SOCKET STREAM)
Change accordingly
'''


class Network:
    # IP ADDRESS AND PORT NUMBER OF THE SERVER (MACHINE ON WHICH THIS SCRIPT IS RUNNING)
    def __init__(self, ip, port):
        self.CONNECTION_LIST = []
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ip, self.port)
        self.server.bind(self.server_address)
        self.server.listen(10)
        print(bcolors.FAIL + 'SERVER STARTED AT {0}:{1}'.format(self.ip, self.port) + bcolors.ENDC)

        self.CONNECTION_LIST.append(self.server)
        self.client = None

    """ Method to Send JSON Data """

    def send_data(self, d):

        try:
            if self.client.send(d):
                return True
            else:
                return False
        except ConnectionResetError:
            print("CLIENT OFFLINE...")
            self.client = None


''' 
@Brief:
Class which creates simulated Drone and send it's realtime data
'''


class Drone(Network):
    def __init__(self, ip, port, lat, lon):
        self.sitl = dronekit_sitl.start_default(lat, lon)
        self.connection_string = self.sitl.connection_string()
        print(bcolors.OKGREEN + bcolors.BOLD + ">>>> Connecting with the UAV <<<" + bcolors.ENDC)
        self.vehicle = connect(self.sitl.connection_string(), wait_ready=True)
        Network.__init__(self, ip, port)

    # return JSON OBJECT CONTAINING DRONE'S REALTIME DATA
    def get_data(self):
        data = dict()
        data['mode'] = self.vehicle.mode.name
        data['roll'] = degrees(self.vehicle.attitude.roll)
        data['pitch'] = degrees(self.vehicle.attitude.pitch)
        data['yaw'] = degrees(self.vehicle.attitude.yaw)
        data['heading'] = self.vehicle.heading
        data['long'] = self.vehicle.location.global_relative_frame.lon
        data['lat'] = self.vehicle.location.global_relative_frame.lat
        data['alt'] = self.vehicle.location.global_relative_frame.alt
        data_send = json.dumps(data)
        return data_send
        #return data


def run_server(drone):
    isconnected = True
    while isconnected:

        read_sockets, write_sockets, error_sockets = select.select(drone.CONNECTION_LIST, [], [])
        for sock in read_sockets:

            if sock == drone.server:
                # Handle the case in which there is a new connection recieved
                # through server
                drone.client, addr = drone.server.accept()
                drone.CONNECTION_LIST.append(drone.client)
                print(
                    bcolors.OKBLUE + bcolors.BOLD + bcolors.UNDERLINE + "Client (%s, %s) connected" % addr + bcolors.ENDC)

            else:

                try:
                    # Send JSON DATA TO WEB GCS whenever GCS request 'GET'
                    ack = drone.client.recv(1024).decode()
                    if ack == 'GET':
                        drone.send_data(drone.get_data().encode())

                except KeyboardInterrupt:
                    drone.server.close()
                    del drone
                    print('Server Stopped...')
                    exit()

                except ConnectionResetError:
                    drone.client.close()
                    drone.CONNECTION_LIST.remove(sock)
                    continue
                    print('Client disconnected !')
                    isconnected = False

