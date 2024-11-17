from fastapi import FastAPI
from pysnmp.hlapi import *
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dispatch import AsyncioDispatcher

app = FastAPI()

# Configuration SNMP
snmpEngine = engine.SnmpEngine()
config.addV1System(snmpEngine, 'my-area', 'public')
transportTarget = UdpTransportTarget(('votre_hote_snmp', 161))

@app.get("/snmp_get/{oid}")
async def get_snmp_value(oid: str):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(snmpEngine,
              CommunityData('public'),
              UdpTransportTarget(('votre_hote_snmp', 161)),
              ObjectType(ObjectIdentity(oid)))
    )

    if errorIndication:
        print(errorIndication)
        return {"error": errorIndication}
    else:
        for varBind in varBinds:
            return {"value": varBind[1]}

# Démarrage du serveur FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)