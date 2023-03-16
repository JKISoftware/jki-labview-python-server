import labview_api

labview_api.connect()

print(labview_api.Example.Echo("Hello World!"))

print(labview_api.Example.Add(1, 5))

labview_api.disconnect()

