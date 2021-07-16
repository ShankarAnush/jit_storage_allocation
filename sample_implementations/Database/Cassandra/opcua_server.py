from time import sleep
import random
from opcua import Server

def main():
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")
    server.register_namespace("Digital-Twin")
    objects = server.get_objects_node()

    # object to be added
    tempsens = objects.add_object('ns=2;s="TS1"', "Temperature Sensor 1")

    # add variables to the object
    tempsens.add_variable('ns=2;s="TS1_VendorName"', "TS1 Vendor Name", "Sensor king")
    tempsens.add_variable('ns=2;s="TS1_SerialNumber"', "TS1 Serial Number", "12345678")
    temp = tempsens.add_variable('ns=2;s="TS1_Temperature"', "TS1 Temperature", "20")

    # add object bulb
    bulb = objects.add_object(2,"Light Bulb")

    # add state variable to bulb
    state = bulb.add_variable(2, "State of Light Bulb", False)
    state.set_writable()

    temperature = 20.0
    try:
        print("Start Server")
        server.start()
        print("Server Online")
        while True:
            temperature += random.uniform(-1, 1)
            temp.set_value(temperature)
            print("New Temperature: " +str(temp.get_value()))
            print("State of Light bulb: " + str(state.get_value()))
            sleep(2)
    finally:
        server.stop()
        print("Server Offline")




if __name__ == "__main__":
    main()

